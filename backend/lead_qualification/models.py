from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class ScoringRule(models.Model):
    """Custom scoring rules for lead qualification"""
    
    RULE_TYPES = [
        ('demographic', 'Demographic'),
        ('behavioral', 'Behavioral'),
        ('firmographic', 'Firmographic'),
        ('engagement', 'Engagement'),
        ('custom', 'Custom'),
    ]
    
    OPERATOR_CHOICES = [
        ('equals', 'Equals'),
        ('not_equals', 'Not Equals'),
        ('contains', 'Contains'),
        ('not_contains', 'Does Not Contain'),
        ('greater_than', 'Greater Than'),
        ('less_than', 'Less Than'),
        ('in_list', 'In List'),
        ('not_in_list', 'Not In List'),
        ('between', 'Between'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPES)
    field_name = models.CharField(max_length=100, help_text="Field to evaluate (e.g., 'company_size', 'industry')")
    operator = models.CharField(max_length=50, choices=OPERATOR_CHOICES)
    value = models.TextField(help_text="Value to compare against (JSON for complex values)")
    points = models.IntegerField(validators=[MinValueValidator(-100), MaxValueValidator(100)])
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Higher priority rules evaluated first")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='scoring_rules_created')
    
    class Meta:
        db_table = 'lead_scoring_rule'
        ordering = ['-priority', 'name']
        indexes = [
            models.Index(fields=['rule_type', 'is_active']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.points} points)"


class QualificationCriteria(models.Model):
    """Criteria for lead qualification stages"""
    
    STAGE_CHOICES = [
        ('mql', 'Marketing Qualified Lead'),
        ('sql', 'Sales Qualified Lead'),
        ('opportunity', 'Opportunity'),
    ]
    
    name = models.CharField(max_length=200)
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES)
    minimum_score = models.IntegerField(validators=[MinValueValidator(0)])
    required_fields = models.JSONField(default=list, help_text="List of required field names")
    required_actions = models.JSONField(default=list, help_text="List of required actions (e.g., ['email_opened', 'form_submitted'])")
    time_constraint_days = models.IntegerField(null=True, blank=True, help_text="Days since lead creation")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lead_qualification_criteria'
        ordering = ['stage', 'minimum_score']
        indexes = [
            models.Index(fields=['stage', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_stage_display()}"


class LeadScore(models.Model):
    """Stores lead scores and history"""
    
    lead = models.ForeignKey('lead_management.Lead', on_delete=models.CASCADE, related_name='scores')
    score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    previous_score = models.IntegerField(null=True, blank=True)
    score_breakdown = models.JSONField(default=dict, help_text="Points by category")
    qualification_stage = models.CharField(max_length=50, blank=True)
    
    # Score components
    demographic_score = models.IntegerField(default=0)
    behavioral_score = models.IntegerField(default=0)
    firmographic_score = models.IntegerField(default=0)
    engagement_score = models.IntegerField(default=0)
    
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'lead_score_history'
        ordering = ['-calculated_at']
        indexes = [
            models.Index(fields=['lead', '-calculated_at']),
            models.Index(fields=['score']),
            models.Index(fields=['qualification_stage']),
        ]
    
    def __str__(self):
        return f"{self.lead} - Score: {self.score}"


class QualificationWorkflow(models.Model):
    """Automated workflows for lead qualification"""
    
    TRIGGER_TYPES = [
        ('score_threshold', 'Score Threshold Reached'),
        ('stage_change', 'Stage Changed'),
        ('field_update', 'Field Updated'),
        ('time_based', 'Time-Based'),
        ('manual', 'Manual Trigger'),
    ]
    
    ACTION_TYPES = [
        ('assign_owner', 'Assign Owner'),
        ('change_status', 'Change Status'),
        ('send_email', 'Send Email'),
        ('create_task', 'Create Task'),
        ('update_field', 'Update Field'),
        ('send_notification', 'Send Notification'),
        ('move_to_stage', 'Move to Stage'),
        ('add_to_campaign', 'Add to Campaign'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPES)
    trigger_config = models.JSONField(default=dict, help_text="Configuration for trigger (e.g., {'score': 70})")
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    action_config = models.JSONField(default=dict, help_text="Configuration for action")
    
    conditions = models.JSONField(default=list, help_text="Additional conditions to check")
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    
    execution_count = models.IntegerField(default=0)
    last_executed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='workflows_created')
    
    class Meta:
        db_table = 'lead_qualification_workflow'
        ordering = ['-priority', 'name']
        indexes = [
            models.Index(fields=['trigger_type', 'is_active']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return self.name


class WorkflowExecution(models.Model):
    """Log of workflow executions"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    
    workflow = models.ForeignKey(QualificationWorkflow, on_delete=models.CASCADE, related_name='executions')
    lead = models.ForeignKey('lead_management.Lead', on_delete=models.CASCADE, related_name='workflow_executions')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    trigger_data = models.JSONField(default=dict)
    result_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'lead_workflow_execution'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['workflow', 'status']),
            models.Index(fields=['lead', '-started_at']),
            models.Index(fields=['status', '-started_at']),
        ]
    
    def __str__(self):
        return f"{self.workflow.name} - {self.lead} - {self.status}"


class LeadEnrichmentData(models.Model):
    """Store enriched data from external sources"""
    
    SOURCE_CHOICES = [
        ('clearbit', 'Clearbit'),
        ('hunter', 'Hunter.io'),
        ('linkedin', 'LinkedIn'),
        ('zoominfo', 'ZoomInfo'),
        ('manual', 'Manual Entry'),
        ('api', 'API Integration'),
    ]
    
    lead = models.ForeignKey('lead_management.Lead', on_delete=models.CASCADE, related_name='enrichment_data')
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    data = models.JSONField(default=dict)
    
    # Common enrichment fields
    company_size = models.CharField(max_length=50, blank=True)
    company_revenue = models.CharField(max_length=50, blank=True)
    company_industry = models.CharField(max_length=100, blank=True)
    company_location = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=200, blank=True)
    job_level = models.CharField(max_length=50, blank=True)
    social_profiles = models.JSONField(default=dict)
    technologies = models.JSONField(default=list)
    
    enriched_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'lead_enrichment_data'
        ordering = ['-enriched_at']
        indexes = [
            models.Index(fields=['lead', '-enriched_at']),
            models.Index(fields=['source']),
        ]
    
    def __str__(self):
        return f"{self.lead} - {self.source}"
