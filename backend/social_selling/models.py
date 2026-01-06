"""
Social Selling Models
LinkedIn and social media integration for prospecting
"""

from django.conf import settings
from django.db import models
from django.utils import timezone


class SocialProfile(models.Model):
    """Social media profile linked to a contact"""

    PLATFORM_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
    ]

    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.CASCADE,
        related_name='social_profiles'
    )
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    profile_url = models.URLField()
    username = models.CharField(max_length=100, blank=True)

    # Profile data
    headline = models.CharField(max_length=500, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=200, blank=True)
    profile_image_url = models.URLField(blank=True)

    # Engagement metrics
    followers_count = models.IntegerField(default=0)
    connections_count = models.IntegerField(default=0)
    posts_count = models.IntegerField(default=0)
    engagement_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Metadata
    last_synced = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['contact', 'platform']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.contact} - {self.get_platform_display()}"


class SocialPost(models.Model):
    """Track social media posts for engagement"""

    profile = models.ForeignKey(
        SocialProfile,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    platform_post_id = models.CharField(max_length=100)
    content = models.TextField()
    post_url = models.URLField(blank=True)
    post_type = models.CharField(max_length=50, blank=True)  # text, image, video, article

    # Engagement
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)

    # Our engagement
    we_liked = models.BooleanField(default=False)
    we_commented = models.BooleanField(default=False)
    our_comment = models.TextField(blank=True)

    posted_at = models.DateTimeField()
    discovered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['profile', 'platform_post_id']
        ordering = ['-posted_at']

    def __str__(self):
        return f"Post by {self.profile.contact} on {self.posted_at.date()}"


class SocialEngagement(models.Model):
    """Track our social selling engagements"""

    ENGAGEMENT_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('share', 'Share'),
        ('connection_request', 'Connection Request'),
        ('message', 'Direct Message'),
        ('endorse', 'Endorsement'),
        ('follow', 'Follow'),
    ]

    ENGAGEMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='social_engagements'
    )
    profile = models.ForeignKey(
        SocialProfile,
        on_delete=models.CASCADE,
        related_name='engagements'
    )
    post = models.ForeignKey(
        SocialPost,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='engagements'
    )

    engagement_type = models.CharField(max_length=20, choices=ENGAGEMENT_TYPES)
    content = models.TextField(blank=True)  # For comments/messages
    status = models.CharField(max_length=20, choices=ENGAGEMENT_STATUS, default='pending')

    # AI assistance
    ai_suggested = models.BooleanField(default=False)
    ai_suggestion_text = models.TextField(blank=True)

    scheduled_for = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_engagement_type_display()} on {self.profile}"


class LinkedInIntegration(models.Model):
    """LinkedIn API integration settings per user"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='linkedin_integration'
    )

    # OAuth tokens
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)

    # Profile info
    linkedin_id = models.CharField(max_length=100, blank=True)
    profile_url = models.URLField(blank=True)

    # Settings
    auto_sync_connections = models.BooleanField(default=False)
    daily_engagement_limit = models.IntegerField(default=50)
    engagement_hours_start = models.IntegerField(default=9)  # 9 AM
    engagement_hours_end = models.IntegerField(default=17)  # 5 PM

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_token_valid(self):
        if not self.token_expires_at:
            return False
        return timezone.now() < self.token_expires_at

    def __str__(self):
        return f"LinkedIn: {self.user.email}"


class SocialSellingSequence(models.Model):
    """Automated social selling sequence"""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='social_sequences'
    )

    # Sequence settings
    is_active = models.BooleanField(default=True)
    max_prospects_per_day = models.IntegerField(default=20)
    delay_between_steps = models.IntegerField(default=2)  # days

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class SocialSellingStep(models.Model):
    """Steps in a social selling sequence"""

    ACTION_TYPES = [
        ('view_profile', 'View Profile'),
        ('follow', 'Follow'),
        ('like_post', 'Like Recent Post'),
        ('comment_post', 'Comment on Post'),
        ('connect', 'Send Connection Request'),
        ('message', 'Send Direct Message'),
        ('endorse', 'Endorse Skills'),
    ]

    sequence = models.ForeignKey(
        SocialSellingSequence,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    order = models.IntegerField(default=0)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)

    # Action settings
    delay_days = models.IntegerField(default=0)
    message_template = models.TextField(blank=True)
    use_ai_personalization = models.BooleanField(default=True)

    class Meta:
        ordering = ['sequence', 'order']

    def __str__(self):
        return f"{self.sequence.name} - Step {self.order}: {self.get_action_type_display()}"


class ProspectInSequence(models.Model):
    """Track prospect's progress through a sequence"""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('responded', 'Responded'),
        ('unsubscribed', 'Unsubscribed'),
    ]

    sequence = models.ForeignKey(
        SocialSellingSequence,
        on_delete=models.CASCADE,
        related_name='prospects'
    )
    profile = models.ForeignKey(
        SocialProfile,
        on_delete=models.CASCADE,
        related_name='sequence_enrollments'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    current_step = models.IntegerField(default=0)
    next_action_at = models.DateTimeField(null=True, blank=True)

    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['sequence', 'profile']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.profile.contact} in {self.sequence.name}"


class SocialInsight(models.Model):
    """AI-generated insights from social activity"""

    INSIGHT_TYPES = [
        ('job_change', 'Job Change'),
        ('company_news', 'Company News'),
        ('engagement_opportunity', 'Engagement Opportunity'),
        ('buying_signal', 'Buying Signal'),
        ('competitor_mention', 'Competitor Mention'),
        ('promotion', 'Promotion'),
        ('funding', 'Funding Announcement'),
    ]

    profile = models.ForeignKey(
        SocialProfile,
        on_delete=models.CASCADE,
        related_name='insights'
    )
    insight_type = models.CharField(max_length=30, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()

    # Related content
    related_post = models.ForeignKey(
        SocialPost,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    source_url = models.URLField(blank=True)

    # Action recommendation
    recommended_action = models.CharField(max_length=200, blank=True)
    suggested_message = models.TextField(blank=True)
    urgency = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )

    is_actioned = models.BooleanField(default=False)
    actioned_at = models.DateTimeField(null=True, blank=True)

    discovered_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-discovered_at']

    def __str__(self):
        return f"{self.get_insight_type_display()}: {self.title}"


class EngagementAnalytics(models.Model):
    """Analytics for social selling performance"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='social_analytics'
    )
    date = models.DateField()

    # Activity metrics
    profiles_viewed = models.IntegerField(default=0)
    connections_sent = models.IntegerField(default=0)
    connections_accepted = models.IntegerField(default=0)
    messages_sent = models.IntegerField(default=0)
    messages_replied = models.IntegerField(default=0)
    posts_liked = models.IntegerField(default=0)
    posts_commented = models.IntegerField(default=0)

    # Conversion metrics
    contacts_created = models.IntegerField(default=0)
    opportunities_created = models.IntegerField(default=0)
    meetings_booked = models.IntegerField(default=0)

    # Engagement score
    engagement_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.email} - {self.date}"
