from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet, LeadActivityViewSet, LeadAssignmentRuleViewSet, LeadConversionViewSet

router = DefaultRouter()
router.register(r'leads', LeadViewSet)
router.register(r'activities', LeadActivityViewSet)
router.register(r'assignment-rules', LeadAssignmentRuleViewSet)
router.register(r'conversions', LeadConversionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
