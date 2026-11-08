from django.db import models
from accounts.models import User


class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    title = models.CharField(
        max_length=255
    )

    message = models.TextField()

    # Frontend route to open when the notification is clicked, e.g. "/modules/3". Blank for none.
    link = models.CharField(
        max_length=255,
        blank=True,
        default=''
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-created_at', '-id']

    def __str__(self):
        return self.title