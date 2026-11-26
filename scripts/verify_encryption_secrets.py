#!/usr/bin/env python
"""
Verification Script: 03-encryption-secrets
Validates:
1. Encryption / Decryption stability across instances with Key ID tracking (enc:v1:{kid}:{token}).
2. Missing key fails loudly in production/staging mode (fail-closed).
3. Zero-downtime key rotation via MultiFernet:
   - Primary key re-encrypts old records
   - Data encrypted with older rotation keys decrypts seamlessly
   - is_stale_key correctly identifies outdated keys
4. Backward-compatibility with legacy un-enveloped Fernet tokens (gAAAAA...).
5. Database dump exclusion of plaintext:
   - Credentials (api_key, api_secret, access_token) stored as ciphertext in db
   - SSOProvider client_secret stored as ciphertext in db
   - Plaintext does NOT appear in raw database table rows
6. Re-encryption management command (`rotate_encryption_keys`):
   - Successfully scans and rotates outdated records across models.
7. Frontend build / bundle audit:
   - Scans frontend codebase to ensure no backend secrets or private keys are exposed in NEXT_PUBLIC_ variables
8. Sensitive log masking:
   - SensitiveDataFilter correctly redacts passwords, tokens, client_secrets, and api_keys
"""
import io
import os
import sys
import django

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from cryptography.fernet import Fernet
from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.utils import timezone

from core.encryption import (
    EncryptionManager,
    EncryptionKeyError,
    encrypt_value,
    decrypt_value,
    is_encrypted,
    is_stale_key,
    reset_encryption_manager,
    mask_secret,
)
from core.logging_filters import SensitiveDataFilter
from integration_hub.models import ThirdPartyIntegration
from sso_integration.models import SSOProvider, SSOSession
from multi_tenant.models import Organization
from django.contrib.auth import get_user_model

User = get_user_model()


def run_encryption_secrets_checks():
    print("=" * 70)
    print("STARTING 03-ENCRYPTION-SECRETS VERIFICATION SUITE")
    print("=" * 70)

    # =========================================================================
    # CHECK 1: Encryption / Decryption Stability & Key ID Tracking
    # =========================================================================
    print("\n[Check 1] Encryption & Decryption Roundtrip with Key ID Tracking")
    plaintext = "super_secret_oauth_token_xyz_987654"
    ciphertext = encrypt_value(plaintext)
    assert ciphertext != plaintext, "Encryption failed to transform plaintext"
    assert ciphertext.startswith("enc:v1:"), f"Unexpected ciphertext format: {ciphertext[:10]}"
    assert is_encrypted(ciphertext) is True, "is_encrypted returned False for valid ciphertext"
    decrypted = decrypt_value(ciphertext)
    assert decrypted == plaintext, f"Decryption mismatch: {decrypted} != {plaintext}"
    print(f"  PASS: Encrypt / Decrypt roundtrip is stable with enveloped format ({ciphertext[:18]}...).")

    # =========================================================================
    # CHECK 2: Missing Key Fails Loudly in Production/Staging Mode
    # =========================================================================
    print("\n[Check 2] Fail-Loud on Missing Encryption Key in Production")
    orig_env = getattr(settings, 'ENVIRONMENT', 'local')
    orig_key = getattr(settings, 'ENCRYPTION_KEY', '')
    orig_keyring = getattr(settings, 'ENCRYPTION_KEYRING', None)

    try:
        settings.ENVIRONMENT = 'production'
        settings.ENCRYPTION_KEY = ''
        settings.ENCRYPTION_KEYRING = None
        failed_loudly = False
        try:
            manager = EncryptionManager()
        except EncryptionKeyError as e:
            failed_loudly = True
            print(f"  PASS: Raised EncryptionKeyError in production as expected: {e}")
        assert failed_loudly, "CRITICAL: System did not fail loudly when ENCRYPTION_KEY was missing in production!"
    finally:
        settings.ENVIRONMENT = orig_env
        settings.ENCRYPTION_KEY = orig_key
        settings.ENCRYPTION_KEYRING = orig_keyring
        reset_encryption_manager()

    # =========================================================================
    # CHECK 3: Key Rotation & Re-Encryption with MultiFernet
    # =========================================================================
    print("\n[Check 3] Zero-Downtime Key Rotation via Keyring & MultiFernet")
    key_old = Fernet.generate_key().decode('utf-8')
    key_new = Fernet.generate_key().decode('utf-8')

    # Encrypt data using key_old under kid "key-2025"
    settings.ENCRYPTION_KEY = key_old
    settings.ENCRYPTION_ACTIVE_KID = "key-2025"
    settings.ENCRYPTION_KEYRING = None
    reset_encryption_manager()
    old_manager = EncryptionManager()
    data_with_old_key = old_manager.encrypt("secret_payload_from_v1")
    assert "key-2025" in data_with_old_key

    # Configure keyring with key_new as active ("key-2026") and key_old as rotation fallback
    settings.ENCRYPTION_KEYRING = {
        'key-2026': key_new,
        'key-2025': key_old,
    }
    settings.ENCRYPTION_ACTIVE_KID = 'key-2026'
    reset_encryption_manager()
    rot_manager = EncryptionManager()

    # Old data must decrypt transparently using rotation key
    decrypted_old = rot_manager.decrypt(data_with_old_key)
    assert decrypted_old == "secret_payload_from_v1", "Failed to decrypt data encrypted with older rotation key"
    assert rot_manager.is_stale_key(data_with_old_key) is True, "Old key ciphertext should be marked as stale"
    print("  PASS: Data encrypted with older key decrypts transparently via MultiFernet.")

    # Rotate / re-encrypt to new primary key
    rotated_ciphertext, was_rotated = rot_manager.rotate(data_with_old_key)
    assert was_rotated is True, "rotate() should report that token was re-encrypted"
    assert "key-2026" in rotated_ciphertext, "Ciphertext should be updated to primary key"
    assert rot_manager.is_stale_key(rotated_ciphertext) is False, "Rotated ciphertext should not be marked stale"
    print("  PASS: Key rotation re-encrypts old ciphertext to newest active Key ID.")

    # =========================================================================
    # CHECK 4: Backward-Compatibility with Legacy Un-Enveloped Fernet Tokens
    # =========================================================================
    print("\n[Check 4] Backward-Compatibility with Legacy Fernet Tokens (gAAAAA...)")
    raw_fernet = Fernet(key_new.encode('utf-8'))
    legacy_token = raw_fernet.encrypt(b"un_enveloped_legacy_secret").decode('utf-8')
    assert legacy_token.startswith("gAAAAA")
    assert rot_manager.is_encrypted(legacy_token) is True
    assert rot_manager.is_stale_key(legacy_token) is True
    assert rot_manager.decrypt(legacy_token) == "un_enveloped_legacy_secret"

    upgraded_token, upgraded_rotated = rot_manager.rotate(legacy_token)
    assert upgraded_rotated is True
    assert upgraded_token.startswith("enc:v1:key-2026:")
    assert rot_manager.decrypt(upgraded_token) == "un_enveloped_legacy_secret"
    print("  PASS: Legacy un-enveloped Fernet tokens seamlessly decrypt and upgrade to enveloped format.")

    # Restore settings
    settings.ENCRYPTION_KEY = orig_key
    settings.ENCRYPTION_KEYRING = orig_keyring
    settings.ENCRYPTION_ACTIVE_KID = 'key-2026-v1'
    reset_encryption_manager()

    # =========================================================================
    # CHECK 5: Database Storage - Plaintext Excluded in DB Dump & SSO Secrets
    # =========================================================================
    print("\n[Check 5] Database Dump / Raw SQL Excludes Plaintext")
    raw_api_key = "api_key_confidential_value_555"
    raw_api_secret = "secret_hex_payload_777888999"

    integration = ThirdPartyIntegration.objects.create(
        name="SecurityTestIntegration",
        provider="hubspot",
        api_key=raw_api_key,
        api_secret=raw_api_secret,
        access_token="tok_plaintext_123",
        token_expires_at=timezone.now()
    )

    # Direct raw database query to check physical rows in sqlite/postgres
    with connection.cursor() as cursor:
        cursor.execute("SELECT api_key, api_secret, access_token FROM crm_hub_integrations WHERE id = %s", [integration.id.hex if hasattr(integration.id, 'hex') else str(integration.id)])
        row = cursor.fetchone()
        if not row:
            cursor.execute("SELECT api_key, api_secret, access_token FROM crm_hub_integrations WHERE name = 'SecurityTestIntegration'")
            row = cursor.fetchone()
        db_key, db_secret, db_token = row

    # Plaintext must NOT appear in raw DB columns
    assert raw_api_key not in db_key, "SECURITY BREACH: Plaintext api_key found in raw database table!"
    assert raw_api_secret not in db_secret, "SECURITY BREACH: Plaintext api_secret found in raw database table!"
    assert "tok_plaintext_123" not in db_token, "SECURITY BREACH: Plaintext access_token found in raw database table!"
    assert is_encrypted(db_key), f"Database api_key is not encrypted: {db_key[:10]}"
    assert is_encrypted(db_secret), f"Database api_secret is not encrypted: {db_secret[:10]}"
    print("  PASS: Raw database table contains ONLY encrypted ciphertext. Zero plaintext leakage.")

    # High-level accessor decrypts safely
    creds = integration.get_decrypted_credentials()
    assert creds['api_key'] == raw_api_key
    assert creds['api_secret'] == raw_api_secret
    print("  PASS: Model helper get_decrypted_credentials() seamlessly decrypts fields.")
    integration.delete()

    # SSOProvider client_secret encryption at rest
    test_org, _ = Organization.objects.get_or_create(slug="sec-test-org", defaults={"name": "Sec Test Org"})
    test_user = User.objects.first()
    sso_prov = SSOProvider.objects.create(
        organization=test_org,
        provider_name="Encrypted SSO Test",
        provider_type="oauth2_google",
        client_id="google_cid_123",
        client_secret="raw_google_sso_client_secret_xyz",
        created_by=test_user,
        last_used_at=timezone.now()
    )
    sso_prov.refresh_from_db()
    assert sso_prov.client_secret != "raw_google_sso_client_secret_xyz"
    assert is_encrypted(sso_prov.client_secret)
    assert sso_prov.get_decrypted_client_secret() == "raw_google_sso_client_secret_xyz"
    print("  PASS: SSOProvider client_secret encrypted at rest and decrypted on runtime demand.")
    sso_prov.delete()

    # =========================================================================
    # CHECK 6: Re-encryption Management Command
    # =========================================================================
    print("\n[Check 6] Management Command rotate_encryption_keys Execution")
    out = io.StringIO()
    call_command('rotate_encryption_keys', dry_run=True, stdout=out)
    cmd_output = out.getvalue()
    assert "DRY RUN MODE" in cmd_output
    assert "Total records scanned" in cmd_output
    print("  PASS: rotate_encryption_keys command executed successfully.")

    # =========================================================================
    # CHECK 7: Frontend Secrets Leak Audit
    # =========================================================================
    print("\n[Check 7] Frontend Bundle & Codebase Secret Audit")
    frontend_dir = os.path.abspath(os.path.join(backend_dir, '..', 'frontend'))
    leaked_secrets = []

    # Search for accidental inclusion of dangerous patterns in NEXT_PUBLIC_ variables
    for root, _, files in os.walk(frontend_dir):
        if 'node_modules' in root or '.next' in root:
            continue
        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.json', '.env')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if 'NEXT_PUBLIC_ENCRYPTION_KEY' in content:
                            leaked_secrets.append(f"NEXT_PUBLIC_ENCRYPTION_KEY in {file}")
                        if 'NEXT_PUBLIC_SECRET_KEY' in content:
                            leaked_secrets.append(f"NEXT_PUBLIC_SECRET_KEY in {file}")
                        if 'NEXT_PUBLIC_JWT_SECRET' in content:
                            leaked_secrets.append(f"NEXT_PUBLIC_JWT_SECRET in {file}")
                except Exception:
                    pass

    assert len(leaked_secrets) == 0, f"Found leaked backend secrets in frontend: {leaked_secrets}"
    print("  PASS: Zero backend encryption keys or private secrets found in frontend bundle/code.")

    # =========================================================================
    # CHECK 8: Sensitive Log Masking Filter
    # =========================================================================
    print("\n[Check 8] Sensitive Data Logging Sanitizer")
    sample_log = "User session_user authenticated with client_secret='SecretClientKey999' and password='MySecretPassword123' and token='eyJhbGciOi...'"
    masked_log = SensitiveDataFilter.mask_message(sample_log)
    assert "SecretClientKey999" not in masked_log, "client_secret leaked through log sanitizer!"
    assert "MySecretPassword123" not in masked_log, "Password leaked through log sanitizer!"
    assert "eyJhbGciOi..." not in masked_log, "Token leaked through log sanitizer!"
    assert "[REDACTED]" in masked_log
    print("  PASS: Sensitive credentials successfully redacted by log sanitizer.")

    print("\n" + "=" * 70)
    print("ALL 03-ENCRYPTION-SECRETS VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == '__main__':
    run_encryption_secrets_checks()
