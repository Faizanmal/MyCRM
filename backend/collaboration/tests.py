from django.contrib.auth.models import User
from django.test import TestCase

from .models import ApprovalWorkflow, Channel, DealRoom, Message


class DealRoomModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_deal_room_creation(self):
        """Test creating a deal room"""
        deal_room = DealRoom.objects.create(
            name='Test Deal Room',
            status='active',
            privacy_level='private',
            created_by=self.user
        )
        self.assertEqual(deal_room.name, 'Test Deal Room')
        self.assertEqual(deal_room.participant_count, 0)
        self.assertEqual(deal_room.message_count, 0)


class ChannelModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_channel_creation(self):
        """Test creating a channel"""
        channel = Channel.objects.create(
            name='Test Channel',
            channel_type='public',
            created_by=self.user
        )
        self.assertEqual(channel.name, 'Test Channel')
        self.assertEqual(channel.member_count, 0)


class MessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.channel = Channel.objects.create(
            name='Test Channel',
            channel_type='public',
            created_by=self.user
        )

    def test_message_creation(self):
        """Test creating a message"""
        message = Message.objects.create(
            sender=self.user,
            channel=self.channel,
            content='Test message'
        )
        self.assertEqual(message.content, 'Test message')
        self.assertEqual(message.thread_reply_count, 0)
        self.assertFalse(message.is_deleted)


class ApprovalWorkflowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_workflow_creation(self):
        """Test creating an approval workflow"""
        workflow = ApprovalWorkflow.objects.create(
            name='Test Workflow',
            created_by=self.user
        )
        self.assertEqual(workflow.name, 'Test Workflow')
        self.assertTrue(workflow.is_active)
        self.assertEqual(workflow.total_instances, 0)
