"""
Data Validation Utilities

Provides comprehensive validation utilities for:
- Email validation
- Phone number validation
- URL validation
- Custom field validation
- Data sanitization
"""

import logging
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import EmailValidator
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    value: Any
    errors: list[str]
    warnings: list[str]

    @classmethod
    def success(cls, value: Any, warnings: list[str] = None) -> 'ValidationResult':
        return cls(is_valid=True, value=value, errors=[], warnings=warnings or [])

    @classmethod
    def failure(cls, errors: list[str], value: Any = None) -> 'ValidationResult':
        return cls(is_valid=False, value=value, errors=errors, warnings=[])


class EmailValidator2:
    """Enhanced email validator with additional checks."""

    # Common disposable email domains
    DISPOSABLE_DOMAINS = {
        'tempmail.com', 'throwaway.com', 'guerrillamail.com',
        'mailinator.com', '10minutemail.com', 'temp-mail.org',
        'fakeinbox.com', 'trashmail.com', 'yopmail.com',
    }

    # Common typos in email domains
    DOMAIN_TYPOS = {
        'gmial.com': 'gmail.com',
        'gmai.com': 'gmail.com',
        'gamil.com': 'gmail.com',
        'hotmal.com': 'hotmail.com',
        'hotmai.com': 'hotmail.com',
        'outloo.com': 'outlook.com',
        'yahooo.com': 'yahoo.com',
        'yaho.com': 'yahoo.com',
    }

    @classmethod
    def validate(cls, email: str, allow_disposable: bool = False) -> ValidationResult:
        """Validate email address with enhanced checks."""
        if not email:
            return ValidationResult.failure(['Email is required'])

        email = email.strip().lower()
        warnings = []

        # Basic format validation
        try:
            EmailValidator()(email)
        except DjangoValidationError:
            return ValidationResult.failure(['Invalid email format'])

        # Extract domain
        parts = email.split('@')
        if len(parts) != 2:
            return ValidationResult.failure(['Invalid email format'])

        local, domain = parts

        # Check for common typos
        if domain in cls.DOMAIN_TYPOS:
            suggested = cls.DOMAIN_TYPOS[domain]
            warnings.append(f'Did you mean {local}@{suggested}?')
            # Auto-correct the domain
            email = f'{local}@{suggested}'
            domain = suggested

        # Check for disposable emails
        if not allow_disposable and domain in cls.DISPOSABLE_DOMAINS:
            return ValidationResult.failure(['Disposable email addresses are not allowed'])

        # Check for obviously invalid patterns
        if '..' in email:
            return ValidationResult.failure(['Email contains consecutive dots'])

        if local.startswith('.') or local.endswith('.'):
            return ValidationResult.failure(['Email local part cannot start or end with a dot'])

        return ValidationResult.success(email, warnings)


class PhoneValidator:
    """Phone number validator and formatter."""

    # Common phone number patterns
    PATTERNS = {
        'US': re.compile(r'^\+?1?\s*\(?([2-9][0-9]{2})\)?[\s.-]?([0-9]{3})[\s.-]?([0-9]{4})$'),
        'UK': re.compile(r'^\+?44\s?[0-9]{10,11}$'),
        'INTL': re.compile(r'^\+[1-9][0-9]{6,14}$'),
    }

    @classmethod
    def validate(cls, phone: str, country: str = 'US') -> ValidationResult:
        """Validate phone number."""
        if not phone:
            return ValidationResult.success(None)  # Phone might be optional

        # Remove common formatting characters
        cleaned = re.sub(r'[\s\-\.\(\)]', '', phone)

        # Try to match patterns
        if country == 'US':
            match = cls.PATTERNS['US'].match(phone)
            if match:
                # Format as US phone number
                formatted = f'+1 ({match.group(1)}) {match.group(2)}-{match.group(3)}'
                return ValidationResult.success(formatted)

        # Try international format
        if cleaned.startswith('+') and cls.PATTERNS['INTL'].match(cleaned):
            return ValidationResult.success(cleaned)

        # Try to add country code
        if cleaned.isdigit() and len(cleaned) == 10:
            formatted = f'+1 ({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}'
            return ValidationResult.success(
                formatted,
                warnings=['Assumed US country code (+1)']
            )

        return ValidationResult.failure([
            'Invalid phone number format. Please use format: +1 (XXX) XXX-XXXX'
        ])

    @classmethod
    def format(cls, phone: str, format_type: str = 'E164') -> str:
        """Format phone number to specified format."""
        result = cls.validate(phone)
        if not result.is_valid:
            return phone

        cleaned = re.sub(r'[^\d+]', '', result.value)

        if format_type == 'E164':
            return cleaned
        elif format_type == 'NATIONAL' and cleaned.startswith('+1') and len(cleaned) == 12:
            return f'({cleaned[2:5]}) {cleaned[5:8]}-{cleaned[8:]}'

        return result.value


class URLValidator:
    """URL validator with security checks."""

    ALLOWED_SCHEMES = {'http', 'https'}
    BLOCKED_HOSTS = {'localhost', '127.0.0.1', '0.0.0.0'}

    URL_PATTERN = re.compile(
        r'^(?:(?:https?):\/\/)'  # Scheme
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # Domain
        r'[A-Z]{2,6}\.?|'  # TLD
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # Port
        r'(?:/?|[/?]\S+)$',
        re.IGNORECASE
    )

    @classmethod
    def validate(cls, url: str, allow_localhost: bool = False) -> ValidationResult:
        """Validate URL with security checks."""
        if not url:
            return ValidationResult.success(None)

        url = url.strip()

        # Check for valid format
        if not cls.URL_PATTERN.match(url):
            # Try adding https://
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'
                if not cls.URL_PATTERN.match(url):
                    return ValidationResult.failure(['Invalid URL format'])

        # Parse URL
        from urllib.parse import urlparse
        parsed = urlparse(url)

        # Check scheme
        if parsed.scheme not in cls.ALLOWED_SCHEMES:
            return ValidationResult.failure(['URL scheme must be http or https'])

        # Check host
        host = parsed.hostname.lower() if parsed.hostname else ''

        if not allow_localhost and host in cls.BLOCKED_HOSTS:
            return ValidationResult.failure(['Local URLs are not allowed'])

        # Warn about http
        warnings = []
        if parsed.scheme == 'http':
            warnings.append('URL uses insecure HTTP. Consider using HTTPS.')

        return ValidationResult.success(url, warnings)


class DataSanitizer:
    """Sanitize user input data."""

    # HTML entity patterns
    HTML_ENTITIES = {
        '<': '&lt;',
        '>': '&gt;',
        '&': '&amp;',
        '"': '&quot;',
        "'": '&#x27;',
    }

    @classmethod
    def sanitize_string(cls, value: str, max_length: int | None = None) -> str:
        """Sanitize a string value."""
        if not value:
            return ''

        # Strip whitespace
        value = value.strip()

        # Remove null bytes
        value = value.replace('\x00', '')

        # Normalize whitespace
        value = ' '.join(value.split())

        # Truncate if needed
        if max_length and len(value) > max_length:
            value = value[:max_length]

        return value

    @classmethod
    def escape_html(cls, value: str) -> str:
        """Escape HTML entities."""
        for char, entity in cls.HTML_ENTITIES.items():
            value = value.replace(char, entity)
        return value

    @classmethod
    def sanitize_dict(cls, data: dict[str, Any], schema: dict[str, dict] | None = None) -> dict[str, Any]:
        """Sanitize a dictionary of values."""
        result = {}

        for key, value in data.items():
            if isinstance(value, str):
                result[key] = cls.sanitize_string(value)
            elif isinstance(value, dict):
                result[key] = cls.sanitize_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    cls.sanitize_string(v) if isinstance(v, str) else v
                    for v in value
                ]
            else:
                result[key] = value

        return result


def validate_required(value: Any, field_name: str) -> ValidationResult:
    """Validate that a value is not empty."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return ValidationResult.failure([f'{field_name} is required'])
    return ValidationResult.success(value)


def validate_length(
    value: str,
    min_length: int = 0,
    max_length: int | None = None,
    field_name: str = 'Field'
) -> ValidationResult:
    """Validate string length."""
    if not value:
        value = ''

    length = len(value)
    errors = []

    if length < min_length:
        errors.append(f'{field_name} must be at least {min_length} characters')

    if max_length and length > max_length:
        errors.append(f'{field_name} must be at most {max_length} characters')

    if errors:
        return ValidationResult.failure(errors)

    return ValidationResult.success(value)


def validate_choices(
    value: Any,
    choices: list[Any],
    field_name: str = 'Field'
) -> ValidationResult:
    """Validate that value is one of allowed choices."""
    if value not in choices:
        return ValidationResult.failure([
            f'{field_name} must be one of: {", ".join(str(c) for c in choices)}'
        ])
    return ValidationResult.success(value)


def validate_numeric_range(
    value: float,
    min_value: float | None = None,
    max_value: float | None = None,
    field_name: str = 'Value'
) -> ValidationResult:
    """Validate numeric value is within range."""
    errors = []

    if min_value is not None and value < min_value:
        errors.append(f'{field_name} must be at least {min_value}')

    if max_value is not None and value > max_value:
        errors.append(f'{field_name} must be at most {max_value}')

    if errors:
        return ValidationResult.failure(errors)

    return ValidationResult.success(value)


class FormValidator:
    """Validator for form data with multiple fields."""

    def __init__(self):
        self.errors: dict[str, list[str]] = {}
        self.warnings: dict[str, list[str]] = {}
        self.cleaned_data: dict[str, Any] = {}

    def add_error(self, field: str, error: str) -> None:
        """Add an error for a field."""
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(error)

    def add_warning(self, field: str, warning: str) -> None:
        """Add a warning for a field."""
        if field not in self.warnings:
            self.warnings[field] = []
        self.warnings[field].append(warning)

    def validate_field(
        self,
        field: str,
        value: Any,
        validators: list[Callable[[Any], ValidationResult]]
    ) -> None:
        """Validate a field with multiple validators."""
        current_value = value

        for validator in validators:
            result = validator(current_value)

            if not result.is_valid:
                for error in result.errors:
                    self.add_error(field, error)
                return  # Stop on first error

            for warning in result.warnings:
                self.add_warning(field, warning)

            current_value = result.value

        self.cleaned_data[field] = current_value

    def is_valid(self) -> bool:
        """Check if validation passed."""
        return len(self.errors) == 0

    def raise_if_invalid(self) -> None:
        """Raise ValidationError if validation failed."""
        if not self.is_valid():
            raise ValidationError(self.errors)
