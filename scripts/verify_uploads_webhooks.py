"""
Forensic Verification Harness: 04-uploads-webhooks
Validates:
1. Upload disguised executable denied (PE, ELF, scripts disguised as PDF/PNG).
2. IDOR across orgs denied (cross-tenant document access/download).
3. Expired URL denied (signed URLs and expired shares).
4. Internal-IP SSRF blocked (loopback, RFC1918, cloud metadata 169.254.169.254).
5. Invalid or replayed webhook denied (bad HMAC, stale timestamp, duplicate event ID).
6. Forged tenant identity ignored (untrusted payload tenant overridden by endpoint boundary).
"""

import hashlib
import hmac
import io
import json
import os
import sys
import time
from datetime import timedelta

import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
os.environ['DEBUG'] = 'True'
os.environ['USE_SQLITE'] = 'True'
django.setup()

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.signing import BadSignature, SignatureExpired
from django.test import RequestFactory
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from core.signed_urls import generate_signed_download_token, verify_signed_download_token
from core.ssrf_protection import SSRFProtectionError, validate_safe_url
from core.upload_security import validate_uploaded_file
from document_management.models import Document, DocumentShare
from document_management.views import DocumentShareViewSet, DocumentViewSet
from integration_hub.inbound_views import InboundWebhookReceiverView
from integration_hub.models import InboundWebhookDelivery, InboundWebhookEndpoint
from multi_tenant.models import Organization, OrganizationMember

User = get_user_model()


def run_all_checks():
    print("=" * 70)
    print("STARTING 04-UPLOADS-WEBHOOKS VERIFICATION HARNESS")
    print("=" * 70)

    # Clean up test entities if any exist
    Organization.objects.filter(slug__in=['test-org-alpha', 'test-org-beta']).delete()
    User.objects.filter(username__in=['user_alpha', 'user_beta']).delete()

    # Create test tenants
    org_alpha = Organization.objects.create(name="Org Alpha", slug="test-org-alpha")
    org_beta = Organization.objects.create(name="Org Beta", slug="test-org-beta")

    user_alpha = User.objects.create_user(username="user_alpha", password="Password123!")
    user_beta = User.objects.create_user(username="user_beta", password="Password123!")

    OrganizationMember.objects.create(organization=org_alpha, user=user_alpha, role="member", is_active=True)
    OrganizationMember.objects.create(organization=org_beta, user=user_beta, role="member", is_active=True)

    # -------------------------------------------------------------------------
    # CHECK 1: Upload disguised executable denied
    # -------------------------------------------------------------------------
    print("\n[Check 1] Upload Disguised Executable Denied")

    # 1. PE executable disguised as PDF
    disguised_pe = SimpleUploadedFile("invoice.pdf", b"MZ\x90\x00\x03\x00\x00\x00" + b"A" * 100, content_type="application/pdf")
    try:
        validate_uploaded_file(disguised_pe)
        assert False, "FAILED: Disguised PE executable was not rejected!"
    except ValidationError as e:
        assert "disguised executable detected" in str(e)
        print("  PASS: Disguised Windows PE executable rejected:", str(e))

    # 2. ELF binary disguised as DOCX
    disguised_elf = SimpleUploadedFile("report.docx", b"\x7fELF\x02\x01\x01\x00" + b"B" * 100, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    try:
        validate_uploaded_file(disguised_elf)
        assert False, "FAILED: Disguised ELF binary was not rejected!"
    except ValidationError as e:
        assert "disguised executable detected" in str(e)
        print("  PASS: Disguised Linux ELF binary rejected:", str(e))

    # 3. Shell script disguised as PNG
    disguised_sh = SimpleUploadedFile("photo.png", b"#!/bin/bash\nrm -rf /", content_type="image/png")
    try:
        validate_uploaded_file(disguised_sh)
        assert False, "FAILED: Disguised shell script was not rejected!"
    except ValidationError as e:
        assert "disguised executable detected" in str(e)
        print("  PASS: Disguised shell script rejected:", str(e))

    # 4. Active PHP script in text
    disguised_php = SimpleUploadedFile("notes.txt", b"<?php system($_GET['cmd']); ?>", content_type="text/plain")
    try:
        validate_uploaded_file(disguised_php)
        assert False, "FAILED: Active script code was not rejected!"
    except ValidationError as e:
        assert "active script code detected" in str(e)
        print("  PASS: Active script injection rejected:", str(e))

    # 5. Legitimate PDF accepted
    valid_pdf = SimpleUploadedFile("contract.pdf", b"%PDF-1.4 legitimate document content here", content_type="application/pdf")
    validate_uploaded_file(valid_pdf)
    print("  PASS: Legitimate PDF successfully accepted.")

    # -------------------------------------------------------------------------
    # CHECK 2: IDOR across orgs denied
    # -------------------------------------------------------------------------
    print("\n[Check 2] IDOR Across Orgs Denied")

    doc_alpha = Document.objects.create(
        name="Confidential_Strategy_Alpha.pdf",
        file=SimpleUploadedFile("strategy.pdf", b"%PDF-1.4 confidential alpha strategy"),
        file_size=36,
        mime_type="application/pdf",
        organization=org_alpha,
        uploaded_by=user_alpha,
        last_accessed=timezone.now()
    )

    factory = APIRequestFactory()

    # User Beta (Org Beta) attempts to view Document Alpha (Org Alpha)
    req_beta_view = factory.get(f'/api/documents/documents/{doc_alpha.id}/')
    force_authenticate(req_beta_view, user=user_beta)
    req_beta_view.organization = org_beta
    view_set = DocumentViewSet.as_view({'get': 'retrieve'})
    res_beta_view = view_set(req_beta_view, pk=str(doc_alpha.id))
    assert res_beta_view.status_code == 404, f"Expected 404 for cross-tenant IDOR retrieve, got {res_beta_view.status_code}"
    print("  PASS: User Beta retrieve of Org Alpha document denied with HTTP 404 (IDOR blocked).")

    # User Beta attempts to download Document Alpha
    req_beta_dl = factory.get(f'/api/documents/documents/{doc_alpha.id}/download/')
    force_authenticate(req_beta_dl, user=user_beta)
    req_beta_dl.organization = org_beta
    dl_set = DocumentViewSet.as_view({'get': 'download'})
    res_beta_dl = dl_set(req_beta_dl, pk=str(doc_alpha.id))
    assert res_beta_dl.status_code == 404, f"Expected 404 for cross-tenant IDOR download, got {res_beta_dl.status_code}"
    print("  PASS: User Beta download of Org Alpha document denied with HTTP 404 (IDOR blocked).")

    # User Alpha accesses own document
    req_alpha_view = factory.get(f'/api/documents/documents/{doc_alpha.id}/')
    force_authenticate(req_alpha_view, user=user_alpha)
    req_alpha_view.organization = org_alpha
    res_alpha_view = view_set(req_alpha_view, pk=str(doc_alpha.id))
    assert res_alpha_view.status_code == 200, f"Expected 200 for tenant owner, got {res_alpha_view.status_code}"
    print("  PASS: User Alpha can access their own organization's document (HTTP 200).")

    # -------------------------------------------------------------------------
    # CHECK 3: Expired URL denied
    # -------------------------------------------------------------------------
    print("\n[Check 3] Expired Signed URL Denied")

    # 1. Time-limited signed URL token
    token = generate_signed_download_token(doc_alpha.id, user_alpha.id, expires_in_seconds=1)
    # Validate token immediately works
    payload = verify_signed_download_token(token, max_age=5)
    assert payload['doc_id'] == str(doc_alpha.id)
    print("  PASS: Signed token verified successfully within TTL.")

    # Expire token
    time.sleep(1.2)
    try:
        verify_signed_download_token(token, max_age=1)
        assert False, "FAILED: Expired token was not rejected!"
    except SignatureExpired:
        print("  PASS: SignatureExpired raised for expired token.")

    # Tampered token
    tampered_token = token[:-4] + "xxxx"
    try:
        verify_signed_download_token(tampered_token, max_age=300)
        assert False, "FAILED: Tampered token was not rejected!"
    except BadSignature:
        print("  PASS: BadSignature raised for tampered token.")

    # 2. DocumentShare expiration check
    expired_share = DocumentShare.objects.create(
        document=doc_alpha,
        shared_with_email="client@example.com",
        expires_at=timezone.now() - timedelta(minutes=10),
        shared_by=user_alpha,
        last_accessed=timezone.now()
    )
    req_share = factory.get(f'/api/documents/shares/download/?token={expired_share.access_token}')
    share_view = DocumentShareViewSet.as_view({'get': 'download'})
    res_share = share_view(req_share)
    assert res_share.status_code == 403, f"Expected 403 for expired share, got {res_share.status_code}"
    assert "Share link has expired" in res_share.data.get('error', '')
    print("  PASS: Expired DocumentShare download denied with HTTP 403 ('Share link has expired').")

    # -------------------------------------------------------------------------
    # CHECK 4: Internal-IP SSRF blocked
    # -------------------------------------------------------------------------
    print("\n[Check 4] Internal-IP SSRF Blocked")

    ssrf_targets = [
        ("http://127.0.0.1:8000/api/internal", "127.0.0.1"),
        ("http://localhost/metrics", "localhost"),
        ("http://169.254.169.254/latest/meta-data/", "169.254.169.254"),
        ("http://10.0.0.1/admin", "10.0.0.1"),
        ("http://192.168.1.1/router", "192.168.1.1"),
        ("http://172.16.0.5/api", "172.16.0.5"),
    ]

    for target_url, label in ssrf_targets:
        try:
            validate_safe_url(target_url)
            assert False, f"FAILED: SSRF to {label} was not blocked!"
        except SSRFProtectionError as e:
            print(f"  PASS: Blocked SSRF attempt to {label}: {str(e)}")

    # Valid external URL
    safe_url = "https://httpbin.org/status/200"
    validated = validate_safe_url(safe_url)
    assert validated == safe_url
    print(f"  PASS: Valid external URL allowed: {safe_url}")

    # -------------------------------------------------------------------------
    # CHECK 5: Invalid or replayed webhook denied
    # -------------------------------------------------------------------------
    print("\n[Check 5] Invalid or Replayed Webhook Denied")

    webhook_secret = "whsec_super_secret_signing_key_42"
    inbound_endpoint = InboundWebhookEndpoint.objects.create(
        organization=org_alpha,
        name="Stripe Inbound Listener",
        secret_key=webhook_secret,
        tolerance_seconds=300,
        is_active=True
    )

    receiver_view = InboundWebhookReceiverView.as_view()

    # 1. Invalid signature
    payload_body = json.dumps({"event": "payment.succeeded", "amount": 5000})
    ts_now = str(int(time.time()))
    bad_req = factory.post(
        f'/api/integrations/webhooks/inbound/{inbound_endpoint.id}/',
        data=payload_body,
        content_type='application/json',
        HTTP_X_WEBHOOK_TIMESTAMP=ts_now,
        HTTP_X_WEBHOOK_SIGNATURE="bad_signature_deadbeef"
    )
    bad_res = receiver_view(bad_req, endpoint_id=inbound_endpoint.id)
    assert bad_res.status_code == 401, f"Expected 401 for bad signature, got {bad_res.status_code}"
    print("  PASS: Tampered/invalid HMAC signature denied with HTTP 401.")

    # 2. Stale / Expired timestamp (Replay scenario)
    stale_ts = str(int(time.time()) - 600)  # 10 minutes ago
    stale_sig = hmac.new(webhook_secret.encode('utf-8'), f"{stale_ts}.{payload_body}".encode('utf-8'), hashlib.sha256).hexdigest()
    stale_req = factory.post(
        f'/api/integrations/webhooks/inbound/{inbound_endpoint.id}/',
        data=payload_body,
        content_type='application/json',
        HTTP_X_WEBHOOK_TIMESTAMP=stale_ts,
        HTTP_X_WEBHOOK_SIGNATURE=stale_sig
    )
    stale_res = receiver_view(stale_req, endpoint_id=inbound_endpoint.id)
    assert stale_res.status_code == 400, f"Expected 400 for stale timestamp, got {stale_res.status_code}"
    print("  PASS: Stale timestamp rejected with HTTP 400 (replay defense).")

    # 3. Valid webhook delivery
    event_id = "evt_stripe_payment_9999"
    valid_sig = hmac.new(webhook_secret.encode('utf-8'), f"{ts_now}.{payload_body}".encode('utf-8'), hashlib.sha256).hexdigest()
    valid_req = factory.post(
        f'/api/integrations/webhooks/inbound/{inbound_endpoint.id}/',
        data=payload_body,
        content_type='application/json',
        HTTP_X_WEBHOOK_TIMESTAMP=ts_now,
        HTTP_X_WEBHOOK_SIGNATURE=valid_sig,
        HTTP_X_WEBHOOK_ID=event_id
    )
    valid_res = receiver_view(valid_req, endpoint_id=inbound_endpoint.id)
    assert valid_res.status_code == 200, f"Expected 200 for valid webhook, got {valid_res.status_code}"
    assert valid_res.data['status'] == 'processed'
    print("  PASS: Valid webhook processed successfully (HTTP 200).")

    # 4. Duplicate / Replay with same event ID
    replay_req = factory.post(
        f'/api/integrations/webhooks/inbound/{inbound_endpoint.id}/',
        data=payload_body,
        content_type='application/json',
        HTTP_X_WEBHOOK_TIMESTAMP=ts_now,
        HTTP_X_WEBHOOK_SIGNATURE=valid_sig,
        HTTP_X_WEBHOOK_ID=event_id
    )
    replay_res = receiver_view(replay_req, endpoint_id=inbound_endpoint.id)
    assert replay_res.status_code == 409, f"Expected 409 for duplicate event ID, got {replay_res.status_code}"
    assert "Duplicate or replayed webhook event rejected" in replay_res.data['error']
    print("  PASS: Replayed event with duplicate event ID rejected with HTTP 409 Conflict.")

    # -------------------------------------------------------------------------
    # CHECK 6: Forged tenant identity ignored
    # -------------------------------------------------------------------------
    print("\n[Check 6] Forged Tenant Identity Ignored")

    # Attacker crafts webhook payload specifying Org Beta ID, but submits to Org Alpha endpoint
    forged_event_id = "evt_forged_tenant_1001"
    forged_payload = json.dumps({
        "event": "invoice.payment_succeeded",
        "tenant_id": str(org_beta.id),
        "organization_id": str(org_beta.id),
        "amount": 250000
    })
    ts_forged = str(int(time.time()))
    forged_sig = hmac.new(webhook_secret.encode('utf-8'), f"{ts_forged}.{forged_payload}".encode('utf-8'), hashlib.sha256).hexdigest()

    forged_req = factory.post(
        f'/api/integrations/webhooks/inbound/{inbound_endpoint.id}/',
        data=forged_payload,
        content_type='application/json',
        HTTP_X_WEBHOOK_TIMESTAMP=ts_forged,
        HTTP_X_WEBHOOK_SIGNATURE=forged_sig,
        HTTP_X_WEBHOOK_ID=forged_event_id
    )
    forged_res = receiver_view(forged_req, endpoint_id=inbound_endpoint.id)
    assert forged_res.status_code == 200
    assert forged_res.data['tenant_id'] == str(org_alpha.id)
    assert forged_res.data['forged_tenant_ignored'] is True

    # Verify delivery record in DB
    delivery = InboundWebhookDelivery.objects.get(endpoint=inbound_endpoint, event_id=forged_event_id)
    assert delivery.forged_tenant_detected is True
    # Verify internal execution context tenant was forced to Org Alpha
    assert delivery.payload['tenant_id'] == str(org_alpha.id)
    print("  PASS: Forged tenant identity was detected, ignored, and strictly bound to endpoint organization.")

    print("\n" + "=" * 70)
    print("ALL 04-UPLOADS-WEBHOOKS ACCEPTANCE CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == '__main__':
    run_all_checks()
