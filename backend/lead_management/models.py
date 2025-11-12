from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Lead(models.Model):
    """Lead model for managing sales leads"""
    LEAD_STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('unqualified', 'Unqualified'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    ]
    
    LEAD_SOURCE_CHOICES = [
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('email_campaign', 'Email Campaign'),
        ('cold_call', 'Cold Call'),
        ('trade_show', 'Trade Show'),
        ('advertisement', 'Advertisement'),
        ('other', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    
    # Lead Information
    lead_source = models.CharField(max_length=50, choices=LEAD_SOURCE_CHOICES, default='website')
    status = models.CharField(max_length=20, choices=LEAD_STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Assignment and Ownership
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_leads')
    
    # Lead Scoring and Qualification
    lead_score = models.IntegerField(default=0)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    probability = models.IntegerField(default=0)  # Percentage
    
    # Communication
    last_contact_date = models.DateTimeField(null=True, blank=True)
    next_follow_up = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    notes = models.TextField(blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'crm_leads'
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class LeadActivity(models.Model):
    """Track activities related to leads"""
    ACTIVITY_TYPE_CHOICES = [
        ('call', 'Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('note', 'Note'),
        ('task', 'Task'),
        ('status_change', 'Status Change'),
    ]
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_lead_activities'
        verbose_name = 'Lead Activity'
        verbose_name_plural = 'Lead Activities'
        ordering = ['-created_at']


class LeadAssignmentRule(models.Model):
    """Rules for automatic lead assignment"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    criteria = models.JSONField(default=dict)  # Conditions for assignment
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignment_rules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_lead_assignment_rules'
        verbose_name = 'Lead Assignment Rule'
        verbose_name_plural = 'Lead Assignment Rules'
        ordering = ['priority', '-created_at']
    
    def __str__(self):
        return self.name


class LeadConversion(models.Model):
    """Track lead conversions to opportunities"""
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name='conversion')
    opportunity = models.ForeignKey('opportunity_management.Opportunity', on_delete=models.CASCADE, null=True, blank=True)
    converted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    conversion_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    conversion_notes = models.TextField(blank=True, null=True)
    converted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_lead_conversions'
        verbose_name = 'Lead Conversion'
        verbose_name_plural = 'Lead Conversions'