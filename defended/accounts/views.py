from datetime import timedelta

import base64
import io

import pyotp
import qrcode

from django.contrib.auth import authenticate
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User2FA, MFAChallenge
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    MFALoginSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class Generate2FAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user

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

        totp = pyotp.TOTP(twofa.secret_key)

        if totp.verify(str(otp), valid_window=1):

            twofa.enabled = True
            twofa.save(update_fields=["enabled"])

            user.is_2fa_enabled = True
            user.save(update_fields=["is_2fa_enabled"])

            return Response({
                "message": "2FA enabled"
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
        otp = serializer.validated_data["otp"]

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

        totp = pyotp.TOTP(twofa.secret_key)

        if not totp.verify(
            str(otp),
            valid_window=1
        ):

            return Response(
                {
                    "message": "Invalid OTP."
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