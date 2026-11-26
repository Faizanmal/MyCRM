"""
Enterprise Encryption and Key Management
=========================================
Implements robust field-level encryption with:
- Key ID (kid) tracking and Keyring architecture
- Multiple keys support (MultiFernet) for zero-downtime key rotation
- Strict fail-loud / fail-closed semantics in production / staging when ENCRYPTION_KEY is unset or corrupted
- Enveloped ciphertext format: enc:v1:{kid}:{fernet_token}
- Seamless backward-compatibility with legacy un-enveloped Fernet tokens (gAAAAA...)
- Automatic re-encryption / migration helpers for key rotation
- Masking filters for logs, dumps, and serializers
"""
import json
import logging
from typing import Dict, List, Optional, Tuple, Union

from cryptography.fernet import Fernet, MultiFernet, InvalidToken
from django.conf import settings

logger = logging.getLogger('security.encryption')

ENCRYPTION_PREFIX = "enc:v1:"
LEGACY_FERNET_PREFIX = "gAAAAA"


class EncryptionKeyError(RuntimeError):
    """Raised when encryption key configuration is missing, invalid, or decryption fails."""
    pass


class EncryptionManager:
    """
    Manages primary and fallback rotation keys using a Keyring and cryptography MultiFernet.
    Tracks active Key ID (kid) and supports safe re-encryption.
    """

    def __init__(self):
        self._keyring: Dict[str, Fernet] = {}
        self._active_kid: str = "default"
        self._primary_fernet: Optional[Fernet] = None
        self._multi_fernet: Optional[MultiFernet] = None
        self._initialize_keys()

    @property
    def active_kid(self) -> str:
        return self._active_kid

    def _initialize_keys(self):
        environment = getattr(settings, 'ENVIRONMENT', 'local').lower()
        is_prod = environment in ('production', 'prod', 'staging', 'stage')

        keyring_config = getattr(settings, 'ENCRYPTION_KEYRING', None)
        active_kid = getattr(settings, 'ENCRYPTION_ACTIVE_KID', 'default')

        keyring_dict: Dict[str, str] = {}

        if keyring_config:
            if isinstance(keyring_config, str):
                try:
                    keyring_dict = json.loads(keyring_config)
                except Exception as e:
                    raise EncryptionKeyError(f"Invalid JSON in ENCRYPTION_KEYRING: {e}") from e
            elif isinstance(keyring_config, dict):
                keyring_dict = dict(keyring_config)

        if not keyring_dict:
            # Fall back to ENCRYPTION_KEY and ENCRYPTION_KEYS_ROTATION
            primary_key = getattr(settings, 'ENCRYPTION_KEY', '') or ''
            rotation_keys_raw = getattr(settings, 'ENCRYPTION_KEYS_ROTATION', '') or ''

            keys_list = []
            if primary_key:
                keys_list.extend([k.strip() for k in primary_key.split(',') if k.strip()])
            if rotation_keys_raw:
                keys_list.extend([k.strip() for k in rotation_keys_raw.split(',') if k.strip()])

            if not keys_list:
                if is_prod:
                    raise EncryptionKeyError(
                        f"CRITICAL: ENCRYPTION_KEY is not configured in '{environment}' environment! Fail-closed."
                    )
                # In local/test development, auto-derive or provide fallback with warning
                logger.warning("ENCRYPTION_KEY not configured. Generating ephemeral development key.")
                ephemeral = Fernet.generate_key().decode('utf-8')
                keys_list = [ephemeral]

            keyring_dict[active_kid] = keys_list[0]
            for idx, rot_k in enumerate(keys_list[1:], start=1):
                keyring_dict[f"rot-{idx}"] = rot_k

        # Validate and construct Fernet instances
        fernets_ordered: List[Fernet] = []
        parsed_keyring: Dict[str, Fernet] = {}

        # Ensure active_kid is in keyring
        if active_kid not in keyring_dict:
            # Default to first key in keyring if active_kid not explicitly found
            first_kid = next(iter(keyring_dict.keys()))
            active_kid = first_kid

        self._active_kid = active_kid

        # Build primary first
        primary_raw = keyring_dict[active_kid]
        try:
            primary_bytes = primary_raw.encode('utf-8') if isinstance(primary_raw, str) else primary_raw
            self._primary_fernet = Fernet(primary_bytes)
            fernets_ordered.append(self._primary_fernet)
            parsed_keyring[active_kid] = self._primary_fernet
        except Exception as e:
            raise EncryptionKeyError(f"Invalid primary encryption key '{active_kid}': {e}") from e

        # Add remaining fallback keys to MultiFernet
        for kid, raw_k in keyring_dict.items():
            if kid == active_kid:
                continue
            try:
                k_bytes = raw_k.encode('utf-8') if isinstance(raw_k, str) else raw_k
                f = Fernet(k_bytes)
                fernets_ordered.append(f)
                parsed_keyring[kid] = f
            except Exception as e:
                raise EncryptionKeyError(f"Invalid rotation encryption key '{kid}': {e}") from e

        self._keyring = parsed_keyring
        self._multi_fernet = MultiFernet(fernets_ordered)

    def is_encrypted(self, value: Union[str, bytes]) -> bool:
        """Determines if value is already encrypted (envelope or legacy Fernet)."""
        if not value:
            return False
        val_str = value.decode('utf-8') if isinstance(value, bytes) else str(value)
        return val_str.startswith(ENCRYPTION_PREFIX) or val_str.startswith(LEGACY_FERNET_PREFIX)

    def get_key_id(self, ciphertext: Union[str, bytes]) -> Optional[str]:
        """Extracts the Key ID (kid) from enveloped ciphertext or returns 'legacy'."""
        if not ciphertext:
            return None
        c_str = ciphertext.decode('utf-8') if isinstance(ciphertext, bytes) else str(ciphertext)
        if c_str.startswith(ENCRYPTION_PREFIX):
            parts = c_str.split(':', 3)
            if len(parts) >= 4:
                return parts[2]
        elif c_str.startswith(LEGACY_FERNET_PREFIX):
            return "legacy"
        return None

    def is_stale_key(self, ciphertext: Union[str, bytes]) -> bool:
        """
        Returns True if ciphertext was encrypted with an older rotation key or legacy format,
        indicating that re-encryption is needed.
        """
        if not self.is_encrypted(ciphertext):
            return False
        kid = self.get_key_id(ciphertext)
        return kid != self._active_kid

    def encrypt(self, data: Union[str, bytes], kid: Optional[str] = None) -> str:
        """
        Encrypts plaintext into enveloped format: enc:v1:{kid}:{raw_fernet_token}
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

        target_kid = kid or self._active_kid
        fernet = self._keyring.get(target_kid, self._primary_fernet)

        token = fernet.encrypt(data_bytes).decode('utf-8')
        return f"{ENCRYPTION_PREFIX}{target_kid}:{token}"

    def decrypt(self, ciphertext: Union[str, bytes]) -> str:
        """
        Decrypts enveloped ciphertext (or legacy Fernet token).
        Uses O(1) kid lookup when available, falling back to MultiFernet.
        """
        if not ciphertext:
            return ""

        c_str = ciphertext.decode('utf-8') if isinstance(ciphertext, bytes) else str(ciphertext)

        if not self._multi_fernet:
            self._initialize_keys()

        raw_token: str
        kid: Optional[str] = None

        if c_str.startswith(ENCRYPTION_PREFIX):
            parts = c_str.split(':', 3)
            if len(parts) >= 4:
                kid = parts[2]
                raw_token = parts[3]
            else:
                raise EncryptionKeyError("Malformed enveloped ciphertext structure.")
        elif c_str.startswith(LEGACY_FERNET_PREFIX):
            raw_token = c_str
        else:
            # If not starting with recognized prefix, attempt raw MultiFernet decrypt in case of custom tokens
            raw_token = c_str

        # If kid is known in keyring, attempt direct O(1) decryption
        token_bytes = raw_token.encode('utf-8')
        if kid and kid in self._keyring:
            try:
                decrypted = self._keyring[kid].decrypt(token_bytes)
                return decrypted.decode('utf-8')
            except InvalidToken:
                # Key might have been re-indexed, fall back to MultiFernet
                pass

        # Fallback to MultiFernet search across all active and rotation keys
        try:
            decrypted = self._multi_fernet.decrypt(token_bytes)
            return decrypted.decode('utf-8')
        except InvalidToken as e:
            raise EncryptionKeyError(
                "Decryption failed: Token is invalid, corrupted, or encrypted with an unknown key."
            ) from e

    def rotate(self, ciphertext: Union[str, bytes]) -> Tuple[str, bool]:
        """
        Re-encrypts data with the active primary key if it was encrypted with an older key
        or legacy format. Returns (new_ciphertext, was_rotated).
        """
        if not ciphertext:
            return "", False

        c_str = ciphertext.decode('utf-8') if isinstance(ciphertext, bytes) else str(ciphertext)

        if not self.is_encrypted(c_str):
            return c_str, False

        if not self.is_stale_key(c_str):
            return c_str, False

        # Stale key: decrypt and re-encrypt with current primary key
        plaintext = self.decrypt(c_str)
        new_ciphertext = self.encrypt(plaintext)
        return new_ciphertext, True


# Singleton instance
_encryption_manager: Optional[EncryptionManager] = None


def get_encryption_manager() -> EncryptionManager:
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager


def reset_encryption_manager():
    """Reset singleton for tests or configuration changes."""
    global _encryption_manager
    _encryption_manager = None


def encrypt_value(value: Union[str, bytes], kid: Optional[str] = None) -> str:
    """Convenience encryptor function."""
    return get_encryption_manager().encrypt(value, kid=kid)


def decrypt_value(value: Union[str, bytes]) -> str:
    """Convenience decryptor function."""
    return get_encryption_manager().decrypt(value)


def is_encrypted(value: Union[str, bytes]) -> bool:
    """Convenience check whether value is encrypted."""
    if not value:
        return False
    val_str = value.decode('utf-8') if isinstance(value, bytes) else str(value)
    return val_str.startswith(ENCRYPTION_PREFIX) or val_str.startswith(LEGACY_FERNET_PREFIX)


def is_stale_key(value: Union[str, bytes]) -> bool:
    """Convenience check whether value needs re-encryption under active key."""
    return get_encryption_manager().is_stale_key(value)


def mask_secret(secret: str, show_prefix: int = 4, show_suffix: int = 4) -> str:
    """Masks secrets for logs, dumps, and responses."""
    if not secret:
        return ""
    if len(secret) <= (show_prefix + show_suffix):
        return "********"
    return f"{secret[:show_prefix]}...{secret[-show_suffix:]}"
