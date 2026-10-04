from django.db import models
from accounts.models import User

class Module(models.Model):

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('ARCHIVED', 'Archived'),
    ]

    title = models.CharField(max_length=255)

    slug = models.SlugField(
        unique=True,
    )

    summary = models.TextField(
        blank=True
    )

    description = models.TextField()

    category = models.CharField(
        max_length=100
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )

    pass_mark = models.IntegerField(
        default=80
    )

    max_attempts = models.IntegerField(
        null=True,
        blank=True
    )

    time_limit_minutes = models.IntegerField(
        null=True,
        blank=True
    )

    questions_per_attempt = models.IntegerField(
        null=True,
        blank=True
    )

    shuffle_questions = models.BooleanField(
        default=False
    )

    self_enroll_allowed = models.BooleanField(
        default=True
    )

    estimated_minutes = models.IntegerField(
        null=True,
        blank=True
    )

    version = models.IntegerField(
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title


class Section(models.Model):

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='sections'
    )

    title = models.CharField(
        max_length=255
    )

    body = models.TextField()

    order = models.PositiveIntegerField(
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title

class Pathway(models.Model):

    name = models.CharField(
        max_length=255
    )

    description = models.TextField()

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name

class PathwayModule(models.Model):

    pathway = models.ForeignKey(
        Pathway,
        on_delete=models.CASCADE
    )

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE
    )

    order = models.PositiveIntegerField(
        default=1
    )

    class Meta:
        unique_together = ('pathway', 'module')

    def __str__(self):
        return f"{self.pathway.name} - {self.module.title}"

class Enrollment(models.Model):

    SOURCE_CHOICES = [
        ('SELF', 'Self Assigned'),
        ('ADMIN', 'Admin Assigned'),
        ('PATHWAY', 'Pathway')
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE
    )

    pathway = models.ForeignKey(
        Pathway,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='SELF'
    )

    enrolled_at = models.DateTimeField(
        auto_now_add=True
    )

    due_at = models.DateTimeField(
        null=True,
        blank=True
    )

    last_passed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('user', 'module')

    def __str__(self):
        return f"{self.user.username} - {self.module.title}"

class SectionProgress(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE
    )

    completed_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ('user', 'section')


class ModuleSchedule(models.Model):

    FREQUENCY_CHOICES = [
        ('ONCE', 'Once'),
        ('WEEKLY', 'Weekly'),
        ('FORTNIGHTLY', 'Fortnightly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('SIX_MONTHLY', 'Every 6 Months'),
        ('ANNUAL', 'Annual'),
        ('CUSTOM', 'Custom'),
    ]

    module = models.OneToOneField(
        Module,
        on_delete=models.CASCADE
    )

    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='ANNUAL'
    )

    custom_interval_days = models.IntegerField(
        null=True,
        blank=True
    )

    initial_due_days = models.IntegerField(
        default=30
    )

    reminder_days_before = models.IntegerField(
        default=7
    )

    overdue_reminder_days = models.IntegerField(
        default=3
    )

    is_active = models.BooleanField(
        default=True
    )