from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ABTestViewSet,
    AutomatedTriggerViewSet,
    EmailPersonalizationTokenViewSet,
    EmailSequenceViewSet,
    SequenceAnalyticsViewSet,
    SequenceEmailViewSet,
    SequenceEnrollmentViewSet,
    SequenceStepViewSet,
)

router = DefaultRouter()
router.register(r'sequences', EmailSequenceViewSet, basename='email-sequence')
router.register(r'steps', SequenceStepViewSet, basename='sequence-step')
router.register(r'emails', SequenceEmailViewSet, basename='sequence-email')
router.register(r'enrollments', SequenceEnrollmentViewSet, basename='sequence-enrollment')
router.register(r'ab-tests', ABTestViewSet, basename='ab-test')
router.register(r'triggers', AutomatedTriggerViewSet, basename='automated-trigger')
router.register(r'tokens', EmailPersonalizationTokenViewSet, basename='personalization-token')
router.register(r'analytics', SequenceAnalyticsViewSet, basename='sequence-analytics')

urlpatterns = [
    path('', include(router.urls)),
]
