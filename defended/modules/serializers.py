from django.utils import timezone
from django.utils.text import slugify

from rest_framework import serializers

from .models import (
    Module,
    Section,
    Pathway,
    PathwayModule,
    Enrollment,
    SectionProgress,
    ModuleSchedule,
)


def generate_unique_slug(title):
    base = slugify(title)[:44]
    slug = base

    n = 2
    while Module.objects.filter(slug=slug).exists():
        slug = f"{base}-{n}"
        n += 1

    return slug


class UserBriefSerializer(serializers.Serializer):

    id = serializers.IntegerField()

    username = serializers.CharField()


class SectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Section
        fields = ['id', 'module', 'title', 'body', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class ScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = ModuleSchedule
        fields = [
            'id',
            'frequency',
            'custom_interval_days',
            'initial_due_days',
            'reminder_days_before',
            'overdue_reminder_days',
            'is_active',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        frequency = attrs.get('frequency', getattr(self.instance, 'frequency', None))
        custom_days = attrs.get('custom_interval_days', getattr(self.instance, 'custom_interval_days', None))

        if frequency == 'CUSTOM' and not custom_days:
            raise serializers.ValidationError(
                {'custom_interval_days': 'Required when frequency is CUSTOM.'}
            )

        return attrs


class ModuleSerializer(serializers.ModelSerializer):

    created_by = UserBriefSerializer(read_only=True)

    sections = SectionSerializer(many=True, read_only=True)

    schedule = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = [
            'id',
            'title',
            'slug',
            'summary',
            'description',
            'category',
            'created_by',
            'status',
            'pass_mark',
            'max_attempts',
            'time_limit_minutes',
            'questions_per_attempt',
            'shuffle_questions',
            'self_enroll_allowed',
            'estimated_minutes',
            'version',
            'sections',
            'schedule',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_by', 'version', 'created_at', 'updated_at']

    def get_schedule(self, obj):
        try:
            return ScheduleSerializer(obj.moduleschedule).data
        except ModuleSchedule.DoesNotExist:
            return None

    def validate_pass_mark(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError('Must be between 0 and 100.')
        return value

    def create(self, validated_data):
        validated_data['slug'] = generate_unique_slug(validated_data['title'])
        return super().create(validated_data)


class PathwayModuleSerializer(serializers.ModelSerializer):

    module_title = serializers.CharField(source='module.title', read_only=True)

    class Meta:
        model = PathwayModule
        fields = ['id', 'module', 'module_title', 'order']
        read_only_fields = ['id', 'module_title']


class PathwaySerializer(serializers.ModelSerializer):

    owner = UserBriefSerializer(read_only=True)

    modules = serializers.SerializerMethodField()

    module_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Pathway
        fields = ['id', 'name', 'description', 'owner', 'modules', 'module_ids', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']

    def get_modules(self, obj):
        links = obj.pathwaymodule_set.select_related('module').order_by('order')
        return PathwayModuleSerializer(links, many=True).data

    def validate_module_ids(self, value):
        if Module.objects.filter(id__in=value).count() != len(set(value)):
            raise serializers.ValidationError('One or more modules were not found.')
        return value

    def create(self, validated_data):
        module_ids = validated_data.pop('module_ids', [])
        pathway = super().create(validated_data)
        self._sync_modules(pathway, module_ids)
        return pathway

    def update(self, instance, validated_data):
        module_ids = validated_data.pop('module_ids', None)
        pathway = super().update(instance, validated_data)
        if module_ids is not None:
            self._sync_modules(pathway, module_ids)
        return pathway

    def _sync_modules(self, pathway, module_ids):
        PathwayModule.objects.filter(pathway=pathway).delete()
        PathwayModule.objects.bulk_create([
            PathwayModule(pathway=pathway, module_id=module_id, order=index)
            for index, module_id in enumerate(module_ids)
        ])


class EnrollmentSerializer(serializers.ModelSerializer):

    user = UserBriefSerializer(read_only=True)

    module_title = serializers.CharField(source='module.title', read_only=True)

    pathway_name = serializers.CharField(source='pathway.name', read_only=True, default=None)

    status = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = [
            'id',
            'user',
            'module',
            'module_title',
            'pathway',
            'pathway_name',
            'source',
            'enrolled_at',
            'due_at',
            'last_passed_at',
            'status',
        ]
        read_only_fields = ['id', 'user', 'module_title', 'pathway_name', 'enrolled_at', 'last_passed_at', 'status']

    def get_status(self, obj):
        if obj.due_at is None:
            return 'PENDING'

        now = timezone.now()

        if obj.due_at < now:
            return 'OVERDUE'

        schedule = getattr(obj.module, 'moduleschedule', None)
        warn_days = schedule.reminder_days_before if schedule else 7

        if obj.due_at - now <= timezone.timedelta(days=warn_days):
            return 'DUE_SOON'

        return 'COMPLIANT'

    def create(self, validated_data):
        module = validated_data['module']

        if validated_data.get('due_at') is None:
            schedule = getattr(module, 'moduleschedule', None)
            if schedule:
                validated_data['due_at'] = timezone.now() + timezone.timedelta(days=schedule.initial_due_days)

        return super().create(validated_data)


class SectionProgressSerializer(serializers.ModelSerializer):

    user = UserBriefSerializer(read_only=True)

    class Meta:
        model = SectionProgress
        fields = ['id', 'user', 'section', 'completed_at']
        read_only_fields = ['id', 'user', 'completed_at']