"""
Customer Success Service Layer
"""

import contextlib
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


class CustomerSuccessService:
    """Service for customer success operations"""

    def calculate_health_score(self, account):
        """Calculate health score for an account"""
        from .models import HealthScore, HealthScoreConfig

        # Get config
        config = HealthScoreConfig.objects.filter(is_active=True).first()
        if not config:
            config = HealthScoreConfig.objects.create()

        # Calculate component scores
        usage_score = self._calc_usage_score(account)
        engagement_score = self._calc_engagement_score(account)
        support_score = self._calc_support_score(account)
        payment_score = self._calc_payment_score(account)
        sentiment_score = self._calc_sentiment_score(account)

        # Weighted average
        total_score = (
            (usage_score * config.usage_weight) +
            (engagement_score * config.engagement_weight) +
            (support_score * config.support_weight) +
            (payment_score * config.payment_weight) +
            (sentiment_score * config.sentiment_weight)
        ) / 100

        total_score = round(total_score)

        # Determine status
        if total_score >= config.healthy_threshold:
            status = 'healthy'
        elif total_score >= config.critical_threshold:
            status = 'at_risk'
        else:
            status = 'critical'

        # Calculate trends
        prev_score = account.health_scores.first()
        score_change_7d = 0
        score_change_30d = 0

        if prev_score:
            score_change_7d = total_score - prev_score.score

            score_30d = account.health_scores.filter(
                calculated_at__gte=timezone.now() - timedelta(days=30)
            ).last()
            if score_30d:
                score_change_30d = total_score - score_30d.score

        # Create health score
        score = HealthScore.objects.create(
            account=account,
            score=total_score,
            usage_score=usage_score,
            engagement_score=engagement_score,
            support_score=support_score,
            payment_score=payment_score,
            sentiment_score=sentiment_score,
            status=status,
            score_change_7d=score_change_7d,
            score_change_30d=score_change_30d
        )

        # Trigger alerts if needed
        if status == 'critical':
            self._trigger_critical_alert(account, score)

        return score

    def _calc_usage_score(self, account):
        """Calculate usage-based health score"""
        # In production, this would check actual usage data
        # For now, return placeholder
        return 70

    def _calc_engagement_score(self, account):
        """Calculate engagement-based health score"""
        # Check recent interactions
        notes_count = account.notes.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()

        if notes_count >= 5:
            return 90
        elif notes_count >= 2:
            return 70
        elif notes_count >= 1:
            return 50
        return 30

    def _calc_support_score(self, account):
        """Calculate support-based health score"""
        # In production, check support ticket data
        return 80

    def _calc_payment_score(self, account):
        """Calculate payment-based health score"""
        # Check payment history
        # For now, assume good standing
        return 100

    def _calc_sentiment_score(self, account):
        """Calculate sentiment-based health score"""
        # Check NPS and feedback
        recent_nps = account.nps_surveys.filter(
            responded_at__gte=timezone.now() - timedelta(days=90),
            score__isnull=False
        ).order_by('-responded_at').first()

        if recent_nps:
            return recent_nps.score * 10  # Convert 0-10 to 0-100
        return 50  # Neutral if no data

    def _trigger_critical_alert(self, account, score):
        """Alert CSM about critical health score"""
        if not account.customer_success_manager:
            return

        subject = f"ALERT: {account.name} health score is critical"
        body = f"""
{account.name} has a critical health score of {score.score}.

Component Scores:
- Usage: {score.usage_score}
- Engagement: {score.engagement_score}
- Support: {score.support_score}
- Payment: {score.payment_score}
- Sentiment: {score.sentiment_score}

Please review and take action.
        """

        with contextlib.suppress(Exception):
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[account.customer_success_manager.email],
                fail_silently=True
            )

    def advance_playbook(self, execution):
        """Advance playbook to next step"""
        from .models import PlaybookStep

        playbook = execution.playbook
        current_step = execution.current_step

        # Get next step
        try:
            step = playbook.steps.get(order=current_step)
        except PlaybookStep.DoesNotExist:
            # Playbook completed
            execution.status = 'completed'
            execution.completed_at = timezone.now()
            execution.save()
            return

        # Execute step action
        self._execute_step(execution, step)

        # Move to next step
        execution.current_step += 1
        execution.next_step_at = timezone.now() + timedelta(days=step.delay_days)

        # Check if completed
        if not playbook.steps.filter(order=execution.current_step).exists():
            execution.status = 'completed'
            execution.completed_at = timezone.now()

        execution.save()

    def _execute_step(self, execution, step):
        """Execute a playbook step"""
        account = execution.account

        if step.step_type == 'task':
            # Create task for CSM
            pass
        elif step.step_type == 'email':
            # Send email
            if step.email_template and account.company:
                contacts = account.company.contacts.all()[:1]
                for contact in contacts:
                    self._send_playbook_email(account, contact, step.email_template)
        elif step.step_type == 'call':
            # Create call task
            pass
        elif step.step_type == 'meeting':
            # Create meeting task
            pass

    def _send_playbook_email(self, account, contact, template):
        """Send email from playbook"""
        # Replace template variables
        content = template.replace('{{first_name}}', contact.first_name or '')
        content = content.replace('{{company}}', account.name)

        with contextlib.suppress(Exception):
            send_mail(
                subject=f"Checking in - {account.name}",
                message=content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[contact.email],
                fail_silently=True
            )

    def send_nps_surveys(self, account_id, contact_ids):
        """Send NPS surveys to contacts"""
        from contact_management.models import Contact

        from .models import CustomerAccount, NPSSurvey

        account = CustomerAccount.objects.get(id=account_id)
        contacts = Contact.objects.filter(id__in=contact_ids)

        surveys = []
        for contact in contacts:
            survey = NPSSurvey.objects.create(
                account=account,
                contact=contact,
                sent_at=timezone.now()
            )

            self._send_nps_email(survey)
            surveys.append(survey)

        return surveys

    def _send_nps_email(self, survey):
        """Send NPS survey email"""
        survey_url = f"{settings.SITE_URL}/nps/{survey.id}"

        subject = f"Quick question about your experience with {survey.account.name}"
        body = f"""
Hi {survey.contact.first_name if survey.contact else 'there'},

We'd love to hear your feedback!

On a scale of 0-10, how likely are you to recommend us to a friend or colleague?

Click here to respond: {survey_url}

Thank you for your time!
        """

        with contextlib.suppress(Exception):
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[survey.contact.email] if survey.contact else [],
                fail_silently=True
            )

    def check_renewal_risks(self, account):
        """Identify renewal risk factors"""
        risks = []

        # Check health score
        latest_health = account.health_scores.first()
        if latest_health and latest_health.status in ['at_risk', 'critical']:
            risks.append({
                'factor': 'Low health score',
                'severity': 'high' if latest_health.status == 'critical' else 'medium',
                'details': f'Current health score: {latest_health.score}'
            })

        # Check engagement
        recent_notes = account.notes.filter(
            created_at__gte=timezone.now() - timedelta(days=60)
        ).count()

        if recent_notes == 0:
            risks.append({
                'factor': 'No recent engagement',
                'severity': 'medium',
                'details': 'No customer interactions in last 60 days'
            })

        # Check NPS
        recent_nps = account.nps_surveys.filter(
            score__isnull=False
        ).order_by('-responded_at').first()

        if recent_nps and recent_nps.classification == 'detractor':
            risks.append({
                'factor': 'Detractor NPS',
                'severity': 'high',
                'details': f'NPS score: {recent_nps.score}'
            })

        return risks
