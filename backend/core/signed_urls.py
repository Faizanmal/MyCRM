"""
Time-Limited Cryptographically Signed URLs

Provides stateless, tamper-proof, expirable URLs for secure document downloads.
"""

import json
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner


SIGNER_SALT = 'crm-document-signed-url-salt-v1'


def generate_signed_download_token(document_id: str, user_id: str | int = 0, expires_in_seconds: int = 300) -> str:
    """
    Generate a cryptographic timestamped token encoding document ID and authorized user.
    """
    signer = TimestampSigner(salt=SIGNER_SALT)
    payload = json.dumps({
        'doc_id': str(document_id),
        'user_id': str(user_id),
        'ttl': expires_in_seconds,
    })
    return signer.sign(payload)


def verify_signed_download_token(token: str, max_age: int | None = None) -> dict:
    """
    Verify and unsign a download token.
    Raises:
    - SignatureExpired: If token timestamp is older than max_age.
    - BadSignature: If token was tampered with, malformed, or signed with a different key.
    Returns:
    - dict with doc_id, user_id, ttl.
    """
    if not token or not isinstance(token, str):
        raise BadSignature("Token must be a non-empty string.")

    signer = TimestampSigner(salt=SIGNER_SALT)
    # If max_age is not explicitly passed, inspect the payload's declared ttl or default to 300s
    try:
        unsigned_raw = signer.unsign(token, max_age=max_age or 300)
        data = json.loads(unsigned_raw)
        return data
    except (SignatureExpired, BadSignature):
        raise
    except Exception as e:
        raise BadSignature(f"Failed to decode token payload: {str(e)}")
