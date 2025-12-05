"""
Data Enrichment Models
Models for automated data enrichment and lead intelligence
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class EnrichmentProvider(models.Model):
    """External data enrichment provider configuration"""
    
    PROVIDER_TYPES = [
        ('clearbit', 'Clearbit'),
        ('zoominfo', 'ZoomInfo'),
        ('linkedin', 'LinkedIn Sales Navigator'),
        ('apollo', 'Apollo.io'),
        ('hunter', 'Hunter.io'),
        ('fullcontact', 'FullContact'),
        ('pipl', 'Pipl'),
        ('builtwith', 'BuiltWith'),
        ('similarweb', 'SimilarWeb'),
        ('crunchbase', 'Crunchbase'),
        ('glassdoor', 'Glassdoor'),
        ('news_api', 'News API'),
        ('custom', 'Custom API'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    provider_type = models.CharField(max_length=50, choices=PROVIDER_TYPES, unique=True)
    
    # API Configuration
    api_key = models.TextField(blank=True, help_text="Encrypted API key")
    api_secret = models.TextField(blank=True, help_text="Encrypted API secret")
    api_endpoint = models.URLField(blank=True)
    
    # Rate limiting
    requests_per_minute = models.IntegerField(default=60)
    requests_per_day = models.IntegerField(default=10000)
    daily_requests_used = models.IntegerField(default=0)
    last_request_reset = models.DateField(auto_now_add=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_configured = models.BooleanField(default=False)
    
    # Capabilities
    can_enrich_person = models.BooleanField(default=True)
    can_enrich_company = models.BooleanField(default=True)
    can_find_email = models.BooleanField(default=False)
    can_verify_email = models.BooleanField(default=False)
    can_get_technographics = models.BooleanField(default=False)
    can_get_intent = models.BooleanField(default=False)
    
    # Metrics
    total_requests = models.IntegerField(default=0)
    successful_requests = models.IntegerField(default=0)
    average_response_time = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'enrichment_providers'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"


class EnrichmentProfile(models.Model):
    """Enrichment profile linked to a contact or lead"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Enrichment'),
        ('enriching', 'Enriching'),
        ('enriched', 'Enriched'),
        ('partial', 'Partially Enriched'),
        ('failed', 'Enrichment Failed'),
        ('stale', 'Data Stale'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Link to contact or lead
    contact = models.OneToOneField(
        'contact_management.Contact',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='enrichment_profile'
    )
    lead = models.OneToOneField(
        'lead_management.Lead',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='enrichment_profile'
    )
    
    # Original input data
    email = models.EmailField(db_index=True)
    domain = models.CharField(max_length=255, blank=True, db_index=True)
    linkedin_url = models.URLField(blank=True)
    
    # Enrichment status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    enrichment_score = models.IntegerField(default=0, help_text="0-100 completeness score")
    
    # Person data
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    full_name = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=200, blank=True)
    seniority = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Contact info
    phone = models.CharField(max_length=50, blank=True)
    mobile_phone = models.CharField(max_length=50, blank=True)
    work_email = models.EmailField(blank=True)
    personal_email = models.EmailField(blank=True)
    
    # Location
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    
    # Social profiles
    linkedin_profile = models.JSONField(default=dict)
    twitter_handle = models.CharField(max_length=100, blank=True)
    github_username = models.CharField(max_length=100, blank=True)
    
    # Professional history
    employment_history = models.JSONField(default=list)
    education = models.JSONField(default=list)
    skills = models.JSONField(default=list)
    
    # Enrichment metadata
    last_enriched_at = models.DateTimeField(null=True, blank=True)
    enrichment_sources = models.JSONField(default=list)
    data_freshness_score = models.FloatField(default=1.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'enrichment_profiles'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['domain']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Enrichment: {self.email}"


class CompanyEnrichment(models.Model):
    """Enriched company data"""
    
    COMPANY_SIZE_CHOICES = [
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'),
        ('1001-5000', '1001-5000 employees'),
        ('5001-10000', '5001-10000 employees'),
        ('10000+', '10000+ employees'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    domain = models.CharField(max_length=255, unique=True, db_index=True)
    
    # Basic info
    name = models.CharField(max_length=300, blank=True)
    legal_name = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    founded_year = models.IntegerField(null=True, blank=True)
    
    # Classification
    industry = models.CharField(max_length=200, blank=True)
    sub_industry = models.CharField(max_length=200, blank=True)
    industry_codes = models.JSONField(default=dict, help_text="SIC, NAICS codes")
    sector = models.CharField(max_length=100, blank=True)
    
    # Size and financials
    employee_count = models.IntegerField(null=True, blank=True)
    employee_range = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES, blank=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    revenue_range = models.CharField(max_length=100, blank=True)
    funding_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    funding_rounds = models.JSONField(default=list)
    
    # Location
    headquarters_address = models.TextField(blank=True)
    headquarters_city = models.CharField(max_length=100, blank=True)
    headquarters_state = models.CharField(max_length=100, blank=True)
    headquarters_country = models.CharField(max_length=100, blank=True)
    headquarters_postal_code = models.CharField(max_length=20, blank=True)
    office_locations = models.JSONField(default=list)
    
    # Contact
    phone = models.CharField(max_length=50, blank=True)
    email_patterns = models.JSONField(default=list, help_text="Common email patterns")
    
    # Online presence
    website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    crunchbase_url = models.URLField(blank=True)
    
    # Logo and branding
    logo_url = models.URLField(blank=True)
    brand_colors = models.JSONField(default=list)
    
    # Leadership
    ceo_name = models.CharField(max_length=200, blank=True)
    key_people = models.JSONField(default=list)
    
    # Tech stack (technographics)
    technologies = models.JSONField(default=list)
    tech_categories = models.JSONField(default=dict)
    
    # Metrics
    alexa_rank = models.IntegerField(null=True, blank=True)
    monthly_visits = models.BigIntegerField(null=True, blank=True)
    traffic_rank = models.IntegerField(null=True, blank=True)
    
    # Enrichment metadata
    enrichment_score = models.IntegerField(default=0)
    last_enriched_at = models.DateTimeField(null=True, blank=True)
    enrichment_sources = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'company_enrichments'
        verbose_name_plural = 'Company Enrichments'
    
    def __str__(self):
        return f"{self.name} ({self.domain})"


class TechnographicData(models.Model):
    """Technology stack detection for companies"""
    
    CATEGORY_CHOICES = [
        ('analytics', 'Analytics'),
        ('advertising', 'Advertising'),
        ('cms', 'CMS'),
        ('crm', 'CRM'),
        ('ecommerce', 'E-commerce'),
        ('email', 'Email Marketing'),
        ('framework', 'Framework'),
        ('hosting', 'Hosting'),
        ('language', 'Programming Language'),
        ('marketing_automation', 'Marketing Automation'),
        ('payment', 'Payment'),
        ('security', 'Security'),
        ('social', 'Social Media'),
        ('support', 'Customer Support'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    company = models.ForeignKey(
        CompanyEnrichment,
        on_delete=models.CASCADE,
        related_name='technographics'
    )
    
    technology_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    version = models.CharField(max_length=50, blank=True)
    
    # Detection info
    first_detected = models.DateTimeField(auto_now_add=True)
    last_detected = models.DateTimeField(auto_now=True)
    confidence_score = models.FloatField(default=0.0)
    detection_method = models.CharField(max_length=100, blank=True)
    
    # Competitive intelligence
    is_competitor_product = models.BooleanField(default=False)
    competitor_of = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'technographic_data'
        unique_together = ['company', 'technology_name']
    
    def __str__(self):
        return f"{self.company.name} - {self.technology_name}"


class IntentSignal(models.Model):
    """Buyer intent signals"""
    
    INTENT_TYPES = [
        ('search', 'Search Intent'),
        ('content', 'Content Consumption'),
        ('comparison', 'Comparison Shopping'),
        ('review', 'Review Research'),
        ('social', 'Social Engagement'),
        ('job_posting', 'Job Posting'),
        ('tech_install', 'Technology Install'),
        ('funding', 'Funding Event'),
        ('expansion', 'Expansion Signal'),
    ]
    
    STRENGTH_CHOICES = [
        ('weak', 'Weak'),
        ('moderate', 'Moderate'),
        ('strong', 'Strong'),
        ('very_strong', 'Very Strong'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Can be linked to company, contact, or lead
    company = models.ForeignKey(
        CompanyEnrichment,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='intent_signals'
    )
    enrichment_profile = models.ForeignKey(
        EnrichmentProfile,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='intent_signals'
    )
    
    intent_type = models.CharField(max_length=50, choices=INTENT_TYPES)
    topic = models.CharField(max_length=200)
    topic_category = models.CharField(max_length=100, blank=True)
    
    # Signal strength
    strength = models.CharField(max_length=20, choices=STRENGTH_CHOICES, default='moderate')
    score = models.IntegerField(default=50, help_text="0-100 intent score")
    
    # Details
    description = models.TextField(blank=True)
    source = models.CharField(max_length=100, blank=True)
    source_url = models.URLField(blank=True)
    
    # Timing
    detected_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Action taken
    was_actioned = models.BooleanField(default=False)
    actioned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='actioned_intent_signals'
    )
    actioned_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'intent_signals'
        ordering = ['-detected_at']
    
    def __str__(self):
        return f"{self.get_intent_type_display()} - {self.topic}"


class NewsAlert(models.Model):
    """News and trigger event alerts"""
    
    ALERT_TYPES = [
        ('funding', 'Funding Round'),
        ('acquisition', 'Acquisition'),
        ('ipo', 'IPO'),
        ('executive_change', 'Executive Change'),
        ('expansion', 'Expansion/New Office'),
        ('product_launch', 'Product Launch'),
        ('partnership', 'Partnership'),
        ('layoff', 'Layoffs/Restructuring'),
        ('award', 'Award/Recognition'),
        ('earnings', 'Earnings Report'),
        ('legal', 'Legal/Regulatory'),
        ('general', 'General News'),
    ]
    
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    company = models.ForeignKey(
        CompanyEnrichment,
        on_delete=models.CASCADE,
        related_name='news_alerts'
    )
    
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    
    # News content
    title = models.CharField(max_length=500)
    summary = models.TextField(blank=True)
    full_content = models.TextField(blank=True)
    
    # Source
    source_name = models.CharField(max_length=200, blank=True)
    source_url = models.URLField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Analysis
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='neutral')
    relevance_score = models.FloatField(default=0.5)
    
    # Key entities mentioned
    people_mentioned = models.JSONField(default=list)
    companies_mentioned = models.JSONField(default=list)
    amounts_mentioned = models.JSONField(default=list)
    
    # Sales relevance
    is_sales_trigger = models.BooleanField(default=False)
    trigger_reason = models.TextField(blank=True)
    recommended_action = models.TextField(blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='read_news_alerts'
    )
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'news_alerts'
        ordering = ['-published_at']
    
    def __str__(self):
        return f"{self.company.name} - {self.title[:50]}"


class EmailVerification(models.Model):
    """Email verification results"""
    
    STATUS_CHOICES = [
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
        ('risky', 'Risky'),
        ('unknown', 'Unknown'),
        ('catch_all', 'Catch-All'),
        ('disposable', 'Disposable'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    email = models.EmailField(unique=True, db_index=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')
    
    # Verification details
    is_deliverable = models.BooleanField(null=True)
    is_smtp_valid = models.BooleanField(null=True)
    is_free_email = models.BooleanField(null=True)
    is_role_email = models.BooleanField(null=True)  # info@, support@, etc.
    is_disposable = models.BooleanField(null=True)
    is_catch_all = models.BooleanField(null=True)
    
    # Domain info
    domain = models.CharField(max_length=255)
    mx_records = models.JSONField(default=list)
    has_mx_records = models.BooleanField(null=True)
    
    # Scores
    quality_score = models.FloatField(default=0.0, help_text="0-1 quality score")
    
    # Verification metadata
    verified_at = models.DateTimeField(auto_now_add=True)
    verification_provider = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'email_verifications'
    
    def __str__(self):
        return f"{self.email} - {self.status}"


class EnrichmentJob(models.Model):
    """Enrichment job tracking"""
    
    JOB_TYPES = [
        ('single', 'Single Record'),
        ('bulk', 'Bulk Import'),
        ('scheduled', 'Scheduled Refresh'),
        ('webhook', 'Webhook Trigger'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partial', 'Partially Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Job details
    total_records = models.IntegerField(default=0)
    processed_records = models.IntegerField(default=0)
    successful_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # User who initiated
    initiated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='enrichment_jobs'
    )
    
    # Configuration
    enrichment_types = models.JSONField(default=list, help_text="Types of enrichment to perform")
    providers_used = models.JSONField(default=list)
    
    # Results
    results_summary = models.JSONField(default=dict)
    error_log = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'enrichment_jobs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Enrichment Job {self.id} - {self.status}"


class EnrichmentRule(models.Model):
    """Rules for automatic enrichment triggers"""
    
    TRIGGER_TYPES = [
        ('new_lead', 'New Lead Created'),
        ('new_contact', 'New Contact Created'),
        ('email_received', 'Email Received'),
        ('form_submit', 'Form Submission'),
        ('import', 'Data Import'),
        ('schedule', 'Scheduled'),
        ('manual', 'Manual Trigger'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPES)
    
    # Conditions
    conditions = models.JSONField(default=dict, help_text="Conditions for rule to apply")
    
    # What to enrich
    enrich_person = models.BooleanField(default=True)
    enrich_company = models.BooleanField(default=True)
    verify_email = models.BooleanField(default=True)
    get_technographics = models.BooleanField(default=False)
    get_intent = models.BooleanField(default=False)
    get_news = models.BooleanField(default=False)
    
    # Provider preferences
    preferred_providers = models.JSONField(default=list)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Stats
    times_triggered = models.IntegerField(default=0)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='enrichment_rules'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'enrichment_rules'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_trigger_type_display()})"


class SocialProfile(models.Model):
    """Extracted social media profile data"""
    
    PLATFORM_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('github', 'GitHub'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('medium', 'Medium'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    enrichment_profile = models.ForeignKey(
        EnrichmentProfile,
        on_delete=models.CASCADE,
        related_name='social_profiles'
    )
    
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    profile_url = models.URLField()
    username = models.CharField(max_length=200, blank=True)
    
    # Profile data
    display_name = models.CharField(max_length=200, blank=True)
    headline = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)
    
    # Metrics
    followers_count = models.IntegerField(null=True, blank=True)
    following_count = models.IntegerField(null=True, blank=True)
    connections_count = models.IntegerField(null=True, blank=True)
    posts_count = models.IntegerField(null=True, blank=True)
    
    # Activity
    last_active = models.DateTimeField(null=True, blank=True)
    recent_posts = models.JSONField(default=list)
    interests = models.JSONField(default=list)
    
    # Engagement
    engagement_rate = models.FloatField(null=True, blank=True)
    
    last_synced_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'social_profiles'
        unique_together = ['enrichment_profile', 'platform']
    
    def __str__(self):
        return f"{self.enrichment_profile.email} - {self.platform}"


class FinancialData(models.Model):
    """Financial and firmographic data for companies"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    company = models.OneToOneField(
        CompanyEnrichment,
        on_delete=models.CASCADE,
        related_name='financial_data'
    )
    
    # Revenue
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    revenue_currency = models.CharField(max_length=3, default='USD')
    revenue_year = models.IntegerField(null=True, blank=True)
    revenue_growth_rate = models.FloatField(null=True, blank=True)
    
    # Funding
    total_funding = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    last_funding_round = models.CharField(max_length=50, blank=True)
    last_funding_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    last_funding_date = models.DateField(null=True, blank=True)
    investors = models.JSONField(default=list)
    
    # Valuation
    estimated_valuation = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valuation_date = models.DateField(null=True, blank=True)
    
    # Market
    market_cap = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    stock_symbol = models.CharField(max_length=10, blank=True)
    stock_exchange = models.CharField(max_length=20, blank=True)
    
    # Credit and risk
    credit_rating = models.CharField(max_length=20, blank=True)
    risk_score = models.IntegerField(null=True, blank=True)
    
    last_updated_at = models.DateTimeField(auto_now=True)
    data_source = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'financial_data'
    
    def __str__(self):
        return f"Financials for {self.company.name}"


class EnrichmentActivity(models.Model):
    """Log of enrichment activities"""
    
    ACTIVITY_TYPES = [
        ('enrich_person', 'Person Enrichment'),
        ('enrich_company', 'Company Enrichment'),
        ('verify_email', 'Email Verification'),
        ('get_technographics', 'Technographics'),
        ('get_intent', 'Intent Signal'),
        ('get_news', 'News Alert'),
        ('get_social', 'Social Profile'),
        ('get_financial', 'Financial Data'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    
    # What was enriched
    enrichment_profile = models.ForeignKey(
        EnrichmentProfile,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='activities'
    )
    company = models.ForeignKey(
        CompanyEnrichment,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='activities'
    )
    
    # Provider used
    provider = models.ForeignKey(
        EnrichmentProvider,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    
    # Status
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    # Data returned
    fields_enriched = models.JSONField(default=list)
    data_returned = models.JSONField(default=dict)
    
    # Performance
    response_time_ms = models.IntegerField(null=True, blank=True)
    api_credits_used = models.IntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'enrichment_activities'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.activity_type} - {self.created_at}"
