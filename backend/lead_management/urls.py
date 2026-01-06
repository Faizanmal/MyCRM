from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LeadActivityViewSet,
    LeadAssignmentRuleViewSet,
    LeadConversionViewSet,
    LeadViewSet,
)

router = DefaultRouter()
router.register(r'leads', LeadViewSet)
router.register(r'activities', LeadActivityViewSet)
router.register(r'assignment-rules', LeadAssignmentRuleViewSet)
router.register(r'conversions', LeadConversionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
