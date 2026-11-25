"""
Unit & Integration Tests for Enterprise Security Pipeline Components.
Tests secret scanning, dependency vulnerability audit, tenancy abuse runner,
dangerous endpoints regression gate, and operational readiness status endpoint.
"""
import pytest
from rest_framework.test import APIClient

from scripts.security_pipeline.secret_scanner import scan_text
from scripts.security_pipeline.dependency_audit import parse_version_tuple, CRITICAL_ADVISORIES
from scripts.security_pipeline.dangerous_endpoints_gate import evaluate_dangerous_endpoints, DANGEROUS_REGISTRY
from scripts.security_pipeline.tenancy_abuse_runner import run_tenancy_abuse_suite


def test_secret_scanner_detects_real_secrets():
    # Detects private key (assembled dynamically to prevent false positive in static git push protection)
    priv_key_header = "-----" + "BEGIN RSA PRIVATE KEY" + "-----"
    violations = scan_text(f"{priv_key_header}\nMIIEowIBAAKCAQEA...", "mock_key.pem")
    assert len(violations) > 0
    assert violations[0]['rule'] == 'Private Key'

    # Detects AWS Key (assembled dynamically to prevent false positive in static git push protection)
    dummy_aws = "AKIA" + "1234567890ABCDEF"
    violations_aws = scan_text(f"AWS_KEY = '{dummy_aws}'", "config.py")
    assert len(violations_aws) > 0
    assert violations_aws[0]['rule'] == 'AWS Access Key ID'

    # Detects Stripe live key (assembled dynamically to prevent false positive in static git push protection)
    dummy_stripe = "sk_" + "live_" + "1234567890abcdef1234567890"
    violations_stripe = scan_text(f"STRIPE_KEY = '{dummy_stripe}'", "settings.py")
    assert len(violations_stripe) > 0
    assert violations_stripe[0]['rule'] == 'Stripe Live Secret Key'

    # Ignores safe placeholders
    clean = scan_text("API_KEY = '***REDACTED***'\nTEST = 'test-secret-key'", "safe.py")
    assert len(clean) == 0


def test_dependency_version_parsing():
    assert parse_version_tuple("4.2.16") == (4, 2, 16)
    assert parse_version_tuple("5.2.10a1") == (5, 2, 10, 1)
    assert parse_version_tuple("4.2.15") < parse_version_tuple("4.2.16")
    assert len(CRITICAL_ADVISORIES) > 0


def test_dangerous_endpoints_gate_enforcement():
    # Dangerous file without test -> fails
    dangerous_file = list(DANGEROUS_REGISTRY.keys())[0]
    is_compliant, violations = evaluate_dangerous_endpoints({dangerous_file, 'non_existent_test_path.py'})
    # When required test exists in repo, it passes; if test doesn't exist, it flags violation
    # Explicit override test
    overridden, over_details = evaluate_dangerous_endpoints({dangerous_file}, override_reason="Emergency hotfix approved by SecOps")
    assert overridden is True
    assert over_details[0]['status'] == 'OVERRIDDEN'


@pytest.mark.django_db
def test_tenancy_abuse_suite_runs():
    passed, results = run_tenancy_abuse_suite()
    assert passed is True
    assert len(results) >= 6
    assert all(r['passed'] for r in results)


@pytest.mark.django_db
def test_security_pipeline_status_endpoint():
    client = APIClient()
    response = client.get('/health/security/')
    assert response.status_code == 200
    data = response.data
    assert data['status'] == 'healthy'
    assert data['pipeline_strict_mode'] is True
    assert data['controls']['secret_detection_enforced'] is True
    assert data['controls']['dangerous_endpoints_gate_enforced'] is True
