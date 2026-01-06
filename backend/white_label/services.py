"""
White Label and Billing Service Layer
"""

import contextlib
import os

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


class BillingService:
    """Service for billing operations"""

    def __init__(self):
        self.stripe_available = bool(os.environ.get('STRIPE_SECRET_KEY'))
        if self.stripe_available:
            import stripe
            stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
            self.stripe = stripe

    def invite_member(self, organization, inviter, email, role='user',
                      can_manage_users=False, can_manage_billing=False):
        """Invite a member to an organization"""
        from django.contrib.auth import get_user_model

        from .models import OrganizationMember
        User = get_user_model()

        # Check limits
        if organization.current_users >= organization.plan.max_users:
            return False, "User limit reached for your plan"

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Send invitation email
            self._send_invitation_email(organization, inviter, email)
            return True, "Invitation sent"

        # Check if already a member
        if OrganizationMember.objects.filter(organization=organization, user=user).exists():
            return False, "User is already a member"

        # Add member
        OrganizationMember.objects.create(
            organization=organization,
            user=user,
            role=role,
            can_manage_users=can_manage_users,
            can_manage_billing=can_manage_billing,
            invited_by=inviter
        )

        # Update user count
        organization.current_users += 1
        organization.save()

        # Send welcome email
        self._send_welcome_email(organization, user)

        return True, "Member added successfully"

    def _send_invitation_email(self, organization, inviter, email):
        """Send invitation to non-existent user"""
        signup_url = f"{settings.SITE_URL}/signup?org={organization.uuid}&email={email}"

        subject = f"You've been invited to join {organization.name}"
        body = f"""
{inviter.get_full_name()} has invited you to join {organization.name} on our CRM platform.

Click here to accept the invitation and create your account:
{signup_url}

This invitation will expire in 7 days.
        """

        with contextlib.suppress(Exception):
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True
            )

    def _send_welcome_email(self, organization, user):
        """Send welcome email to new member"""
        login_url = f"{settings.SITE_URL}/login"

        subject = f"Welcome to {organization.name}"
        body = f"""
Welcome to {organization.name}!

You've been added as a member. Log in to get started:
{login_url}
        """

        with contextlib.suppress(Exception):
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )

    def change_plan(self, organization, plan_id):
        """Change subscription plan"""
        from .models import SubscriptionPlan

        try:
            new_plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return False, "Plan not found"

        # Check if downgrading within limits
        if organization.current_users > new_plan.max_users:
            return False, f"Cannot downgrade: you have {organization.current_users} users but the plan only allows {new_plan.max_users}"

        if organization.current_contacts > new_plan.max_contacts:
            return False, f"Cannot downgrade: you have {organization.current_contacts} contacts but the plan only allows {new_plan.max_contacts}"

        # Update Stripe subscription if exists
        if self.stripe_available and organization.stripe_subscription_id:
            try:
                self.stripe.Subscription.modify(
                    organization.stripe_subscription_id,
                    items=[{
                        'id': organization.stripe_subscription_id,
                        'price': new_plan.stripe_price_id,
                    }],
                    proration_behavior='create_prorations'
                )
            except Exception as e:
                return False, f"Payment error: {str(e)}"

        organization.plan = new_plan
        organization.save()

        return True, f"Plan changed to {new_plan.name}"

    def cancel_subscription(self, organization):
        """Cancel subscription"""
        if self.stripe_available and organization.stripe_subscription_id:
            try:
                self.stripe.Subscription.modify(
                    organization.stripe_subscription_id,
                    cancel_at_period_end=True
                )
            except Exception as e:
                return False, f"Error: {str(e)}"

        organization.subscription_status = 'canceled'
        organization.save()

        return True, "Subscription will be canceled at the end of the billing period"

    def add_payment_method(self, organization, payment_method_id, set_as_default=True):
        """Add a payment method"""
        from .models import PaymentMethod

        if not self.stripe_available:
            return False, "Payment processing not configured"

        try:
            # Attach to customer
            if not organization.stripe_customer_id:
                customer = self.stripe.Customer.create(
                    email=organization.owner.email,
                    name=organization.name,
                )
                organization.stripe_customer_id = customer.id
                organization.save()

            self.stripe.PaymentMethod.attach(
                payment_method_id,
                customer=organization.stripe_customer_id,
            )

            if set_as_default:
                self.stripe.Customer.modify(
                    organization.stripe_customer_id,
                    invoice_settings={'default_payment_method': payment_method_id}
                )

            # Get card details
            pm = self.stripe.PaymentMethod.retrieve(payment_method_id)

            # Unset other defaults if setting as default
            if set_as_default:
                PaymentMethod.objects.filter(
                    organization=organization, is_default=True
                ).update(is_default=False)

            # Save payment method
            PaymentMethod.objects.create(
                organization=organization,
                stripe_payment_method_id=payment_method_id,
                card_brand=pm.card.brand,
                card_last4=pm.card.last4,
                card_exp_month=pm.card.exp_month,
                card_exp_year=pm.card.exp_year,
                is_default=set_as_default
            )

            return True, "Payment method added"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def create_checkout_session(self, user, plan_id, success_url, cancel_url):
        """Create Stripe checkout session"""
        from .models import SubscriptionPlan

        if not self.stripe_available:
            return None

        plan = SubscriptionPlan.objects.get(id=plan_id)

        session = self.stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plan.stripe_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=user.email,
            metadata={
                'user_id': user.id,
                'plan_id': plan_id,
            }
        )

        return session.url

    def handle_webhook(self, request):
        """Handle Stripe webhook events"""
        if not self.stripe_available:
            return False

        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

        try:
            event = self.stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except Exception:
            return False

        # Handle specific events
        if event['type'] == 'checkout.session.completed':
            self._handle_checkout_completed(event['data']['object'])
        elif event['type'] == 'invoice.paid':
            self._handle_invoice_paid(event['data']['object'])
        elif event['type'] == 'invoice.payment_failed':
            self._handle_payment_failed(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            self._handle_subscription_deleted(event['data']['object'])

        return True

    def _handle_checkout_completed(self, session):
        """Handle successful checkout"""
        from django.contrib.auth import get_user_model

        from .models import Organization, OrganizationMember, SubscriptionPlan
        User = get_user_model()

        user_id = session['metadata']['user_id']
        plan_id = session['metadata']['plan_id']

        user = User.objects.get(id=user_id)
        plan = SubscriptionPlan.objects.get(id=plan_id)

        # Create organization
        org = Organization.objects.create(
            name=f"{user.first_name}'s Organization",
            slug=f"org-{user.id}",
            owner=user,
            plan=plan,
            subscription_status='active',
            stripe_customer_id=session['customer'],
            stripe_subscription_id=session['subscription'],
        )

        # Add owner as member
        OrganizationMember.objects.create(
            organization=org,
            user=user,
            role='owner',
            can_manage_users=True,
            can_manage_billing=True,
            can_export_data=True,
            can_delete_data=True
        )

    def _handle_invoice_paid(self, invoice):
        """Handle paid invoice"""
        from .models import Invoice, InvoiceLineItem, Organization

        try:
            org = Organization.objects.get(stripe_customer_id=invoice['customer'])
        except Organization.DoesNotExist:
            return

        # Create invoice record
        inv = Invoice.objects.create(
            invoice_number=invoice['number'],
            organization=org,
            subtotal=invoice['subtotal'] / 100,
            tax_amount=invoice['tax'] / 100 if invoice['tax'] else 0,
            total=invoice['total'] / 100,
            status='paid',
            issued_at=timezone.now(),
            paid_at=timezone.now(),
            period_start=timezone.datetime.fromtimestamp(invoice['period_start']).date(),
            period_end=timezone.datetime.fromtimestamp(invoice['period_end']).date(),
            stripe_invoice_id=invoice['id'],
        )

        # Add line items
        for line in invoice['lines']['data']:
            InvoiceLineItem.objects.create(
                invoice=inv,
                description=line['description'] or 'Subscription',
                quantity=line['quantity'],
                unit_price=line['unit_amount'] / 100 if line['unit_amount'] else 0,
                total=line['amount'] / 100,
            )

        # Update org status
        org.subscription_status = 'active'
        org.current_period_ends_at = timezone.datetime.fromtimestamp(
            invoice['lines']['data'][0]['period']['end']
        )
        org.save()

    def _handle_payment_failed(self, invoice):
        """Handle failed payment"""
        from .models import Organization

        try:
            org = Organization.objects.get(stripe_customer_id=invoice['customer'])
            org.subscription_status = 'past_due'
            org.save()
        except Organization.DoesNotExist:
            pass

    def _handle_subscription_deleted(self, subscription):
        """Handle subscription cancellation"""
        from .models import Organization

        try:
            org = Organization.objects.get(stripe_subscription_id=subscription['id'])
            org.subscription_status = 'expired'
            org.stripe_subscription_id = ''
            org.save()
        except Organization.DoesNotExist:
            pass

    def generate_invoice_pdf(self, invoice):
        """Generate PDF for invoice"""
        # In production, use a PDF library
        # For now, return placeholder
        return f"/invoices/{invoice.uuid}.pdf"


class WhiteLabelService:
    """Service for white-label operations"""

    def get_branding_for_request(self, request):
        """Get branding based on request domain"""
        from .models import WhiteLabelPartner

        host = request.get_host()

        # Check custom domain
        partner = WhiteLabelPartner.objects.filter(
            custom_domain=host, is_active=True
        ).first()

        if not partner:
            # Check subdomain
            parts = host.split('.')
            if len(parts) > 2:
                subdomain = parts[0]
                partner = WhiteLabelPartner.objects.filter(
                    subdomain=subdomain, is_active=True
                ).first()

        return partner

    def apply_branding_context(self, context, partner):
        """Add branding to template context"""
        if partner:
            context['brand_name'] = partner.brand_name
            context['logo'] = partner.logo.url if partner.logo else None
            context['primary_color'] = partner.primary_color
            context['secondary_color'] = partner.secondary_color
            context['support_email'] = partner.support_email
            context['hide_powered_by'] = partner.hide_powered_by
        else:
            context['brand_name'] = 'MyCRM'
            context['logo'] = None
            context['primary_color'] = '#2563eb'
            context['secondary_color'] = '#1e40af'
            context['support_email'] = settings.DEFAULT_FROM_EMAIL
            context['hide_powered_by'] = False

        return context
