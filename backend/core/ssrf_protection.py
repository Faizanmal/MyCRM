"""
SSRF (Server-Side Request Forgery) Defense Engine

Protects outgoing webhooks, integration connectors, and URL fetchers
against internal network scans, cloud metadata exfiltration, and localhost targeting.
"""

import ipaddress
import logging
import socket
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


class SSRFProtectionError(ValueError):
    """Raised when a URL targets a prohibited internal, loopback, or metadata destination."""
    pass


# Prohibited hostnames
BLOCKED_HOSTNAMES = {
    'localhost',
    'localhost.localdomain',
    '127.0.0.1',
    '::1',
    '0.0.0.0',
    'metadata.google.internal',
    'metadata.goog',
    'instance-data',
}

# Specific cloud metadata IP strings
CLOUD_METADATA_IPS = {
    '169.254.169.254',  # AWS, GCP, Azure, OpenStack instance metadata
    '100.100.100.200',  # Alibaba Cloud metadata
}

# Carrier-Grade NAT network
CGNAT_NETWORK = ipaddress.ip_network('100.64.0.0/10')


def is_ip_prohibited(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Check if an IP address belongs to internal, loopback, link-local, or cloud metadata ranges."""
    # Check string match for cloud metadata
    if str(ip) in CLOUD_METADATA_IPS:
        return True

    # Standard IP flags
    if ip.is_loopback:
        return True
    if ip.is_private:
        return True
    if ip.is_link_local:
        return True
    if ip.is_reserved:
        return True
    if ip.is_multicast:
        return True
    if ip.is_unspecified:
        return True

    # Carrier-grade NAT (100.64.0.0/10)
    if isinstance(ip, ipaddress.IPv4Address) and ip in CGNAT_NETWORK:
        return True

    return False


def validate_safe_url(url: str, allow_private: bool = False) -> str:
    """
    Validate that a URL is safe to request from the backend.
    Enforces:
    - HTTP or HTTPS scheme only
    - Non-empty hostname
    - Blacklisted hostname check
    - DNS resolution checking against loopback, RFC1918, link-local, and cloud metadata

    Returns validated URL or raises SSRFProtectionError.
    """
    if not url or not isinstance(url, str):
        raise SSRFProtectionError("URL must be a non-empty string.")

    try:
        parsed = urlparse(url.strip())
    except Exception as e:
        raise SSRFProtectionError(f"Malformed URL: {str(e)}")

    if parsed.scheme.lower() not in ('http', 'https'):
        raise SSRFProtectionError(f"Prohibited URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFProtectionError("URL is missing a valid hostname.")

    hostname_lower = hostname.lower()

    if hostname_lower in BLOCKED_HOSTNAMES:
        raise SSRFProtectionError(f"Target hostname '{hostname}' is prohibited (SSRF blocked).")

    if allow_private:
        return url

    # Resolve hostname to IP addresses
    try:
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as e:
        # If hostname does not resolve at all, treat as invalid target
        raise SSRFProtectionError(f"Hostname resolution failed for '{hostname}': {str(e)}")
    except Exception as e:
        raise SSRFProtectionError(f"DNS lookup error for '{hostname}': {str(e)}")

    for family, socktype, proto, canonname, sockaddr in addr_info:
        ip_str = sockaddr[0]
        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError:
            raise SSRFProtectionError(f"Invalid IP address format: {ip_str}")

        if is_ip_prohibited(ip_obj):
            logger.warning(
                "SSRF Protection triggered: hostname '%s' resolved to prohibited IP '%s'",
                hostname,
                ip_str
            )
            raise SSRFProtectionError(
                f"Target URL '{url}' resolves to prohibited internal address {ip_str} (SSRF blocked)."
            )

    return url


def safe_requests_request(method: str, url: str, **kwargs) -> requests.Response:
    """
    Execute an HTTP request while enforcing strict SSRF validation.
    Also validates intermediate redirect destinations if redirects are allowed.
    """
    validate_safe_url(url)

    # Set conservative default timeout
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 15

    # Check redirects safely
    session = requests.Session()

    def check_redirect(response, *args, **hook_kwargs):
        if response.is_redirect or response.status_code in (301, 302, 303, 307, 308):
            redirect_url = response.headers.get('Location')
            if redirect_url:
                validate_safe_url(redirect_url)

    response = session.request(
        method=method,
        url=url,
        hooks={'response': check_redirect},
        **kwargs
    )
    return response
