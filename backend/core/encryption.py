"""
Enterprise Encryption and Key Management
=========================================
Implements robust field-level encryption with:
- Multiple keys support (MultiFernet) for zero-downtime key rotation
- Strict fail-loud semantics in production / staging when ENCRYPTION_KEY is unset or corrupted
- Automatic re-encryption / migration helpers for key rotation
- Masking filters for logs, dumps, and serializers
"""
import logging
from typing import List, Optional, Tuple, Union

from cryptography.fernet import Fernet, MultiFernet, InvalidToken
from django.conf import settings

logger = logging.getLogger('security.encryption')


class EncryptionKeyError(RuntimeError):
    """Raised when encryption key configuration is missing, invalid, or decryption fails."""
    pass


class EncryptionManager:
    """
    Manages primary and fallback rotation keys using cryptography MultiFernet.
    """

    def __init__(self):
        self._multi_fernet: Optional[MultiFernet] = None
        self._primary_fernet: Optional[Fernet] = None
        self._initialize_keys()

    def _get_key_list(self) -> List[str]:
        """
        Parses ENCRYPTION_KEY and ENCRYPTION_KEYS_ROTATION from settings / environment.
        Supports comma-separated keys or single base64-encoded 32-byte Fernet key.
        """
        keys: List[str] = []

        primary_key = getattr(settings, 'ENCRYPTION_KEY', '') or ''
        if primary_key:
            keys.extend([k.strip() for k in primary_key.split(',') if k.strip()])

        rotation_keys = getattr(settings, 'ENCRYPTION_KEYS_ROTATION', '') or ''
        if rotation_keys:
            keys.extend([k.strip() for k in rotation_keys.split(',') if k.strip()])

        return keys

    def _initialize_keys(self):
        keys = self._get_key_list()
        environment = getattr(settings, 'ENVIRONMENT', 'local').lower()
        is_prod = environment in ('production', 'prod', 'staging', 'stage')

        if not keys:
            if is_prod:
                raise EncryptionKeyError(
                    f"CRITICAL: ENCRYPTION_KEY is not configured in '{environment}' environment! Fail-closed."
                )
            # In local/test development, auto-derive or provide fallback with warning
            logger.warning("ENCRYPTION_KEY not configured. Generating ephemeral development key.")
            ephemeral = Fernet.generate_key().decode('utf-8')
            keys = [ephemeral]

        fernets = []
        for idx, k in enumerate(keys):
            try:
                # Ensure key is bytes
                k_bytes = k.encode('utf-8') if isinstance(k, str) else k
                fernets.append(Fernet(k_bytes))
            except Exception as e:
                raise EncryptionKeyError(f"Invalid encryption key at index {idx}: {e}") from e

        self._primary_fernet = fernets[0]
        self._multi_fernet = MultiFernet(fernets)

    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        Encrypts plaintext using the primary active encryption key.
        """
        if data is None:
            return ""

        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data

        if not data_bytes:
            return ""

        if not self._primary_fernet:
            self._initialize_keys()

        encrypted = self._primary_fernet.encrypt(data_bytes)
        return encrypted.decode('utf-8')

    def decrypt(self, encrypted_data: Union[str, bytes]) -> str:
        """
        Decrypts data using MultiFernet. Tries primary key first,
        then fallback keys in rotation list.
        """
        if not encrypted_data:
            return ""

        if isinstance(encrypted_data, str):
            enc_bytes = encrypted_data.encode('utf-8')
        else:
            enc_bytes = encrypted_data

        if not self._multi_fernet:
            self._initialize_keys()

        try:
            decrypted = self._multi_fernet.decrypt(enc_bytes)
            return decrypted.decode('utf-8')
        except InvalidToken as e:
            raise EncryptionKeyError(
                "Decryption failed: Token is invalid, corrupted, or encrypted with an unknown key."
            ) from e

    def rotate(self, encrypted_data: Union[str, bytes]) -> Tuple[str, bool]:
        """
        Re-encrypts data with the newest primary key if it was encrypted with an older rotation key.
        Returns (new_ciphertext, was_rotated).
        """
        if not encrypted_data:
            return "", False

        if isinstance(encrypted_data, str):
            enc_bytes = encrypted_data.encode('utf-8')
        else:
            enc_bytes = encrypted_data

        if not self._multi_fernet:
            self._initialize_keys()

        try:
            new_ciphertext = self._multi_fernet.rotate(enc_bytes)
            was_rotated = (new_ciphertext != enc_bytes)
            return new_ciphertext.decode('utf-8'), was_rotated
        except InvalidToken as e:
            raise EncryptionKeyError(f"Key rotation failed: {e}") from e


# Singleton instance
_encryption_manager = None


def get_encryption_manager() -> EncryptionManager:
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager


def encrypt_value(value: Union[str, bytes]) -> str:
    """Convenience encryptor function."""
    return get_encryption_manager().encrypt(value)


def decrypt_value(value: Union[str, bytes]) -> str:
    """Convenience decryptor function."""
    return get_encryption_manager().decrypt(value)


def mask_secret(secret: str, show_prefix: int = 4, show_suffix: int = 4) -> str:
    """Masks secrets for logs, dumps, and responses."""
    if not secret:
        return ""
    if len(secret) <= (show_prefix + show_suffix):
        return "********"
    return f"{secret[:show_prefix]}...{secret[-show_suffix:]}"
