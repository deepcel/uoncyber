from django.contrib.auth import get_user_model

from rest_framework import serializers


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
