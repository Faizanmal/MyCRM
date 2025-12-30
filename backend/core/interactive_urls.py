"""
Interactive Features URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .interactive_views import (
    UserPreferencesViewSet,
    OnboardingProgressViewSet,
    AIRecommendationViewSet,
    GlobalSearchView,
    SmartFilterViewSet,
    QuickActionViewSet,
    RecentSearchesView
)

router = DefaultRouter()
router.register(r'preferences', UserPreferencesViewSet, basename='user-preferences')
router.register(r'onboarding', OnboardingProgressViewSet, basename='onboarding')
router.register(r'recommendations', AIRecommendationViewSet, basename='ai-recommendations')
router.register(r'smart-filters', SmartFilterViewSet, basename='smart-filters')
router.register(r'quick-actions', QuickActionViewSet, basename='quick-actions')

urlpatterns = [
    path('', include(router.urls)),
    
    # Global search
    path('search/', GlobalSearchView.as_view(), name='global-search'),
    
    # Recent searches
    path('search/recent/', RecentSearchesView.as_view(), name='recent-searches'),
    
    # Convenience endpoints for preferences
    path('preferences/me/', 
         UserPreferencesViewSet.as_view({'get': 'me', 'put': 'me', 'patch': 'me'}),
         name='my-preferences'),
    path('preferences/dashboard/', 
         UserPreferencesViewSet.as_view({'post': 'save_dashboard_layout'}),
         name='save-dashboard-layout'),
    path('preferences/recent-item/',
         UserPreferencesViewSet.as_view({'post': 'add_recent_item'}),
         name='add-recent-item'),
    
    # Convenience endpoints for onboarding
    path('onboarding/status/',
         OnboardingProgressViewSet.as_view({'get': 'status'}),
         name='onboarding-status'),
    path('onboarding/step/',
         OnboardingProgressViewSet.as_view({'post': 'complete_step'}),
         name='complete-onboarding-step'),
    path('onboarding/tour/complete/',
         OnboardingProgressViewSet.as_view({'post': 'complete_tour'}),
         name='complete-tour'),
    path('onboarding/tour/dismiss/',
         OnboardingProgressViewSet.as_view({'post': 'dismiss_tour'}),
         name='dismiss-tour'),
    
    # Convenience endpoints for recommendations
    path('recommendations/active/',
         AIRecommendationViewSet.as_view({'get': 'active'}),
         name='active-recommendations'),
    path('recommendations/generate/',
         AIRecommendationViewSet.as_view({'post': 'generate'}),
         name='generate-recommendations'),
    
    # Quick actions
    path('quick-actions/pinned/',
         QuickActionViewSet.as_view({'get': 'pinned'}),
         name='pinned-quick-actions'),
]
