"""
Unit and Integration Tests for Enterprise Encryption, Key Management, and Secrets Hardening
=============================================================================================
Validates:
1. Enveloped encryption format (enc:v1:{kid}:{token}) with Key ID tracking.
2. Encryption & decryption roundtrip stability across keys.
3. Fail-closed / fail-loud behavior when ENCRYPTION_KEY is missing in production/staging.
4. Keyring-based key rotation via MultiFernet and is_stale_key identification.
5. Backward-compatibility with legacy un-enveloped Fernet tokens (gAAAAA...).
6. Raw database dump confidentiality: ThirdPartyIntegration, SSOProvider, and SSOSession exclude plaintext.
7. Transparent EncryptedCharField & EncryptedTextField model fields.
8. Re-encryption management command (`rotate_encryption_keys`) batch execution and dry-run.
9. Sensitive log filtering: redaction of secrets, tokens, client_secrets, passwords, and api_keys.
"""
import io
import pytest
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone
from django.contrib.auth import get_user_model

from core.encryption import (
    EncryptionKeyError,
    EncryptionManager,
    encrypt_value,
    decrypt_value,
    is_encrypted,
    is_stale_key,
    reset_encryption_manager,
    mask_secret,
)
from core.fields import EncryptedCharField, EncryptedTextField
from core.logging_filters import SensitiveDataFilter
from integration_hub.models import ThirdPartyIntegration
from sso_integration.models import SSOProvider, SSOSession
from multi_tenant.models import Organization

User = get_user_model()


@pytest.mark.django_db
class TestEncryptionAndSecrets:
    """Verifies encryption stability, rotation, fail-loud semantics, and DB confidentiality"""

    def setup_method(self):
        reset_encryption_manager()

    def teardown_method(self):
        reset_encryption_manager()

    def test_encrypt_decrypt_roundtrip(self):
        """Standard encrypt and decrypt roundtrip produces original plaintext with enveloped kid format"""
        text = "confidential_api_token_123"
        ciphertext = encrypt_value(text)
        assert ciphertext != text
        assert ciphertext.startswith("enc:v1:")
        assert is_encrypted(ciphertext) is True
        assert decrypt_value(ciphertext) == text

    def test_missing_key_fails_loudly_in_production(self, monkeypatch):
        """In production or staging environment, missing ENCRYPTION_KEY raises EncryptionKeyError"""
        monkeypatch.setattr(settings, 'ENVIRONMENT', 'production')
        monkeypatch.setattr(settings, 'ENCRYPTION_KEY', '')
        monkeypatch.setattr(settings, 'ENCRYPTION_KEYRING', None, raising=False)

        with pytest.raises(EncryptionKeyError) as exc_info:
            EncryptionManager()
        assert "CRITICAL: ENCRYPTION_KEY is not configured" in str(exc_info.value)

    def test_multifernet_key_rotation_and_kid_tracking(self, monkeypatch):
        """MultiFernet decrypts older ciphertext, tracks key IDs, and rotates it to new active kid"""
        old_key = Fernet.generate_key().decode('utf-8')
        new_key = Fernet.generate_key().decode('utf-8')

        # Encrypt with old key using explicit kid "key-2025-v1"
        monkeypatch.setattr(settings, 'ENCRYPTION_KEY', old_key, raising=False)
        monkeypatch.setattr(settings, 'ENCRYPTION_ACTIVE_KID', 'key-2025-v1', raising=False)
        old_manager = EncryptionManager()
        old_ciphertext = old_manager.encrypt("rotate_me_safely")
        assert "key-2025-v1" in old_ciphertext

        # Now configure new active key "key-2026-v1" with old key as rotation fallback
        keyring = {
            'key-2026-v1': new_key,
            'key-2025-v1': old_key,
        }
        monkeypatch.setattr(settings, 'ENCRYPTION_KEYRING', keyring, raising=False)
        monkeypatch.setattr(settings, 'ENCRYPTION_ACTIVE_KID', 'key-2026-v1', raising=False)

        manager = EncryptionManager()
        assert manager.active_kid == 'key-2026-v1'

        # Old ciphertext is detected as stale and needs rotation
        assert manager.is_stale_key(old_ciphertext) is True
        # Yet decrypts seamlessly
        assert manager.decrypt(old_ciphertext) == "rotate_me_safely"

        # Rotate updates ciphertext to new primary key
        new_ciphertext, rotated = manager.rotate(old_ciphertext)
        assert rotated is True
        assert "key-2026-v1" in new_ciphertext
        assert manager.is_stale_key(new_ciphertext) is False

        # Verify new ciphertext decrypts with new key alone
        fernet_new = Fernet(new_key.encode('utf-8'))
        token_part = new_ciphertext.split(':', 3)[3]
        assert fernet_new.decrypt(token_part.encode('utf-8')).decode('utf-8') == "rotate_me_safely"

    def test_legacy_fernet_token_backward_compatibility(self, monkeypatch):
        """Legacy un-enveloped Fernet tokens (gAAAAA...) decrypt seamlessly and are flagged as stale"""
        legacy_key = Fernet.generate_key().decode('utf-8')
        fernet = Fernet(legacy_key.encode('utf-8'))
        legacy_token = fernet.encrypt(b"legacy_plain_text").decode('utf-8')
        assert legacy_token.startswith("gAAAAA")

        monkeypatch.setattr(settings, 'ENCRYPTION_KEY', legacy_key, raising=False)
        monkeypatch.setattr(settings, 'ENCRYPTION_ACTIVE_KID', 'key-v1', raising=False)

        manager = EncryptionManager()
        assert manager.is_encrypted(legacy_token) is True
        assert manager.is_stale_key(legacy_token) is True
        assert manager.decrypt(legacy_token) == "legacy_plain_text"

        # Rotating legacy token envelops it into enc:v1:key-v1:...
        upgraded, rotated = manager.rotate(legacy_token)
        assert rotated is True
        assert upgraded.startswith("enc:v1:key-v1:")
        assert manager.decrypt(upgraded) == "legacy_plain_text"
        assert manager.is_stale_key(upgraded) is False

    def test_database_dump_excludes_plaintext_in_integration_hub(self):
        """ThirdPartyIntegration auto-encrypts credentials on save; raw rows exclude plaintext"""
        raw_secret = "provider_test_secret_payload_888"
        integration = ThirdPartyIntegration.objects.create(
            name="TestIntegrationForDBDump",
            provider="stripe",
            api_secret=raw_secret,
            api_key="api_key_plaintext_123"
        )

        integration.refresh_from_db()
        assert integration.api_secret != raw_secret
        assert is_encrypted(integration.api_secret) is True
        assert is_encrypted(integration.api_key) is True

        creds = integration.get_decrypted_credentials()
        assert creds['api_secret'] == raw_secret
        assert creds['api_key'] == "api_key_plaintext_123"
        integration.delete()

    def test_sso_provider_and_session_credential_encryption(self):
        """SSOProvider and SSOSession encrypt secrets and tokens at rest in database"""
        org = Organization.objects.create(slug="encrypt-sso-org", name="Encrypt SSO Org", status="active")
        user = User.objects.create_user(username="sso_enc_user", password="pwd")

        provider = SSOProvider.objects.create(
            organization=org,
            provider_type='oauth2_google',
            provider_name='Google Encrypted SSO',
            client_id='google_client_id_456',
            client_secret='raw_super_secret_client_key_999',
            created_by=user,
            last_used_at=timezone.now()
        )

        provider.refresh_from_db()
        # Raw database field contains ciphertext
        assert provider.client_secret != 'raw_super_secret_client_key_999'
        assert is_encrypted(provider.client_secret) is True
        # Method / property returns decrypted secret
        assert provider.get_decrypted_client_secret() == 'raw_super_secret_client_key_999'
        assert provider.decrypted_client_secret == 'raw_super_secret_client_key_999'

        # SSOSession token encryption
        session = SSOSession.objects.create(
            user=user,
            provider=provider,
            sso_token='plain_access_token_xyz',
            refresh_token='plain_refresh_token_abc'
        )
        session.refresh_from_db()
        assert session.sso_token != 'plain_access_token_xyz'
        assert is_encrypted(session.sso_token) is True
        assert is_encrypted(session.refresh_token) is True
        assert session.get_decrypted_tokens()['sso_token'] == 'plain_access_token_xyz'
        assert session.get_decrypted_tokens()['refresh_token'] == 'plain_refresh_token_abc'

    def test_rotate_encryption_keys_management_command(self, monkeypatch):
        """Management command rotate_encryption_keys scans and re-encrypts stale credentials"""
        # Step 1: Create record under old key
        old_key = Fernet.generate_key().decode('utf-8')
        new_key = Fernet.generate_key().decode('utf-8')

        monkeypatch.setattr(settings, 'ENCRYPTION_KEY', old_key, raising=False)
        monkeypatch.setattr(settings, 'ENCRYPTION_ACTIVE_KID', 'key-old', raising=False)
        reset_encryption_manager()

        integration = ThirdPartyIntegration.objects.create(
            name="RotationTargetIntegration",
            provider="hubspot",
            api_secret="hubspot_secret_payload"
        )
        integration.refresh_from_db()
        assert "key-old" in integration.api_secret

        # Step 2: Switch to new active key with old key in rotation fallback
        keyring = {
            'key-new': new_key,
            'key-old': old_key,
        }
        monkeypatch.setattr(settings, 'ENCRYPTION_KEYRING', keyring, raising=False)
        monkeypatch.setattr(settings, 'ENCRYPTION_ACTIVE_KID', 'key-new', raising=False)
        reset_encryption_manager()

        # Step 3: Run rotate_encryption_keys in dry-run mode
        out_dry = io.StringIO()
        call_command('rotate_encryption_keys', dry_run=True, stdout=out_dry)
        dry_output = out_dry.getvalue()
        assert "DRY RUN MODE" in dry_output
        integration.refresh_from_db()
        assert "key-old" in integration.api_secret  # Unchanged in dry run

        # Step 4: Run rotate_encryption_keys live
        out_live = io.StringIO()
        call_command('rotate_encryption_keys', stdout=out_live)
        live_output = out_live.getvalue()
        assert "Total fields rotated" in live_output

        integration.refresh_from_db()
        assert "key-new" in integration.api_secret
        assert integration.get_decrypted_credentials()['api_secret'] == "hubspot_secret_payload"
        integration.delete()

    def test_sensitive_data_log_sanitizer(self):
        """SensitiveDataFilter masks passwords, secrets, client_secrets, and auth tokens"""
        raw_log = "Auth failed: client_secret='top_secret_val' and password='Password456!' and token='jwt_token_777'"
        masked = SensitiveDataFilter.mask_message(raw_log)
        assert "top_secret_val" not in masked
        assert "Password456!" not in masked
        assert "jwt_token_777" not in masked
        assert "[REDACTED]" in masked

    def test_mask_secret_helper(self):
        """mask_secret masks strings preserving only prefix and suffix"""
        assert mask_secret("sk_test_1234567890abcdef") == "sk_t...cdef"
        assert mask_secret("short") == "********"
        assert mask_secret("") == ""
