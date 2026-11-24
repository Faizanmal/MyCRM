"""
Inbound Webhook Receiver Views

Features:
1. Strict HMAC-SHA256 signature verification.
2. Timestamp tolerance window (prevents replay attacks).
3. Nonce / Event-ID idempotency checking (prevents duplicate delivery processing).
4. Forged tenant identity rejection/isolation (tenant context strictly bound to endpoint configuration).
"""

import hashlib
import hmac
import json
import logging
import time
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import InboundWebhookDelivery, InboundWebhookEndpoint

logger = logging.getLogger(__name__)


class InboundWebhookReceiverView(APIView):
    """
    Receives incoming webhooks from external third-party services.
    Validates HMAC signature, timestamp age, nonce uniqueness, and protects tenant boundaries.
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Inbound webhooks use signature-based auth

    def post(self, request, endpoint_id):
        raw_body = request.body
        body_text = raw_body.decode('utf-8', errors='replace')

        # 1. Look up endpoint
        try:
            endpoint = InboundWebhookEndpoint.objects.select_related('organization').get(id=endpoint_id)
        except (InboundWebhookEndpoint.DoesNotExist, ValueError):
            return Response(
                {'error': 'Webhook endpoint not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not endpoint.is_active:
            return Response(
                {'error': 'Webhook endpoint is inactive'},
                status=status.HTTP_403_FORBIDDEN
            )

        # 2. Timestamp tolerance check (Replay defense)
        timestamp_header = request.headers.get('X-Webhook-Timestamp')
        if not timestamp_header:
            return Response(
                {'error': 'Missing required X-Webhook-Timestamp header'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            timestamp = float(timestamp_header)
        except ValueError:
            return Response(
                {'error': 'Invalid timestamp format in X-Webhook-Timestamp header'},
                status=status.HTTP_400_BAD_REQUEST
            )

        now = time.time()
        drift = abs(now - timestamp)
        if drift > endpoint.tolerance_seconds:
            logger.warning(
                "Webhook timestamp drift %.2fs exceeds tolerance %ds for endpoint %s",
                drift,
                endpoint.tolerance_seconds,
                endpoint.id
            )
            return Response(
                {'error': f'Webhook timestamp outside tolerance window ({drift:.1f}s > {endpoint.tolerance_seconds}s); rejected as potential replay'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. HMAC-SHA256 Signature verification
        signature_header = request.headers.get('X-Webhook-Signature')
        if not signature_header:
            return Response(
                {'error': 'Missing required X-Webhook-Signature header'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Strip optional 'sha256=' prefix if provided
        received_sig = signature_header
        if received_sig.startswith('sha256='):
            received_sig = received_sig[7:]

        # Compute expected signature over timestamp + body or raw body
        secret_bytes = endpoint.secret_key.encode('utf-8')
        sig_with_ts = hmac.new(
            secret_bytes,
            f"{timestamp_header}.{body_text}".encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        sig_raw_body = hmac.new(
            secret_bytes,
            raw_body,
            hashlib.sha256
        ).hexdigest()

        is_valid = hmac.compare_digest(received_sig, sig_with_ts) or hmac.compare_digest(received_sig, sig_raw_body)
        if not is_valid:
            logger.warning("Invalid webhook signature received for endpoint %s", endpoint.id)
            return Response(
                {'error': 'Invalid webhook signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Parse JSON payload
        try:
            payload = json.loads(body_text) if body_text else {}
        except json.JSONDecodeError:
            return Response(
                {'error': 'Malformed JSON payload'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Replay / Event ID Idempotency Check
        event_id = request.headers.get('X-Webhook-ID') or payload.get('id') or payload.get('event_id') or ''
        if event_id:
            duplicate = InboundWebhookDelivery.objects.filter(
                endpoint=endpoint,
                event_id=str(event_id),
                status='processed'
            ).exists()
            if duplicate:
                logger.warning(
                    "Duplicate webhook event ID '%s' received on endpoint %s; rejected",
                    event_id,
                    endpoint.id
                )
                InboundWebhookDelivery.objects.create(
                    endpoint=endpoint,
                    event_id=str(event_id),
                    event_type=payload.get('event', payload.get('type', 'unknown')),
                    payload=payload,
                    status='duplicate',
                )
                return Response(
                    {'error': 'Duplicate or replayed webhook event rejected'},
                    status=status.HTTP_409_CONFLICT
                )

        # 5. Forged Tenant Identity Protection
        # Verify if payload attempts to inject or forge a tenant/organization identity
        forged_tenant_detected = False
        payload_tenant_id = payload.get('tenant_id') or payload.get('organization_id') or payload.get('tenant')
        bound_tenant_id = str(endpoint.organization.id)

        if payload_tenant_id and str(payload_tenant_id) != bound_tenant_id:
            forged_tenant_detected = True
            logger.critical(
                "SECURITY ALERT: Inbound webhook on endpoint %s received forged tenant ID '%s' (bound organization is '%s'). Overriding untrusted payload tenant.",
                endpoint.id,
                payload_tenant_id,
                bound_tenant_id
            )
            # Force the internal execution context strictly to the bound organization
            payload['tenant_id'] = bound_tenant_id
            payload['organization_id'] = bound_tenant_id

        # 6. Record Delivery
        delivery = InboundWebhookDelivery.objects.create(
            endpoint=endpoint,
            event_id=str(event_id),
            event_type=payload.get('event', payload.get('type', 'generic.webhook')),
            payload=payload,
            status='processed',
            forged_tenant_detected=forged_tenant_detected,
        )

        return Response(
            {
                'status': 'processed',
                'delivery_id': str(delivery.id),
                'tenant_id': bound_tenant_id,
                'forged_tenant_ignored': forged_tenant_detected,
            },
            status=status.HTTP_200_OK
        )
