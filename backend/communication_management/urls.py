from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommunicationViewSet, EmailTemplateViewSet, EmailCampaignViewSet,
    CommunicationRuleViewSet, CommunicationLogViewSet
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
