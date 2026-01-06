"""
Gamification 2.0 Models
AI-powered challenges, competitions, recognition, and rewards
"""

import uuid

from django.contrib.auth import get_user_model
from django.db import models


class Achievement(models.Model):
    """Achievement/Badge definitions"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic info
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)  # Icon identifier
    color = models.CharField(max_length=20, default='blue')

    # Categorization
    CATEGORY_CHOICES = [
        ('sales', 'Sales'),
        ('activity', 'Activity'),
        ('engagement', 'Engagement'),
        ('learning', 'Learning'),
        ('teamwork', 'Teamwork'),
        ('milestone', 'Milestone'),
        ('special', 'Special'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    # Rarity
    RARITY_CHOICES = [
        ('common', 'Common'),
        ('uncommon', 'Uncommon'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')

    # Requirements
    criteria = models.JSONField(default=dict)  # Conditions to earn
    points = models.IntegerField(default=0)  # XP awarded

    # Tiered achievements
    tier = models.IntegerField(default=1)  # 1=Bronze, 2=Silver, 3=Gold
    next_tier = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='previous_tier'
    )

    # Secret achievements
    is_secret = models.BooleanField(default=False)
    hint = models.CharField(max_length=255, blank=True)

    # Status
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', '-points']

    def __str__(self):
        return f"{self.name} ({self.rarity})"


class UserAchievement(models.Model):
    """User earned achievements"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)

    # Progress for incremental achievements
    progress = models.FloatField(default=0)  # 0-100%
    progress_details = models.JSONField(default=dict)

    # Completion
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Showcase
    is_showcased = models.BooleanField(default=False)  # Display on profile

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'achievement']

    def __str__(self):
        return f"{self.user} - {self.achievement}"


class Challenge(models.Model):
    """AI-powered challenges and competitions"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic info
    name = models.CharField(max_length=100)
    description = models.TextField()

    # Type
    TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('team', 'Team'),
        ('organization', 'Organization-wide'),
        ('head_to_head', 'Head to Head'),
        ('leaderboard', 'Leaderboard'),
    ]
    challenge_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    # Timing
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    # Goals
    goal_type = models.CharField(max_length=50)  # e.g., 'deals_closed', 'calls_made'
    goal_target = models.DecimalField(max_digits=15, decimal_places=2)
    goal_unit = models.CharField(max_length=50)  # e.g., 'deals', 'dollars', 'calls'

    # AI-generated
    is_ai_generated = models.BooleanField(default=False)
    ai_difficulty = models.CharField(max_length=20, blank=True)  # easy/medium/hard
    ai_reasoning = models.TextField(blank=True)  # Why AI created this challenge

    # Rewards
    points_reward = models.IntegerField(default=0)
    badge_reward = models.ForeignKey(
        Achievement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    prize_description = models.TextField(blank=True)

    # Participation
    min_participants = models.IntegerField(default=1)
    max_participants = models.IntegerField(null=True, blank=True)

    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_challenges'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class ChallengeParticipant(models.Model):
    """Challenge participants and progress"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='challenge_participations'
    )
    team = models.ForeignKey(
        'Team',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='challenge_participations'
    )

    # Progress
    current_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    progress_percentage = models.FloatField(default=0)

    # Ranking
    rank = models.IntegerField(null=True, blank=True)

    # Status
    is_winner = models.BooleanField(default=False)
    prize_claimed = models.BooleanField(default=False)

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['challenge', 'user']

    def __str__(self):
        return f"{self.user} in {self.challenge}"


class Team(models.Model):
    """Teams for team-based challenges"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    avatar = models.URLField(blank=True)

    # Members
    leader = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='led_teams'
    )
    members = models.ManyToManyField(
        get_user_model(),
        through='TeamMembership',
        related_name='gamification_teams'
    )

    # Stats
    total_points = models.IntegerField(default=0)
    challenges_won = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TeamMembership(models.Model):
    """Team membership details"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    ROLE_CHOICES = [
        ('member', 'Member'),
        ('captain', 'Captain'),
        ('leader', 'Leader'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')

    points_contributed = models.IntegerField(default=0)

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['team', 'user']


class LeaderboardEntry(models.Model):
    """Leaderboard entries"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Period
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('all_time', 'All Time'),
    ]
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()

    # Entity
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)

    # Metrics
    METRIC_CHOICES = [
        ('xp', 'Experience Points'),
        ('deals_closed', 'Deals Closed'),
        ('revenue', 'Revenue'),
        ('activities', 'Activities'),
        ('streak', 'Streak Days'),
    ]
    metric = models.CharField(max_length=30, choices=METRIC_CHOICES)
    value = models.DecimalField(max_digits=15, decimal_places=2)

    # Ranking
    rank = models.IntegerField()
    previous_rank = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['rank']


class Recognition(models.Model):
    """Peer recognition and kudos"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Participants
    sender = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='sent_recognitions'
    )
    recipient = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='received_recognitions'
    )

    # Content
    TYPE_CHOICES = [
        ('kudos', 'Kudos'),
        ('shoutout', 'Shoutout'),
        ('thank_you', 'Thank You'),
        ('great_job', 'Great Job'),
        ('teamwork', 'Teamwork'),
        ('innovation', 'Innovation'),
        ('leadership', 'Leadership'),
    ]
    recognition_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()

    # Points
    points_awarded = models.IntegerField(default=10)

    # Visibility
    is_public = models.BooleanField(default=True)

    # Reactions
    reactions = models.JSONField(default=dict)  # {"emoji": count}

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.recognition_type}"


class Streak(models.Model):
    """User activity streaks"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='streaks'
    )

    # Streak type
    STREAK_TYPE_CHOICES = [
        ('login', 'Daily Login'),
        ('activity', 'Daily Activity'),
        ('deal', 'Daily Deal'),
        ('call', 'Daily Call'),
        ('email', 'Daily Email'),
    ]
    streak_type = models.CharField(max_length=20, choices=STREAK_TYPE_CHOICES)

    # Current streak
    current_count = models.IntegerField(default=0)
    last_activity_date = models.DateField()

    # Best streak
    best_count = models.IntegerField(default=0)

    # Milestones reached
    milestones = models.JSONField(default=list)  # [7, 30, 100, ...]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'streak_type']

    def __str__(self):
        return f"{self.user} - {self.streak_type}: {self.current_count} days"


class UserLevel(models.Model):
    """User experience and leveling"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='gamification_level'
    )

    # XP
    total_xp = models.IntegerField(default=0)
    current_level = models.IntegerField(default=1)
    xp_for_current_level = models.IntegerField(default=0)
    xp_for_next_level = models.IntegerField(default=100)

    # Title/Rank
    title = models.CharField(max_length=50, default='Rookie')

    # Rewards
    coins = models.IntegerField(default=0)  # Virtual currency

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - Level {self.current_level}"


class Reward(models.Model):
    """Redeemable rewards"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.URLField(blank=True)

    # Cost
    coins_cost = models.IntegerField(default=0)
    points_cost = models.IntegerField(default=0)

    # Type
    TYPE_CHOICES = [
        ('digital', 'Digital'),
        ('physical', 'Physical'),
        ('experience', 'Experience'),
        ('recognition', 'Recognition'),
    ]
    reward_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    # Availability
    quantity_available = models.IntegerField(null=True, blank=True)  # None = unlimited

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class RewardRedemption(models.Model):
    """Reward redemption history"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='reward_redemptions'
    )
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)

    # Cost paid
    coins_paid = models.IntegerField(default=0)
    points_paid = models.IntegerField(default=0)

    # Fulfillment
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    fulfilled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} redeemed {self.reward}"
