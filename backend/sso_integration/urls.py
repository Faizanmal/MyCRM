from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SSOProviderViewSet,
    SSOSessionViewSet,
    SSOLoginAttemptViewSet,
    SSOCallbackView
)

router = DefaultRouter()
router.register(r'providers', SSOProviderViewSet, basename='sso-provider')
router.register(r'sessions', SSOSessionViewSet, basename='sso-session')
router.register(r'attempts', SSOLoginAttemptViewSet, basename='sso-attempt')
router.register(r'callback', SSOCallbackView, basename='sso-callback')

urlpatterns = [
    path('', include(router.urls)),
]
