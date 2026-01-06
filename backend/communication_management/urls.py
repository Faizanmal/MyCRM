from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CommunicationLogViewSet,
    CommunicationRuleViewSet,
    CommunicationViewSet,
    EmailCampaignViewSet,
    EmailTemplateViewSet,
)

router = DefaultRouter()
router.register(r'communications', CommunicationViewSet)
router.register(r'email-templates', EmailTemplateViewSet)
router.register(r'email-campaigns', EmailCampaignViewSet)
router.register(r'communication-rules', CommunicationRuleViewSet)
router.register(r'communication-logs', CommunicationLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
