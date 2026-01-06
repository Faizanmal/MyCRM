"""
HashiCorp Vault Integration for Enterprise Secrets Management

Provides:
- Centralized secrets storage
- Dynamic database credentials
- Encryption as a service (transit)
- PKI certificate management
- Automatic secret rotation
- Audit logging for all secret access
"""

import logging
import os
import threading
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class VaultConfig:
    """Vault configuration settings"""

    def __init__(self):
        self.addr = os.getenv('VAULT_ADDR', 'http://127.0.0.1:8200')
        self.token = os.getenv('VAULT_TOKEN')
        self.role_id = os.getenv('VAULT_ROLE_ID')
        self.secret_id = os.getenv('VAULT_SECRET_ID')
        self.namespace = os.getenv('VAULT_NAMESPACE', 'mycrm')
        self.mount_point = os.getenv('VAULT_MOUNT_POINT', 'secret')
        self.transit_mount = os.getenv('VAULT_TRANSIT_MOUNT', 'transit')
        self.database_mount = os.getenv('VAULT_DATABASE_MOUNT', 'database')
        self.pki_mount = os.getenv('VAULT_PKI_MOUNT', 'pki')

        # TLS settings
        self.ca_cert = os.getenv('VAULT_CACERT')
        self.client_cert = os.getenv('VAULT_CLIENT_CERT')
        self.client_key = os.getenv('VAULT_CLIENT_KEY')
        self.skip_verify = os.getenv('VAULT_SKIP_VERIFY', 'false').lower() == 'true'


class VaultClient:
    """
    Low-level Vault HTTP client
    Handles authentication and API calls
    """

    def __init__(self, config: VaultConfig):
        self.config = config
        self._token = config.token
        self._token_expires = None
        self._lock = threading.Lock()

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with token"""
        headers = {
            'Content-Type': 'application/json',
        }
        if self._token:
            headers['X-Vault-Token'] = self._token
        if self.config.namespace:
            headers['X-Vault-Namespace'] = self.config.namespace
        return headers

    def _request(self, method: str, path: str, data: dict | None = None) -> dict:
        """Make HTTP request to Vault"""
        import requests

        url = f"{self.config.addr}/v1/{path}"

        verify = self.config.ca_cert if self.config.ca_cert else not self.config.skip_verify
        cert = None
        if self.config.client_cert and self.config.client_key:
            cert = (self.config.client_cert, self.config.client_key)

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                json=data,
                verify=verify,
                cert=cert,
                timeout=30
            )
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Vault request failed: {e}")
            raise VaultError(f"Vault request failed: {e}")

    def authenticate_approle(self) -> str:
        """Authenticate using AppRole"""
        if not self.config.role_id or not self.config.secret_id:
            raise VaultError("AppRole credentials not configured")

        data = {
            'role_id': self.config.role_id,
            'secret_id': self.config.secret_id
        }

        response = self._request('POST', 'auth/approle/login', data)
        self._token = response['auth']['client_token']
        lease_duration = response['auth']['lease_duration']
        self._token_expires = datetime.now() + timedelta(seconds=lease_duration - 60)

        logger.info("Successfully authenticated with Vault using AppRole")
        return self._token

    def authenticate_kubernetes(self, role: str) -> str:
        """Authenticate using Kubernetes service account"""
        jwt_path = '/var/run/secrets/kubernetes.io/serviceaccount/token'

        try:
            with open(jwt_path) as f:
                jwt = f.read()
        except FileNotFoundError:
            raise VaultError("Kubernetes service account token not found")

        data = {
            'role': role,
            'jwt': jwt
        }

        response = self._request('POST', 'auth/kubernetes/login', data)
        self._token = response['auth']['client_token']
        lease_duration = response['auth']['lease_duration']
        self._token_expires = datetime.now() + timedelta(seconds=lease_duration - 60)

        logger.info("Successfully authenticated with Vault using Kubernetes")
        return self._token

    def ensure_authenticated(self):
        """Ensure we have a valid token"""
        with self._lock:
            if self._token and self._token_expires and datetime.now() < self._token_expires:
                return

            # Try AppRole first
            if self.config.role_id and self.config.secret_id:
                self.authenticate_approle()
            # Then try Kubernetes
            elif os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount/token'):
                self.authenticate_kubernetes(os.getenv('VAULT_K8S_ROLE', 'mycrm'))
            elif self.config.token:
                self._token = self.config.token
            else:
                raise VaultError("No authentication method available")


class VaultError(Exception):
    """Vault-related errors"""
    pass


class VaultManager:
    """
    Enterprise Secrets Manager using HashiCorp Vault

    Features:
    - KV secrets storage (v2)
    - Dynamic database credentials
    - Transit encryption (encrypt/decrypt)
    - PKI certificate generation
    - Secret rotation
    - Lease management

    Usage:
        vault = VaultManager()

        # Read a secret
        secret = vault.get_secret('database/config')

        # Encrypt sensitive data
        ciphertext = vault.encrypt('mykey', 'sensitive data')
        plaintext = vault.decrypt('mykey', ciphertext)

        # Get dynamic database credentials
        db_creds = vault.get_database_credentials('mycrm-role')
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern for Vault manager"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.config = VaultConfig()
        self.client = VaultClient(self.config)
        self._secret_cache = {}
        self._cache_ttl = int(os.getenv('VAULT_CACHE_TTL', '300'))
        self._leases = {}
        self._initialized = True

        logger.info(f"VaultManager initialized with server: {self.config.addr}")

    # =====================
    # KV Secrets Engine
    # =====================

    def get_secret(self, path: str, version: int | None = None) -> dict[str, Any]:
        """
        Get a secret from KV v2 secrets engine

        Args:
            path: Secret path (e.g., 'database/config')
            version: Specific version to retrieve (optional)

        Returns:
            dict: Secret data
        """
        self.client.ensure_authenticated()

        # Check cache
        cache_key = f"{path}:{version}"
        if cache_key in self._secret_cache:
            cached_time, cached_data = self._secret_cache[cache_key]
            if (datetime.now() - cached_time).seconds < self._cache_ttl:
                return cached_data

        # Build path
        api_path = f"{self.config.mount_point}/data/{path}"
        if version:
            api_path += f"?version={version}"

        try:
            response = self.client._request('GET', api_path)
            data = response.get('data', {}).get('data', {})

            # Cache the result
            self._secret_cache[cache_key] = (datetime.now(), data)

            logger.debug(f"Retrieved secret from path: {path}")
            return data
        except Exception as e:
            logger.error(f"Failed to get secret at {path}: {e}")
            raise VaultError(f"Failed to get secret: {e}")

    def set_secret(self, path: str, data: dict[str, Any], cas: int | None = None) -> dict:
        """
        Write a secret to KV v2 secrets engine

        Args:
            path: Secret path
            data: Secret data (dict)
            cas: Check-and-set version (for optimistic locking)

        Returns:
            dict: Write metadata
        """
        self.client.ensure_authenticated()

        api_path = f"{self.config.mount_point}/data/{path}"

        payload = {'data': data}
        if cas is not None:
            payload['options'] = {'cas': cas}

        try:
            response = self.client._request('POST', api_path, payload)

            # Invalidate cache
            for key in list(self._secret_cache.keys()):
                if key.startswith(f"{path}:"):
                    del self._secret_cache[key]

            logger.info(f"Written secret to path: {path}")
            return response.get('data', {})
        except Exception as e:
            logger.error(f"Failed to write secret at {path}: {e}")
            raise VaultError(f"Failed to write secret: {e}")

    def delete_secret(self, path: str, versions: list[int] | None = None):
        """
        Delete secret versions (soft delete)

        Args:
            path: Secret path
            versions: Specific versions to delete (or latest if None)
        """
        self.client.ensure_authenticated()

        if versions:
            api_path = f"{self.config.mount_point}/delete/{path}"
            payload = {'versions': versions}
            self.client._request('POST', api_path, payload)
        else:
            api_path = f"{self.config.mount_point}/data/{path}"
            self.client._request('DELETE', api_path)

        # Invalidate cache
        for key in list(self._secret_cache.keys()):
            if key.startswith(f"{path}:"):
                del self._secret_cache[key]

        logger.info(f"Deleted secret at path: {path}")

    def list_secrets(self, path: str = '') -> list[str]:
        """List secrets at a path"""
        self.client.ensure_authenticated()

        api_path = f"{self.config.mount_point}/metadata/{path}"

        try:
            response = self.client._request('LIST', api_path)
            return response.get('data', {}).get('keys', [])
        except Exception as e:
            logger.error(f"Failed to list secrets at {path}: {e}")
            return []

    # =====================
    # Transit Encryption
    # =====================

    def encrypt(self, key_name: str, plaintext: str) -> str:
        """
        Encrypt data using Transit secrets engine

        Args:
            key_name: Encryption key name
            plaintext: Data to encrypt

        Returns:
            str: Ciphertext (vault:v1:...)
        """
        self.client.ensure_authenticated()

        import base64
        encoded = base64.b64encode(plaintext.encode()).decode()

        api_path = f"{self.config.transit_mount}/encrypt/{key_name}"
        payload = {'plaintext': encoded}

        try:
            response = self.client._request('POST', api_path, payload)
            return response['data']['ciphertext']
        except Exception as e:
            logger.error(f"Transit encryption failed: {e}")
            raise VaultError(f"Encryption failed: {e}")

    def decrypt(self, key_name: str, ciphertext: str) -> str:
        """
        Decrypt data using Transit secrets engine

        Args:
            key_name: Encryption key name
            ciphertext: Encrypted data (vault:v1:...)

        Returns:
            str: Decrypted plaintext
        """
        self.client.ensure_authenticated()

        import base64

        api_path = f"{self.config.transit_mount}/decrypt/{key_name}"
        payload = {'ciphertext': ciphertext}

        try:
            response = self.client._request('POST', api_path, payload)
            encoded = response['data']['plaintext']
            return base64.b64decode(encoded).decode()
        except Exception as e:
            logger.error(f"Transit decryption failed: {e}")
            raise VaultError(f"Decryption failed: {e}")

    def create_transit_key(self, key_name: str, key_type: str = 'aes256-gcm96'):
        """
        Create a new transit encryption key

        Args:
            key_name: Key name
            key_type: Key type (aes256-gcm96, chacha20-poly1305, etc.)
        """
        self.client.ensure_authenticated()

        api_path = f"{self.config.transit_mount}/keys/{key_name}"
        payload = {'type': key_type}

        try:
            self.client._request('POST', api_path, payload)
            logger.info(f"Created transit key: {key_name}")
        except Exception as e:
            logger.error(f"Failed to create transit key: {e}")
            raise VaultError(f"Failed to create key: {e}")

    def rotate_transit_key(self, key_name: str):
        """Rotate a transit encryption key"""
        self.client.ensure_authenticated()

        api_path = f"{self.config.transit_mount}/keys/{key_name}/rotate"

        try:
            self.client._request('POST', api_path)
            logger.info(f"Rotated transit key: {key_name}")
        except Exception as e:
            logger.error(f"Failed to rotate transit key: {e}")
            raise VaultError(f"Failed to rotate key: {e}")

    # =====================
    # Dynamic Database Credentials
    # =====================

    def get_database_credentials(self, role: str) -> dict[str, str]:
        """
        Get dynamic database credentials

        Args:
            role: Database role name

        Returns:
            dict: {'username': ..., 'password': ..., 'lease_id': ..., 'lease_duration': ...}
        """
        self.client.ensure_authenticated()

        api_path = f"{self.config.database_mount}/creds/{role}"

        try:
            response = self.client._request('GET', api_path)

            creds = {
                'username': response['data']['username'],
                'password': response['data']['password'],
                'lease_id': response['lease_id'],
                'lease_duration': response['lease_duration']
            }

            # Track the lease
            self._leases[response['lease_id']] = {
                'type': 'database',
                'role': role,
                'expires': datetime.now() + timedelta(seconds=response['lease_duration'])
            }

            logger.info(f"Generated database credentials for role: {role}")
            return creds
        except Exception as e:
            logger.error(f"Failed to get database credentials: {e}")
            raise VaultError(f"Failed to get database credentials: {e}")

    def renew_lease(self, lease_id: str, increment: int = 3600) -> dict:
        """Renew a lease"""
        self.client.ensure_authenticated()

        api_path = 'sys/leases/renew'
        payload = {
            'lease_id': lease_id,
            'increment': increment
        }

        try:
            response = self.client._request('POST', api_path, payload)

            if lease_id in self._leases:
                self._leases[lease_id]['expires'] = datetime.now() + timedelta(seconds=response['lease_duration'])

            logger.info(f"Renewed lease: {lease_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to renew lease: {e}")
            raise VaultError(f"Failed to renew lease: {e}")

    def revoke_lease(self, lease_id: str):
        """Revoke a lease"""
        self.client.ensure_authenticated()

        api_path = 'sys/leases/revoke'
        payload = {'lease_id': lease_id}

        try:
            self.client._request('POST', api_path, payload)

            if lease_id in self._leases:
                del self._leases[lease_id]

            logger.info(f"Revoked lease: {lease_id}")
        except Exception as e:
            logger.error(f"Failed to revoke lease: {e}")
            raise VaultError(f"Failed to revoke lease: {e}")

    # =====================
    # PKI Certificates
    # =====================

    def generate_certificate(self, role: str, common_name: str,
                           ttl: str = '720h', alt_names: list[str] | None = None) -> dict:
        """
        Generate a PKI certificate

        Args:
            role: PKI role name
            common_name: Certificate common name
            ttl: Certificate TTL
            alt_names: Subject alternative names

        Returns:
            dict: {'certificate': ..., 'private_key': ..., 'ca_chain': ...}
        """
        self.client.ensure_authenticated()

        api_path = f"{self.config.pki_mount}/issue/{role}"
        payload = {
            'common_name': common_name,
            'ttl': ttl
        }

        if alt_names:
            payload['alt_names'] = ','.join(alt_names)

        try:
            response = self.client._request('POST', api_path, payload)

            logger.info(f"Generated certificate for: {common_name}")
            return {
                'certificate': response['data']['certificate'],
                'private_key': response['data']['private_key'],
                'ca_chain': response['data'].get('ca_chain', []),
                'serial_number': response['data']['serial_number'],
                'expiration': response['data']['expiration']
            }
        except Exception as e:
            logger.error(f"Failed to generate certificate: {e}")
            raise VaultError(f"Failed to generate certificate: {e}")

    # =====================
    # Utility Methods
    # =====================

    def health_check(self) -> dict:
        """Check Vault health status"""
        import requests

        try:
            response = requests.get(
                f"{self.config.addr}/v1/sys/health",
                timeout=5
            )
            return {
                'initialized': response.json().get('initialized', False),
                'sealed': response.json().get('sealed', True),
                'standby': response.json().get('standby', False),
                'version': response.json().get('version', 'unknown'),
                'status': 'healthy' if response.status_code == 200 else 'unhealthy'
            }
        except Exception as e:
            return {
                'status': 'unreachable',
                'error': str(e)
            }

    def get_django_settings(self) -> dict[str, Any]:
        """
        Get Django settings from Vault
        Useful for loading configuration at startup
        """
        try:
            return self.get_secret('mycrm/django/settings')
        except VaultError:
            logger.warning("Could not load Django settings from Vault, using defaults")
            return {}

    def get_api_keys(self) -> dict[str, str]:
        """Get all API keys from Vault"""
        try:
            return self.get_secret('mycrm/api-keys')
        except VaultError:
            logger.warning("Could not load API keys from Vault")
            return {}


# Django integration helper
def get_vault_secret(path: str, key: str | None = None, default: Any = None) -> Any:
    """
    Helper function to get secrets from Vault for Django settings

    Usage in settings.py:
        from enterprise.vault_manager import get_vault_secret

        SECRET_KEY = get_vault_secret('django/secrets', 'secret_key', 'fallback-key')
        DATABASE_PASSWORD = get_vault_secret('database/config', 'password')
    """
    try:
        vault = VaultManager()
        secret = vault.get_secret(path)

        if key:
            return secret.get(key, default)
        return secret
    except Exception as e:
        logger.warning(f"Could not get secret from Vault: {e}")
        return default


# Context manager for database credentials
class VaultDatabaseCredentials:
    """
    Context manager for dynamic database credentials

    Usage:
        with VaultDatabaseCredentials('mycrm-role') as creds:
            connection = psycopg2.connect(
                user=creds['username'],
                password=creds['password'],
                ...
            )
    """

    def __init__(self, role: str):
        self.role = role
        self.vault = VaultManager()
        self.creds = None
        self.lease_id = None

    def __enter__(self):
        self.creds = self.vault.get_database_credentials(self.role)
        self.lease_id = self.creds['lease_id']
        return self.creds

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lease_id:
            try:
                self.vault.revoke_lease(self.lease_id)
            except Exception as e:
                logger.warning(f"Could not revoke lease: {e}")
        return False
