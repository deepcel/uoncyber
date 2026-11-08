from django.db import models
from accounts.models import User


class AuditLog(models.Model):

    ACTIONS = [
        ('LOGIN_SUCCESS', 'Login Success'),
        ('LOGIN_FAILED', 'Login Failed'),
        ('LOGIN_BLOCKED', 'Login Blocked (Locked Out)'),
        ('ACCOUNT_LOCKED', 'Account Locked'),
        ('MFA_SUCCESS', 'MFA Success'),
        ('MFA_FAILED', 'MFA Failed'),
        ('LOGOUT', 'Logout'),
        ('USER_REGISTERED', 'User Registered'),
        ('2FA_ENABLED', '2FA Enabled'),
        ('2FA_DISABLED', '2FA Disabled'),
        ('2FA_RESET', '2FA Reset by Admin'),
        ('RECOVERY_CODES_REGENERATED', 'Recovery Codes Regenerated'),
        ('ROLE_CHANGED', 'Role Changed'),
        ('USER_DELETED', 'User Deleted'),
        ('MODULE_CREATED', 'Module Created'),
        ('QUIZ_PASSED', 'Quiz Passed'),
    ]

    # Who performed the action (null for anonymous/failed logins of unknown users).
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action = models.CharField(
        max_length=50,
        choices=ACTIONS
    )

    ip_address = models.GenericIPAddressField()

    # Context such as the target user, old/new role or attempted username.
    # Stored as plain values so it survives the target being deleted.
    details = models.JSONField(
        default=dict,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.action
