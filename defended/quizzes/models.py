from django.db import models
from accounts.models import User
from modules.models import Module


class Question(models.Model):

    QUESTION_TYPES = [
        ('SINGLE', 'Single Choice'),
        ('MULTIPLE', 'Multiple Choice'),
    ]

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='questions'
    )

    text = models.TextField()

    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES
    )

    explanation = models.TextField(
        blank=True
    )

    points = models.IntegerField(
        default=1
    )

    order = models.IntegerField(
        default=1
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.text[:50]


class Choice(models.Model):

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )

    text = models.CharField(
        max_length=500
    )

    is_correct = models.BooleanField(
        default=False
    )

    order = models.IntegerField(
        default=1
    )

    def __str__(self):
        return self.text


class Attempt(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE
    )

    started_at = models.DateTimeField(
        auto_now_add=True
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    score_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    passed = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.user.username} - {self.module.title}"


class AttemptAnswer(models.Model):

    attempt = models.ForeignKey(
        Attempt,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    is_correct = models.BooleanField(
        default=False
    )

    points_awarded = models.IntegerField(
        default=0
    )