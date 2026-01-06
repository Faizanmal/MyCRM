"""
Customer Success URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'accounts', views.CustomerAccountViewSet, basename='customer-account')
router.register(r'playbooks', views.SuccessPlaybookViewSet, basename='playbook')
router.register(r'executions', views.PlaybookExecutionViewSet, basename='execution')
router.register(r'renewals', views.RenewalOpportunityViewSet, basename='renewal')
router.register(r'expansions', views.ExpansionOpportunityViewSet, basename='expansion')
router.register(r'nps', views.NPSSurveyViewSet, basename='nps')
router.register(r'analytics', views.CustomerSuccessAnalyticsViewSet, basename='cs-analytics')

urlpatterns = [
    path('', include(router.urls)),
]
