"""
Forensic Verification Harness: 05-async-realtime
Validates:
1. Wrong-org subscribe and guessed group IDs rejected on Channels WebSockets.
2. Revoked or deactivated users denied connection or disconnected mid-session.
3. Duplicate job execution does not duplicate side effects (Idempotency).
4. Queue poison data quarantined and audited into PoisonPillQuarantine.
"""

import asyncio
import json
import os
import sys

import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
os.environ['DEBUG'] = 'True'
os.environ['USE_SQLITE'] = 'True'
django.setup()

from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.async_idempotency import idempotent_task
from core.async_models import PoisonPillQuarantine, TaskExecutionRecord
from core.consumers import NotificationConsumer, RealtimeConsumer
from core.poison_queue import MalformedPayloadError, quarantine_poison_pill
from core.websocket_security import arevoke_user_websocket_sessions, revoke_user_websocket_sessions
from document_management.models import Document
from multi_tenant.models import Organization, OrganizationMember
from realtime_collaboration.consumers import DocumentCollaborationConsumer

User = get_user_model()


async def run_websocket_checks(org_alpha, org_beta, user_alpha, user_beta, user_revoked, doc_alpha, doc_beta):
    print("\n[Check 1] Wrong-org subscribe and guessed group IDs rejected")

    # 1. User Alpha connects to RealtimeConsumer
    communicator_alpha = WebsocketCommunicator(
        RealtimeConsumer.as_asgi(),
        "/ws/realtime/"
    )
    communicator_alpha.scope['user'] = user_alpha
    connected, _ = await communicator_alpha.connect()
    assert connected, "Failed to connect User Alpha to RealtimeConsumer"
    init_msg = await communicator_alpha.receive_json_from()
    assert init_msg['type'] == 'connection_established'
    print("  PASS: User Alpha connected to RealtimeConsumer.")

    # 2. User Alpha attempts to subscribe to Org Beta's tenant activity feed
    await communicator_alpha.send_json_to({
        'type': 'subscribe',
        'channel': f'activity_feed_tenant_{org_beta.id}'
    })
    res_wrong_org = await communicator_alpha.receive_json_from()
    assert res_wrong_org['type'] == 'subscription_error'
    assert "outside your organization" in res_wrong_org['error']
    print(f"  PASS: Cross-org subscribe rejected: {res_wrong_org['error']}")

    # 3. User Alpha attempts to subscribe to User Beta's private notifications
    await communicator_alpha.send_json_to({
        'type': 'subscribe',
        'channel': f'notifications_{user_beta.id}'
    })
    res_wrong_user = await communicator_alpha.receive_json_from()
    assert res_wrong_user['type'] == 'subscription_error'
    assert "another user's notification channel" in res_wrong_user['error']
    print(f"  PASS: Cross-user notifications subscribe rejected: {res_wrong_user['error']}")

    # 4. User Alpha attempts to subscribe to an arbitrary guessed group ID
    await communicator_alpha.send_json_to({
        'type': 'subscribe',
        'channel': 'admin_secret_super_feed'
    })
    res_guessed = await communicator_alpha.receive_json_from()
    assert res_guessed['type'] == 'subscription_error'
    assert "unrecognized channel group identifier" in res_guessed['error']
    print(f"  PASS: Guessed group ID rejected: {res_guessed['error']}")

    # 5. User Alpha attempts to join DocumentCollaborationConsumer for Doc Beta (Org Beta)
    comm_doc_beta = WebsocketCommunicator(
        DocumentCollaborationConsumer.as_asgi(),
        f"/ws/documents/{doc_beta.id}/"
    )
    comm_doc_beta.scope['user'] = user_alpha
    comm_doc_beta.scope['url_route'] = {'kwargs': {'document_id': str(doc_beta.id)}}
    connected_wrong_doc, close_code = await comm_doc_beta.connect()
    assert not connected_wrong_doc, "Cross-org document collaboration was not rejected!"
    assert close_code == 4403, f"Expected close code 4403, got {close_code}"
    print(f"  PASS: Cross-org document room connection denied (close code {close_code}).")

    # 6. User Alpha subscribes to their own authorized channel
    await communicator_alpha.send_json_to({
        'type': 'subscribe',
        'channel': f'activity_feed_tenant_{org_alpha.id}'
    })
    res_valid = await communicator_alpha.receive_json_from()
    assert res_valid['type'] == 'subscribed'
    print(f"  PASS: Authorized tenant channel subscription accepted ({res_valid['channel']}).")

    # Clean disconnect
    await communicator_alpha.disconnect()

    # -------------------------------------------------------------------------
    # CHECK 2: Revoked users disconnected or denied
    # -------------------------------------------------------------------------
    print("\n[Check 2] Revoked users disconnected or denied")

    # 1. Deny initial connection for deactivated user
    comm_deactivated = WebsocketCommunicator(
        NotificationConsumer.as_asgi(),
        "/ws/notifications/"
    )
    comm_deactivated.scope['user'] = user_revoked
    connected_revoked, code_revoked = await comm_deactivated.connect()
    assert not connected_revoked, "Deactivated user connection was not rejected!"
    assert code_revoked == 4401, f"Expected code 4401 for deactivated user, got {code_revoked}"
    print(f"  PASS: Deactivated user connection rejected with code {code_revoked}.")

    # 2. Mid-session revocation disconnect
    comm_active = WebsocketCommunicator(
        NotificationConsumer.as_asgi(),
        "/ws/notifications/"
    )
    comm_active.scope['user'] = user_alpha
    connected_active, _ = await comm_active.connect()
    assert connected_active
    await comm_active.receive_json_from()  # connection_established
    print("  PASS: Active user connected before revocation test.")

    # Trigger mid-session revocation broadcast
    await arevoke_user_websocket_sessions(user_alpha.id)

    # Consumer should receive revocation message and close
    revocation_msg = await comm_active.receive_json_from()
    assert revocation_msg['type'] == 'revoked'
    print(f"  PASS: Received real-time revocation notice: '{revocation_msg['message']}'")

    # Check connection closes with 4401
    close_event = await comm_active.receive_output()
    assert close_event['type'] == 'websocket.close'
    assert close_event['code'] == 4401, f"Expected close code 4401, got {close_event['code']}"
    await comm_active.disconnect()
    print("  PASS: Revoked user WebSocket connection terminated with code 4401.")


def run_celery_and_quarantine_checks(org_alpha):
    print("\n[Check 3] Duplicate job does not duplicate side effects (Idempotency)")

    side_effects = {'emails_sent': 0, 'billing_charged': 0}

    @idempotent_task()
    def process_billing_and_email(customer_id, amount_cents):
        side_effects['billing_charged'] += amount_cents
        side_effects['emails_sent'] += 1
        return {'charged': amount_cents, 'customer': customer_id, 'status': 'success'}

    # 1. Initial Job Execution
    res1 = process_billing_and_email("cust_999", 5000, idempotency_key="tx_unique_batch_001")
    assert res1['status'] == 'success'
    assert side_effects['billing_charged'] == 5000
    assert side_effects['emails_sent'] == 1
    print("  PASS: First execution completed. Side effects: 1 email sent, $50.00 charged.")

    # 2. Duplicate Job Execution (Replay with same idempotency key)
    res2 = process_billing_and_email("cust_999", 5000, idempotency_key="tx_unique_batch_001")
    assert res2['status'] == 'success'
    # Side effects MUST NOT increment!
    assert side_effects['billing_charged'] == 5000, f"Billing double-charged! Got {side_effects['billing_charged']}"
    assert side_effects['emails_sent'] == 1, f"Duplicate email sent! Got {side_effects['emails_sent']}"
    assert res2.get('idempotent_replay') is True
    print("  PASS: Duplicate execution returned cached result without duplicating side effects.")

    print("\n[Check 4] Queue poison data quarantined and audited")

    @quarantine_poison_pill()
    def process_sync_task(payload, **kwargs):
        if not payload.get('data'):
            raise MalformedPayloadError("Missing required 'data' field in sync payload; unrecoverable corrupt record.")
        return {'status': 'processed'}

    # Trigger poison pill payload
    corrupted_payload = {'corrupt_bytes': '\x00\xff', 'timestamp': str(timezone.now())}
    result = process_sync_task(corrupted_payload, organization=org_alpha)

    assert result['status'] == 'quarantined'
    quarantine_id = result['quarantine_id']
    assert quarantine_id is not None
    print(f"  PASS: Poison pill was quarantined gracefully (ID: {quarantine_id}).")

    # Verify Quarantine Record in Database
    record = PoisonPillQuarantine.objects.get(id=quarantine_id)
    assert record.error_type == 'MalformedPayloadError'
    assert "Missing required 'data' field" in record.error_message
    assert record.tenant == org_alpha
    assert record.status == 'quarantined'
    print(f"  PASS: Quarantine database record verified with full error traceback and tenant boundary ({record.tenant.name}).")


def main():
    print("=" * 70)
    print("STARTING 05-ASYNC-REALTIME VERIFICATION HARNESS")
    print("=" * 70)

    # Cleanup test data
    TaskExecutionRecord.objects.all().delete()
    PoisonPillQuarantine.objects.all().delete()
    Organization.objects.filter(slug__in=['async-org-alpha', 'async-org-beta']).delete()
    User.objects.filter(username__in=['async_user_alpha', 'async_user_beta', 'async_user_revoked']).delete()

    org_alpha = Organization.objects.create(name="Async Org Alpha", slug="async-org-alpha")
    org_beta = Organization.objects.create(name="Async Org Beta", slug="async-org-beta")

    user_alpha = User.objects.create_user(username="async_user_alpha", password="Password123!")
    user_beta = User.objects.create_user(username="async_user_beta", password="Password123!")
    user_revoked = User.objects.create_user(username="async_user_revoked", password="Password123!", is_active=False)

    OrganizationMember.objects.create(organization=org_alpha, user=user_alpha, role="member", is_active=True)
    OrganizationMember.objects.create(organization=org_beta, user=user_beta, role="member", is_active=True)

    doc_alpha = Document.objects.create(
        name="Doc_Alpha.pdf",
        organization=org_alpha,
        uploaded_by=user_alpha,
        file_size=10,
        last_accessed=timezone.now()
    )
    doc_beta = Document.objects.create(
        name="Doc_Beta.pdf",
        organization=org_beta,
        uploaded_by=user_beta,
        file_size=10,
        last_accessed=timezone.now()
    )

    # Run WebSocket async tests
    asyncio.run(run_websocket_checks(org_alpha, org_beta, user_alpha, user_beta, user_revoked, doc_alpha, doc_beta))

    # Run Celery idempotency & quarantine tests
    run_celery_and_quarantine_checks(org_alpha)

    print("\n" + "=" * 70)
    print("ALL 05-ASYNC-REALTIME ACCEPTANCE CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == '__main__':
    main()
