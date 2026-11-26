"""
Pytest Suite for 05-async-realtime:
1. Wrong-org subscribe and guessed group IDs rejected.
2. Revoked users disconnected or denied.
3. Duplicate job does not duplicate side effects.
4. Queue poison data quarantined and audited.
"""

import pytest
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


@pytest.mark.django_db(transaction=True)
class TestAsyncRealtime:

    @pytest.fixture
    def setup_entities(self):
        org1 = Organization.objects.create(name="Realtime Org 1", slug="rt-org-1")
        org2 = Organization.objects.create(name="Realtime Org 2", slug="rt-org-2")
        user1 = User.objects.create_user(username="rt_user_1", password="Password123!")
        user2 = User.objects.create_user(username="rt_user_2", password="Password123!")
        user_revoked = User.objects.create_user(username="rt_user_revoked", password="Password123!", is_active=False)

        OrganizationMember.objects.create(organization=org1, user=user1, role="member", is_active=True)
        OrganizationMember.objects.create(organization=org2, user=user2, role="member", is_active=True)

        doc1 = Document.objects.create(name="Doc1.pdf", organization=org1, uploaded_by=user1, file_size=10, last_accessed=timezone.now())
        doc2 = Document.objects.create(name="Doc2.pdf", organization=org2, uploaded_by=user2, file_size=10, last_accessed=timezone.now())

        return {
            'org1': org1,
            'org2': org2,
            'user1': user1,
            'user2': user2,
            'user_revoked': user_revoked,
            'doc1': doc1,
            'doc2': doc2,
        }

    @pytest.mark.asyncio
    async def test_wrong_org_subscribe_and_guessed_groups_rejected(self, setup_entities):
        """WebSockets reject cross-org channel subscriptions, cross-user subscriptions, and guessed groups"""
        user1 = setup_entities['user1']
        user2 = setup_entities['user2']
        org2 = setup_entities['org2']
        doc2 = setup_entities['doc2']

        comm = WebsocketCommunicator(RealtimeConsumer.as_asgi(), "/ws/realtime/")
        comm.scope['user'] = user1
        connected, _ = await comm.connect()
        assert connected
        await comm.receive_json_from()  # connection_established

        # 1. Wrong-org subscribe
        await comm.send_json_to({'type': 'subscribe', 'channel': f'activity_feed_tenant_{org2.id}'})
        res1 = await comm.receive_json_from()
        assert res1['type'] == 'subscription_error'
        assert "outside your organization" in res1['error']

        # 2. Cross-user subscribe
        await comm.send_json_to({'type': 'subscribe', 'channel': f'notifications_{user2.id}'})
        res2 = await comm.receive_json_from()
        assert res2['type'] == 'subscription_error'
        assert "another user's notification channel" in res2['error']

        # 3. Guessed group ID
        await comm.send_json_to({'type': 'subscribe', 'channel': 'super_admin_guessed_channel'})
        res3 = await comm.receive_json_from()
        assert res3['type'] == 'subscription_error'
        assert "unrecognized channel group identifier" in res3['error']

        # 4. Cross-org collaborative document
        comm_doc = WebsocketCommunicator(DocumentCollaborationConsumer.as_asgi(), f"/ws/documents/{doc2.id}/")
        comm_doc.scope['user'] = user1
        comm_doc.scope['url_route'] = {'kwargs': {'document_id': str(doc2.id)}}
        doc_conn, close_code = await comm_doc.connect()
        assert not doc_conn
        assert close_code == 4403

        await comm.disconnect()

    @pytest.mark.asyncio
    async def test_revoked_users_disconnected_or_denied(self, setup_entities):
        """Deactivated users are denied connection, and active users are disconnected upon revocation"""
        user_revoked = setup_entities['user_revoked']
        user1 = setup_entities['user1']

        # 1. Deactivated user denied at connect
        comm_rev = WebsocketCommunicator(NotificationConsumer.as_asgi(), "/ws/notifications/")
        comm_rev.scope['user'] = user_revoked
        conn, code = await comm_rev.connect()
        assert not conn
        assert code == 4401

        # 2. Active user disconnected upon revocation broadcast
        comm_active = WebsocketCommunicator(NotificationConsumer.as_asgi(), "/ws/notifications/")
        comm_active.scope['user'] = user1
        conn_active, _ = await comm_active.connect()
        assert conn_active
        await comm_active.receive_json_from()

        await arevoke_user_websocket_sessions(user1.id)
        revoke_msg = await comm_active.receive_json_from()
        assert revoke_msg['type'] == 'revoked'
        close_event = await comm_active.receive_output()
        assert close_event['type'] == 'websocket.close'
        assert close_event['code'] == 4401
        await comm_active.disconnect()

    def test_duplicate_job_does_not_duplicate_side_effects(self, setup_entities):
        """Tasks with duplicate idempotency keys return cached result without repeating side effects"""
        counter = {'invocations': 0}

        @idempotent_task()
        def process_charge(order_id, amount):
            counter['invocations'] += 1
            return {'order': order_id, 'charged': amount}

        # First run
        out1 = process_charge("ord_777", 250, idempotency_key="idemp_key_ord_777")
        assert out1['charged'] == 250
        assert counter['invocations'] == 1

        # Duplicate run
        out2 = process_charge("ord_777", 250, idempotency_key="idemp_key_ord_777")
        assert out2['charged'] == 250
        assert counter['invocations'] == 1  # Side effect did not execute again!
        assert out2.get('idempotent_replay') is True

    def test_queue_poison_data_quarantined_and_audited(self, setup_entities):
        """Poison pill payloads are quarantined without crash-looping and recorded in database"""
        org1 = setup_entities['org1']

        @quarantine_poison_pill()
        def risky_parser(payload, **kwargs):
            if not payload.get('valid'):
                raise MalformedPayloadError("Corrupted payload detected: missing 'valid' flag")
            return "ok"

        res = risky_parser({'bad_data': True}, organization=org1)
        assert res['status'] == 'quarantined'
        qid = res['quarantine_id']

        # Check DB record
        q = PoisonPillQuarantine.objects.get(id=qid)
        assert q.error_type == 'MalformedPayloadError'
        assert q.tenant == org1
        assert q.status == 'quarantined'

    def test_poison_pill_api_rbac_and_replay(self, setup_entities):
        """Admin can list and replay quarantined tasks, while non-admin is rejected with 403"""
        from rest_framework.test import APIClient
        org1 = setup_entities['org1']
        user1 = setup_entities['user1']
        user2 = setup_entities['user2']

        # Promote user1 to admin in org1
        membership = OrganizationMember.objects.get(organization=org1, user=user1)
        membership.role = 'admin'
        membership.save()

        # Create a quarantine record
        q = PoisonPillQuarantine.objects.create(
            task_name='process_webhook',
            task_id='t-123',
            payload={'bad': 'data'},
            error_type='ValueError',
            error_message='Invalid JSON',
            tenant=org1,
            status='quarantined'
        )

        client = APIClient()

        # 1. Non-admin user from org2 is rejected (403)
        client.force_authenticate(user=user2)
        resp_denied = client.get(f'/api/core/poison-jobs/{q.id}/')
        assert resp_denied.status_code in (403, 404)

        # 2. Admin user from org1 can retrieve
        client.force_authenticate(user=user1)
        client.credentials(HTTP_X_ORGANIZATION_SLUG=org1.slug)
        resp = client.get(f'/api/core/poison-jobs/{q.id}/')
        assert resp.status_code == 200
        assert resp.data['task_name'] == 'process_webhook'

        # 3. Admin replays the task
        resp_replay = client.post(f'/api/core/poison-jobs/{q.id}/replay/', {'notes': 'Fix applied'})
        assert resp_replay.status_code == 200
        assert resp_replay.data['status'] == 'replayed'

        q.refresh_from_db()
        assert q.status == 'replayed'
        assert 'Fix applied' in q.resolution_notes

    @pytest.mark.asyncio
    async def test_jwt_websocket_auth_middleware(self, setup_entities):
        """JWT token in query string authenticates user and resolves tenant into scope"""
        from rest_framework_simplejwt.tokens import AccessToken
        from core.websocket_auth_middleware import get_user_from_jwt

        user1 = setup_entities['user1']
        org1 = setup_entities['org1']

        token = str(AccessToken.for_user(user1))
        resolved_user, tenant_id = await get_user_from_jwt(token)

        assert resolved_user.id == user1.id
        assert tenant_id == str(org1.id)
