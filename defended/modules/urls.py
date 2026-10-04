from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EnrollmentViewSet,
    ModuleScheduleView,
    ModuleViewSet,
    PathwayViewSet,
    SectionCompleteView,
    SectionViewSet,
)

router = DefaultRouter()
router.register('modules', ModuleViewSet, basename='module')
router.register('sections', SectionViewSet, basename='section')
router.register('pathways', PathwayViewSet, basename='pathway')
router.register('enrollments', EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
    path('modules/<int:pk>/schedule/', ModuleScheduleView.as_view(), name='module-schedule'),
    path('sections/<int:pk>/complete/', SectionCompleteView.as_view(), name='section-complete'),
]