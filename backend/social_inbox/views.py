"""
Social Inbox Views
API endpoints for omnichannel social media management
"""

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    SocialAccount,
    SocialAnalytics,
    SocialConversation,
    SocialMessage,
    SocialMonitoringRule,
    SocialPost,
)
from .serializers import (
    BulkConversationActionSerializer,
    SendMessageSerializer,
    SocialAccountSerializer,
    SocialAnalyticsSerializer,
    SocialConversationDetailSerializer,
    SocialConversationListSerializer,
    SocialMessageSerializer,
    SocialMonitoringRuleSerializer,
    SocialPostSerializer,
)
from .services import SentimentAnalyzer, SocialPlatformService


class SocialAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for managing social accounts"""
    serializer_class = SocialAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SocialAccount.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Manually sync messages from this account"""
        account = self.get_object()

        try:
            service = SocialPlatformService(account)
            result = service.sync_messages()

            account.last_sync_at = timezone.now()
            account.sync_error = ''
            account.save()

            return Response({
                "message": "Sync completed",
                "new_conversations": result.get('new_conversations', 0),
                "new_messages": result.get('new_messages', 0)
            })
        except Exception as e:
            account.sync_error = str(e)
            account.save()
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None):
        """Refresh OAuth token for this account"""
        account = self.get_object()

        try:
            service = SocialPlatformService(account)
            new_token = service.refresh_access_token()

            account.access_token = new_token['access_token']
            if 'refresh_token' in new_token:
                account.refresh_token = new_token['refresh_token']
            if 'expires_at' in new_token:
                account.token_expires_at = new_token['expires_at']
            account.status = 'active'
            account.save()

            return Response({"message": "Token refreshed successfully"})
        except Exception as e:
            account.status = 'error'
            account.save()
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get analytics for this account"""
        account = self.get_object()

        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timezone.timedelta(days=days)

        analytics = SocialAnalytics.objects.filter(
            social_account=account,
            date__gte=start_date
        ).order_by('date')

        return Response(SocialAnalyticsSerializer(analytics, many=True).data)


class SocialConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing social conversations (unified inbox)"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = SocialConversation.objects.select_related(
            'social_account', 'assigned_to', 'linked_contact', 'linked_lead'
        ).filter(social_account__created_by=self.request.user)

        # Filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        platform = self.request.query_params.get('platform')
        if platform:
            queryset = queryset.filter(social_account__platform=platform)

        assigned = self.request.query_params.get('assigned_to_me')
        if assigned == 'true':
            queryset = queryset.filter(assigned_to=self.request.user)
        elif assigned == 'unassigned':
            queryset = queryset.filter(assigned_to__isnull=True)

        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        sentiment = self.request.query_params.get('sentiment')
        if sentiment:
            queryset = queryset.filter(sentiment_label=sentiment)

        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(participant_name__icontains=search) |
                Q(participant_handle__icontains=search) |
                Q(messages__content__icontains=search)
            ).distinct()

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return SocialConversationListSerializer
        return SocialConversationDetailSerializer

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a reply to a conversation"""
        conversation = self.get_object()
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            service = SocialPlatformService(conversation.social_account)
            result = service.send_message(
                conversation,
                serializer.validated_data['content'],
                serializer.validated_data.get('attachments', [])
            )

            # Create local message record
            message = SocialMessage.objects.create(
                conversation=conversation,
                external_id=result.get('message_id', ''),
                direction='outbound',
                content=serializer.validated_data['content'],
                attachments=serializer.validated_data.get('attachments', []),
                sent_by=request.user,
                platform_created_at=timezone.now()
            )

            # Update conversation
            conversation.last_message_at = timezone.now()
            conversation.message_count += 1
            if not conversation.first_response_at:
                conversation.first_response_at = timezone.now()
            conversation.save()

            return Response(SocialMessageSerializer(message).data)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def analyze_sentiment(self, request, pk=None):
        """Analyze sentiment of conversation"""
        conversation = self.get_object()

        # Get all inbound messages
        messages = conversation.messages.filter(direction='inbound')
        content = ' '.join([m.content for m in messages])

        analyzer = SentimentAnalyzer()
        result = analyzer.analyze(content)

        conversation.sentiment_score = result['score']
        conversation.sentiment_label = result['label']
        conversation.sentiment_analyzed_at = timezone.now()
        conversation.save()

        return Response({
            "sentiment_score": result['score'],
            "sentiment_label": result['label']
        })

    @action(detail=True, methods=['post'])
    def generate_response(self, request, pk=None):
        """Generate AI-suggested response"""
        conversation = self.get_object()

        # Get conversation context
        messages = conversation.messages.order_by('platform_created_at')[:10]
        context = [
            {"role": "customer" if m.direction == "inbound" else "agent", "content": m.content}
            for m in messages
        ]

        tone = request.data.get('tone', 'professional')

        # Use AI to generate response (placeholder - integrate with ai_insights)
        from ai_insights.services import AIService
        ai_service = AIService()
        suggested = ai_service.generate_social_response(context, tone)

        conversation.suggested_response = suggested
        conversation.response_tone = tone
        conversation.save()

        return Response({
            "suggested_response": suggested,
            "tone": tone
        })

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign conversation to a user"""
        conversation = self.get_object()
        user_id = request.data.get('user_id')

        if user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
                conversation.assigned_to = user
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            conversation.assigned_to = None

        conversation.save()
        return Response({"message": "Conversation assigned"})

    @action(detail=True, methods=['post'])
    def link_contact(self, request, pk=None):
        """Link conversation to a CRM contact"""
        conversation = self.get_object()
        contact_id = request.data.get('contact_id')

        if contact_id:
            from contact_management.models import Contact
            try:
                contact = Contact.objects.get(id=contact_id)
                conversation.linked_contact = contact
                conversation.save()
                return Response({"message": "Contact linked"})
            except Contact.DoesNotExist:
                return Response(
                    {"error": "Contact not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(
            {"error": "contact_id required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark all messages in conversation as read"""
        conversation = self.get_object()
        conversation.messages.filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        conversation.unread_count = 0
        conversation.save()
        return Response({"message": "Marked as read"})

    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Perform bulk actions on conversations"""
        serializer = BulkConversationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversations = self.get_queryset().filter(
            id__in=serializer.validated_data['conversation_ids']
        )
        action_type = serializer.validated_data['action']
        value = serializer.validated_data.get('value', '')

        updated = 0
        for conv in conversations:
            if action_type == 'mark_read':
                conv.unread_count = 0
                conv.messages.update(is_read=True, read_at=timezone.now())
            elif action_type == 'mark_unread':
                conv.unread_count = conv.message_count
                conv.messages.update(is_read=False)
            elif action_type == 'resolve':
                conv.status = 'resolved'
                conv.resolved_at = timezone.now()
            elif action_type == 'reopen':
                conv.status = 'open'
                conv.resolved_at = None
            elif action_type == 'mark_spam':
                conv.status = 'spam'
            elif action_type == 'assign' and value:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    conv.assigned_to = User.objects.get(id=value)
                except User.DoesNotExist:
                    continue
            elif action_type == 'add_tag' and value:
                if value not in conv.tags:
                    conv.tags.append(value)
            elif action_type == 'remove_tag' and value:
                if value in conv.tags:
                    conv.tags.remove(value)

            conv.save()
            updated += 1

        return Response({"updated": updated})


class SocialMonitoringRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for social monitoring rules"""
    serializer_class = SocialMonitoringRuleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SocialMonitoringRule.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test a monitoring rule with sample text"""
        rule = self.get_object()
        sample_text = request.data.get('text', '')

        # Check if any keyword matches
        matches = []
        text_lower = sample_text.lower()

        for keyword in rule.keywords:
            if keyword.lower() in text_lower:
                matches.append(keyword)

        # Check exclusions
        excluded = False
        for exclude in rule.exclude_keywords:
            if exclude.lower() in text_lower:
                excluded = True
                break

        return Response({
            "would_match": len(matches) > 0 and not excluded,
            "matched_keywords": matches,
            "excluded": excluded
        })


class SocialPostViewSet(viewsets.ModelViewSet):
    """ViewSet for scheduling and publishing social posts"""
    serializer_class = SocialPostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = SocialPost.objects.prefetch_related('social_accounts').filter(
            created_by=self.request.user
        )

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def publish_now(self, request, pk=None):
        """Publish post immediately"""
        post = self.get_object()

        if post.status == 'published':
            return Response(
                {"error": "Post already published"},
                status=status.HTTP_400_BAD_REQUEST
            )

        post.status = 'publishing'
        post.save()

        results = {}
        for account in post.social_accounts.all():
            try:
                service = SocialPlatformService(account)
                result = service.publish_post(post.content, post.media_urls)
                results[str(account.id)] = {
                    'success': True,
                    'post_id': result.get('post_id'),
                    'url': result.get('url')
                }
            except Exception as e:
                results[str(account.id)] = {
                    'success': False,
                    'error': str(e)
                }

        post.publish_results = results
        post.published_at = timezone.now()

        # Check if any succeeded
        if any(r['success'] for r in results.values()):
            post.status = 'published'
        else:
            post.status = 'failed'

        post.save()

        return Response(SocialPostSerializer(post).data)


class UnifiedInboxDashboardView(APIView):
    """Dashboard view for unified social inbox"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get inbox dashboard summary"""
        accounts = SocialAccount.objects.filter(created_by=request.user)
        conversations = SocialConversation.objects.filter(
            social_account__in=accounts
        )

        # Summary stats
        stats = {
            'total_accounts': accounts.count(),
            'active_accounts': accounts.filter(status='active').count(),
            'total_conversations': conversations.count(),
            'open_conversations': conversations.filter(status__in=['new', 'open', 'pending']).count(),
            'unread_messages': conversations.aggregate(
                total=Count('unread_count')
            )['total'] or 0,
            'assigned_to_me': conversations.filter(
                assigned_to=request.user,
                status__in=['new', 'open', 'pending']
            ).count(),
        }

        # By platform
        by_platform = conversations.values(
            'social_account__platform'
        ).annotate(
            count=Count('id'),
            open_count=Count('id', filter=Q(status__in=['new', 'open']))
        )

        # Recent conversations
        recent = SocialConversationListSerializer(
            conversations.order_by('-last_message_at')[:10],
            many=True
        ).data

        # Sentiment breakdown
        sentiment_breakdown = {
            'positive': conversations.filter(sentiment_label='positive').count(),
            'neutral': conversations.filter(sentiment_label='neutral').count(),
            'negative': conversations.filter(sentiment_label='negative').count(),
        }

        return Response({
            'stats': stats,
            'by_platform': list(by_platform),
            'recent_conversations': recent,
            'sentiment_breakdown': sentiment_breakdown
        })
