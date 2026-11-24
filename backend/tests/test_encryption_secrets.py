"""
Unit tests for Enterprise Encryption and Secrets Hardening
"""
import pytest
from cryptography.fernet import Fernet
from django.conf import settings

from core.encryption import (
    EncryptionKeyError,
    EncryptionManager,
    encrypt_value,
    decrypt_value,
)
from core.logging_filters import SensitiveDataFilter
from integration_hub.models import ThirdPartyIntegration


@pytest.mark.django_db
class TestEncryptionAndSecrets:
    """Verifies encryption stability, rotation, fail-loud semantics, and DB confidentiality"""

    def test_encrypt_decrypt_roundtrip(self):
        """Standard encrypt and decrypt roundtrip produces original plaintext"""
        text = "confidential_api_token_123"
        ciphertext = encrypt_value(text)
        assert ciphertext != text
        assert ciphertext.startswith("gAAAAA")
        assert decrypt_value(ciphertext) == text

    def test_missing_key_fails_loudly_in_production(self, monkeypatch):
        """In production or staging environment, missing ENCRYPTION_KEY raises EncryptionKeyError"""
        monkeypatch.setattr(settings, 'ENVIRONMENT', 'production')
        monkeypatch.setattr(settings, 'ENCRYPTION_KEY', '')

        with pytest.raises(EncryptionKeyError) as exc_info:
            EncryptionManager()
        assert "CRITICAL: ENCRYPTION_KEY is not configured" in str(exc_info.value)

    def test_multifernet_key_rotation(self, monkeypatch):
        """MultiFernet decrypts older ciphertext and rotates it to new primary key"""
        old_key = Fernet.generate_key().decode('utf-8')
        new_key = Fernet.generate_key().decode('utf-8')

        # Encrypt with old key
        fernet_old = Fernet(old_key.encode('utf-8'))
        old_ciphertext = fernet_old.encrypt(b"rotate_me_safely").decode('utf-8')

        # Configure MultiFernet with new_key primary, old_key rotation
        monkeypatch.setattr(settings, 'ENCRYPTION_KEY', new_key, raising=False)
        monkeypatch.setattr(settings, 'ENCRYPTION_KEYS_ROTATION', old_key, raising=False)

        manager = EncryptionManager()
        # Old ciphertext can still be decrypted
        assert manager.decrypt(old_ciphertext) == "rotate_me_safely"

        # Rotate updates ciphertext to new primary key
        new_ciphertext, rotated = manager.rotate(old_ciphertext)
        assert rotated is True
        assert new_ciphertext != old_ciphertext

        # Verify new ciphertext decrypts with new key alone
        fernet_new = Fernet(new_key.encode('utf-8'))
        assert fernet_new.decrypt(new_ciphertext.encode('utf-8')).decode('utf-8') == "rotate_me_safely"

    def test_database_dump_excludes_plaintext(self):
        """ThirdPartyIntegration model auto-encrypts credentials on save; raw rows exclude plaintext"""
        raw_secret = "stripe_live_secret_key_888"
        integration = ThirdPartyIntegration.objects.create(
            name="TestIntegrationForDBDump",
            provider="stripe",
            api_secret=raw_secret
        )

        integration.refresh_from_db()
        assert integration.api_secret != raw_secret
        assert integration.api_secret.startswith("gAAAAA")

        creds = integration.get_decrypted_credentials()
        assert creds['api_secret'] == raw_secret
        integration.delete()

    def test_sensitive_data_log_sanitizer(self):
        """SensitiveDataFilter masks passwords, secrets, and auth tokens"""
        raw_log = "Error connecting with api_key='secret_key_123' and password='Password456!'"
        masked = SensitiveDataFilter.mask_message(raw_log)
        assert "secret_key_123" not in masked
        assert "Password456!" not in masked
        assert "[REDACTED]" in masked
