from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Opportunity(models.Model):
    """Opportunity model for sales pipeline management"""
    STAGE_CHOICES = [
        ('prospecting', 'Prospecting'),
        ('qualification', 'Qualification'),
        ('proposal', 'Proposal'),
        ('negotiation', 'Negotiation'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    ]
    
    PROBABILITY_CHOICES = [
        (10, '10%'),
        (25, '25%'),
        (50, '50%'),
        (75, '75%'),
        (90, '90%'),
        (100, '100%'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Contact and Company
    contact = models.ForeignKey('contact_management.Contact', on_delete=models.CASCADE, related_name='opportunities')
    company_name = models.CharField(max_length=200, blank=True, null=True)
    
    # Sales Information
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='prospecting')
    probability = models.IntegerField(choices=PROBABILITY_CHOICES, default=10)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Assignment and Ownership
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_opportunities')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_opportunities')
    
    # Dates
    expected_close_date = models.DateField()
    actual_close_date = models.DateField(null=True, blank=True)
    last_activity_date = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    notes = models.TextField(blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_opportunities'
        verbose_name = 'Opportunity'
        verbose_name_plural = 'Opportunities'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.company_name}"
    
    @property
    def weighted_amount(self):
        """Calculate weighted amount based on probability"""
        return (self.amount * self.probability) / 100


class OpportunityStage(models.Model):
    """Custom stages for opportunities"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    probability = models.IntegerField(default=0)
    order = models.IntegerField(default=0)
    is_closed = models.BooleanField(default=False)
    is_won = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_opportunity_stages'
        verbose_name = 'Opportunity Stage'
        verbose_name_plural = 'Opportunity Stages'
        ordering = ['order']
    
    def __str__(self):
        return self.name


class OpportunityActivity(models.Model):
    """Track activities related to opportunities"""
    ACTIVITY_TYPE_CHOICES = [
        ('call', 'Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('note', 'Note'),
        ('task', 'Task'),
        ('stage_change', 'Stage Change'),
        ('proposal_sent', 'Proposal Sent'),
        ('contract_sent', 'Contract Sent'),
    ]
    
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_opportunity_activities'
        verbose_name = 'Opportunity Activity'
        verbose_name_plural = 'Opportunity Activities'
        ordering = ['-created_at']


class Product(models.Model):
    """Products/Services that can be sold"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    category = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
    
    def __str__(self):
        return self.name


class OpportunityProduct(models.Model):
    """Products associated with opportunities"""
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        db_table = 'crm_opportunity_products'
        verbose_name = 'Opportunity Product'
        verbose_name_plural = 'Opportunity Products'
        unique_together = ['opportunity', 'product']
    
    def save(self, *args, **kwargs):
        # Calculate total price
        discount_amount = (self.unit_price * self.discount_percentage) / 100
        discounted_price = self.unit_price - discount_amount
        self.total_price = discounted_price * self.quantity
        super().save(*args, **kwargs)