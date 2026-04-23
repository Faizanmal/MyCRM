from django.urls import path

from . import views

urlpatterns = [
    path('achievements/', views.AchievementListView.as_view(), name='achievements'),
    path('achievements/my_achievements/', views.MyAchievementsView.as_view(), name='my-achievements'),
    path('achievements/<int:pk>/progress/', views.AchievementProgressView.as_view(), name='achievement-progress'),

    path('user-points/', views.UserPointsView.as_view(), name='user-points'),
    path('user-points/my_points/', views.MyPointsView.as_view(), name='my-points'),
    path('user-points/points_history/', views.PointsHistoryView.as_view(), name='points-history'),

    path('leaderboards/', views.LeaderboardListView.as_view(), name='leaderboards'),
    path('leaderboards/<int:pk>/rankings/', views.LeaderboardRankingsView.as_view(), name='leaderboard-rankings'),

    path('challenges/', views.ChallengeListView.as_view(), name='challenges'),
    path('challenges/my_challenges/', views.MyChallengesView.as_view(), name='my-challenges'),
    path('challenges/<int:pk>/join/', views.ChallengeJoinView.as_view(), name='challenge-join'),
    path('challenges/<int:pk>/leave/', views.ChallengeLeaveView.as_view(), name='challenge-leave'),
    path('challenges/active_team_challenges/', views.ActiveTeamChallengesView.as_view(), name='active-team-challenges'),

    path('point-transactions/', views.PointTransactionsView.as_view(), name='point-transactions'),
    path('point-transactions/my_transactions/', views.MyTransactionsView.as_view(), name='my-transactions'),
]
