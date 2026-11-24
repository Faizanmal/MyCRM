from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AuditLogViewSet,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    PermissionViewSet,
    RolePermissionViewSet,
    TwoFactorLoginVerifyView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'role-permissions', RolePermissionViewSet)
router.register(r'audit-logs', AuditLogViewSet)

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('verify-2fa/', TwoFactorLoginVerifyView.as_view(), name='verify_2fa_login'),
    path('', include(router.urls)),
]
