"""
Customer Portal Views
API endpoints for customer self-service portal
"""

import hashlib
import secrets
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import CustomerTokenAuthentication
from .models import (
    CustomerAccount,
    CustomerOrder,
    KnowledgeBaseArticle,
    PortalNotification,
    PortalSession,
    SupportTicket,
    TicketComment,
)
from .permissions import IsCustomerAuthenticated
from .serializers import (
    CustomerAccountSerializer,
    CustomerOrderSerializer,
    CustomerProfileUpdateSerializer,
    KnowledgeBaseArticleDetailSerializer,
    KnowledgeBaseArticleListSerializer,
    PortalLoginSerializer,
    PortalNotificationSerializer,
    PortalPasswordResetRequestSerializer,
    PortalPasswordResetSerializer,
    SupportTicketCreateSerializer,
    SupportTicketDetailSerializer,
    SupportTicketListSerializer,
    TicketCommentSerializer,
    TicketFeedbackSerializer,
)


class PortalAuthView(APIView):
    """Handle customer portal authentication"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Login to customer portal"""
        serializer = PortalLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            customer = CustomerAccount.objects.get(email=email)
        except CustomerAccount.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if customer.is_locked():
            return Response(
                {"error": "Account is locked. Please try again later."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Verify password (simplified - use proper password hashing in production)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if customer.password_hash != password_hash:
            customer.failed_login_attempts += 1
            if customer.failed_login_attempts >= 5:
                customer.locked_until = timezone.now() + timedelta(minutes=30)
            customer.save()
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not customer.is_active or not customer.portal_access_enabled:
            return Response(
                {"error": "Account is not active"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Create session
        session = PortalSession.objects.create(
            customer=customer,
            session_token=secrets.token_urlsafe(32),
            refresh_token=secrets.token_urlsafe(32),
            ip_address=request.META.get('REMOTE_ADDR', '0.0.0.0'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            expires_at=timezone.now() + timedelta(hours=24)
        )

        customer.record_login()

        return Response({
            "access_token": session.session_token,
            "refresh_token": session.refresh_token,
            "expires_at": session.expires_at.isoformat(),
            "customer": CustomerAccountSerializer(customer).data
        })


class PortalLogoutView(APIView):
    """Handle customer portal logout"""
    authentication_classes = [CustomerTokenAuthentication]
    permission_classes = [IsCustomerAuthenticated]

    def post(self, request):
        """Logout from customer portal"""
        if hasattr(request, 'portal_session'):
            request.portal_session.is_active = False
            request.portal_session.save()
        return Response({"message": "Logged out successfully"})


class PortalPasswordResetView(APIView):
    """Handle password reset for customer portal"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Request password reset"""
        serializer = PortalPasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            customer = CustomerAccount.objects.get(email=email)
            # Generate reset token
            customer.password_reset_token = secrets.token_urlsafe(32)
            customer.password_reset_expires = timezone.now() + timedelta(hours=1)
            customer.save()

            # TODO: Send email with reset link
            # send_password_reset_email(customer)

        except CustomerAccount.DoesNotExist:
            pass  # Don't reveal if email exists

        return Response({
            "message": "If an account exists with this email, you will receive a password reset link."
        })

    def put(self, request):
        """Reset password with token"""
        serializer = PortalPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        password = serializer.validated_data['password']

        try:
            customer = CustomerAccount.objects.get(
                password_reset_token=token,
                password_reset_expires__gt=timezone.now()
            )
        except CustomerAccount.DoesNotExist:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        customer.password_hash = hashlib.sha256(password.encode()).hexdigest()
        customer.password_reset_token = None
        customer.password_reset_expires = None
        customer.failed_login_attempts = 0
        customer.locked_until = None
        customer.save()

        # Invalidate all sessions
        PortalSession.objects.filter(customer=customer).update(is_active=False)

        return Response({"message": "Password reset successfully"})


class CustomerProfileView(APIView):
    """Customer profile management"""
    authentication_classes = [CustomerTokenAuthentication]
    permission_classes = [IsCustomerAuthenticated]

    def get(self, request):
        """Get customer profile"""
        serializer = CustomerAccountSerializer(request.customer)
        return Response(serializer.data)

    def patch(self, request):
        """Update customer profile"""
        serializer = CustomerProfileUpdateSerializer(
            request.customer,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CustomerAccountSerializer(request.customer).data)


class SupportTicketViewSet(viewsets.ModelViewSet):
    """ViewSet for customer support tickets"""
    authentication_classes = [CustomerTokenAuthentication]
    permission_classes = [IsCustomerAuthenticated]

    def get_queryset(self):
        return SupportTicket.objects.filter(customer=self.request.customer)

    def get_serializer_class(self):
        if self.action == 'list':
            return SupportTicketListSerializer
        elif self.action == 'create':
            return SupportTicketCreateSerializer
        return SupportTicketDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['customer'] = getattr(self.request, 'customer', None)
        return context

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add a comment to a ticket"""
        ticket = self.get_object()

        content = request.data.get('content')
        if not content:
            return Response(
                {"error": "Content is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        comment = TicketComment.objects.create(
            ticket=ticket,
            customer=request.customer,
            content=content,
            attachments=request.data.get('attachments', [])
        )

        # Reopen ticket if it was resolved
        if ticket.status in ['resolved', 'closed']:
            ticket.status = 'open'
            ticket.save()

        return Response(TicketCommentSerializer(comment).data)

    @action(detail=True, methods=['post'])
    def feedback(self, request, pk=None):
        """Submit satisfaction feedback for resolved ticket"""
        ticket = self.get_object()

        if ticket.status not in ['resolved', 'closed']:
            return Response(
                {"error": "Ticket must be resolved to submit feedback"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TicketFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket.satisfaction_rating = serializer.validated_data['rating']
        ticket.satisfaction_feedback = serializer.validated_data.get('feedback', '')
        ticket.save()

        return Response({"message": "Feedback submitted successfully"})


class CustomerOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for customer orders (read-only)"""
    authentication_classes = [CustomerTokenAuthentication]
    permission_classes = [IsCustomerAuthenticated]
    serializer_class = CustomerOrderSerializer

    def get_queryset(self):
        return CustomerOrder.objects.filter(customer=self.request.customer)


class KnowledgeBaseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for knowledge base articles"""
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = KnowledgeBaseArticle.objects.filter(status='published')

        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(tags__contains=[search])
            )

        # Category filter
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Featured filter
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return KnowledgeBaseArticleListSerializer
        return KnowledgeBaseArticleDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def helpful(self, request, slug=None):
        """Mark article as helpful"""
        article = self.get_object()
        helpful = request.data.get('helpful', True)

        if helpful:
            article.helpful_count += 1
        else:
            article.not_helpful_count += 1

        article.save(update_fields=['helpful_count', 'not_helpful_count'])
        return Response({"message": "Feedback recorded"})

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all article categories"""
        categories = KnowledgeBaseArticle.objects.filter(
            status='published'
        ).values_list('category', flat=True).distinct()
        return Response(list(categories))


class PortalNotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for portal notifications"""
    authentication_classes = [CustomerTokenAuthentication]
    permission_classes = [IsCustomerAuthenticated]
    serializer_class = PortalNotificationSerializer
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        return PortalNotification.objects.filter(customer=self.request.customer)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({"message": "All notifications marked as read"})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"count": count})


class PortalDashboardView(APIView):
    """Customer portal dashboard data"""
    authentication_classes = [CustomerTokenAuthentication]
    permission_classes = [IsCustomerAuthenticated]

    def get(self, request):
        """Get dashboard summary"""
        customer = request.customer

        # Get summary data
        open_tickets = SupportTicket.objects.filter(
            customer=customer,
            status__in=['open', 'in_progress', 'waiting_customer']
        ).count()

        recent_orders = CustomerOrder.objects.filter(
            customer=customer
        ).order_by('-ordered_at')[:5]

        unread_notifications = PortalNotification.objects.filter(
            customer=customer,
            is_read=False
        ).count()

        recent_tickets = SupportTicket.objects.filter(
            customer=customer
        ).order_by('-updated_at')[:5]

        return Response({
            "open_tickets": open_tickets,
            "unread_notifications": unread_notifications,
            "recent_orders": CustomerOrderSerializer(recent_orders, many=True).data,
            "recent_tickets": SupportTicketListSerializer(recent_tickets, many=True).data,
            "customer": CustomerAccountSerializer(customer).data
        })
