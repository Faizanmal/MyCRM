"""
SSO Authentication Services for OAuth2 and SAML.
"""
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import requests
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import SSOLoginAttempt, SSOProvider, SSOSession

User = get_user_model()


class OAuth2Service:
    """
    OAuth2 authentication service supporting multiple providers.
    """

    def __init__(self, provider: SSOProvider):
        self.provider = provider
        if not provider.is_oauth2:
            raise ValueError("Provider must be an OAuth2 provider")

    def generate_authorization_url(self, state: str = None, redirect_uri: str = None, nonce: str = None) -> tuple[str, str, str]:
        """
        Generate OAuth2 authorization URL with PKCE and state/nonce validation.
        Returns: (authorization_url, code_verifier, state)
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
        if nonce:
            params['nonce'] = nonce

        # Provider-specific parameters
        if self.provider.provider_type == 'oauth2_microsoft':
            params['response_mode'] = 'query'
            params['prompt'] = 'select_account'
        elif self.provider.provider_type == 'oauth2_google':
            params['access_type'] = 'offline'
            params['prompt'] = 'consent'

        authorization_url = f"{self.provider.authorization_url}?{urlencode(params)}"
        return authorization_url, code_verifier, state

    @staticmethod
    def validate_state(expected_state: str, received_state: str) -> bool:
        """
        Validates state parameter using constant-time comparison to prevent OAuth CSRF attacks.
        """
        if not expected_state or not received_state:
            return False
        return secrets.compare_digest(str(expected_state), str(received_state))

    def validate_redirect_uri(self, redirect_uri: str) -> bool:
        """
        Validates that redirect URI strictly matches configured provider redirect URI.
        Prevents open redirectors and credential leakage.
        """
        if not redirect_uri:
            return False
        return redirect_uri == self.provider.get_redirect_uri()

    def validate_id_token(
        self,
        id_token_payload: dict[str, Any],
        expected_nonce: str = None,
        expected_audience: str = None
    ) -> bool:
        """
        Validates OIDC ID token audience, expiration, and nonce.
        """
        if not id_token_payload or not isinstance(id_token_payload, dict):
            return False

        # Validate audience
        aud = id_token_payload.get('aud')
        target_aud = expected_audience or self.provider.client_id
        if aud != target_aud:
            return False

        # Validate expiration
        exp = id_token_payload.get('exp')
        if exp:
            from datetime import timezone as dt_timezone
            exp_dt = datetime.fromtimestamp(exp, tz=dt_timezone.utc)
            if exp_dt < timezone.now():
                return False

        # Validate nonce if required
        if expected_nonce and id_token_payload.get('nonce') != expected_nonce:
            return False

        return True

    def exchange_code_for_token(
        self,
        code: str,
        code_verifier: str,
        redirect_uri: str = None
    ) -> dict[str, Any]:
        """
        Exchange authorization code for access token.
        """
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri or self.provider.get_redirect_uri(),
            'client_id': self.provider.client_id,
            'client_secret': self.provider.get_decrypted_client_secret(),
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

    def get_user_info(self, access_token: str) -> dict[str, Any]:
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

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """
        Refresh access token using refresh token.
        """
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.provider.client_id,
            'client_secret': self.provider.get_decrypted_client_secret(),
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

    def map_user_attributes(self, user_info: dict[str, Any]) -> dict[str, Any]:
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
        import uuid

        from django.conf import settings

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

    def parse_saml_response(self, saml_response: str) -> dict[str, Any]:
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

    def validate_saml_response(
        self,
        saml_response: str,
        expected_audience: str = None,
        expected_recipient: str = None
    ) -> bool:
        """
        Validates SAML assertion audience restriction, destination recipient, and timestamp constraints.
        """
        import xml.etree.ElementTree as ET

        try:
            decoded = base64.b64decode(saml_response)
            root = ET.fromstring(decoded)
            ns = {
                'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
                'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol'
            }

            # 1. Validate Audience restriction
            target_aud = expected_audience or self.provider.entity_id
            aud_elem = root.find('.//saml:Audience', ns)
            if aud_elem is not None and aud_elem.text and aud_elem.text != target_aud:
                return False

            # 2. Validate Destination / Recipient ACS URL
            dest = root.get('Destination')
            if expected_recipient and dest and dest != expected_recipient:
                return False

            # 3. Validate timestamp conditions
            conditions = root.find('.//saml:Conditions', ns)
            if conditions is not None:
                not_on_or_after = conditions.get('NotOnOrAfter')
                if not_on_or_after:
                    expiry = datetime.strptime(not_on_or_after, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc if hasattr(timezone, 'utc') else None)
                    if expiry < timezone.now():
                        return False

            return True
        except Exception:
            return False

    def map_user_attributes(self, saml_data: dict[str, Any]) -> dict[str, Any]:
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
        user_data: dict[str, Any],
        request_meta: dict[str, Any] = None
    ) -> tuple[User, bool]:
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
            user_agent=(request_meta.get('HTTP_USER_AGENT') if request_meta else '') or '',
        )

        # Try to find existing user
        try:
            user = User.objects.get(email=email)
            created = False

            # Validate Tenant Binding for existing user
            from multi_tenant.models import OrganizationMember
            membership = OrganizationMember.objects.filter(
                organization=provider.organization,
                user=user,
                is_active=True
            ).first()

            if not membership:
                if provider.auto_create_users:
                    OrganizationMember.objects.create(
                        organization=provider.organization,
                        user=user,
                        role=provider.default_role or 'member',
                        is_active=True
                    )
                else:
                    attempt.status = 'failed'
                    attempt.error_message = f"Cross-tenant SSO denied: User is not an active member of organization '{provider.organization.slug}'"
                    attempt.save()
                    raise ValueError(f"Cross-tenant SSO denied: User is not an active member of organization '{provider.organization.slug}'")

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
        session_data: dict[str, Any],
        request_meta: dict[str, Any] = None
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
