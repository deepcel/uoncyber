from datetime import timedelta

import base64
import hashlib
import io
import secrets

import pyotp
import qrcode

from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Max, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from audit_log.utils import client_ip, log_event
from notifications.utils import notify

from .models import User, User2FA, MFAChallenge, MFARecoveryCode, LoginAttempt
from .permissions import IsAdminRole
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    MFALoginSerializer,
    ConfirmIdentitySerializer,
    LogoutSerializer,
    UserSerializer,
    UserRoleSerializer,
)


RECOVERY_CODE_COUNT = 10

ROLE_LABELS = dict(User.ROLE_CHOICES)


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


def _normalise_username(username):
    return username.strip().lower()


def _is_locked_out(username):
    """Too many failed password/2FA attempts since the window began or the last successful login."""
    since = timezone.now() - settings.LOGIN_LOCKOUT_WINDOW
    attempts = LoginAttempt.objects.filter(username=_normalise_username(username))

    last_success = attempts.filter(
        successful=True,
        created_at__gt=since
    ).aggregate(Max("created_at"))["created_at__max"]

    failures = attempts.filter(
        successful=False,
        created_at__gt=last_success or since
    )

    return failures.count() >= settings.LOGIN_LOCKOUT_THRESHOLD


def _record_attempt(request, username, user, successful, reason=""):
    LoginAttempt.objects.create(
        username=_normalise_username(username),
        user=user,
        ip_address=client_ip(request),
        successful=successful,
        failure_reason=reason
    )


def _record_failure(request, username, user, reason, action):
    """Log a failed password or 2FA attempt. Returns True if this failure has just locked the account."""
    _record_attempt(request, username, user, False, reason)
    log_event(request, action, user=user, username=username)

    if _is_locked_out(username):
        log_event(request, "ACCOUNT_LOCKED", user=user, username=username)
        return True

    return False


def _locked_response():
    # Same response whether or not the username exists, so lockouts don't reveal accounts.
    return Response(
        {
            "message": "Too many failed attempts. Try again later."
        },
        status=status.HTTP_429_TOO_MANY_REQUESTS
    )


def _token_response(user):
    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "mfa_required": False,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
        status=status.HTTP_200_OK
    )


def _revoke_all_tokens(user):
    """Blacklist every refresh token issued to the user. Access tokens already issued live out their short lifetime."""
    BlacklistedToken.objects.bulk_create(
        [
            BlacklistedToken(token=token)
            for token in OutstandingToken.objects.filter(user=user, blacklistedtoken__isnull=True)
        ],
        ignore_conflicts=True
    )


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
        # Not counted towards lockout: someone holding a stolen access token could otherwise lock the
        # real user out. These endpoints are throttled instead.
        log_event(request, "MFA_FAILED", user=user, username=user.username, context="confirm_identity")

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
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"

    def perform_create(self, serializer):
        user = serializer.save()
        log_event(self.request, "USER_REGISTERED", user=user)


class LogoutView(APIView):
    """Blacklist a refresh token, or every refresh token the user holds with {"all": true}."""

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data["all"]:
            _revoke_all_tokens(request.user)
            log_event(request, "LOGOUT", user=request.user, all_sessions=True)

            return Response({
                "message": "Logged out of all sessions."
            })

        try:
            token = RefreshToken(serializer.validated_data["refresh"])
        except TokenError:
            token = None

        # Don't let one user revoke another's token, and don't reveal whether it was valid.
        if token is None or str(token.payload.get(jwt_settings.USER_ID_CLAIM)) != str(request.user.pk):
            return Response(
                {
                    "message": "Invalid or expired refresh token."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        token.blacklist()
        log_event(request, "LOGOUT", user=request.user, all_sessions=False)

        return Response({
            "message": "Logged out."
        })


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserSerializer(request.user)

        return Response(serializer.data)


def _is_last_admin(user):
    """True if removing this user's admin rights would leave no admins at all."""
    admins = User.objects.select_for_update().filter(
        Q(role="ADMIN") | Q(is_superuser=True)
    )

    return not admins.exclude(pk=user.pk).exists()


class UserListView(generics.ListAPIView):
    queryset = User.objects.order_by("id")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    @transaction.atomic
    def patch(self, request, pk):

        user = get_object_or_404(User, pk=pk)

        serializer = UserRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = serializer.validated_data["role"]

        # Demoting the last admin locks everyone out just like deleting them would.
        if role != "ADMIN" and _is_last_admin(user):
            return Response(
                {
                    "message": "Cannot remove the last admin."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        old_role = user.role

        user.role = role
        user.is_staff = role in ("OWNER", "ADMIN")
        user.is_superuser = role == "ADMIN"
        user.save(update_fields=["role", "is_staff", "is_superuser"])

        if role != old_role:
            log_event(
                request, "ROLE_CHANGED", user=request.user,
                target_id=user.pk, target_username=user.username, old_role=old_role, new_role=role
            )
            notify(
                user, "Your role has changed",
                f"An administrator changed your role from {ROLE_LABELS.get(old_role, old_role)} "
                f"to {ROLE_LABELS.get(role, role)}.",
                link="/"
            )

        return Response(UserSerializer(user).data)

    @transaction.atomic
    def delete(self, request, pk):

        user = get_object_or_404(User, pk=pk)

        if user.pk == request.user.pk:
            return Response(
                {
                    "message": "You cannot delete your own account."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if _is_last_admin(user):
            return Response(
                {
                    "message": "Cannot delete the last admin."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        log_event(
            request, "USER_DELETED", user=request.user,
            target_id=user.pk, target_username=user.username, target_email=user.email, target_role=user.role
        )

        _revoke_all_tokens(user)
        user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


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

            log_event(request, "2FA_ENABLED", user=user)

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
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        # Checked before the password, so a locked account can't be used to confirm a guess.
        if _is_locked_out(username):
            log_event(request, "LOGIN_BLOCKED", username=username)
            return _locked_response()

        user = authenticate(
            request=request,
            username=username,
            password=password
        )

        if user is None:
            known_user = User.objects.filter(username=username).first()

            if _record_failure(request, username, known_user, "BAD_PASSWORD", "LOGIN_FAILED"):
                return _locked_response()

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
        _record_attempt(request, username, user, True)
        log_event(request, "LOGIN_SUCCESS", user=user)

        return _token_response(user)


class MFALoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "mfa"

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

        # Lockout counts password and 2FA failures together, so logging in again with a
        # known password doesn't buy an attacker a fresh set of code guesses.
        if _is_locked_out(user.username):
            challenge.used = True
            challenge.save(update_fields=["used"])

            log_event(request, "LOGIN_BLOCKED", user=user, username=user.username)
            return _locked_response()

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

        method = "recovery_code" if serializer.validated_data.get("recovery_code") else "otp"

        if not _check_second_factor(user, twofa, serializer.validated_data):

            if _record_failure(request, user.username, user, "BAD_2FA_CODE", "MFA_FAILED"):
                challenge.used = True
                challenge.save(update_fields=["used"])
                return _locked_response()

            return Response(
                {
                    "message": "Invalid code."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Mark challenge as used
        challenge.used = True
        challenge.save(update_fields=["used"])

        _record_attempt(request, user.username, user, True)
        log_event(request, "MFA_SUCCESS", user=user, method=method)

        # Issue JWT only after successful MFA
        return _token_response(user)


class Disable2FAView(APIView):
    """Turn 2FA off, e.g. before moving to a new phone. Needs password plus a code."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "confirm_identity"

    def post(self, request):

        twofa, error = _confirm_identity(request)

        if error:
            return error

        _clear_2fa(request.user)
        log_event(request, "2FA_DISABLED", user=request.user)
        notify(
            request.user, "Two-factor authentication turned off",
            "2FA was turned off for your account. If this wasn't you, change your password "
            "and turn 2FA back on straight away.",
            link="/account"
        )

        return Response({
            "message": "2FA disabled"
        })


class RegenerateRecoveryCodesView(APIView):
    """Replace all recovery codes. Old codes stop working."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "confirm_identity"

    def post(self, request):

        twofa, error = _confirm_identity(request)

        if error:
            return error

        codes = _issue_recovery_codes(request.user)

        log_event(request, "RECOVERY_CODES_REGENERATED", user=request.user)
        notify(
            request.user, "New recovery codes created",
            "Your 2FA recovery codes were replaced. The old codes no longer work. "
            "If this wasn't you, change your password straight away.",
            link="/account"
        )

        return Response({
            "recovery_codes": codes
        })


class AdminReset2FAView(APIView):
    """For users who lost both their device and their recovery codes."""

    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, pk):

        user = get_object_or_404(User, pk=pk)

        _clear_2fa(user)

        # A lost device may be in someone else's hands: end every session the user has.
        _revoke_all_tokens(user)

        log_event(
            request, "2FA_RESET", user=request.user,
            target_id=user.pk, target_username=user.username
        )
        notify(
            user, "Your 2FA was reset",
            "An administrator reset two-factor authentication on your account and signed you out "
            "everywhere. Set up 2FA again from your account page.",
            link="/account/2fa/setup"
        )

        return Response({
            "message": f"2FA reset for {user.username}"
        })
