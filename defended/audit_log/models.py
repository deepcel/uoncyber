from django.db import models
from accounts.models import User


class AuditLog(models.Model):

    ACTIONS = [
        ('LOGIN_SUCCESS', 'Login Success'),
        ('LOGIN_FAILED', 'Login Failed'),
        ('MFA_SUCCESS', 'MFA Success'),
        ('MFA_FAILED', 'MFA Failed'),
        ('MODULE_CREATED', 'Module Created'),
        ('QUIZ_PASSED', 'Quiz Passed'),
    ]

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

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.action