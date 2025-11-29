"""
Gamification Tests
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Achievement, UserPoints, Challenge

User = get_user_model()


class AchievementModelTest(TestCase):
    def setUp(self):
        self.achievement = Achievement.objects.create(
            name='First Deal',
            description='Close your first deal',
            category='sales',
            difficulty='bronze',
            criteria_type='deals_won',
            criteria_value=1,
            points=50
        )
    
    def test_achievement_creation(self):
        self.assertEqual(self.achievement.name, 'First Deal')
        self.assertEqual(self.achievement.points, 50)
        self.assertTrue(self.achievement.is_active)


class UserPointsModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.points = UserPoints.objects.create(user=self.user)
    
    def test_add_points(self):
        self.points.add_points(100, 'sales')
        self.assertEqual(self.points.total_points, 100)
        self.assertEqual(self.points.sales_points, 100)
    
    def test_level_calculation(self):
        self.points.add_points(250)
        self.assertEqual(self.points.level, 3)


class ChallengeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.challenge = Challenge.objects.create(
            name='Monthly Sales Challenge',
            description='Close 10 deals this month',
            challenge_type='individual',
            goal_metric='deals_won',
            goal_value=10,
            reward_points=500,
            start_date='2024-01-01',
            end_date='2024-01-31',
            created_by=self.user
        )
    
    def test_challenge_creation(self):
        self.assertEqual(self.challenge.name, 'Monthly Sales Challenge')
        self.assertEqual(self.challenge.reward_points, 500)
