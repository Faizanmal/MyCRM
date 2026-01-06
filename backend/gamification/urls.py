"""
Gamification URLs
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AchievementViewSet,
    ChallengeProgressViewSet,
    ChallengeViewSet,
    LeaderboardViewSet,
    PointTransactionViewSet,
    UserAchievementViewSet,
    UserPointsViewSet,
)

router = DefaultRouter()
router.register(r'achievements', AchievementViewSet, basename='achievement')
router.register(r'user-achievements', UserAchievementViewSet, basename='user-achievement')
router.register(r'leaderboards', LeaderboardViewSet, basename='leaderboard')
router.register(r'points', UserPointsViewSet, basename='points')
router.register(r'transactions', PointTransactionViewSet, basename='transaction')
router.register(r'challenges', ChallengeViewSet, basename='challenge')
router.register(r'challenge-progress', ChallengeProgressViewSet, basename='challenge-progress')

urlpatterns = [
    path('', include(router.urls)),
]
