from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SSOCallbackView, SSOLoginAttemptViewSet, SSOProviderViewSet, SSOSessionViewSet

router = DefaultRouter()
router.register(r'providers', SSOProviderViewSet, basename='sso-provider')
router.register(r'sessions', SSOSessionViewSet, basename='sso-session')
router.register(r'attempts', SSOLoginAttemptViewSet, basename='sso-attempt')
router.register(r'callback', SSOCallbackView, basename='sso-callback')

urlpatterns = [
    path('', include(router.urls)),
]
