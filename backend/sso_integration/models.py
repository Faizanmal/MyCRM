import uuid

from django.contrib.auth import get_user_model
from django.db import models

from multi_tenant.models import Organization

User = get_user_model()


class SSOProvider(models.Model):
    """
    SSO Provider configuration for an organization.
    Supports OAuth2 (Google, Microsoft, GitHub) and SAML (Okta, OneLogin, etc.)
    """
    PROVIDER_TYPE_CHOICES = [
        ('oauth2_google', 'Google OAuth2'),
        ('oauth2_microsoft', 'Microsoft OAuth2'),
        ('oauth2_github', 'GitHub OAuth2'),
        ('oauth2_okta', 'Okta OAuth2'),
        ('saml_okta', 'Okta SAML'),
        ('saml_onelogin', 'OneLogin SAML'),
        ('saml_azure', 'Azure AD SAML'),
        ('saml_custom', 'Custom SAML'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('testing', 'Testing'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='sso_providers'
    )
    provider_type = models.CharField(max_length=50, choices=PROVIDER_TYPE_CHOICES)
    provider_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')

    # OAuth2 Configuration
    client_id = models.CharField(max_length=500, blank=True)
    client_secret = models.CharField(max_length=500, blank=True)
    authorization_url = models.URLField(max_length=500, blank=True)
    token_url = models.URLField(max_length=500, blank=True)
    user_info_url = models.URLField(max_length=500, blank=True)
    scope = models.CharField(max_length=500, blank=True, default='openid profile email')

    # SAML Configuration
    entity_id = models.CharField(max_length=500, blank=True)
    sso_url = models.URLField(max_length=500, blank=True)
    slo_url = models.URLField(max_length=500, blank=True, help_text='Single Logout URL')
    x509_cert = models.TextField(blank=True, help_text='X.509 Certificate')

    # Attribute Mapping (JSON)
    attribute_mapping = models.JSONField(
        default=dict,
        blank=True,
        help_text='Map SSO attributes to user fields: {"email": "mail", "first_name": "givenName"}'
    )

    # Settings
    auto_create_users = models.BooleanField(
        default=True,
        help_text='Automatically create users on first SSO login'
    )
    auto_update_user_info = models.BooleanField(
        default=True,
        help_text='Update user information from SSO on each login'
    )
    default_role = models.CharField(
        max_length=20,
        default='member',
        help_text='Default role for auto-created users'
    )
    required_domains = models.JSONField(
        default=list,
        blank=True,
        help_text='Restrict SSO to specific email domains (e.g., ["company.com"])'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_sso_providers'
    )

    # Statistics
    total_logins = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['provider_type']),
        ]
        unique_together = [('organization', 'provider_name')]

    def __str__(self):
        return f"{self.provider_name} - {self.organization.name}"

    @property
    def is_oauth2(self):
        return self.provider_type.startswith('oauth2_')

    @property
    def is_saml(self):
        return self.provider_type.startswith('saml_')

    @property
    def is_active(self):
        return self.status == 'active'

    def get_redirect_uri(self):
        """Get the OAuth2 redirect URI for this provider."""
        from django.conf import settings
        base_url = settings.BASE_URL or 'http://localhost:8000'
        return f"{base_url}/api/v1/sso/callback/{self.id}/"


class SSOSession(models.Model):
    """
    Track SSO login sessions for auditing and single logout support.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(
        SSOProvider,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sso_sessions'
    )

    # Session data
    session_index = models.CharField(max_length=500, blank=True)  # SAML session index
    name_id = models.CharField(max_length=500, blank=True)  # SAML name ID
    sso_token = models.TextField(blank=True)  # OAuth2 access token
    refresh_token = models.TextField(blank=True)  # OAuth2 refresh token
    expires_at = models.DateTimeField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True)
    user_agent = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    ended_at = models.DateTimeField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['provider', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.provider.provider_name}"


class SSOLoginAttempt(models.Model):
    """
    Log all SSO login attempts for security auditing.
    """
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('error', 'Error'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(
        SSOProvider,
        on_delete=models.CASCADE,
        related_name='login_attempts'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sso_login_attempts'
    )

    # Attempt details
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True)

    # SSO data
    sso_user_id = models.CharField(max_length=500, blank=True)
    sso_attributes = models.JSONField(default=dict, blank=True)

    # Request metadata
    ip_address = models.GenericIPAddressField(blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['email', 'created_at']),
        ]

    def __str__(self):
        return f"{self.email} - {self.status} ({self.provider.provider_name})"
