from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Enrollment, Module, ModuleSchedule, Pathway, Section, SectionProgress
from .serializers import (
    EnrollmentSerializer,
    ModuleSerializer,
    PathwaySerializer,
    ScheduleSerializer,
    SectionSerializer,
)


# Placeholder for "owns this module" until there is a real role system: is_staff stands in
# for "module owner", is_superuser stands in for "admin, manages every module". Swap this
# out once accounts.models.User has a real role field.
def _check_module_owner(request, module):
    if not request.user.is_staff:
        raise PermissionDenied('Module owner access required.')

    if not request.user.is_superuser and module.created_by_id != request.user.id:
        raise PermissionDenied('You do not manage this module.')


def _due_at_from_schedule(module):
    schedule = getattr(module, 'moduleschedule', None)

    if schedule is None:
        return None

    return timezone.now() + timezone.timedelta(days=schedule.initial_due_days)


class ModuleViewSet(viewsets.ModelViewSet):

    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Module.objects.select_related('created_by').prefetch_related('sections')
        user = self.request.user

        if user.is_superuser:
            return qs

        if user.is_staff:
            return qs.filter(Q(created_by=user) | Q(status='PUBLISHED'))

        return qs.filter(status='PUBLISHED')

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied('Module owner access required.')

        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        _check_module_owner(self.request, serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        _check_module_owner(self.request, instance)
        instance.delete()


class SectionViewSet(viewsets.ModelViewSet):

    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Section.objects.select_related('module').order_by('order', 'id')
        module_id = self.request.query_params.get('module')

        if module_id:
            qs = qs.filter(module_id=module_id)

        return qs

    def perform_create(self, serializer):
        _check_module_owner(self.request, serializer.validated_data['module'])
        serializer.save()

    def perform_update(self, serializer):
        _check_module_owner(self.request, serializer.instance.module)
        serializer.save()

    def perform_destroy(self, instance):
        _check_module_owner(self.request, instance.module)
        instance.delete()


class ModuleScheduleView(APIView):
    """GET/PUT the one schedule belonging to a module. PUT creates it the first time."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        module = get_object_or_404(Module, pk=pk)
        schedule = ModuleSchedule.objects.filter(module=module).first()

        if schedule is None:
            return Response(None)

        return Response(ScheduleSerializer(schedule).data)

    def put(self, request, pk):
        module = get_object_or_404(Module, pk=pk)
        _check_module_owner(request, module)

        schedule, _ = ModuleSchedule.objects.get_or_create(module=module)

        serializer = ScheduleSerializer(schedule, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class PathwayViewSet(viewsets.ModelViewSet):

    serializer_class = PathwaySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Pathway.objects.select_related('owner').prefetch_related('pathwaymodule_set__module')
        user = self.request.user

        if user.is_staff and not user.is_superuser:
            return qs.filter(owner=user)

        return qs

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied('Module owner access required.')

        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        self._check_owner(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        self._check_owner(instance)
        instance.delete()

    def _check_owner(self, pathway):
        user = self.request.user

        if not user.is_staff or (not user.is_superuser and pathway.owner_id != user.id):
            raise PermissionDenied('You do not manage this pathway.')

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        pathway = self.get_object()
        self._check_owner(pathway)

        user_ids = request.data.get('user_ids', [])
        modules = Module.objects.filter(
            id__in=pathway.pathwaymodule_set.values_list('module_id', flat=True)
        )

        created = []
        for module in modules:
            due_at = _due_at_from_schedule(module)

            for user_id in user_ids:
                enrollment, is_new = Enrollment.objects.get_or_create(
                    user_id=user_id,
                    module=module,
                    defaults={'source': 'PATHWAY', 'pathway': pathway, 'due_at': due_at}
                )
                if is_new:
                    created.append(enrollment)

        return Response({'enrolled': len(created)}, status=status.HTTP_201_CREATED)


class EnrollmentViewSet(viewsets.ModelViewSet):

    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Enrollment.objects.select_related('user', 'module', 'pathway')
        module_id = self.request.query_params.get('module')

        if module_id:
            module = get_object_or_404(Module, pk=module_id)
            _check_module_owner(self.request, module)
            return qs.filter(module=module)

        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        module = serializer.validated_data['module']

        if module.status != 'PUBLISHED':
            raise PermissionDenied('This module is not open for enrolment.')

        if not module.self_enroll_allowed:
            raise PermissionDenied('Self-enrolment is not allowed for this module. Ask the module owner to assign you.')

        if Enrollment.objects.filter(user=self.request.user, module=module).exists():
            raise ValidationError('You are already enrolled in this module.')

        serializer.save(
            user=self.request.user,
            source='SELF',
            due_at=serializer.validated_data.get('due_at') or _due_at_from_schedule(module)
        )

    @action(detail=False, methods=['post'])
    def assign(self, request):
        module = get_object_or_404(Module, pk=request.data.get('module'))
        _check_module_owner(request, module)

        user_ids = request.data.get('user_ids', [])
        due_at = _due_at_from_schedule(module)

        created = []
        for user_id in user_ids:
            enrollment, is_new = Enrollment.objects.get_or_create(
                user_id=user_id,
                module=module,
                defaults={'source': 'ADMIN', 'due_at': due_at}
            )
            if is_new:
                created.append(enrollment)

        return Response(
            EnrollmentSerializer(created, many=True).data,
            status=status.HTTP_201_CREATED
        )


class SectionCompleteView(APIView):
    """A learner marks a section as read. Idempotent — calling it twice is harmless."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        section = get_object_or_404(Section, pk=pk)
        SectionProgress.objects.get_or_create(user=request.user, section=section)
        return Response(status=status.HTTP_204_NO_CONTENT)