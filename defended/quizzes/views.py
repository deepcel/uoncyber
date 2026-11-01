import random
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from audit_log.models import AuditLog
from modules.models import Enrollment, Module
from modules.permissions import check_can_author, check_module_owner, is_admin
from modules.serializers import parse_id

from .models import Attempt, AttemptAnswer, Question
from .serializers import AttemptSerializer, QuestionSerializer, SubmitAttemptSerializer


# Submissions this long after expires_at are still accepted, to allow for network delay.
SUBMIT_GRACE = timedelta(seconds=30)

FREQUENCY_DAYS = {
    'WEEKLY': 7,
    'FORTNIGHTLY': 14,
    'MONTHLY': 30,
    'QUARTERLY': 91,
    'SIX_MONTHLY': 182,
    'ANNUAL': 365,
}


def _next_due_at(module, passed_at):
    """When the module must be passed again, or None if it never recurs."""
    schedule = getattr(module, 'moduleschedule', None)

    if schedule is None or not schedule.is_active:
        return None

    if schedule.frequency == 'CUSTOM':
        days = schedule.custom_interval_days
    else:
        days = FREQUENCY_DAYS.get(schedule.frequency)

    return passed_at + timedelta(days=days) if days else None


def _expire_stale_attempts(user, module):
    """Close attempts whose time ran out without a submission. They score 0 and count as used."""
    now = timezone.now()

    Attempt.objects.filter(
        user=user,
        module=module,
        submitted_at__isnull=True,
        expires_at__lt=now - SUBMIT_GRACE
    ).update(submitted_at=now, score_percent=Decimal('0'), passed=False)


class QuestionViewSet(viewsets.ModelViewSet):
    """Question bank authoring. Owner of the module or ADMIN only - learners never see the answer key."""

    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        check_can_author(user)

        qs = Question.objects.select_related('module').prefetch_related('choices').order_by('order', 'id')

        if not is_admin(user):
            qs = qs.filter(module__created_by=user)

        module_id = self.request.query_params.get('module')

        if module_id:
            qs = qs.filter(module_id=parse_id(module_id, 'module'))

        return qs

    def perform_create(self, serializer):
        check_module_owner(self.request.user, serializer.validated_data['module'])
        serializer.save()

    def perform_update(self, serializer):
        check_module_owner(self.request.user, serializer.instance.module)

        if 'module' in serializer.validated_data:
            check_module_owner(self.request.user, serializer.validated_data['module'])

        serializer.save()

    def perform_destroy(self, instance):
        check_module_owner(self.request.user, instance.module)

        # Keep questions that appear in past attempts so learners' results stay intact.
        if AttemptAnswer.objects.filter(question=instance).exists():
            instance.is_active = False
            instance.save(update_fields=['is_active'])
        else:
            instance.delete()


class AttemptViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """
    POST   /attempts/              {"module": id}  start (or resume) an attempt
    GET    /attempts/              my attempts; ?module=<id> for everyone's (owner/admin)
    GET    /attempts/<id>/         questions while in progress, results once submitted
    POST   /attempts/<id>/submit/  {"answers": [{"question": id, "choices": [id, ...]}]}
    """

    serializer_class = AttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Attempt.objects.select_related('module', 'user').order_by('-started_at')
        module_id = self.request.query_params.get('module')

        if module_id and self.action == 'list':
            module = get_object_or_404(Module, pk=parse_id(module_id, 'module'))
            check_module_owner(self.request.user, module)
            return qs.filter(module=module)

        return qs.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        module = get_object_or_404(
            Module.objects.select_related('moduleschedule'),
            pk=parse_id(request.data.get('module'), 'module'),
            status='PUBLISHED'
        )
        user = request.user

        enrollment = Enrollment.objects.filter(user=user, module=module).first()

        if enrollment is None:
            raise PermissionDenied('You are not enrolled in this module.')

        _expire_stale_attempts(user, module)

        in_progress = Attempt.objects.filter(user=user, module=module, submitted_at__isnull=True).first()

        if in_progress is not None:
            return Response(self.get_serializer(in_progress).data, status=status.HTTP_200_OK)

        if module.max_attempts:
            # Attempts reset after a pass, so recurring training can be retaken next cycle.
            used = Attempt.objects.filter(user=user, module=module)

            if enrollment.last_passed_at:
                used = used.filter(started_at__gt=enrollment.last_passed_at)

            if used.count() >= module.max_attempts:
                raise PermissionDenied('No attempts remaining for this module.')

        questions = list(module.questions.filter(is_active=True).order_by('order', 'id'))

        if not questions:
            raise ValidationError('This module has no quiz questions yet.')

        if module.questions_per_attempt and module.questions_per_attempt < len(questions):
            questions = random.sample(questions, module.questions_per_attempt)

            if not module.shuffle_questions:
                questions.sort(key=lambda q: (q.order, q.id))

        elif module.shuffle_questions:
            random.shuffle(questions)

        with transaction.atomic():
            attempt = Attempt.objects.create(user=user, module=module)

            if module.time_limit_minutes:
                attempt.expires_at = attempt.started_at + timedelta(minutes=module.time_limit_minutes)
                attempt.save(update_fields=['expires_at'])

            AttemptAnswer.objects.bulk_create([
                AttemptAnswer(attempt=attempt, question=question, order=index)
                for index, question in enumerate(questions, start=1)
            ])

        return Response(self.get_serializer(attempt).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        serializer = SubmitAttemptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        submitted = {a['question']: set(a['choices']) for a in serializer.validated_data['answers']}

        with transaction.atomic():
            # Lock the row so a double-click can't grade the same attempt twice.
            attempt = get_object_or_404(
                Attempt.objects.select_for_update(of=('self',)).select_related('module__moduleschedule'),
                pk=pk,
                user=request.user
            )

            if attempt.submitted_at is not None:
                raise ValidationError('This attempt has already been submitted.')

            now = timezone.now()
            late = attempt.expires_at is not None and now > attempt.expires_at + SUBMIT_GRACE

            answers = list(attempt.answers.select_related('question').prefetch_related('question__choices'))
            served = {a.question_id for a in answers}

            unknown = set(submitted) - served
            if unknown:
                raise ValidationError(f'Questions not in this attempt: {sorted(unknown)}')

            total_points = 0
            awarded_points = 0

            for answer in answers:
                question = answer.question
                choice_ids = {c.id for c in question.choices.all()}
                correct_ids = {c.id for c in question.choices.all() if c.is_correct}
                selected = submitted.get(question.id, set())

                if not selected <= choice_ids:
                    raise ValidationError(f'Invalid choice for question {question.id}.')

                if question.question_type == 'SINGLE' and len(selected) > 1:
                    raise ValidationError(f'Question {question.id} takes a single choice.')

                # All-or-nothing: every correct choice and no wrong ones.
                answer.is_correct = not late and selected == correct_ids
                answer.points_awarded = question.points if answer.is_correct else 0
                answer.save(update_fields=['is_correct', 'points_awarded'])
                answer.selected_choices.set(selected)

                total_points += question.points
                awarded_points += answer.points_awarded

            score = (Decimal(awarded_points) * 100 / total_points).quantize(Decimal('0.01')) if total_points else Decimal('0')

            attempt.submitted_at = now
            attempt.score_percent = score
            attempt.passed = not late and score >= attempt.module.pass_mark
            attempt.save(update_fields=['submitted_at', 'score_percent', 'passed'])

            if attempt.passed:
                Enrollment.objects.filter(user=request.user, module=attempt.module).update(
                    last_passed_at=now,
                    due_at=_next_due_at(attempt.module, now)
                )

                AuditLog.objects.create(
                    user=request.user,
                    action='QUIZ_PASSED',
                    ip_address=request.META.get('REMOTE_ADDR', '0.0.0.0')
                )

        data = self.get_serializer(attempt).data

        if late:
            data['message'] = 'Time limit exceeded. The attempt was recorded as a fail.'

        return Response(data)
