"""
Campaign Management URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CampaignViewSet, CampaignSegmentViewSet,
    CampaignRecipientViewSet, EmailTemplateViewSet
)

router = DefaultRouter()
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'segments', CampaignSegmentViewSet, basename='segment')
router.register(r'recipients', CampaignRecipientViewSet, basename='recipient')
router.register(r'templates', EmailTemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
]
