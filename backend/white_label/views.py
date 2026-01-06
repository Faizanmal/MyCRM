"""
White Label and Billing Views
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import (
    FeatureFlag,
    Invoice,
    Organization,
    OrganizationMember,
    PartnerPayout,
    SubscriptionPlan,
    WhiteLabelPartner,
)
from .serializers import (
    AddPaymentMethodSerializer,
    ChangePlanSerializer,
    CreateCheckoutSessionSerializer,
    InviteMemberSerializer,
    InvoiceSerializer,
    OrganizationCreateSerializer,
    OrganizationMemberSerializer,
    OrganizationSerializer,
    PartnerPayoutSerializer,
    PaymentMethodSerializer,
    SubscriptionPlanPublicSerializer,
    SubscriptionPlanSerializer,
    WhiteLabelBrandingSerializer,
    WhiteLabelPartnerSerializer,
)
from .services import BillingService


class WhiteLabelPartnerViewSet(viewsets.ModelViewSet):
    """Manage white-label partners (admin only)"""
    serializer_class = WhiteLabelPartnerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show partners user is admin of
        return WhiteLabelPartner.objects.filter(
            admin_users=self.request.user
        )

    @action(detail=True, methods=['get'])
    def analytics(self, request, _pk=None):
        """Get partner analytics"""
        partner = self.get_object()

        orgs = partner.organizations.all()
        return Response({
            'total_organizations': orgs.count(),
            'active_organizations': orgs.filter(subscription_status='active').count(),
            'total_users': sum(o.current_users for o in orgs),
            'mrr': self._calculate_mrr(orgs),
        })

    def _calculate_mrr(self, orgs):
        """Calculate monthly recurring revenue"""
        mrr = 0
        for org in orgs.filter(subscription_status='active'):
            if org.plan.billing_period == 'monthly':
                mrr += float(org.plan.price)
            elif org.plan.billing_period == 'yearly':
                mrr += float(org.plan.price) / 12
        return round(mrr, 2)


class BrandingViewSet(viewsets.ViewSet):
    """Public endpoint for white-label branding"""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def by_domain(self, request):
        """Get branding for a domain"""
        domain = request.query_params.get('domain', '')
        subdomain = request.query_params.get('subdomain', '')

        partner = None
        if domain:
            partner = WhiteLabelPartner.objects.filter(
                custom_domain=domain, is_active=True
            ).first()
        if not partner and subdomain:
            partner = WhiteLabelPartner.objects.filter(
                subdomain=subdomain, is_active=True
            ).first()

        if not partner:
            return Response({'branding': None})

        serializer = WhiteLabelBrandingSerializer(partner)
        return Response({'branding': serializer.data})


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """View subscription plans"""
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return SubscriptionPlanSerializer
        return SubscriptionPlanPublicSerializer

    def get_queryset(self):
        qs = SubscriptionPlan.objects.filter(is_active=True, partner__isnull=True)
        return qs.order_by('display_order', 'price')


class OrganizationViewSet(viewsets.ModelViewSet):
    """Manage organizations"""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrganizationCreateSerializer
        return OrganizationSerializer

    def get_queryset(self):
        return Organization.objects.filter(
            members__user=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        org = serializer.save(
            owner=self.request.user,
            subscription_status='trialing',
            trial_ends_at=timezone.now() + timedelta(days=serializer.validated_data['plan'].trial_days)
        )

        # Add creator as owner
        OrganizationMember.objects.create(
            organization=org,
            user=self.request.user,
            role='owner',
            can_manage_users=True,
            can_manage_billing=True,
            can_export_data=True,
            can_delete_data=True
        )

    @action(detail=True, methods=['post'])
    def invite_member(self, request, _pk=None):
        """Invite a member to organization"""
        org = self.get_object()
        serializer = InviteMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = BillingService()
        success, message = service.invite_member(
            org,
            request.user,
            **serializer.validated_data
        )

        if success:
            return Response({'status': 'invited', 'message': message})
        return Response({'status': 'error', 'message': message}, status=400)

    @action(detail=True, methods=['get'])
    def members(self, request, _pk=None):
        """Get organization members"""
        org = self.get_object()
        members = org.members.all()
        serializer = OrganizationMemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def change_plan(self, request, _pk=None):
        """Change subscription plan"""
        org = self.get_object()
        serializer = ChangePlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = BillingService()
        success, message = service.change_plan(
            org,
            serializer.validated_data['plan_id']
        )

        if success:
            return Response({'status': 'changed', 'message': message})
        return Response({'status': 'error', 'message': message}, status=400)

    @action(detail=True, methods=['post'])
    def cancel_subscription(self, request, _pk=None):
        """Cancel subscription"""
        org = self.get_object()

        service = BillingService()
        success, message = service.cancel_subscription(org)

        if success:
            return Response({'status': 'canceled', 'message': message})
        return Response({'status': 'error', 'message': message}, status=400)

    @action(detail=True, methods=['get'])
    def usage(self, request, _pk=None):
        """Get usage summary"""
        org = self.get_object()
        plan = org.plan

        def calc_percent(current, limit):
            if limit == 0:
                return 0
            return round((current / limit) * 100, 1)

        storage_limit_bytes = plan.max_storage_gb * 1024 * 1024 * 1024

        return Response({
            'users': org.current_users,
            'users_limit': plan.max_users,
            'users_percent': calc_percent(org.current_users, plan.max_users),
            'contacts': org.current_contacts,
            'contacts_limit': plan.max_contacts,
            'contacts_percent': calc_percent(org.current_contacts, plan.max_contacts),
            'storage_bytes': org.current_storage_bytes,
            'storage_limit_bytes': storage_limit_bytes,
            'storage_percent': calc_percent(org.current_storage_bytes, storage_limit_bytes),
        })

    @action(detail=True, methods=['get'])
    def invoices(self, request, _pk=None):
        """Get organization invoices"""
        org = self.get_object()
        invoices = org.invoices.all()
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def payment_methods(self, request, _pk=None):
        """Get payment methods"""
        org = self.get_object()
        methods = org.payment_methods.all()
        serializer = PaymentMethodSerializer(methods, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_payment_method(self, request, _pk=None):
        """Add payment method"""
        org = self.get_object()
        serializer = AddPaymentMethodSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = BillingService()
        success, message = service.add_payment_method(
            org,
            serializer.validated_data['payment_method_id'],
            serializer.validated_data['set_as_default']
        )

        if success:
            return Response({'status': 'added', 'message': message})
        return Response({'status': 'error', 'message': message}, status=400)

    @action(detail=True, methods=['get'])
    def features(self, request, _pk=None):
        """Get enabled features for organization"""
        org = self.get_object()

        features = {}
        for flag in FeatureFlag.objects.all():
            features[flag.name] = flag.is_enabled_for(org)

        return Response(features)


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """View invoices"""
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(
            organization__members__user=self.request.user
        ).distinct()

    @action(detail=True, methods=['get'])
    def download(self, request, _pk=None):
        """Get invoice PDF download URL"""
        invoice = self.get_object()

        if not invoice.pdf_url:
            service = BillingService()
            invoice.pdf_url = service.generate_invoice_pdf(invoice)
            invoice.save()

        return Response({'download_url': invoice.pdf_url})


class PartnerPayoutViewSet(viewsets.ReadOnlyModelViewSet):
    """View partner payouts"""
    serializer_class = PartnerPayoutSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PartnerPayout.objects.filter(
            partner__admin_users=self.request.user
        )


class CheckoutViewSet(viewsets.ViewSet):
    """Handle checkout process"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_session(self, request):
        """Create Stripe checkout session"""
        serializer = CreateCheckoutSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = BillingService()
        session_url = service.create_checkout_session(
            user=request.user,
            plan_id=serializer.validated_data['plan_id'],
            success_url=serializer.validated_data['success_url'],
            cancel_url=serializer.validated_data['cancel_url']
        )

        return Response({'checkout_url': session_url})

    @action(detail=False, methods=['post'])
    def webhook(self, request):
        """Handle Stripe webhooks"""
        service = BillingService()
        success = service.handle_webhook(request)

        if success:
            return Response({'received': True})
        return Response({'error': 'Webhook processing failed'}, status=400)
