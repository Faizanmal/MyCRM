"""
AI Sales Assistant Models
Your AI-powered sales coach
Features that NO competitor has out of the box!
"""

import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class AIEmailDraft(models.Model):
    """AI-generated email drafts"""

    EMAIL_TYPES = [
        ('cold_outreach', 'Cold Outreach'),
        ('follow_up', 'Follow Up'),
        ('proposal', 'Proposal'),
        ('meeting_request', 'Meeting Request'),
        ('thank_you', 'Thank You'),
        ('re_engagement', 'Re-engagement'),
        ('objection_handling', 'Objection Handling'),
        ('closing', 'Closing'),
        ('custom', 'Custom'),
    ]

    TONE_CHOICES = [
        ('professional', 'Professional'),
        ('friendly', 'Friendly'),
        ('casual', 'Casual'),
        ('formal', 'Formal'),
        ('urgent', 'Urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_email_drafts')

    # Context
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    # Generation parameters
    email_type = models.CharField(max_length=50, choices=EMAIL_TYPES)
    tone = models.CharField(max_length=20, choices=TONE_CHOICES, default='professional')
    context = models.TextField(help_text="Additional context for AI")
    key_points = models.JSONField(default=list, help_text="Key points to include")

    # Generated content
    subject = models.CharField(max_length=500)
    body = models.TextField()

    # Variations
    variations = models.JSONField(default=list, help_text="Alternative versions")

    # Feedback
    was_used = models.BooleanField(default=False)
    user_rating = models.IntegerField(null=True, blank=True)  # 1-5 stars
    user_feedback = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_email_drafts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_email_type_display()}: {self.subject[:50]}"


class SalesCoachAdvice(models.Model):
    """AI-generated sales coaching advice"""

    ADVICE_TYPES = [
        ('deal_strategy', 'Deal Strategy'),
        ('objection_response', 'Objection Response'),
        ('negotiation_tip', 'Negotiation Tip'),
        ('timing_suggestion', 'Timing Suggestion'),
        ('relationship_building', 'Relationship Building'),
        ('competitive_positioning', 'Competitive Positioning'),
        ('upsell_opportunity', 'Upsell Opportunity'),
        ('risk_mitigation', 'Risk Mitigation'),
    ]

    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales_coaching')

    # Related to
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='ai_advice'
    )
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    # Advice
    advice_type = models.CharField(max_length=50, choices=ADVICE_TYPES)
    title = models.CharField(max_length=200)
    advice = models.TextField()
    reasoning = models.TextField(help_text="Why this advice is given")

    # Action items
    action_items = models.JSONField(default=list)

    # Priority
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')

    # Effectiveness
    was_helpful = models.BooleanField(null=True)
    outcome = models.TextField(blank=True)

    # Status
    is_dismissed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'sales_coach_advice'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_advice_type_display()}: {self.title}"


class ObjectionResponse(models.Model):
    """Library of objection handling responses"""

    OBJECTION_CATEGORIES = [
        ('price', 'Price/Budget'),
        ('timing', 'Timing'),
        ('competitor', 'Competitor'),
        ('authority', 'Decision Authority'),
        ('need', 'Need/Fit'),
        ('trust', 'Trust/Risk'),
        ('implementation', 'Implementation'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The objection
    category = models.CharField(max_length=50, choices=OBJECTION_CATEGORIES)
    objection = models.TextField(help_text="The customer's objection")
    keywords = models.JSONField(default=list, help_text="Keywords to match")

    # Responses
    responses = models.JSONField(default=list, help_text="List of response options")
    best_response = models.TextField(help_text="The recommended response")

    # Context
    when_to_use = models.TextField(blank=True)
    follow_up_questions = models.JSONField(default=list)

    # Effectiveness tracking
    times_used = models.IntegerField(default=0)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Ownership
    is_system = models.BooleanField(default=False)  # Built-in vs user-created
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'objection_responses'
        ordering = ['-times_used', 'category']

    def __str__(self):
        return f"{self.get_category_display()}: {self.objection[:50]}"


class CallScript(models.Model):
    """AI-generated call scripts"""

    SCRIPT_TYPES = [
        ('discovery', 'Discovery Call'),
        ('demo', 'Demo Call'),
        ('follow_up', 'Follow-up Call'),
        ('closing', 'Closing Call'),
        ('cold_call', 'Cold Call'),
        ('check_in', 'Check-in Call'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='call_scripts')

    # Script details
    name = models.CharField(max_length=200)
    script_type = models.CharField(max_length=50, choices=SCRIPT_TYPES)
    description = models.TextField(blank=True)

    # The script content (structured)
    opening = models.TextField(help_text="Opening statement")
    discovery_questions = models.JSONField(default=list)
    value_propositions = models.JSONField(default=list)
    objection_handlers = models.JSONField(default=dict)
    closing_techniques = models.JSONField(default=list)
    next_steps = models.TextField(blank=True)

    # AI-generated talking points based on contact/opportunity
    personalized_points = models.JSONField(default=list)

    # Stats
    times_used = models.IntegerField(default=0)
    avg_call_duration = models.IntegerField(null=True)  # minutes
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    is_template = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'call_scripts'
        ordering = ['-times_used', 'name']

    def __str__(self):
        return self.name


class DealInsight(models.Model):
    """AI-generated insights for deals"""

    INSIGHT_TYPES = [
        ('win_factor', 'Win Factor'),
        ('risk_factor', 'Risk Factor'),
        ('opportunity', 'Opportunity'),
        ('warning', 'Warning'),
        ('suggestion', 'Suggestion'),
        ('benchmark', 'Benchmark Comparison'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.CASCADE,
        related_name='ai_insights'
    )

    insight_type = models.CharField(max_length=50, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    insight = models.TextField()

    # Data points that led to this insight
    data_points = models.JSONField(default=list)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Impact
    impact_score = models.IntegerField(default=0)  # -100 to 100

    # Status
    is_acknowledged = models.BooleanField(default=False)
    is_actioned = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'deal_insights'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_insight_type_display()}: {self.title}"


class WinLossAnalysis(models.Model):
    """AI analysis of won/lost deals"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    opportunity = models.OneToOneField(
        'opportunity_management.Opportunity',
        on_delete=models.CASCADE,
        related_name='win_loss_analysis'
    )

    # Outcome
    outcome = models.CharField(max_length=20)  # won or lost

    # AI Analysis
    primary_factors = models.JSONField(default=list, help_text="Main reasons for outcome")
    secondary_factors = models.JSONField(default=list)

    # What worked/didn't work
    what_worked = models.JSONField(default=list)
    what_didnt_work = models.JSONField(default=list)

    # Competitive analysis
    competitor_impact = models.TextField(blank=True)

    # Recommendations for future
    lessons_learned = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)

    # Deal characteristics
    deal_duration_days = models.IntegerField(null=True)
    stakeholders_involved = models.IntegerField(null=True)
    touchpoints_count = models.IntegerField(null=True)

    # Similar deals
    similar_won_deals = models.JSONField(default=list)
    similar_lost_deals = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'win_loss_analyses'
        ordering = ['-created_at']

    def __str__(self):
        return f"Analysis: {self.opportunity.name} ({self.outcome})"


class PersonaProfile(models.Model):
    """AI-generated buyer personas"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)  # e.g., "Technical Decision Maker"
    description = models.TextField()

    # Demographics
    typical_titles = models.JSONField(default=list)
    typical_industries = models.JSONField(default=list)
    company_size_range = models.CharField(max_length=100, blank=True)

    # Psychology
    motivations = models.JSONField(default=list)
    pain_points = models.JSONField(default=list)
    goals = models.JSONField(default=list)
    fears = models.JSONField(default=list)

    # Communication preferences
    preferred_channels = models.JSONField(default=list)
    communication_style = models.TextField(blank=True)
    best_times_to_contact = models.JSONField(default=list)

    # Sales approach
    key_value_props = models.JSONField(default=list)
    common_objections = models.JSONField(default=list)
    winning_approaches = models.JSONField(default=list)
    things_to_avoid = models.JSONField(default=list)

    # Content preferences
    content_types_preferred = models.JSONField(default=list)

    # Stats
    contacts_matched = models.IntegerField(default=0)
    deals_won = models.IntegerField(default=0)
    deals_lost = models.IntegerField(default=0)
    avg_deal_size = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_system = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'persona_profiles'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def win_rate(self):
        total = self.deals_won + self.deals_lost
        if total == 0:
            return 0
        return round((self.deals_won / total) * 100, 1)


class ContactPersonaMatch(models.Model):
    """Match contacts to personas"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.CASCADE,
        related_name='persona_matches'
    )
    persona = models.ForeignKey(PersonaProfile, on_delete=models.CASCADE)

    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)
    matching_factors = models.JSONField(default=list)

    # Recommended approach
    recommended_approach = models.TextField(blank=True)
    talking_points = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contact_persona_matches'
        ordering = ['-confidence_score']
        unique_together = ['contact', 'persona']

    def __str__(self):
        return f"{self.contact.full_name} → {self.persona.name}"
