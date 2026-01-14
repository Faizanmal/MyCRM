"""
App Marketplace URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AppCategoryViewSet,
    DeveloperPortalViewSet,
    MarketplaceAppViewSet,
    MarketplaceDashboardView,
    MyAppsViewSet,
)

app_name = 'app_marketplace'

router = DefaultRouter()
router.register(r'categories', AppCategoryViewSet, basename='categories')
router.register(r'apps', MarketplaceAppViewSet, basename='apps')
router.register(r'my-apps', MyAppsViewSet, basename='my-apps')
router.register(r'developer', DeveloperPortalViewSet, basename='developer')

urlpatterns = [
    path('dashboard/', MarketplaceDashboardView.as_view(), name='dashboard'),
    path('', include(router.urls)),
]
