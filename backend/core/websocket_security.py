"""
Channels & WebSocket Multi-Tenant Authorization and Revocation Engine

Protects against:
1. Cross-organization group subscriptions.
2. Guessed / arbitrary channel group subscriptions.
3. Access by deactivated, anonymous, or revoked users.
4. Mid-session connection termination upon credential/membership revocation.
"""

import logging
import re
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


def get_user_active_organization_id(user) -> str | None:
    """Resolve the active organization UUID for a given user"""
    if not user or user.is_anonymous:
        return None

    # Check direct foreign key
    if getattr(user, 'organization_id', None):
        return str(user.organization_id)

    # Check active membership
    from multi_tenant.models import OrganizationMember
    membership = OrganizationMember.objects.filter(user=user, is_active=True).first()
    if membership:
        return str(membership.organization_id)

    return None


def is_user_still_active(user_id) -> bool:
    """Verify if user exists, is active, and has not been revoked"""
    try:
        user = User.objects.get(id=user_id)
        if not user.is_active:
            return False
        # Verify active organization membership
        from multi_tenant.models import OrganizationMember
        has_membership = OrganizationMember.objects.filter(user=user, is_active=True).exists()
        if not has_membership and not user.is_superuser:
            return False
        return True
    except User.DoesNotExist:
        return False


def is_user_authorized_for_channel(user, channel_name: str) -> tuple[bool, str]:
    """
    Validate whether an authenticated user is authorized to subscribe to a Channels group.
    Blocks wrong-tenant subscriptions, cross-user subscriptions, and guessed groups.
    """
    from django.conf import settings
    if not getattr(settings, 'REALTIME_WEBSOCKET_ENABLED', True):
        return False, "Realtime subscriptions temporarily disabled by operational switch"

    if not user or user.is_anonymous:
        return False, "Authentication required"

    if not user.is_active:
        return False, "Account is deactivated"

    user_tenant_id = get_user_active_organization_id(user)
    if not user_tenant_id and not user.is_superuser:
        return False, "User has no active organization membership"

    # Rule 1: User private notifications channel: notifications_<user_id>
    notif_match = re.match(r'^notifications_([a-zA-Z0-9_\-]+)$', channel_name)
    if notif_match:
        target_user_id = notif_match.group(1)
        if str(user.id) != target_user_id:
            logger.warning(
                "SECURITY ALERT: User %s attempted to subscribe to notifications for User %s",
                user.id,
                target_user_id
            )
            return False, "Forbidden: Cannot subscribe to another user's notification channel"
        return True, "Authorized"

    # Rule 2: Tenant-scoped activity feeds & broadcasts
    # activity_feed_tenant_<tenant_id>, tenant_<tenant_id>_feed, tenant_<tenant_id>_notifications
    tenant_match = (
        re.match(r'^activity_feed_tenant_([a-zA-Z0-9_\-]+)$', channel_name) or
        re.match(r'^tenant_([a-zA-Z0-9_\-]+)_[a-zA-Z0-9_\-]+$', channel_name)
    )
    if tenant_match:
        target_tenant_id = tenant_match.group(1)
        if user_tenant_id != target_tenant_id and not user.is_superuser:
            logger.warning(
                "SECURITY ALERT: User %s (Tenant %s) attempted to subscribe to Tenant %s channel '%s'",
                user.id,
                user_tenant_id,
                target_tenant_id,
                channel_name
            )
            return False, "Forbidden: Cannot subscribe to channel outside your organization"
        return True, "Authorized"

    # Rule 3: Document collaboration rooms: document_<document_id>
    doc_match = re.match(r'^document_([a-zA-Z0-9_\-]+)$', channel_name)
    if doc_match:
        doc_id = doc_match.group(1)
        from document_management.models import Document
        from realtime_collaboration.models import CollaborativeDocument

        doc_tenant = None
        # Check CollaborativeDocument
        collab_doc = CollaborativeDocument.objects.filter(id=doc_id).first()
        if collab_doc and collab_doc.tenant_id:
            doc_tenant = str(collab_doc.tenant_id)
        else:
            doc = Document.objects.filter(id=doc_id).first()
            if doc and doc.organization_id:
                doc_tenant = str(doc.organization_id)

        if doc_tenant and doc_tenant != user_tenant_id and not user.is_superuser:
            logger.warning(
                "SECURITY ALERT: User %s (Tenant %s) attempted to access Document %s (Tenant %s)",
                user.id,
                user_tenant_id,
                doc_id,
                doc_tenant
            )
            return False, "Forbidden: Cannot access document belonging to another organization"
        return True, "Authorized"

    # Rule 4: System ping / health channels
    if channel_name in ('ping', 'health'):
        return True, "Authorized"

    # Any other guessed or unmapped channel group
    logger.warning("SECURITY ALERT: User %s attempted to subscribe to unknown/guessed channel '%s'", user.id, channel_name)
    return False, "Forbidden: Invalid or unrecognized channel group identifier"


async def arevoke_user_websocket_sessions(user_id):
    """Async broadcast of a forced disconnection event to all active WebSocket connections for a user."""
    channel_layer = get_channel_layer()
    if channel_layer:
        group_name = f"user_revocation_{user_id}"
        await channel_layer.group_send(
            group_name,
            {
                'type': 'user_session_revoked',
                'user_id': str(user_id),
                'message': 'Account access or session has been revoked. Connection terminated.'
            }
        )
        logger.info("Sent WebSocket revocation event to group '%s'", group_name)


def revoke_user_websocket_sessions(user_id):
    """
    Broadcast a forced disconnection event to all active WebSocket connections for a user.
    Safe to call from synchronous views, signals, tasks, or running event loops.
    """
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.create_task(arevoke_user_websocket_sessions(user_id))
    else:
        channel_layer = get_channel_layer()
        if channel_layer:
            group_name = f"user_revocation_{user_id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'user_session_revoked',
                    'user_id': str(user_id),
                    'message': 'Account access or session has been revoked. Connection terminated.'
                }
            )
            logger.info("Sent WebSocket revocation event to group '%s'", group_name)
