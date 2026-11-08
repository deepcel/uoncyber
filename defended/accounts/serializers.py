from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from rest_framework_simplejwt.serializers import TokenRefreshSerializer


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password"
        ]

    def validate(self, attrs):
        # create_user() doesn't run AUTH_PASSWORD_VALIDATORS, so do it here. The unsaved user lets
        # UserAttributeSimilarityValidator reject passwords close to the username or email.
        candidate = User(username=attrs["username"], email=attrs["email"])

        try:
            validate_password(attrs["password"], user=candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})

        return attrs

    def create(self, validated_data):

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )

        return user


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()

    password = serializers.CharField(
        write_only=True
    )


class SecondFactorSerializer(serializers.Serializer):
    """Either a 6-digit authenticator code or a one-time recovery code."""

    otp = serializers.CharField(
        min_length=6,
        max_length=6,
        required=False
    )

    recovery_code = serializers.CharField(
        max_length=32,
        required=False
    )

    def validate(self, attrs):
        if bool(attrs.get("otp")) == bool(attrs.get("recovery_code")):
            raise serializers.ValidationError(
                "Provide either otp or recovery_code."
            )

        return attrs


class MFALoginSerializer(SecondFactorSerializer):

    challenge_id = serializers.UUIDField()


class ConfirmIdentitySerializer(SecondFactorSerializer):

    password = serializers.CharField(
        write_only=True
    )

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "is_2fa_enabled",
        ]
        read_only_fields = fields


class SafeTokenRefreshSerializer(TokenRefreshSerializer):
    """simplejwt looks the user up with .get(), so a deleted user's refresh token would 500."""

    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except User.DoesNotExist:
            raise AuthenticationFailed(
                "No active account found for the given token.",
                "no_active_account"
            )


class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField(
        required=False
    )

    # End every session for this user, not just the one holding this refresh token.
    all = serializers.BooleanField(
        default=False
    )

    def validate(self, attrs):
        if not attrs["all"] and not attrs.get("refresh"):
            raise serializers.ValidationError(
                "Provide refresh, or set all to true."
            )

        return attrs


class UserRoleSerializer(serializers.Serializer):

    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES
    )
