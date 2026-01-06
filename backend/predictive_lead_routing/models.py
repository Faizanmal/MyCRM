"""
Predictive Lead Routing Models
AI-powered lead assignment with skill-based routing and intelligent matching
"""

import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

User = get_user_model()


class SalesRepProfile(models.Model):
    """Extended profile for sales reps with routing-relevant data"""

    EXPERTISE_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sales_profile')

    # Capacity & Availability
    max_leads_per_day = models.IntegerField(default=10)
    max_active_leads = models.IntegerField(default=50)
    current_lead_count = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    availability_schedule = models.JSONField(default=dict, help_text="Weekly availability schedule")

    # Expertise & Skills
    industries = models.JSONField(default=list, help_text="Industries rep specializes in")
    certifications = models.JSONField(default=list, help_text="Relevant certifications")
    languages = models.JSONField(default=list, help_text="Languages spoken")
    expertise_level = models.CharField(max_length=20, choices=EXPERTISE_LEVELS, default='intermediate')

    # Geographic Coverage
    regions = models.JSONField(default=list, help_text="Geographic regions covered")
    countries = models.JSONField(default=list, help_text="Countries covered")
    timezones = models.JSONField(default=list, help_text="Timezones rep can work in")

    # Deal Size Preferences
    min_deal_size = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_deal_size = models.DecimalField(max_digits=12, decimal_places=2, default=1000000)
    preferred_deal_size = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Performance Metrics
    total_leads_assigned = models.IntegerField(default=0)
    total_leads_converted = models.IntegerField(default=0)
    avg_conversion_time_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_deal_size = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    response_time_minutes = models.IntegerField(default=0, help_text="Average response time")
    customer_satisfaction = models.DecimalField(max_digits=3, decimal_places=2, default=0, help_text="0-5 rating")

    # AI Scoring
    overall_performance_score = models.DecimalField(max_digits=5, decimal_places=2, default=50)
    last_performance_update = models.DateTimeField(null=True, blank=True)

    # Round Robin
    last_assignment_at = models.DateTimeField(null=True, blank=True)
    assignment_weight = models.IntegerField(default=100, validators=[MinValueValidator(1), MaxValueValidator(200)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sales_rep_profiles'
        ordering = ['-overall_performance_score']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.expertise_level}"

    @property
    def conversion_rate(self):
        if self.total_leads_assigned == 0:
            return 0
        return round((self.total_leads_converted / self.total_leads_assigned) * 100, 2)

    @property
    def capacity_utilization(self):
        if self.max_active_leads == 0:
            return 100
        return round((self.current_lead_count / self.max_active_leads) * 100, 1)

    @property
    def is_at_capacity(self):
        return self.current_lead_count >= self.max_active_leads


class RoutingRule(models.Model):
    """Rules for automatic lead routing"""

    RULE_TYPES = [
        ('round_robin', 'Round Robin'),
        ('skill_based', 'Skill Based'),
        ('territory', 'Territory Based'),
        ('performance', 'Performance Based'),
        ('custom', 'Custom Logic'),
    ]

    PRIORITY_LEVELS = [
        (1, 'Highest'),
        (2, 'High'),
        (3, 'Medium'),
        (4, 'Low'),
        (5, 'Lowest'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Rule configuration
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES, default='round_robin')
    priority = models.IntegerField(choices=PRIORITY_LEVELS, default=3)

    # Matching criteria
    criteria = models.JSONField(default=dict, help_text="Criteria to match leads")

    # Target reps
    target_reps = models.ManyToManyField(User, blank=True, related_name='routing_rules')
    target_teams = models.JSONField(default=list, help_text="Team IDs to route to")

    # Fallback
    fallback_rep = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='fallback_rules')

    # Settings
    is_active = models.BooleanField(default=True)
    respect_capacity = models.BooleanField(default=True)
    consider_availability = models.BooleanField(default=True)

    # Statistics
    total_matches = models.IntegerField(default=0)
    total_assignments = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lead_routing_rules'
        ordering = ['priority', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.rule_type})"


class LeadAssignment(models.Model):
    """Track lead assignments and routing decisions"""

    ASSIGNMENT_METHODS = [
        ('manual', 'Manual'),
        ('round_robin', 'Round Robin'),
        ('skill_match', 'Skill Match'),
        ('ai_routing', 'AI Routing'),
        ('territory', 'Territory'),
        ('auto_escalation', 'Auto Escalation'),
        ('rebalancing', 'Rebalancing'),
    ]

    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('reassigned', 'Reassigned'),
        ('escalated', 'Escalated'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey('lead_management.Lead', on_delete=models.CASCADE, related_name='assignments')

    # Assignment details
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lead_assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='made_assignments')
    previous_assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_assignments')

    # Method and rule
    assignment_method = models.CharField(max_length=20, choices=ASSIGNMENT_METHODS)
    routing_rule = models.ForeignKey(RoutingRule, on_delete=models.SET_NULL, null=True, blank=True)

    # AI Routing scores
    match_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="AI match score 0-100")
    match_factors = models.JSONField(default=dict, help_text="Factors contributing to match")

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    status_reason = models.CharField(max_length=200, blank=True)

    # Timing
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    first_response_at = models.DateTimeField(null=True, blank=True)

    # Outcome tracking
    outcome = models.CharField(max_length=50, blank=True)
    outcome_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'lead_assignments'
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['lead', '-assigned_at']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return f"{self.lead} -> {self.assigned_to.get_full_name()}"

    @property
    def response_time_minutes(self):
        if not self.first_response_at:
            return None
        delta = self.first_response_at - self.assigned_at
        return int(delta.total_seconds() / 60)


class EscalationRule(models.Model):
    """Rules for auto-escalating hot leads"""

    TRIGGER_TYPES = [
        ('lead_score', 'Lead Score Threshold'),
        ('no_response', 'No Response'),
        ('deal_size', 'Deal Size'),
        ('vip_customer', 'VIP Customer'),
        ('time_sensitive', 'Time Sensitive'),
        ('custom', 'Custom'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Trigger
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPES)
    trigger_config = models.JSONField(default=dict)

    # Escalation target
    escalate_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escalation_targets')
    escalate_to_manager = models.BooleanField(default=False, help_text="Escalate to assigned rep's manager")

    # Settings
    notify_original_rep = models.BooleanField(default=True)
    notify_manager = models.BooleanField(default=True)

    # Timing
    wait_hours = models.IntegerField(default=24, help_text="Hours before escalation")

    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=5)

    # Statistics
    total_escalations = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lead_escalation_rules'
        ordering = ['priority']

    def __str__(self):
        return self.name


class RebalancingEvent(models.Model):
    """Track lead rebalancing events"""

    TRIGGER_REASONS = [
        ('overload', 'Rep Overloaded'),
        ('underperformance', 'Underperformance'),
        ('availability', 'Availability Change'),
        ('manual', 'Manual Rebalance'),
        ('scheduled', 'Scheduled Rebalance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    trigger_reason = models.CharField(max_length=20, choices=TRIGGER_REASONS)
    triggered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Scope
    affected_reps = models.ManyToManyField(User, related_name='rebalancing_events')

    # Results
    leads_moved = models.IntegerField(default=0)
    movements = models.JSONField(default=list, help_text="List of lead movements")

    # Analytics
    before_distribution = models.JSONField(default=dict)
    after_distribution = models.JSONField(default=dict)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'lead_rebalancing_events'
        ordering = ['-started_at']

    def __str__(self):
        return f"Rebalancing: {self.trigger_reason} - {self.leads_moved} leads"


class RoutingAnalytics(models.Model):
    """Daily analytics for lead routing performance"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()

    # Volume metrics
    total_leads_routed = models.IntegerField(default=0)
    auto_routed = models.IntegerField(default=0)
    manual_routed = models.IntegerField(default=0)
    escalations = models.IntegerField(default=0)
    rebalanced = models.IntegerField(default=0)

    # Performance metrics
    avg_match_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_response_time_minutes = models.IntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Distribution
    routing_by_method = models.JSONField(default=dict)
    routing_by_rule = models.JSONField(default=dict)
    rep_distribution = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lead_routing_analytics'
        ordering = ['-date']
        unique_together = ['date']

    def __str__(self):
        return f"Routing Analytics: {self.date}"


class SkillCertification(models.Model):
    """Certifications and skills that can be assigned to reps"""

    SKILL_TYPES = [
        ('product', 'Product Knowledge'),
        ('industry', 'Industry Expertise'),
        ('technical', 'Technical Skill'),
        ('language', 'Language'),
        ('certification', 'Certification'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    skill_type = models.CharField(max_length=20, choices=SKILL_TYPES)
    description = models.TextField(blank=True)

    # Value for routing
    routing_weight = models.IntegerField(default=10, help_text="Importance in routing decisions")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'skill_certifications'
        ordering = ['skill_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.skill_type})"


class RepSkillAssignment(models.Model):
    """Assign skills/certifications to reps"""

    PROFICIENCY_LEVELS = [
        (1, 'Basic'),
        (2, 'Intermediate'),
        (3, 'Advanced'),
        (4, 'Expert'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rep = models.ForeignKey(SalesRepProfile, on_delete=models.CASCADE, related_name='skill_assignments')
    skill = models.ForeignKey(SkillCertification, on_delete=models.CASCADE, related_name='rep_assignments')

    proficiency_level = models.IntegerField(choices=PROFICIENCY_LEVELS, default=2)
    certified_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    # Verification
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rep_skill_assignments'
        unique_together = ['rep', 'skill']

    def __str__(self):
        return f"{self.rep.user.get_full_name()} - {self.skill.name}"

    @property
    def is_expired(self):
        if not self.expiry_date:
            return False
        return self.expiry_date < timezone.now().date()


class TerritoryDefinition(models.Model):
    """Geographic territory definitions for routing"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    # Geographic boundaries
    countries = models.JSONField(default=list)
    states = models.JSONField(default=list)
    cities = models.JSONField(default=list)
    postal_codes = models.JSONField(default=list)

    # Assignment
    primary_rep = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_territories')
    backup_reps = models.ManyToManyField(User, blank=True, related_name='backup_territories')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'territory_definitions'
        ordering = ['name']

    def __str__(self):
        return self.name


class LeadQualityScore(models.Model):
    """AI-generated lead quality scores for routing priority"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.OneToOneField('lead_management.Lead', on_delete=models.CASCADE, related_name='quality_score')

    # Scores
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fit_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="ICP fit")
    engagement_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    intent_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    timing_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Factors
    scoring_factors = models.JSONField(default=dict)

    # Routing recommendations
    recommended_rep_ids = models.JSONField(default=list)
    recommended_rule_id = models.UUIDField(null=True, blank=True)
    priority_tier = models.CharField(max_length=20, default='standard')

    # Metadata
    model_version = models.CharField(max_length=50)
    scored_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lead_quality_scores'

    def __str__(self):
        return f"{self.lead} - Score: {self.overall_score}"
