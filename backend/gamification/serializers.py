"""
Gamification Serializers
"""

from rest_framework import serializers

from .models import (
    Achievement,
    Challenge,
    ChallengeProgress,
    Leaderboard,
    PointTransaction,
    UserAchievement,
    UserPoints,
)


class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for Achievement"""
    progress_required = serializers.IntegerField(source='criteria_value', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)

    class Meta:
        model = Achievement
        fields = '__all__'


class UserAchievementSerializer(serializers.ModelSerializer):
    """Serializer for User Achievement"""
    achievement_details = AchievementSerializer(source='achievement', read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserAchievement
        fields = '__all__'

    def get_progress_percentage(self, obj):
        return obj.progress_percentage


class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for Leaderboard"""
    metric_display = serializers.CharField(source='get_metric_display', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)

    class Meta:
        model = Leaderboard
        fields = '__all__'


class UserPointsSerializer(serializers.ModelSerializer):
    """Serializer for User Points"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    total_achievements = serializers.SerializerMethodField()
    next_level_points = serializers.SerializerMethodField()

    class Meta:
        model = UserPoints
        fields = '__all__'

    def get_total_achievements(self, obj):
        return obj.user.achievements.filter(is_completed=True).count()

    def get_next_level_points(self, obj):
        # Points needed for next level (100 points per level)
        next_level = obj.level + 1
        points_for_next = next_level * 100
        return points_for_next - obj.total_points


class PointTransactionSerializer(serializers.ModelSerializer):
    """Serializer for Point Transaction"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)

    class Meta:
        model = PointTransaction
        fields = '__all__'


class ChallengeSerializer(serializers.ModelSerializer):
    """Serializer for Challenge"""
    challenge_type_display = serializers.CharField(source='get_challenge_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    participant_count = serializers.SerializerMethodField()
    is_currently_active = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = '__all__'

    def get_participant_count(self, obj):
        return obj.participants.count()

    def get_is_currently_active(self, obj):
        return obj.is_active()


class ChallengeProgressSerializer(serializers.ModelSerializer):
    """Serializer for Challenge Progress"""
    challenge_details = ChallengeSerializer(source='challenge', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = ChallengeProgress
        fields = '__all__'

    def get_progress_percentage(self, obj):
        return obj.progress_percentage
