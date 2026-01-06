"""
Internationalization (i18n) Models
Multi-language, multi-currency, and timezone support
"""

import uuid

from django.contrib.auth import get_user_model
from django.db import models


class Language(models.Model):
    """Supported languages"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=10, unique=True)  # e.g., 'en-US', 'fr-FR'
    name = models.CharField(max_length=100)  # English name
    native_name = models.CharField(max_length=100)  # Name in native language

    # RTL support
    is_rtl = models.BooleanField(default=False)

    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    # Completeness
    translation_coverage = models.FloatField(default=0)  # 0-100%

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class TranslationKey(models.Model):
    """Translation keys/strings"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=255, unique=True)  # e.g., 'dashboard.title'
    namespace = models.CharField(max_length=100, db_index=True)  # e.g., 'dashboard', 'common'
    description = models.TextField(blank=True)  # Context for translators

    # Default value (usually English)
    default_value = models.TextField()

    # Metadata
    max_length = models.IntegerField(null=True, blank=True)  # For UI constraints
    context_screenshot = models.URLField(blank=True)  # Screenshot showing context

    # Status
    is_active = models.BooleanField(default=True)
    needs_review = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['namespace', 'key']

    def __str__(self):
        return self.key


class Translation(models.Model):
    """Actual translations"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.ForeignKey(TranslationKey, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='translations')

    # Translation
    value = models.TextField()

    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('needs_review', 'Needs Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Quality
    is_machine_translated = models.BooleanField(default=False)
    confidence_score = models.FloatField(null=True, blank=True)  # For MT

    # Audit
    translated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='translations'
    )
    reviewed_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='reviewed_translations'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['key', 'language']
        ordering = ['key__key']

    def __str__(self):
        return f"{self.key.key} - {self.language.code}"


class Currency(models.Model):
    """Supported currencies"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=3, unique=True)  # ISO 4217
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)

    # Display format
    decimal_places = models.IntegerField(default=2)
    decimal_separator = models.CharField(max_length=5, default='.')
    thousands_separator = models.CharField(max_length=5, default=',')
    symbol_position = models.CharField(
        max_length=10,
        choices=[('before', 'Before'), ('after', 'After')],
        default='before'
    )

    # Exchange rate (relative to base currency)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=10, default=1)
    exchange_rate_updated_at = models.DateTimeField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_base = models.BooleanField(default=False)  # Base currency for org

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'currencies'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} ({self.symbol})"


class ExchangeRateHistory(models.Model):
    """Historical exchange rates"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='rate_history')
    rate = models.DecimalField(max_digits=20, decimal_places=10)
    source = models.CharField(max_length=100)  # API provider

    recorded_at = models.DateTimeField()

    class Meta:
        ordering = ['-recorded_at']


class Timezone(models.Model):
    """Timezone definitions"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)  # IANA name
    display_name = models.CharField(max_length=150)
    abbreviation = models.CharField(max_length=10)
    offset = models.CharField(max_length=10)  # e.g., '+05:30'
    offset_minutes = models.IntegerField()  # For sorting

    # DST info
    uses_dst = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['offset_minutes', 'name']

    def __str__(self):
        return f"{self.display_name} ({self.offset})"


class Locale(models.Model):
    """Complete locale configuration"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)  # e.g., 'en-US', 'de-DE'
    name = models.CharField(max_length=100)

    # References
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    timezone = models.ForeignKey(Timezone, on_delete=models.CASCADE)

    # Date/Time formats
    date_format = models.CharField(max_length=50, default='MM/DD/YYYY')
    time_format = models.CharField(max_length=50, default='HH:mm:ss')
    datetime_format = models.CharField(max_length=100, default='MM/DD/YYYY HH:mm:ss')
    first_day_of_week = models.IntegerField(default=0)  # 0=Sunday, 1=Monday

    # Number formats
    number_format = models.CharField(max_length=50, default='#,##0.##')

    # Regional
    country_code = models.CharField(max_length=2)  # ISO 3166-1 alpha-2

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class UserLocalePreference(models.Model):
    """User-specific locale preferences"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='locale_preference'
    )

    # Preferences
    language = models.ForeignKey(
        Language,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    timezone = models.ForeignKey(
        Timezone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    locale = models.ForeignKey(
        Locale,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Overrides
    date_format_override = models.CharField(max_length=50, blank=True)
    time_format_override = models.CharField(max_length=50, blank=True)
    first_day_of_week_override = models.IntegerField(null=True, blank=True)

    # Auto-detection
    auto_detect_timezone = models.BooleanField(default=True)
    last_detected_timezone = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Locale preferences for {self.user}"


class ContentLocalization(models.Model):
    """Localized content for dynamic data"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Content reference
    content_type = models.CharField(max_length=100)  # e.g., 'product', 'email_template'
    content_id = models.UUIDField()
    field_name = models.CharField(max_length=100)  # e.g., 'name', 'description'

    # Localization
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    value = models.TextField()

    # Status
    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['content_type', 'content_id', 'field_name', 'language']

    def __str__(self):
        return f"{self.content_type}:{self.content_id}:{self.field_name} - {self.language.code}"


class LocalizationExport(models.Model):
    """Track translation exports for external tools"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('xliff', 'XLIFF'),
        ('csv', 'CSV'),
        ('po', 'Gettext PO'),
    ]
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES)

    # Scope
    languages = models.ManyToManyField(Language)
    namespaces = models.JSONField(default=list)  # List of namespaces to export

    # Export details
    file_url = models.URLField(blank=True)
    record_count = models.IntegerField(default=0)

    # Audit
    exported_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True
    )
    exported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Export {self.id} ({self.format})"
