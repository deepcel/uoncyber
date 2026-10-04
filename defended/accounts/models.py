import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    ROLE_CHOICES = [
        ('USER', 'User'),
        ('OWNER', 'Module Owner'),
        ('ADMIN', 'Admin'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='USER'
    )

    is_2fa_enabled = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class User2FA(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='two_factor'
    )

    secret_key = models.CharField(
        max_length=255
    )

    enabled = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class MFAChallenge(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mfa_challenges'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()

    used = models.BooleanField(
        default=False
    )

class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    email_notifications = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.user.username

class LoginAttempt(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    ip_address = models.GenericIPAddressField()

    successful = models.BooleanField(
        default=False
    )

    failure_reason = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.ip_address