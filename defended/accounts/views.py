from datetime import timedelta

import base64
import hashlib
import io
import secrets

import pyotp
import qrcode

from django.contrib.auth import authenticate
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, User2FA, MFAChallenge, MFARecoveryCode
from .permissions import IsAdminRole
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    MFALoginSerializer,
    ConfirmIdentitySerializer,
    UserSerializer,
)


RECOVERY_CODE_COUNT = 10


def _hash_recovery_code(code):
    normalised = code.replace("-", "").replace(" ", "").upper()
    return hashlib.sha256(normalised.encode()).hexdigest()


@transaction.atomic
def _issue_recovery_codes(user):
    """Replace the user's recovery codes. The plain codes are returned once and never stored."""
    MFARecoveryCode.objects.filter(user=user).delete()

    codes = []
    for _ in range(RECOVERY_CODE_COUNT):
        raw = secrets.token_hex(5).upper()
        codes.append(f"{raw[:5]}-{raw[5:]}")

    MFARecoveryCode.objects.bulk_create([
        MFARecoveryCode(user=user, code_hash=_hash_recovery_code(code))
        for code in codes
    ])

    return codes


def _check_second_factor(user, twofa, data):
    """Check an authenticator code, or use up a recovery code."""
    if data.get("otp"):
        return pyotp.TOTP(twofa.secret_key).verify(str(data["otp"]), valid_window=1)

    # A single conditional UPDATE, so two simultaneous requests can't both spend the same code.
    used = MFARecoveryCode.objects.filter(
        user=user,
        code_hash=_hash_recovery_code(data["recovery_code"]),
        used_at__isnull=True
    ).update(used_at=timezone.now())

    return used == 1


@transaction.atomic
def _clear_2fa(user):
    User2FA.objects.filter(user=user).delete()
    MFARecoveryCode.objects.filter(user=user).delete()
    MFAChallenge.objects.filter(user=user).delete()

    user.is_2fa_enabled = False
    user.save(update_fields=["is_2fa_enabled"])


def _confirm_identity(request):
    """Password plus a second factor, for changes to an account that already has 2FA on."""
    serializer = ConfirmIdentitySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = request.user
    twofa = User2FA.objects.filter(user=user, enabled=True).first()

    if twofa is None:
        return None, Response(
            {
                "message": "2FA is not enabled."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not user.check_password(serializer.validated_data["password"]) or             not _check_second_factor(user, twofa, serializer.validated_data):
        return None, Response(
            {
                "message": "Invalid password or code."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    return twofa, None


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserSerializer(request.user)

        return Response(serializer.data)


class Generate2FAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user

        # Re-running setup while a code is still pending is fine, but once 2FA is on,
        # overwriting the secret would lock the user out.
        if User2FA.objects.filter(user=user, enabled=True).exists():
            return Response(
                {
                    "message": "2FA is already enabled."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        secret = pyotp.random_base32()

        User2FA.objects.update_or_create(
            user=user,
            defaults={
                "secret_key": secret,
                "enabled": False,
            }
        )

        return Response({
            "secret": secret
        })


class GenerateQRCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        try:
            twofa = User2FA.objects.get(user=user)
        except User2FA.DoesNotExist:
            return Response(
                {
                    "message": "2FA has not been set up yet."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Once enabled, the secret must not be retrievable again.
        if twofa.enabled:
            return Response(
                {
                    "message": "2FA is already enabled."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        totp = pyotp.TOTP(twofa.secret_key)

        uri = totp.provisioning_uri(
            name=user.email,
            issuer_name="DefendEd"
        )

        qr = qrcode.make(uri)

        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")

        qr_base64 = base64.b64encode(
            buffer.getvalue()
        ).decode()

        return Response({
            "qr_code": qr_base64
        })


class Verify2FAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        otp = request.data.get("otp")

        if not otp:
            return Response(
                {
                    "message": "OTP is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user

        try:
            twofa = User2FA.objects.get(user=user)
        except User2FA.DoesNotExist:
            return Response(
                {
                    "message": "2FA has not been set up yet."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if twofa.enabled:
            return Response(
                {
                    "message": "2FA is already enabled."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        totp = pyotp.TOTP(twofa.secret_key)

        if totp.verify(str(otp), valid_window=1):

            twofa.enabled = True
            twofa.save(update_fields=["enabled"])

            user.is_2fa_enabled = True
            user.save(update_fields=["is_2fa_enabled"])

            return Response({
                "message": "2FA enabled",
                "recovery_codes": _issue_recovery_codes(user),
            })

        return Response(
            {
                "message": "Invalid OTP"
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(
            request=request,
            username=username,
            password=password
        )

        if user is None:
            return Response(
                {
                    "message": "Invalid username or password."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {
                    "message": "User account is disabled."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # MFA is enabled for this user
        if user.is_2fa_enabled:

            # Remove previous unused challenges
            MFAChallenge.objects.filter(
                user=user,
                used=False
            ).delete()

            challenge = MFAChallenge.objects.create(
                user=user,
                expires_at=(
                    timezone.now()
                    + timedelta(minutes=5)
                )
            )

            return Response(
                {
                    "mfa_required": True,
                    "challenge_id": str(challenge.id),
                    "message": "MFA verification required."
                },
                status=status.HTTP_200_OK
            )

        # MFA is not enabled
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "mfa_required": False,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK
        )


class MFALoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = MFALoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        challenge_id = serializer.validated_data["challenge_id"]

        try:
            challenge = MFAChallenge.objects.select_related(
                "user"
            ).get(
                id=challenge_id,
                used=False
            )

        except MFAChallenge.DoesNotExist:

            return Response(
                {
                    "message": "Invalid or expired MFA challenge."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check expiration
        if timezone.now() > challenge.expires_at:

            challenge.used = True
            challenge.save(update_fields=["used"])

            return Response(
                {
                    "message": "MFA challenge has expired."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = challenge.user

        try:
            twofa = User2FA.objects.get(user=user)

        except User2FA.DoesNotExist:

            return Response(
                {
                    "message": "2FA is not configured."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not twofa.enabled:

            return Response(
                {
                    "message": "2FA is not enabled."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not _check_second_factor(user, twofa, serializer.validated_data):

            return Response(
                {
                    "message": "Invalid code."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Mark challenge as used
        challenge.used = True
        challenge.save(update_fields=["used"])

        # Issue JWT only after successful MFA
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "mfa_required": False,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK
        )


class Disable2FAView(APIView):
    """Turn 2FA off, e.g. before moving to a new phone. Needs password plus a code."""

    permission_classes = [IsAuthenticated]

    def post(self, request):

        twofa, error = _confirm_identity(request)

        if error:
            return error

        _clear_2fa(request.user)

        return Response({
            "message": "2FA disabled"
        })


class RegenerateRecoveryCodesView(APIView):
    """Replace all recovery codes. Old codes stop working."""

    permission_classes = [IsAuthenticated]

    def post(self, request):

        twofa, error = _confirm_identity(request)

        if error:
            return error

        return Response({
            "recovery_codes": _issue_recovery_codes(request.user)
        })


class AdminReset2FAView(APIView):
    """For users who lost both their device and their recovery codes."""

    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, pk):

        user = get_object_or_404(User, pk=pk)

        _clear_2fa(user)

        return Response({
            "message": f"2FA reset for {user.username}"
        })
