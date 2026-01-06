from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrganizationInvitationViewSet, OrganizationMemberViewSet, OrganizationViewSet

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'members', OrganizationMemberViewSet, basename='organization-member')
router.register(r'invitations', OrganizationInvitationViewSet, basename='organization-invitation')

urlpatterns = [
    path('', include(router.urls)),
]
