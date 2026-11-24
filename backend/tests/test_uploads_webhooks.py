"""
Unit and Integration Tests for 04-uploads-webhooks
"""

import hashlib
import hmac
import json
import time
from datetime import timedelta

import pytest
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


@pytest.mark.django_db
class TestUploadsAndWebhooks:

    @pytest.fixture
    def test_tenants(self):
        org1 = Organization.objects.create(name="Tenant One", slug="test-tenant-1")
        org2 = Organization.objects.create(name="Tenant Two", slug="test-tenant-2")
        user1 = User.objects.create_user(username="t1_user", password="Password123!")
        user2 = User.objects.create_user(username="t2_user", password="Password123!")
        OrganizationMember.objects.create(organization=org1, user=user1, role="member", is_active=True)
        OrganizationMember.objects.create(organization=org2, user=user2, role="member", is_active=True)
        return {'org1': org1, 'org2': org2, 'user1': user1, 'user2': user2}

    def test_upload_disguised_executable_denied(self):
        """Reject files with executable byte headers disguised under allowed extensions"""
        # Windows PE in PDF
        pe_file = SimpleUploadedFile("fake.pdf", b"MZ\x90\x00executable_data", content_type="application/pdf")
        with pytest.raises(ValidationError) as exc:
            validate_uploaded_file(pe_file)
        assert "disguised executable detected" in str(exc.value)

        # ELF binary in DOCX
        elf_file = SimpleUploadedFile("fake.docx", b"\x7fELF\x02\x01\x01\x00data", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        with pytest.raises(ValidationError) as exc:
            validate_uploaded_file(elf_file)
        assert "disguised executable detected" in str(exc.value)

        # Shell script in PNG
        sh_file = SimpleUploadedFile("fake.png", b"#!/bin/sh\necho pwned", content_type="image/png")
        with pytest.raises(ValidationError) as exc:
            validate_uploaded_file(sh_file)
        assert "disguised executable detected" in str(exc.value)

        # Legitimate PDF accepted
        good_pdf = SimpleUploadedFile("legit.pdf", b"%PDF-1.5 test document", content_type="application/pdf")
        validate_uploaded_file(good_pdf)

    def test_idor_across_orgs_denied(self, test_tenants):
        """User from Tenant 2 cannot view or download Tenant 1's document"""
        org1 = test_tenants['org1']
        org2 = test_tenants['org2']
        user1 = test_tenants['user1']
        user2 = test_tenants['user2']

        doc1 = Document.objects.create(
            name="Secret1.pdf",
            file=SimpleUploadedFile("secret1.pdf", b"%PDF-1.4 tenant 1 only"),
            file_size=20,
            mime_type="application/pdf",
            organization=org1,
            uploaded_by=user1,
            last_accessed=timezone.now()
        )

        factory = APIRequestFactory()

        # Tenant 2 user tries to retrieve Tenant 1 document -> 404
        req_view = factory.get(f'/api/documents/documents/{doc1.id}/')
        force_authenticate(req_view, user=user2)
        req_view.organization = org2
        view_func = DocumentViewSet.as_view({'get': 'retrieve'})
        res_view = view_func(req_view, pk=str(doc1.id))
        assert res_view.status_code == 404

        # Tenant 2 user tries to download Tenant 1 document -> 404
        req_dl = factory.get(f'/api/documents/documents/{doc1.id}/download/')
        force_authenticate(req_dl, user=user2)
        req_dl.organization = org2
        dl_func = DocumentViewSet.as_view({'get': 'download'})
        res_dl = dl_func(req_dl, pk=str(doc1.id))
        assert res_dl.status_code == 404

    def test_expired_url_denied(self, test_tenants):
        """Expired signed tokens and share links are rejected with 403"""
        org1 = test_tenants['org1']
        user1 = test_tenants['user1']

        doc1 = Document.objects.create(
            name="Contract.pdf",
            file=SimpleUploadedFile("contract.pdf", b"%PDF-1.4 contract text"),
            file_size=20,
            mime_type="application/pdf",
            organization=org1,
            uploaded_by=user1,
            last_accessed=timezone.now()
        )

        # 1. Signed download token expired
        token = generate_signed_download_token(doc1.id, user1.id, expires_in_seconds=1)
        time.sleep(1.1)
        with pytest.raises(SignatureExpired):
            verify_signed_download_token(token, max_age=1)

        # 2. DocumentShare expired link
        expired_share = DocumentShare.objects.create(
            document=doc1,
            shared_with_email="vendor@example.com",
            expires_at=timezone.now() - timedelta(minutes=5),
            shared_by=user1,
            last_accessed=timezone.now()
        )
        factory = APIRequestFactory()
        req_share = factory.get(f'/api/documents/shares/download/?token={expired_share.access_token}')
        share_view = DocumentShareViewSet.as_view({'get': 'download'})
        res_share = share_view(req_share)
        assert res_share.status_code == 403
        assert "expired" in res_share.data.get('error', '').lower()

    def test_internal_ip_ssrf_blocked(self):
        """Internal IP, loopback, and cloud metadata URLs are blocked by SSRF validator"""
        blocked_urls = [
            "http://127.0.0.1:8000/internal",
            "http://localhost:5000/api",
            "http://169.254.169.254/latest/meta-data/",
            "http://10.1.2.3/secret",
            "http://192.168.10.1/admin",
        ]
        for url in blocked_urls:
            with pytest.raises(SSRFProtectionError):
                validate_safe_url(url)

    def test_invalid_or_replayed_webhook_denied(self, test_tenants):
        """Reject invalid HMAC, stale timestamps, and duplicate event IDs"""
        org1 = test_tenants['org1']
        secret = "test_webhook_secret_key_123"
        endpoint = InboundWebhookEndpoint.objects.create(
            organization=org1,
            name="Test Webhook",
            secret_key=secret,
            tolerance_seconds=300
        )
        receiver = InboundWebhookReceiverView.as_view()
        factory = APIRequestFactory()

        # Bad signature
        ts = str(int(time.time()))
        body = json.dumps({"event": "order.created", "id": "evt_001"})
        bad_req = factory.post(
            f'/api/integrations/webhooks/inbound/{endpoint.id}/',
            data=body,
            content_type='application/json',
            HTTP_X_WEBHOOK_TIMESTAMP=ts,
            HTTP_X_WEBHOOK_SIGNATURE="tampered_hex"
        )
        bad_res = receiver(bad_req, endpoint_id=endpoint.id)
        assert bad_res.status_code == 401

        # Stale timestamp
        stale_ts = str(int(time.time()) - 500)
        stale_sig = hmac.new(secret.encode(), f"{stale_ts}.{body}".encode(), hashlib.sha256).hexdigest()
        stale_req = factory.post(
            f'/api/integrations/webhooks/inbound/{endpoint.id}/',
            data=body,
            content_type='application/json',
            HTTP_X_WEBHOOK_TIMESTAMP=stale_ts,
            HTTP_X_WEBHOOK_SIGNATURE=stale_sig
        )
        stale_res = receiver(stale_req, endpoint_id=endpoint.id)
        assert stale_res.status_code == 400

        # Valid delivery
        valid_sig = hmac.new(secret.encode(), f"{ts}.{body}".encode(), hashlib.sha256).hexdigest()
        valid_req = factory.post(
            f'/api/integrations/webhooks/inbound/{endpoint.id}/',
            data=body,
            content_type='application/json',
            HTTP_X_WEBHOOK_TIMESTAMP=ts,
            HTTP_X_WEBHOOK_SIGNATURE=valid_sig,
            HTTP_X_WEBHOOK_ID="evt_001"
        )
        valid_res = receiver(valid_req, endpoint_id=endpoint.id)
        assert valid_res.status_code == 200

        # Duplicate replay
        replay_req = factory.post(
            f'/api/integrations/webhooks/inbound/{endpoint.id}/',
            data=body,
            content_type='application/json',
            HTTP_X_WEBHOOK_TIMESTAMP=ts,
            HTTP_X_WEBHOOK_SIGNATURE=valid_sig,
            HTTP_X_WEBHOOK_ID="evt_001"
        )
        replay_res = receiver(replay_req, endpoint_id=endpoint.id)
        assert replay_res.status_code == 409

    def test_forged_tenant_identity_ignored(self, test_tenants):
        """Payload declaring another tenant is overridden to bound endpoint tenant"""
        org1 = test_tenants['org1']
        org2 = test_tenants['org2']
        secret = "test_webhook_secret_key_456"
        endpoint = InboundWebhookEndpoint.objects.create(
            organization=org1,
            name="Tenant 1 Listener",
            secret_key=secret
        )
        receiver = InboundWebhookReceiverView.as_view()
        factory = APIRequestFactory()

        ts = str(int(time.time()))
        # Attacker injects org2 ID in payload
        forged_body = json.dumps({"event": "lead.created", "tenant_id": str(org2.id)})
        sig = hmac.new(secret.encode(), f"{ts}.{forged_body}".encode(), hashlib.sha256).hexdigest()

        req = factory.post(
            f'/api/integrations/webhooks/inbound/{endpoint.id}/',
            data=forged_body,
            content_type='application/json',
            HTTP_X_WEBHOOK_TIMESTAMP=ts,
            HTTP_X_WEBHOOK_SIGNATURE=sig,
            HTTP_X_WEBHOOK_ID="evt_forged_1"
        )
        res = receiver(req, endpoint_id=endpoint.id)
        assert res.status_code == 200
        assert res.data['tenant_id'] == str(org1.id)
        assert res.data['forged_tenant_ignored'] is True

        delivery = InboundWebhookDelivery.objects.get(endpoint=endpoint, event_id="evt_forged_1")
        assert delivery.forged_tenant_detected is True
        assert delivery.payload['tenant_id'] == str(org1.id)
