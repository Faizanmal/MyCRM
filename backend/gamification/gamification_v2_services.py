"""
Gamification 2.0 Services - Advanced gamification business logic.
Includes achievements, challenges, leaderboards, recognition, streaks, and rewards.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class AchievementService:
    """Service for managing achievements and user progress."""

    def get_user_achievements(
        self,
        user_id: str,
        category: str | None = None,
        include_locked: bool = True,
        include_secret: bool = False,
    ) -> dict[str, Any]:
        """Get all achievements for a user with progress."""
        achievements = []

        # Mock data - in production, query from database
        all_achievements = self._get_all_achievements()
        user_progress = self._get_user_progress(user_id)

        for achievement in all_achievements:
            if category and achievement['category'] != category:
                continue
            if achievement['is_secret'] and not include_secret:
                user_completed = user_progress.get(achievement['id'], {}).get('completed', False)
                if not user_completed:
                    continue

            progress = user_progress.get(achievement['id'], {'progress': 0, 'completed': False})

            if not include_locked and not progress['completed']:
                continue

            achievements.append({
                **achievement,
                'progress': progress['progress'],
                'is_completed': progress['completed'],
                'completed_at': progress.get('completed_at'),
            })

        return {
            'achievements': achievements,
            'total_count': len(all_achievements),
            'completed_count': sum(1 for a in achievements if a.get('is_completed')),
            'categories': list({a['category'] for a in all_achievements}),
        }

    def check_and_award_achievements(self, user_id: str, event_type: str, event_data: dict) -> list[dict]:
        """Check if user has earned any achievements based on an event."""
        awarded = []

        # Get applicable achievements for this event type
        achievements = self._get_achievements_for_event(event_type)

        for achievement in achievements:
            if self._check_criteria(user_id, achievement, event_data):
                # Award the achievement
                result = self._award_achievement(user_id, achievement)
                if result:
                    awarded.append(result)

        return awarded

    def _award_achievement(self, user_id: str, achievement: dict) -> dict | None:
        """Award an achievement to a user."""
        # Check if already awarded
        # In production, this would create a UserAchievement record
        return {
            'achievement_id': achievement['id'],
            'name': achievement['name'],
            'points': achievement['points'],
            'rarity': achievement['rarity'],
            'awarded_at': timezone.now().isoformat(),
        }

    def _get_all_achievements(self) -> list[dict]:
        """Get all available achievements."""
        return [
            {
                'id': '1',
                'name': 'First Deal',
                'description': 'Close your first deal',
                'category': 'sales',
                'rarity': 'common',
                'points': 50,
                'icon': 'trophy',
                'is_secret': False,
                'criteria': {'deals_closed': 1},
            },
            {
                'id': '2',
                'name': 'Deal Master',
                'description': 'Close 100 deals',
                'category': 'sales',
                'rarity': 'epic',
                'points': 500,
                'icon': 'target',
                'is_secret': False,
                'criteria': {'deals_closed': 100},
            },
        ]

    def _get_user_progress(self, user_id: str) -> dict[str, dict]:
        """Get user's progress on all achievements."""
        return {}

    def _get_achievements_for_event(self, event_type: str) -> list[dict]:
        """Get achievements that might be triggered by an event type."""
        return []

    def _check_criteria(self, user_id: str, achievement: dict, event_data: dict) -> bool:
        """Check if achievement criteria are met."""
        return False


class ChallengeService:
    """Service for managing challenges and competitions."""

    def get_active_challenges(
        self,
        user_id: str,
        challenge_type: str | None = None,
    ) -> list[dict]:
        """Get all active challenges for a user."""
        now = timezone.now()

        challenges = []

        # In production, query from database
        all_challenges = self._get_all_challenges()

        for challenge in all_challenges:
            if challenge_type and challenge['type'] != challenge_type:
                continue

            start = datetime.fromisoformat(challenge['start_date'])
            end = datetime.fromisoformat(challenge['end_date'])

            if start <= now <= end:
                user_progress = self._get_user_challenge_progress(user_id, challenge['id'])
                challenges.append({
                    **challenge,
                    'current_value': user_progress.get('current_value', 0),
                    'rank': user_progress.get('rank'),
                    'progress_percent': min(
                        (user_progress.get('current_value', 0) / challenge['goal_target']) * 100,
                        100
                    ),
                })

        return challenges

    def join_challenge(self, user_id: str, challenge_id: str, team_id: str | None = None) -> dict:
        """Join a challenge."""
        # In production, create ChallengeParticipant record
        return {
            'challenge_id': challenge_id,
            'user_id': user_id,
            'team_id': team_id,
            'joined_at': timezone.now().isoformat(),
            'status': 'active',
        }

    def update_progress(self, user_id: str, challenge_id: str, value: float) -> dict:
        """Update user's progress in a challenge."""
        # In production, update ChallengeParticipant record
        return {
            'challenge_id': challenge_id,
            'user_id': user_id,
            'current_value': value,
            'updated_at': timezone.now().isoformat(),
        }

    def get_challenge_leaderboard(self, challenge_id: str, limit: int = 10) -> list[dict]:
        """Get leaderboard for a specific challenge."""
        # In production, query from database
        return []

    def create_ai_challenge(self, user_id: str, difficulty: str = 'medium') -> dict:
        """Generate an AI-powered personalized challenge."""
        # Analyze user's performance and create appropriate challenge
        user_stats = self._analyze_user_performance(user_id)

        # Determine appropriate goals based on difficulty
        multipliers = {'easy': 0.8, 'medium': 1.0, 'hard': 1.3}
        multiplier = multipliers.get(difficulty, 1.0)

        # Create personalized challenge
        goal_target = int(user_stats.get('avg_weekly_deals', 5) * multiplier)

        return {
            'id': str(uuid.uuid4()),
            'name': f'Personal Challenge: Close {goal_target} deals',
            'description': 'AI-generated challenge based on your performance',
            'type': 'individual',
            'goal_type': 'deals_closed',
            'goal_target': goal_target,
            'goal_unit': 'deals',
            'start_date': timezone.now().isoformat(),
            'end_date': (timezone.now() + timedelta(days=7)).isoformat(),
            'is_ai_generated': True,
            'ai_difficulty': difficulty,
            'ai_reasoning': f'Based on your average of {user_stats.get("avg_weekly_deals", 5)} deals per week',
            'reward': {'points': goal_target * 20},
        }

    def _get_all_challenges(self) -> list[dict]:
        """Get all challenges."""
        return []

    def _get_user_challenge_progress(self, user_id: str, challenge_id: str) -> dict:
        """Get user's progress in a specific challenge."""
        return {}

    def _analyze_user_performance(self, user_id: str) -> dict:
        """Analyze user's historical performance for AI challenge generation."""
        return {'avg_weekly_deals': 5, 'avg_weekly_calls': 20}


class LeaderboardService:
    """Service for managing leaderboards."""

    def get_leaderboard(
        self,
        period: str = 'weekly',
        metric: str = 'xp',
        limit: int = 10,
        team_id: str | None = None,
    ) -> dict[str, Any]:
        """Get leaderboard for a specific period and metric."""
        # Calculate date range based on period
        now = timezone.now()

        if period == 'daily':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'weekly':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'monthly':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'quarterly':
            quarter_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(month=quarter_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'yearly':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = None  # all_time

        # In production, query aggregated data from database
        entries = self._get_leaderboard_entries(start_date, metric, limit, team_id)

        return {
            'period': period,
            'metric': metric,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': now.isoformat(),
            'entries': entries,
            'total_participants': len(entries),
            'last_updated': now.isoformat(),
        }

    def get_user_rank(self, user_id: str, period: str = 'weekly', metric: str = 'xp') -> dict:
        """Get a specific user's rank in the leaderboard."""
        # In production, query from database
        return {
            'user_id': user_id,
            'rank': 5,
            'previous_rank': 7,
            'value': 4500,
            'percentile': 85,
        }

    def update_leaderboard(self, user_id: str, metric: str, value_delta: float) -> None:
        """Update leaderboard entry for a user."""
        # In production, update LeaderboardEntry record
        pass

    def _get_leaderboard_entries(
        self,
        start_date: datetime | None,
        metric: str,
        limit: int,
        team_id: str | None,
    ) -> list[dict]:
        """Get leaderboard entries."""
        return []


class RecognitionService:
    """Service for peer recognition and kudos."""

    def send_recognition(
        self,
        sender_id: str,
        recipient_id: str,
        recognition_type: str,
        message: str,
        points: int = 10,
        is_public: bool = True,
    ) -> dict:
        """Send recognition to a teammate."""
        # Validate sender can send recognition
        if sender_id == recipient_id:
            raise ValueError("Cannot send recognition to yourself")

        recognition = {
            'id': str(uuid.uuid4()),
            'sender_id': sender_id,
            'recipient_id': recipient_id,
            'type': recognition_type,
            'message': message,
            'points': points,
            'is_public': is_public,
            'created_at': timezone.now().isoformat(),
            'reactions': {},
        }

        # In production, save to database and award points
        return recognition

    def get_recognition_feed(
        self,
        user_id: str | None = None,
        team_id: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """Get recognition feed for a user or team."""
        # In production, query from database
        return []

    def add_reaction(self, user_id: str, recognition_id: str, emoji: str) -> dict:
        """Add a reaction to a recognition."""
        return {
            'recognition_id': recognition_id,
            'user_id': user_id,
            'emoji': emoji,
            'created_at': timezone.now().isoformat(),
        }

    def get_recognition_stats(self, user_id: str) -> dict:
        """Get recognition statistics for a user."""
        return {
            'sent_count': 25,
            'received_count': 18,
            'total_points_received': 180,
            'top_recognizers': [],
            'recognition_types_received': {'kudos': 10, 'great_job': 5, 'teamwork': 3},
        }


class StreakService:
    """Service for managing streaks."""

    def get_user_streaks(self, user_id: str) -> list[dict]:
        """Get all streaks for a user."""
        streak_types = ['login', 'activity', 'deal', 'call', 'email']
        streaks = []

        for streak_type in streak_types:
            streak = self._get_streak(user_id, streak_type)
            if streak:
                streaks.append(streak)

        return streaks

    def check_and_update_streak(self, user_id: str, streak_type: str) -> dict:
        """Check and update a streak based on user activity."""
        current_streak = self._get_streak(user_id, streak_type)

        if not current_streak:
            # Start new streak
            return self._start_streak(user_id, streak_type)

        last_activity = datetime.fromisoformat(current_streak['last_activity_date'])
        now = timezone.now()

        # Check if streak continues or breaks
        if (now - last_activity).days == 1:
            # Continue streak
            return self._continue_streak(user_id, streak_type, current_streak)
        elif (now - last_activity).days > 1:
            # Streak broken, start new
            return self._start_streak(user_id, streak_type)
        else:
            # Same day, no update needed
            return current_streak

    def get_milestone_progress(self, user_id: str, streak_type: str) -> dict:
        """Get progress towards streak milestones."""
        streak = self._get_streak(user_id, streak_type)
        milestones = [7, 14, 30, 60, 90, 180, 365]

        if not streak:
            return {'next_milestone': 7, 'progress': 0}

        current = streak['current_count']
        next_milestone = next((m for m in milestones if m > current), milestones[-1])

        return {
            'current_count': current,
            'next_milestone': next_milestone,
            'progress': (current / next_milestone) * 100,
            'milestones_achieved': [m for m in milestones if m <= current],
        }

    def _get_streak(self, user_id: str, streak_type: str) -> dict | None:
        """Get a specific streak for a user."""
        return None

    def _start_streak(self, user_id: str, streak_type: str) -> dict:
        """Start a new streak."""
        return {
            'user_id': user_id,
            'streak_type': streak_type,
            'current_count': 1,
            'best_count': 1,
            'start_date': timezone.now().isoformat(),
            'last_activity_date': timezone.now().isoformat(),
        }

    def _continue_streak(self, user_id: str, streak_type: str, streak: dict) -> dict:
        """Continue an existing streak."""
        new_count = streak['current_count'] + 1
        return {
            **streak,
            'current_count': new_count,
            'best_count': max(streak['best_count'], new_count),
            'last_activity_date': timezone.now().isoformat(),
        }


class LevelService:
    """Service for managing user levels and XP."""

    # XP required for each level
    XP_PER_LEVEL = [
        0, 100, 250, 450, 700, 1000, 1400, 1900, 2500, 3200,
        4000, 5000, 6200, 7600, 9200, 11000, 13000, 15200, 17600, 20200,
    ]

    LEVEL_TITLES = {
        1: 'Rookie',
        5: 'Apprentice',
        10: 'Professional',
        15: 'Expert',
        20: 'Master',
        25: 'Champion',
        30: 'Legend',
    }

    def get_user_level(self, user_id: str) -> dict:
        """Get user's current level and XP."""
        # In production, query from database
        total_xp = 4850  # Mock data
        level = self._calculate_level(total_xp)

        return {
            'level': level,
            'title': self._get_title(level),
            'total_xp': total_xp,
            'xp_for_current_level': self.XP_PER_LEVEL[min(level - 1, len(self.XP_PER_LEVEL) - 1)],
            'xp_for_next_level': self.XP_PER_LEVEL[min(level, len(self.XP_PER_LEVEL) - 1)],
            'xp_progress': total_xp - self.XP_PER_LEVEL[min(level - 1, len(self.XP_PER_LEVEL) - 1)],
        }

    def award_xp(self, user_id: str, amount: int, source: str) -> dict:
        """Award XP to a user."""
        user_level = self.get_user_level(user_id)
        new_total = user_level['total_xp'] + amount
        new_level = self._calculate_level(new_total)

        level_up = new_level > user_level['level']

        # In production, update database

        return {
            'previous_xp': user_level['total_xp'],
            'new_xp': new_total,
            'xp_awarded': amount,
            'source': source,
            'previous_level': user_level['level'],
            'new_level': new_level,
            'level_up': level_up,
            'new_title': self._get_title(new_level) if level_up else None,
        }

    def _calculate_level(self, total_xp: int) -> int:
        """Calculate level from total XP."""
        for i, threshold in enumerate(self.XP_PER_LEVEL):
            if total_xp < threshold:
                return max(1, i)
        return len(self.XP_PER_LEVEL)

    def _get_title(self, level: int) -> str:
        """Get title for a level."""
        title = 'Rookie'
        for lvl, t in sorted(self.LEVEL_TITLES.items()):
            if level >= lvl:
                title = t
        return title


class RewardService:
    """Service for managing rewards and redemptions."""

    def get_available_rewards(self, user_id: str) -> list[dict]:
        """Get all rewards available for redemption."""
        user_coins = self._get_user_coins(user_id)

        rewards = self._get_all_rewards()

        for reward in rewards:
            reward['can_redeem'] = user_coins >= reward['coin_cost']
            reward['stock_available'] = reward.get('remaining_quantity', 999) > 0

        return rewards

    def redeem_reward(self, user_id: str, reward_id: str) -> dict:
        """Redeem a reward."""
        user_coins = self._get_user_coins(user_id)
        reward = self._get_reward(reward_id)

        if not reward:
            raise ValueError("Reward not found")

        if user_coins < reward['coin_cost']:
            raise ValueError("Insufficient coins")

        if reward.get('remaining_quantity', 999) <= 0:
            raise ValueError("Reward out of stock")

        # Process redemption
        redemption = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'reward_id': reward_id,
            'coin_cost': reward['coin_cost'],
            'status': 'pending',
            'redeemed_at': timezone.now().isoformat(),
        }

        # Deduct coins
        # In production, update user's coin balance

        return redemption

    def get_redemption_history(self, user_id: str) -> list[dict]:
        """Get user's reward redemption history."""
        # In production, query from database
        return []

    def _get_user_coins(self, user_id: str) -> int:
        """Get user's coin balance."""
        return 2400  # Mock data

    def _get_all_rewards(self) -> list[dict]:
        """Get all available rewards."""
        return [
            {
                'id': '1',
                'name': 'Coffee Gift Card',
                'description': '$10 Starbucks gift card',
                'category': 'gift_cards',
                'coin_cost': 500,
                'remaining_quantity': 50,
            },
            {
                'id': '2',
                'name': 'Extra PTO Day',
                'description': 'One additional day of paid time off',
                'category': 'experiences',
                'coin_cost': 5000,
                'remaining_quantity': 10,
            },
        ]

    def _get_reward(self, reward_id: str) -> dict | None:
        """Get a specific reward."""
        rewards = {r['id']: r for r in self._get_all_rewards()}
        return rewards.get(reward_id)


class GamificationEventHandler:
    """Handler for gamification events across the CRM."""

    def __init__(self):
        self.achievement_service = AchievementService()
        self.challenge_service = ChallengeService()
        self.streak_service = StreakService()
        self.level_service = LevelService()
        self.leaderboard_service = LeaderboardService()

    def handle_event(self, user_id: str, event_type: str, event_data: dict) -> dict:
        """Handle a gamification event and trigger appropriate updates."""
        results = {
            'achievements_earned': [],
            'xp_awarded': 0,
            'streak_updates': [],
            'level_up': False,
        }

        # Check achievements
        earned = self.achievement_service.check_and_award_achievements(
            user_id, event_type, event_data
        )
        results['achievements_earned'] = earned

        # Award XP for the event
        xp_amounts = {
            'deal_closed': 100,
            'call_made': 5,
            'email_sent': 3,
            'meeting_completed': 25,
            'task_completed': 10,
        }

        if event_type in xp_amounts:
            xp_result = self.level_service.award_xp(
                user_id, xp_amounts[event_type], event_type
            )
            results['xp_awarded'] = xp_result['xp_awarded']
            results['level_up'] = xp_result['level_up']

            # Update leaderboard
            self.leaderboard_service.update_leaderboard(
                user_id, 'xp', xp_amounts[event_type]
            )

        # Update streaks
        streak_mapping = {
            'deal_closed': 'deal',
            'call_made': 'call',
            'email_sent': 'email',
            'login': 'login',
        }

        if event_type in streak_mapping:
            streak_result = self.streak_service.check_and_update_streak(
                user_id, streak_mapping[event_type]
            )
            results['streak_updates'].append(streak_result)

        # Update challenge progress
        self._update_challenge_progress(user_id, event_type, event_data)

        return results

    def _update_challenge_progress(self, user_id: str, event_type: str, event_data: dict) -> None:
        """Update progress for relevant challenges."""
        # Map event types to challenge goal types
        goal_mapping = {
            'deal_closed': 'deals_closed',
            'revenue_added': 'revenue',
            'pipeline_added': 'pipeline_value',
        }

        if event_type in goal_mapping:
            # In production, find active challenges and update progress
            pass
