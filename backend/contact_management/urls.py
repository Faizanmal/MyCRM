from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AccountViewSet,
    ContactGroupViewSet,
    ContactImportViewSet,
    ContactViewSet,
    MergeAuditLogViewSet,
)

router = DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'groups', ContactGroupViewSet, basename='contact-group')
router.register(r'imports', ContactImportViewSet, basename='contact-import')
router.register(r'merge-logs', MergeAuditLogViewSet, basename='merge-log')
router.register(r'', ContactViewSet, basename='contact-direct')

urlpatterns = [
    path('', include(router.urls)),
]
