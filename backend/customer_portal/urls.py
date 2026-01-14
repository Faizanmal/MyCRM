"""
Customer Portal URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomerOrderViewSet,
    CustomerProfileView,
    KnowledgeBaseViewSet,
    PortalAuthView,
    PortalDashboardView,
    PortalLogoutView,
    PortalNotificationViewSet,
    PortalPasswordResetView,
    SupportTicketViewSet,
)

app_name = 'customer_portal'

router = DefaultRouter()
router.register(r'tickets', SupportTicketViewSet, basename='tickets')
router.register(r'orders', CustomerOrderViewSet, basename='orders')
router.register(r'knowledge-base', KnowledgeBaseViewSet, basename='knowledge-base')
router.register(r'notifications', PortalNotificationViewSet, basename='notifications')

urlpatterns = [
    # Authentication
    path('auth/login/', PortalAuthView.as_view(), name='login'),
    path('auth/logout/', PortalLogoutView.as_view(), name='logout'),
    path('auth/password-reset/', PortalPasswordResetView.as_view(), name='password-reset'),

    # Profile
    path('profile/', CustomerProfileView.as_view(), name='profile'),

    # Dashboard
    path('dashboard/', PortalDashboardView.as_view(), name='dashboard'),

    # ViewSet routes
    path('', include(router.urls)),
]
