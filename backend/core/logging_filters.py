"""
Sensitive Data Masking Logging Filter
Prevents secrets, keys, passwords, and tokens from leaking into logs.
"""
import logging
import re

SENSITIVE_PATTERNS = [
    re.compile(r'(password["\':\s=]+)(["\']?)([^"\'\s&]+)\2', re.IGNORECASE),
    re.compile(r'(client_secret["\':\s=]+)(["\']?)([^"\'\s&]+)\2', re.IGNORECASE),
    re.compile(r'(api_secret["\':\s=]+)(["\']?)([^"\'\s&]+)\2', re.IGNORECASE),
    re.compile(r'(api_key["\':\s=]+)(["\']?)([^"\'\s&]+)\2', re.IGNORECASE),
    re.compile(r'(secret["\':\s=]+)(["\']?)([^"\'\s&]+)\2', re.IGNORECASE),
    re.compile(r'(token["\':\s=]+)(["\']?)([^"\'\s&]+)\2', re.IGNORECASE),
    re.compile(r'(access_token["\':\s=]+)(["\']?)([^"\'\s&]+)\2', re.IGNORECASE),
    re.compile(r'(refresh_token["\':\s=]+)(["\']?)([^"\'\s&]+)\2', re.IGNORECASE),
    re.compile(r'(authorization["\':\s=]+Bearer\s+)([^"\'\s&]+)', re.IGNORECASE),
    re.compile(r'(encryption_key["\':\s=]+)(["\']?)([^"\'\s&]+)\2', re.IGNORECASE),
    re.compile(r'(private_key["\':\s=]+)(["\']?)([^"\'\s&]+)\2', re.IGNORECASE),
]


class SensitiveDataFilter(logging.Filter):
    """
    Sanitizes log records to ensure plaintext credentials and tokens are masked.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.mask_message(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self.mask_value(v) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self.mask_value(arg) for arg in record.args)
        return True

    @classmethod
    def mask_message(cls, message: str) -> str:
        for pattern in SENSITIVE_PATTERNS:
            message = pattern.sub(r'\1\2[REDACTED]\2', message)
        return message

    @classmethod
    def mask_value(cls, val):
        if isinstance(val, str):
            return cls.mask_message(val)
        return val
