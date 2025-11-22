from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, OrganizationMemberViewSet, OrganizationInvitationViewSet

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'members', OrganizationMemberViewSet, basename='organization-member')
router.register(r'invitations', OrganizationInvitationViewSet, basename='organization-invitation')

urlpatterns = [
    path('', include(router.urls)),
]
