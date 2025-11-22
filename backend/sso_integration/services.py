"""
SSO Authentication Services for OAuth2 and SAML.
"""
import requests
import base64
import hashlib
import secrets
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlencode, parse_qs, urlparse
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import SSOProvider, SSOSession, SSOLoginAttempt

User = get_user_model()


class OAuth2Service:
    """
    OAuth2 authentication service supporting multiple providers.
    """
    
    def __init__(self, provider: SSOProvider):
        self.provider = provider
        if not provider.is_oauth2:
            raise ValueError("Provider must be an OAuth2 provider")

    def generate_authorization_url(self, state: str = None, redirect_uri: str = None) -> Tuple[str, str]:
        """
        Generate OAuth2 authorization URL with PKCE.
        Returns: (authorization_url, code_verifier)
        """
        if not state:
            state = secrets.token_urlsafe(32)
        
        # Generate PKCE code verifier and challenge
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')
        
        params = {
            'client_id': self.provider.client_id,
            'redirect_uri': redirect_uri or self.provider.get_redirect_uri(),
            'response_type': 'code',
            'scope': self.provider.scope,
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
        }
        
        # Provider-specific parameters
        if self.provider.provider_type == 'oauth2_microsoft':
            params['response_mode'] = 'query'
            params['prompt'] = 'select_account'
        elif self.provider.provider_type == 'oauth2_google':
            params['access_type'] = 'offline'
            params['prompt'] = 'consent'
        
        authorization_url = f"{self.provider.authorization_url}?{urlencode(params)}"
        return authorization_url, code_verifier

    def exchange_code_for_token(
        self,
        code: str,
        code_verifier: str,
        redirect_uri: str = None
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        """
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri or self.provider.get_redirect_uri(),
            'client_id': self.provider.client_id,
            'client_secret': self.provider.client_secret,
            'code_verifier': code_verifier,
        }
        
        try:
            response = requests.post(
                self.provider.token_url,
                data=data,
                headers={'Accept': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Token exchange failed: {str(e)}")

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Fetch user information from OAuth2 provider.
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(
                self.provider.user_info_url,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch user info: {str(e)}")

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        """
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.provider.client_id,
            'client_secret': self.provider.client_secret,
        }
        
        try:
            response = requests.post(
                self.provider.token_url,
                data=data,
                headers={'Accept': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Token refresh failed: {str(e)}")

    def map_user_attributes(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map OAuth2 user info to application user fields.
        """
        # Default mapping for common providers
        default_mappings = {
            'oauth2_google': {
                'email': 'email',
                'first_name': 'given_name',
                'last_name': 'family_name',
                'picture': 'picture',
            },
            'oauth2_microsoft': {
                'email': 'mail',
                'first_name': 'givenName',
                'last_name': 'surname',
                'picture': 'photo',
            },
            'oauth2_github': {
                'email': 'email',
                'first_name': 'name',
                'last_name': '',
                'picture': 'avatar_url',
            },
        }
        
        mapping = self.provider.attribute_mapping or default_mappings.get(
            self.provider.provider_type, {}
        )
        
        mapped_data = {}
        for local_field, remote_field in mapping.items():
            if remote_field and remote_field in user_info:
                mapped_data[local_field] = user_info[remote_field]
        
        # Ensure email is always present
        if 'email' not in mapped_data:
            mapped_data['email'] = user_info.get('email') or user_info.get('mail')
        
        return mapped_data


class SAMLService:
    """
    SAML 2.0 authentication service.
    """
    
    def __init__(self, provider: SSOProvider):
        self.provider = provider
        if not provider.is_saml:
            raise ValueError("Provider must be a SAML provider")

    def generate_authn_request(self, relay_state: str = None) -> str:
        """
        Generate SAML AuthnRequest XML.
        """
        from django.conf import settings
        import uuid
        from datetime import datetime
        
        request_id = f"_{uuid.uuid4()}"
        issue_instant = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        acs_url = f"{settings.BASE_URL}/api/v1/sso/saml/acs/"
        
        authn_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:AuthnRequest 
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="{request_id}"
    Version="2.0"
    IssueInstant="{issue_instant}"
    Destination="{self.provider.sso_url}"
    AssertionConsumerServiceURL="{acs_url}"
    ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">
    <saml:Issuer>{self.provider.entity_id}</saml:Issuer>
    <samlp:NameIDPolicy 
        Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
        AllowCreate="true"/>
</samlp:AuthnRequest>"""
        
        # Base64 encode and deflate
        encoded_request = base64.b64encode(authn_request.encode()).decode()
        
        return encoded_request

    def parse_saml_response(self, saml_response: str) -> Dict[str, Any]:
        """
        Parse and validate SAML response.
        This is a simplified implementation. Production should use python3-saml or similar.
        """
        import xml.etree.ElementTree as ET
        
        try:
            # Decode base64
            decoded = base64.b64decode(saml_response)
            root = ET.fromstring(decoded)
            
            # Extract namespaces
            ns = {
                'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
                'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol'
            }
            
            # Extract attributes
            attributes = {}
            for attr in root.findall('.//saml:Attribute', ns):
                name = attr.get('Name')
                value_elem = attr.find('saml:AttributeValue', ns)
                if value_elem is not None:
                    attributes[name] = value_elem.text
            
            # Extract NameID (typically email)
            name_id_elem = root.find('.//saml:NameID', ns)
            name_id = name_id_elem.text if name_id_elem is not None else None
            
            # Extract SessionIndex
            authn_statement = root.find('.//saml:AuthnStatement', ns)
            session_index = authn_statement.get('SessionIndex') if authn_statement is not None else None
            
            return {
                'name_id': name_id,
                'session_index': session_index,
                'attributes': attributes,
            }
        except Exception as e:
            raise Exception(f"Failed to parse SAML response: {str(e)}")

    def map_user_attributes(self, saml_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map SAML attributes to application user fields.
        """
        attributes = saml_data.get('attributes', {})
        
        # Default SAML attribute mapping
        default_mapping = {
            'email': 'mail',
            'first_name': 'givenName',
            'last_name': 'sn',
        }
        
        mapping = self.provider.attribute_mapping or default_mapping
        
        mapped_data = {}
        for local_field, saml_attr in mapping.items():
            if saml_attr in attributes:
                mapped_data[local_field] = attributes[saml_attr]
        
        # Use NameID as email if not found in attributes
        if 'email' not in mapped_data:
            mapped_data['email'] = saml_data.get('name_id')
        
        return mapped_data


class SSOAuthenticationService:
    """
    Main SSO authentication service coordinating OAuth2 and SAML.
    """
    
    @staticmethod
    def authenticate_user(
        provider: SSOProvider,
        user_data: Dict[str, Any],
        request_meta: Dict[str, Any] = None
    ) -> Tuple[User, bool]:
        """
        Authenticate or create user from SSO data.
        Returns: (user, created)
        """
        email = user_data.get('email')
        if not email:
            raise ValueError("Email is required for SSO authentication")
        
        # Validate email domain if required
        if provider.required_domains:
            domain = email.split('@')[1]
            if domain not in provider.required_domains:
                raise ValueError(f"Email domain {domain} is not allowed for this SSO provider")
        
        # Log login attempt
        attempt = SSOLoginAttempt.objects.create(
            provider=provider,
            email=email,
            status='success',
            sso_attributes=user_data,
            ip_address=request_meta.get('REMOTE_ADDR') if request_meta else None,
            user_agent=request_meta.get('HTTP_USER_AGENT') if request_meta else None,
        )
        
        try:
            # Try to find existing user
            user = User.objects.get(email=email)
            created = False
            
            # Update user info if configured
            if provider.auto_update_user_info:
                if 'first_name' in user_data:
                    user.first_name = user_data['first_name']
                if 'last_name' in user_data:
                    user.last_name = user_data['last_name']
                user.save()
            
        except User.DoesNotExist:
            # Create new user if allowed
            if not provider.auto_create_users:
                attempt.status = 'failed'
                attempt.error_message = 'User does not exist and auto-creation is disabled'
                attempt.save()
                raise ValueError("User does not exist and auto-creation is disabled")
            
            user = User.objects.create_user(
                email=email,
                username=email,
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
            )
            created = True
            
            # Add user to organization with default role
            from multi_tenant.models import OrganizationMember
            OrganizationMember.objects.create(
                organization=provider.organization,
                user=user,
                role=provider.default_role,
            )
        
        # Update attempt with user
        attempt.user = user
        attempt.save()
        
        # Update provider statistics
        provider.total_logins += 1
        provider.last_used_at = timezone.now()
        provider.save(update_fields=['total_logins', 'last_used_at'])
        
        return user, created

    @staticmethod
    def create_session(
        provider: SSOProvider,
        user: User,
        session_data: Dict[str, Any],
        request_meta: Dict[str, Any] = None
    ) -> SSOSession:
        """
        Create SSO session for tracking and single logout.
        """
        expires_at = None
        if 'expires_in' in session_data:
            expires_at = timezone.now() + timedelta(seconds=session_data['expires_in'])
        
        session = SSOSession.objects.create(
            provider=provider,
            user=user,
            session_index=session_data.get('session_index', ''),
            name_id=session_data.get('name_id', ''),
            sso_token=session_data.get('access_token', ''),
            refresh_token=session_data.get('refresh_token', ''),
            expires_at=expires_at,
            ip_address=request_meta.get('REMOTE_ADDR') if request_meta else None,
            user_agent=request_meta.get('HTTP_USER_AGENT') if request_meta else None,
        )
        
        return session

    @staticmethod
    def end_session(session: SSOSession):
        """
        End an SSO session (for logout).
        """
        session.is_active = False
        session.ended_at = timezone.now()
        session.save()
