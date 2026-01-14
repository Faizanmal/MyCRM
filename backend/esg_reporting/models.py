"""
ESG Reporting Models
Environmental, Social, and Governance metrics tracking.
"""

import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ESGFramework(models.Model):
    """Reporting frameworks (GRI, SASB, TCFD, CDP, etc.)"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    version = models.CharField(max_length=20)

    website_url = models.URLField(blank=True)
    documentation_url = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'esg_frameworks'
        verbose_name = 'ESG Framework'
        verbose_name_plural = 'ESG Frameworks'

    def __str__(self):
        return f"{self.name} ({self.code})"


class ESGMetricCategory(models.Model):
    """Categories for ESG metrics"""

    ESG_PILLAR = [
        ('environmental', 'Environmental'),
        ('social', 'Social'),
        ('governance', 'Governance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    pillar = models.CharField(max_length=20, choices=ESG_PILLAR)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'esg_metric_categories'
        verbose_name = 'Metric Category'
        verbose_name_plural = 'Metric Categories'
        ordering = ['pillar', 'order']

    def __str__(self):
        return f"{self.get_pillar_display()} - {self.name}"


class ESGMetricDefinition(models.Model):
    """Definitions of ESG metrics"""

    DATA_TYPE = [
        ('number', 'Number'),
        ('percentage', 'Percentage'),
        ('currency', 'Currency'),
        ('boolean', 'Yes/No'),
        ('text', 'Text'),
        ('rating', 'Rating'),
    ]

    COLLECTION_FREQUENCY = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    category = models.ForeignKey(
        ESGMetricCategory,
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    frameworks = models.ManyToManyField(
        ESGFramework,
        related_name='metrics',
        blank=True
    )

    # Data specifications
    data_type = models.CharField(max_length=20, choices=DATA_TYPE)
    unit = models.CharField(max_length=50, blank=True)  # e.g., "tons CO2", "kWh", "%"
    collection_frequency = models.CharField(
        max_length=20,
        choices=COLLECTION_FREQUENCY,
        default='monthly'
    )

    # Validation
    min_value = models.FloatField(blank=True)
    max_value = models.FloatField(blank=True)

    # Targets
    benchmark_value = models.FloatField(blank=True)
    target_direction = models.CharField(
        max_length=10,
        choices=[('higher', 'Higher is Better'), ('lower', 'Lower is Better')],
        blank=True
    )

    # Calculation
    formula = models.TextField(blank=True)
    is_calculated = models.BooleanField(default=False)
    source_metrics = models.JSONField(default=list, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'esg_metric_definitions'
        verbose_name = 'Metric Definition'
        verbose_name_plural = 'Metric Definitions'
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class ESGDataEntry(models.Model):
    """Actual ESG data entries"""

    STATUS = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    CONFIDENCE_LEVEL = [
        ('verified', 'Verified'),
        ('estimated', 'Estimated'),
        ('provisional', 'Provisional'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    metric = models.ForeignKey(
        ESGMetricDefinition,
        on_delete=models.CASCADE,
        related_name='entries'
    )
    tenant = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='esg_entries'
    )

    # Period
    period_start = models.DateField()
    period_end = models.DateField()
    fiscal_year = models.IntegerField()
    fiscal_quarter = models.IntegerField(blank=True)

    # Value
    value = models.FloatField(blank=True)
    text_value = models.TextField(blank=True)

    # Context
    scope = models.CharField(max_length=100, blank=True)  # e.g., "Scope 1", "Scope 2"
    location = models.CharField(max_length=200, blank=True)
    business_unit = models.CharField(max_length=200, blank=True)

    # Data quality
    confidence_level = models.CharField(max_length=20, choices=CONFIDENCE_LEVEL, default='verified')
    data_source = models.CharField(max_length=200, blank=True)
    methodology = models.TextField(blank=True)

    # Evidence
    evidence_files = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS, default='draft')

    # Audit
    entered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='esg_entries'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_esg_entries'
    )
    approved_at = models.DateTimeField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'esg_data_entries'
        verbose_name = 'Data Entry'
        verbose_name_plural = 'Data Entries'
        ordering = ['-period_end', 'metric']

    def __str__(self):
        return f"{self.metric.name} - {self.period_start} to {self.period_end}"


class ESGTarget(models.Model):
    """ESG targets and goals"""

    TARGET_TYPE = [
        ('reduction', 'Reduction'),
        ('increase', 'Increase'),
        ('maintain', 'Maintain'),
        ('achieve', 'Achieve'),
    ]

    STATUS = [
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('behind', 'Behind'),
        ('achieved', 'Achieved'),
        ('not_started', 'Not Started'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    metric = models.ForeignKey(
        ESGMetricDefinition,
        on_delete=models.CASCADE,
        related_name='targets'
    )
    tenant = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='esg_targets'
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Target details
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE)
    baseline_value = models.FloatField()
    baseline_year = models.IntegerField()
    target_value = models.FloatField()
    target_year = models.IntegerField()

    # Interim targets
    interim_targets = models.JSONField(default=list, blank=True)  # [{year: 2025, value: 50}]

    # Progress
    current_value = models.FloatField(blank=True)
    progress_percentage = models.FloatField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='not_started')

    # Links
    sdg_goals = models.JSONField(default=list, blank=True)  # UN SDG alignment
    science_based = models.BooleanField(default=False)
    net_zero_aligned = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'esg_targets'
        verbose_name = 'ESG Target'
        verbose_name_plural = 'ESG Targets'

    def __str__(self):
        return f"{self.name} ({self.target_year})"


class ESGReport(models.Model):
    """Generated ESG reports"""

    REPORT_TYPE = [
        ('annual', 'Annual Sustainability Report'),
        ('quarterly', 'Quarterly Update'),
        ('framework', 'Framework-Specific Report'),
        ('disclosure', 'Disclosure Document'),
        ('custom', 'Custom Report'),
    ]

    STATUS = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='esg_reports'
    )

    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE)
    framework = models.ForeignKey(
        ESGFramework,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Period
    fiscal_year = models.IntegerField()
    period_start = models.DateField()
    period_end = models.DateField()

    # Content
    executive_summary = models.TextField(blank=True)
    sections = models.JSONField(default=list)  # [{title, content, metrics}]
    included_metrics = models.ManyToManyField(ESGMetricDefinition, blank=True)

    # Files
    pdf_url = models.URLField(blank=True)
    xlsx_url = models.URLField(blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS, default='draft')

    # Workflow
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_esg_reports'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_esg_reports'
    )
    published_at = models.DateTimeField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'esg_reports'
        verbose_name = 'ESG Report'
        verbose_name_plural = 'ESG Reports'
        ordering = ['-fiscal_year', '-period_end']

    def __str__(self):
        return f"{self.name} ({self.fiscal_year})"


class CarbonFootprint(models.Model):
    """Carbon emissions tracking"""

    EMISSION_SCOPE = [
        ('scope1', 'Scope 1 - Direct'),
        ('scope2', 'Scope 2 - Energy Indirect'),
        ('scope3', 'Scope 3 - Other Indirect'),
    ]

    EMISSION_CATEGORY = [
        # Scope 1
        ('stationary_combustion', 'Stationary Combustion'),
        ('mobile_combustion', 'Mobile Combustion'),
        ('process_emissions', 'Process Emissions'),
        ('fugitive_emissions', 'Fugitive Emissions'),
        # Scope 2
        ('purchased_electricity', 'Purchased Electricity'),
        ('purchased_heat', 'Purchased Heat/Steam'),
        ('purchased_cooling', 'Purchased Cooling'),
        # Scope 3
        ('business_travel', 'Business Travel'),
        ('employee_commuting', 'Employee Commuting'),
        ('purchased_goods', 'Purchased Goods & Services'),
        ('waste', 'Waste Generated'),
        ('upstream_transportation', 'Upstream Transportation'),
        ('downstream_transportation', 'Downstream Transportation'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carbon_entries'
    )

    # Classification
    scope = models.CharField(max_length=10, choices=EMISSION_SCOPE)
    category = models.CharField(max_length=50, choices=EMISSION_CATEGORY)

    # Period
    period_start = models.DateField()
    period_end = models.DateField()

    # Location
    location = models.CharField(max_length=200, blank=True)
    facility = models.CharField(max_length=200, blank=True)

    # Emissions data
    activity_data = models.FloatField()  # e.g., kWh, liters, km
    activity_unit = models.CharField(max_length=50)
    emission_factor = models.FloatField()
    emission_factor_source = models.CharField(max_length=200, blank=True)

    # Results (in metric tons CO2e)
    co2_emissions = models.FloatField(default=0)
    ch4_emissions = models.FloatField(default=0)
    n2o_emissions = models.FloatField(default=0)
    total_co2e = models.FloatField()

    # Data quality
    data_source = models.CharField(max_length=200, blank=True)
    methodology = models.CharField(max_length=200, blank=True)
    uncertainty = models.FloatField(blank=True)  # percentage

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'esg_carbon_footprint'
        verbose_name = 'Carbon Footprint Entry'
        verbose_name_plural = 'Carbon Footprint Entries'
        ordering = ['-period_end', 'scope']

    def __str__(self):
        return f"{self.get_scope_display()} - {self.get_category_display()} ({self.total_co2e} tCO2e)"


class SupplierESGAssessment(models.Model):
    """ESG assessments for suppliers/vendors"""

    RATING = [
        ('A', 'A - Excellent'),
        ('B', 'B - Good'),
        ('C', 'C - Average'),
        ('D', 'D - Below Average'),
        ('F', 'F - Fail'),
    ]

    RISK_LEVEL = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='supplier_assessments'
    )

    # Supplier info
    supplier_name = models.CharField(max_length=255)
    supplier_id = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # Assessment
    assessment_date = models.DateField()
    valid_until = models.DateField()

    # Scores (0-100)
    environmental_score = models.IntegerField()
    social_score = models.IntegerField()
    governance_score = models.IntegerField()
    overall_score = models.IntegerField()

    # Ratings
    environmental_rating = models.CharField(max_length=2, choices=RATING)
    social_rating = models.CharField(max_length=2, choices=RATING)
    governance_rating = models.CharField(max_length=2, choices=RATING)
    overall_rating = models.CharField(max_length=2, choices=RATING)

    # Risk
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL)
    risk_factors = models.JSONField(default=list, blank=True)

    # Details
    assessment_details = models.JSONField(default=dict)
    certifications = models.JSONField(default=list, blank=True)
    improvement_areas = models.JSONField(default=list, blank=True)

    # Documents
    questionnaire_responses = models.JSONField(default=dict, blank=True)
    evidence_documents = models.JSONField(default=list, blank=True)

    notes = models.TextField(blank=True)

    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'esg_supplier_assessments'
        verbose_name = 'Supplier Assessment'
        verbose_name_plural = 'Supplier Assessments'
        ordering = ['-assessment_date']

    def __str__(self):
        return f"{self.supplier_name} - {self.overall_rating}"
