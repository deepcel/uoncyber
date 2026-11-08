from django.db import transaction

from rest_framework import serializers

from modules.serializers import EnrollmentSerializer

from .models import Attempt, AttemptAnswer, Choice, Question


# Authoring (module owners / admins) - includes the answers.

class ChoiceSerializer(serializers.ModelSerializer):

    # Writable so an update can match existing choices by id.
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct', 'order']


class QuestionSerializer(serializers.ModelSerializer):

    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = [
            'id',
            'module',
            'text',
            'question_type',
            'explanation',
            'points',
            'order',
            'is_active',
            'choices',
        ]
        read_only_fields = ['id']

    def validate_points(self, value):
        if value < 1:
            raise serializers.ValidationError('Must be at least 1.')
        return value

    def validate(self, attrs):
        question_type = attrs.get('question_type', getattr(self.instance, 'question_type', None))
        choices = attrs.get('choices')

        if choices is None:
            if self.instance is None:
                raise serializers.ValidationError({'choices': 'This field is required.'})

            # Partial update without choices: re-check the type against the stored choices.
            correct = self.instance.choices.filter(is_correct=True).count()
            total = self.instance.choices.count()
        else:
            correct = sum(1 for c in choices if c.get('is_correct'))
            total = len(choices)

        if total < 2:
            raise serializers.ValidationError({'choices': 'A question needs at least two choices.'})

        if question_type == 'SINGLE' and correct != 1:
            raise serializers.ValidationError({'choices': 'A SINGLE question needs exactly one correct choice.'})

        if question_type == 'MULTIPLE' and correct < 1:
            raise serializers.ValidationError({'choices': 'A MULTIPLE question needs at least one correct choice.'})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        choices = validated_data.pop('choices')
        question = Question.objects.create(**validated_data)

        Choice.objects.bulk_create([
            Choice(question=question, **{k: v for k, v in c.items() if k != 'id'})
            for c in choices
        ])

        return question

    @transaction.atomic
    def update(self, instance, validated_data):
        choices = validated_data.pop('choices', None)
        question = super().update(instance, validated_data)

        if choices is not None:
            self._sync_choices(question, choices)

        return question

    def _sync_choices(self, question, choices):
        """Update choices sent with an id, create those without, delete the rest."""
        existing = {c.id: c for c in question.choices.all()}
        keep = set()

        for data in choices:
            choice_id = data.pop('id', None)

            if choice_id is not None:
                choice = existing.get(choice_id)

                if choice is None:
                    raise serializers.ValidationError(
                        {'choices': f'Choice {choice_id} does not belong to this question.'}
                    )

                for field, value in data.items():
                    setattr(choice, field, value)
                choice.save()
                keep.add(choice_id)
            else:
                keep.add(Choice.objects.create(question=question, **data).id)

        question.choices.exclude(id__in=keep).delete()


# Taking a quiz (learners) - never exposes is_correct.

class LearnerChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Choice
        fields = ['id', 'text']


class LearnerQuestionSerializer(serializers.ModelSerializer):

    choices = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'points', 'choices']

    def get_choices(self, obj):
        return LearnerChoiceSerializer(obj.choices.order_by('order', 'id'), many=True).data


class AttemptResultSerializer(serializers.ModelSerializer):
    """Per-question outcome after submitting. Shows right/wrong and the explanation, not the answer key."""

    question = serializers.CharField(source='question.text')

    explanation = serializers.CharField(source='question.explanation')

    selected_choices = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = AttemptAnswer
        fields = ['question', 'selected_choices', 'is_correct', 'points_awarded', 'explanation']


class AttemptSerializer(serializers.ModelSerializer):

    module_title = serializers.CharField(source='module.title', read_only=True)

    username = serializers.CharField(source='user.username', read_only=True)

    pass_mark = serializers.IntegerField(source='module.pass_mark', read_only=True)

    questions = serializers.SerializerMethodField()

    results = serializers.SerializerMethodField()

    class Meta:
        model = Attempt
        fields = [
            'id',
            'module',
            'module_title',
            'username',
            'started_at',
            'expires_at',
            'submitted_at',
            'score_percent',
            'pass_mark',
            'passed',
            'questions',
            'results',
        ]
        read_only_fields = fields

    def get_questions(self, obj):
        if obj.submitted_at is not None:
            return None

        answers = obj.answers.select_related('question').prefetch_related('question__choices')
        return LearnerQuestionSerializer([a.question for a in answers], many=True).data

    def get_results(self, obj):
        if obj.submitted_at is None:
            return None

        answers = obj.answers.select_related('question').prefetch_related('selected_choices')
        return AttemptResultSerializer(answers, many=True).data


class AnswerInputSerializer(serializers.Serializer):

    question = serializers.IntegerField()

    choices = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True
    )


class SubmitAttemptSerializer(serializers.Serializer):

    answers = AnswerInputSerializer(many=True)


class GradebookSerializer(EnrollmentSerializer):
    """An enrollment plus a summary of the learner's submitted attempts (from GradebookView's annotations)."""

    attempts_count = serializers.IntegerField(read_only=True)

    best_score = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    latest_score = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    latest_passed = serializers.BooleanField(read_only=True, allow_null=True)

    latest_attempt_id = serializers.IntegerField(read_only=True)

    latest_submitted_at = serializers.DateTimeField(read_only=True)

    class Meta(EnrollmentSerializer.Meta):
        fields = EnrollmentSerializer.Meta.fields + [
            'attempts_count',
            'best_score',
            'latest_score',
            'latest_passed',
            'latest_attempt_id',
            'latest_submitted_at',
        ]
        read_only_fields = fields
