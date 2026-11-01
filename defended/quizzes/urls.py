from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AttemptViewSet, QuestionViewSet

router = DefaultRouter()
router.register('questions', QuestionViewSet, basename='question')
router.register('attempts', AttemptViewSet, basename='attempt')

urlpatterns = [
    path('', include(router.urls)),
]
