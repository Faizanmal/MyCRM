"""
Gamification Admin
"""

from django.contrib import admin

from .models import (
    Achievement,
    Challenge,
    ChallengeProgress,
    Leaderboard,
    PointTransaction,
    UserAchievement,
    UserPoints,
)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'difficulty', 'points', 'is_active']
    list_filter = ['category', 'difficulty', 'is_active']
    search_fields = ['name', 'description']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'progress_value', 'is_completed', 'earned_at']
    list_filter = ['is_completed', 'achievement__category']
    search_fields = ['user__username', 'achievement__name']
    readonly_fields = ['earned_at']


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'metric', 'period', 'is_active']
    list_filter = ['metric', 'period', 'is_active']
    search_fields = ['name']


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'level', 'level_name', 'current_streak']
    list_filter = ['level']
    search_fields = ['user__username']
    readonly_fields = ['updated_at']


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'points', 'category', 'reason', 'created_at']
    list_filter = ['transaction_type', 'category']
    search_fields = ['user__username', 'reason']
    readonly_fields = ['created_at']


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ['name', 'challenge_type', 'status', 'goal_metric', 'goal_value', 'start_date', 'end_date']
    list_filter = ['challenge_type', 'status']
    search_fields = ['name', 'description']
    filter_horizontal = ['participants']


@admin.register(ChallengeProgress)
class ChallengeProgressAdmin(admin.ModelAdmin):
    list_display = ['challenge', 'user', 'current_value', 'is_completed', 'rank']
    list_filter = ['is_completed']
    search_fields = ['user__username', 'challenge__name']
    readonly_fields = ['completed_at']
