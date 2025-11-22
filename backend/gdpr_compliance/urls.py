from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConsentTypeViewSet, UserConsentViewSet, DataExportRequestViewSet,
    DataDeletionRequestViewSet, DataProcessingActivityViewSet,
    DataBreachIncidentViewSet, DataAccessLogViewSet,
    PrivacyNoticeViewSet, UserPrivacyPreferenceViewSet
)

app_name = 'gdpr_compliance'

router = DefaultRouter()
router.register(r'consent-types', ConsentTypeViewSet, basename='consenttype')
router.register(r'user-consents', UserConsentViewSet, basename='userconsent')
router.register(r'export-requests', DataExportRequestViewSet, basename='exportrequest')
router.register(r'deletion-requests', DataDeletionRequestViewSet, basename='deletionrequest')
router.register(r'processing-activities', DataProcessingActivityViewSet, basename='processingactivity')
router.register(r'breach-incidents', DataBreachIncidentViewSet, basename='breachincident')
router.register(r'access-logs', DataAccessLogViewSet, basename='accesslog')
router.register(r'privacy-notices', PrivacyNoticeViewSet, basename='privacynotice')
router.register(r'privacy-preferences', UserPrivacyPreferenceViewSet, basename='privacypreference')

urlpatterns = [
    path('', include(router.urls)),
]
