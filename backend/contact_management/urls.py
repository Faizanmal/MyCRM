from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactViewSet, ContactGroupViewSet, ContactImportViewSet

router = DefaultRouter()
router.register(r'contacts', ContactViewSet)
router.register(r'groups', ContactGroupViewSet)
router.register(r'imports', ContactImportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
