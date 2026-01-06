from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ContactGroupViewSet, ContactImportViewSet, ContactViewSet

router = DefaultRouter()
router.register(r'contacts', ContactViewSet)
router.register(r'groups', ContactGroupViewSet)
router.register(r'imports', ContactImportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
