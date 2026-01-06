from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Achievement(models.Model):
    """Achievement definitions"""
    CATEGORY_CHOICES = [
        ('sales', 'Sales'),
        ('activity', 'Activity'),
        ('quality', 'Quality'),
        ('collaboration', 'Collaboration'),
        ('milestone', 'Milestone'),
    ]

    DIFFICULTY_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='bronze')

    # Achievement criteria
    criteria_type = models.CharField(
        max_length=50,
        choices=[
            ('deals_won', 'Deals Won'),
            ('revenue_target', 'Revenue Target'),
            ('leads_converted', 'Leads Converted'),
            ('tasks_completed', 'Tasks Completed'),
            ('streak_days', 'Streak Days'),
            ('perfect_week', 'Perfect Week'),
        ]
    )
    criteria_value = models.IntegerField(help_text="Target value to achieve")

    # Rewards
    points = models.IntegerField(default=10)
    badge_icon = models.CharField(max_length=100, blank=True, help_text="Icon name or emoji")

    # Status
    is_active = models.BooleanField(default=True)
    is_repeatable = models.BooleanField(default=False, help_text="Can be earned multiple times")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'difficulty', 'name']
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'

    def __str__(self):
        return f"{self.name} ({self.difficulty})"


class UserAchievement(models.Model):
    """Achievements earned by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)

    # Progress
    earned_at = models.DateTimeField(auto_now_add=True)
    progress_value = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-earned_at']
        unique_together = ['user', 'achievement', 'earned_at']
        verbose_name = 'User Achievement'
        verbose_name_plural = 'User Achievements'

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"

    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.is_completed:
            return 100
        return min(100, (self.progress_value / self.achievement.criteria_value) * 100)


class Leaderboard(models.Model):
    """Leaderboard configurations"""
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('all_time', 'All Time'),
    ]

    METRIC_CHOICES = [
        ('total_points', 'Total Points'),
        ('deals_won', 'Deals Won'),
        ('revenue_generated', 'Revenue Generated'),
        ('leads_converted', 'Leads Converted'),
        ('tasks_completed', 'Tasks Completed'),
        ('achievements_earned', 'Achievements Earned'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    metric = models.CharField(max_length=50, choices=METRIC_CHOICES)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)

    # Display settings
    display_count = models.IntegerField(default=10, help_text="Number of top users to show")
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['period', 'name']
        verbose_name = 'Leaderboard'
        verbose_name_plural = 'Leaderboards'

    def __str__(self):
        return f"{self.name} ({self.period})"


class UserPoints(models.Model):
    """Track user points"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='points')

    # Points breakdown
    total_points = models.IntegerField(default=0)
    sales_points = models.IntegerField(default=0)
    activity_points = models.IntegerField(default=0)
    quality_points = models.IntegerField(default=0)

    # Level
    level = models.IntegerField(default=1)
    level_name = models.CharField(max_length=100, default='Beginner')

    # Streaks
    current_streak = models.IntegerField(default=0, help_text="Days of consecutive activity")
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Points'
        verbose_name_plural = 'User Points'

    def __str__(self):
        return f"{self.user.username} - {self.total_points} points (Level {self.level})"

    def add_points(self, points, category='activity'):
        """Add points to user"""
        self.total_points += points

        if category == 'sales':
            self.sales_points += points
        elif category == 'activity':
            self.activity_points += points
        elif category == 'quality':
            self.quality_points += points

        # Update level
        self._update_level()

        # Update streak
        self._update_streak()

        self.save()

    def _update_level(self):
        """Calculate user level based on points"""
        # Simple leveling: 100 points per level
        new_level = (self.total_points // 100) + 1
        if new_level != self.level:
            self.level = new_level
            self.level_name = self._get_level_name(new_level)

    def _get_level_name(self, level):
        """Get level name"""
        if level < 5:
            return 'Beginner'
        elif level < 10:
            return 'Intermediate'
        elif level < 20:
            return 'Advanced'
        elif level < 30:
            return 'Expert'
        else:
            return 'Master'

    def _update_streak(self):
        """Update activity streak"""
        today = timezone.now().date()

        if self.last_activity_date:
            days_diff = (today - self.last_activity_date).days

            if days_diff == 0:
                # Same day, no change
                return
            elif days_diff == 1:
                # Consecutive day
                self.current_streak += 1
                if self.current_streak > self.longest_streak:
                    self.longest_streak = self.current_streak
            else:
                # Streak broken
                self.current_streak = 1
        else:
            self.current_streak = 1

        self.last_activity_date = today


class PointTransaction(models.Model):
    """Track point transactions"""
    TRANSACTION_TYPES = [
        ('earned', 'Earned'),
        ('bonus', 'Bonus'),
        ('penalty', 'Penalty'),
        ('adjustment', 'Adjustment'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    points = models.IntegerField()
    category = models.CharField(max_length=50, default='activity')

    # Context
    reason = models.CharField(max_length=255)
    reference_type = models.CharField(max_length=50, blank=True, help_text="e.g., 'lead', 'opportunity'")
    reference_id = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
        verbose_name = 'Point Transaction'
        verbose_name_plural = 'Point Transactions'

    def __str__(self):
        return f"{self.user.username} - {self.points} points ({self.reason})"


class Challenge(models.Model):
    """Team or individual challenges"""
    CHALLENGE_TYPES = [
        ('individual', 'Individual'),
        ('team', 'Team'),
    ]

    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')

    # Goals
    goal_metric = models.CharField(max_length=100, help_text="e.g., deals_won, revenue")
    goal_value = models.FloatField()

    # Rewards
    reward_points = models.IntegerField(default=100)
    reward_description = models.TextField(blank=True)

    # Participants
    participants = models.ManyToManyField(User, related_name='challenges', blank=True)

    # Timing
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_challenges')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Challenge'
        verbose_name_plural = 'Challenges'

    def __str__(self):
        return f"{self.name} ({self.status})"

    def is_active(self):
        """Check if challenge is currently active"""
        now = timezone.now()
        return self.status == 'active' and self.start_date <= now <= self.end_date


class ChallengeProgress(models.Model):
    """Track challenge progress for users"""
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='progress')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenge_progress')

    current_value = models.FloatField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Ranking
    rank = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-current_value']
        unique_together = ['challenge', 'user']
        verbose_name = 'Challenge Progress'
        verbose_name_plural = 'Challenge Progress'

    def __str__(self):
        return f"{self.user.username} - {self.challenge.name}"

    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.is_completed:
            return 100
        return min(100, (self.current_value / self.challenge.goal_value) * 100)
