from django.contrib.auth.models import User
from django.test import TestCase

from multi_tenant.models import Organization
from .models import ApprovalWorkflow, Channel, DealRoom, Message


class BaseCollabTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Collab Org', slug='collab-org')
        self.user = User.objects.create_user(username='testuser', password='testpass')


class DealRoomModelTest(BaseCollabTest):
    def test_deal_room_creation(self):
        """Test creating a deal room"""
        deal_room = DealRoom.objects.create(
            organization=self.org,
            name='Test Deal Room',
            status='active',
            privacy='private',
            owner=self.user
        )
        self.assertEqual(deal_room.name, 'Test Deal Room')
        self.assertEqual(deal_room.participant_count, 0)
        self.assertEqual(deal_room.message_count, 0)


class ChannelModelTest(BaseCollabTest):
    def test_channel_creation(self):
        """Test creating a channel"""
        channel = Channel.objects.create(
            organization=self.org,
            name='Test Channel',
            channel_type='public',
            created_by=self.user
        )
        self.assertEqual(channel.name, 'Test Channel')
        self.assertEqual(channel.member_count, 0)


class MessageModelTest(BaseCollabTest):
    def setUp(self):
        super().setUp()
        self.channel = Channel.objects.create(
            organization=self.org,
            name='Test Channel',
            channel_type='public',
            created_by=self.user
        )

    def test_message_creation(self):
        """Test creating a message"""
        message = Message.objects.create(
            organization=self.org,
            sender=self.user,
            channel=self.channel,
            content='Test message'
        )
        self.assertEqual(message.content, 'Test message')
        self.assertEqual(message.thread_reply_count, 0)
        self.assertFalse(message.is_deleted)


class ApprovalWorkflowTest(BaseCollabTest):
    def test_workflow_creation(self):
        """Test creating an approval workflow"""
        workflow = ApprovalWorkflow.objects.create(
            organization=self.org,
            name='Test Workflow',
            created_by=self.user
        )
        self.assertEqual(workflow.name, 'Test Workflow')
        self.assertTrue(workflow.is_active)
        self.assertEqual(workflow.total_instances, 0)
