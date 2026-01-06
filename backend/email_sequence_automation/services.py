"""
Email Sequence Automation Services
Core business logic for sequence execution, A/B testing, and automation
"""

import logging
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import Count, F
from django.template import Context, Template
from django.utils import timezone

from .ai_content_generator import AIEmailContentGenerator
from .models import (
    ABTest,
    AutomatedTrigger,
    EmailSequence,
    SequenceActivity,
    SequenceAnalytics,
    SequenceEmail,
    SequenceEnrollment,
    SequenceStep,
)

logger = logging.getLogger(__name__)


class SequenceExecutionService:
    """Service for executing email sequences"""

    def __init__(self):
        self.ai_generator = AIEmailContentGenerator()

    def enroll_contact(
        self,
        sequence_id: str,
        contact_id: int,
        enrolled_by_id: int | None = None,
        trigger: str = 'manual',
        lead_id: int | None = None,
        personalization_data: dict | None = None
    ) -> tuple[SequenceEnrollment, bool]:
        """
        Enroll a contact in a sequence

        Returns:
            Tuple of (enrollment, created)
        """
        from contact_management.models import Contact
        from lead_management.models import Lead

        sequence = EmailSequence.objects.get(id=sequence_id)
        contact = Contact.objects.get(id=contact_id)
        lead = Lead.objects.get(id=lead_id) if lead_id else None

        # Check if already enrolled
        existing = SequenceEnrollment.objects.filter(
            sequence=sequence,
            contact=contact,
            status__in=['active', 'paused']
        ).first()

        if existing:
            return existing, False

        # Get first step
        first_step = sequence.steps.filter(is_active=True).order_by('step_number').first()

        # Build personalization data
        if not personalization_data:
            personalization_data = self._build_personalization_data(contact, lead)

        # Calculate next action time
        next_action_at = self._calculate_next_action_time(first_step, sequence.settings)

        with transaction.atomic():
            enrollment = SequenceEnrollment.objects.create(
                sequence=sequence,
                contact=contact,
                lead=lead,
                current_step=first_step,
                enrolled_by_id=enrolled_by_id,
                enrollment_trigger=trigger,
                next_action_at=next_action_at,
                personalization_data=personalization_data
            )

            # Log activity
            SequenceActivity.objects.create(
                enrollment=enrollment,
                activity_type='enrolled',
                description=f"Enrolled in sequence via {trigger}",
                metadata={'trigger': trigger}
            )

            # Update sequence stats
            sequence.total_enrolled = F('total_enrolled') + 1
            sequence.save(update_fields=['total_enrolled'])

        return enrollment, True

    def process_due_actions(self) -> dict[str, int]:
        """Process all due sequence actions"""
        results = {
            'processed': 0,
            'emails_sent': 0,
            'errors': 0,
            'skipped': 0
        }

        # Get enrollments with due actions
        due_enrollments = SequenceEnrollment.objects.filter(
            status='active',
            next_action_at__lte=timezone.now()
        ).select_related('sequence', 'current_step', 'contact')

        for enrollment in due_enrollments:
            try:
                result = self._process_enrollment_step(enrollment)
                results['processed'] += 1
                if result.get('email_sent'):
                    results['emails_sent'] += 1
                if result.get('skipped'):
                    results['skipped'] += 1
            except Exception as e:
                logger.error(f"Error processing enrollment {enrollment.id}: {e}")
                results['errors'] += 1

                # Log error activity
                SequenceActivity.objects.create(
                    enrollment=enrollment,
                    step=enrollment.current_step,
                    activity_type='error',
                    description=str(e)
                )

        return results

    def _process_enrollment_step(self, enrollment: SequenceEnrollment) -> dict[str, Any]:
        """Process current step for an enrollment"""
        result = {'email_sent': False, 'skipped': False}

        step = enrollment.current_step
        if not step:
            self._complete_enrollment(enrollment)
            return result

        # Check exit conditions
        if self._should_exit(enrollment):
            self._exit_enrollment(enrollment, 'exit_condition_met')
            result['skipped'] = True
            return result

        # Process based on step type
        step_processors = {
            'email': self._process_email_step,
            'wait': self._process_wait_step,
            'condition': self._process_condition_step,
            'task': self._process_task_step,
            'update_field': self._process_field_update_step,
            'add_tag': self._process_tag_step,
            'remove_tag': self._process_tag_step,
            'notify': self._process_notify_step,
            'webhook': self._process_webhook_step,
        }

        processor = step_processors.get(step.step_type)
        if processor:
            result = processor(enrollment, step)

        # Advance to next step
        if not result.get('branch'):
            self._advance_to_next_step(enrollment)

        return result

    def _process_email_step(self, enrollment: SequenceEnrollment, step: SequenceStep) -> dict:
        """Process an email sending step"""
        result = {'email_sent': False}

        # Select email variant (for A/B testing)
        email = self._select_email_variant(step)
        if not email:
            logger.warning(f"No email found for step {step.id}")
            return result

        # Personalize content
        subject = self._personalize_content(email.subject, enrollment.personalization_data)
        body_html = self._personalize_content(email.body_html, enrollment.personalization_data)
        body_text = self._personalize_content(email.body_text, enrollment.personalization_data)

        # Send email
        try:
            self._send_email(
                to_email=enrollment.contact.email,
                to_name=enrollment.contact.full_name,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                enrollment=enrollment,
                email=email
            )

            result['email_sent'] = True

            # Update stats
            email.total_sent = F('total_sent') + 1
            email.save(update_fields=['total_sent'])

            enrollment.emails_sent = F('emails_sent') + 1
            enrollment.save(update_fields=['emails_sent'])

            # Log activity
            SequenceActivity.objects.create(
                enrollment=enrollment,
                step=step,
                activity_type='email_sent',
                description=f"Email sent: {subject}",
                metadata={'email_id': str(email.id), 'variant': email.variant_name}
            )

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            SequenceActivity.objects.create(
                enrollment=enrollment,
                step=step,
                activity_type='error',
                description=f"Email send failed: {str(e)}"
            )

        return result

    def _process_condition_step(self, enrollment: SequenceEnrollment, step: SequenceStep) -> dict:
        """Process a conditional branch step"""
        result = {'branch': True}

        condition_met = self._evaluate_condition(enrollment, step)

        # Determine next step based on condition
        if condition_met and step.branch_yes_step:
            enrollment.current_step = step.branch_yes_step
            branch_name = 'yes'
        elif not condition_met and step.branch_no_step:
            enrollment.current_step = step.branch_no_step
            branch_name = 'no'
        else:
            result['branch'] = False
            return result

        enrollment.save(update_fields=['current_step'])

        # Log activity
        SequenceActivity.objects.create(
            enrollment=enrollment,
            step=step,
            activity_type='branched',
            description=f"Branched to {branch_name} path",
            metadata={'condition': step.condition_type, 'result': branch_name}
        )

        return result

    def _process_task_step(self, enrollment: SequenceEnrollment, step: SequenceStep) -> dict:
        """Create a task from step configuration"""
        from task_management.models import Task

        config = step.config

        Task.objects.create(
            title=self._personalize_content(config.get('title', 'Follow up'), enrollment.personalization_data),
            description=self._personalize_content(config.get('description', ''), enrollment.personalization_data),
            assigned_to_id=config.get('assignee_id') or enrollment.sequence.owner_id,
            due_date=timezone.now() + timedelta(days=config.get('due_days', 1)),
            priority=config.get('priority', 'medium'),
            related_contact_id=enrollment.contact_id
        )

        SequenceActivity.objects.create(
            enrollment=enrollment,
            step=step,
            activity_type='task_created',
            description=f"Task created: {config.get('title', 'Follow up')}"
        )

        return {'task_created': True}

    def _process_field_update_step(self, enrollment: SequenceEnrollment, step: SequenceStep) -> dict:
        """Update a contact field"""
        config = step.config
        field_name = config.get('field')
        field_value = config.get('value')

        if field_name and hasattr(enrollment.contact, field_name):
            setattr(enrollment.contact, field_name, field_value)
            enrollment.contact.save(update_fields=[field_name])

            SequenceActivity.objects.create(
                enrollment=enrollment,
                step=step,
                activity_type='field_updated',
                description=f"Updated {field_name} to {field_value}"
            )

        return {'field_updated': True}

    def _process_tag_step(self, enrollment: SequenceEnrollment, step: SequenceStep) -> dict:
        """Add or remove tag from contact"""
        config = step.config
        tag = config.get('tag')

        if not tag:
            return {}

        tags = list(enrollment.contact.tags or [])

        if step.step_type == 'add_tag':
            if tag not in tags:
                tags.append(tag)
                activity_type = 'tag_added'
        else:  # remove_tag
            if tag in tags:
                tags.remove(tag)
                activity_type = 'tag_removed'
            else:
                return {}

        enrollment.contact.tags = tags
        enrollment.contact.save(update_fields=['tags'])

        SequenceActivity.objects.create(
            enrollment=enrollment,
            step=step,
            activity_type=activity_type,
            description=f"Tag {'added' if step.step_type == 'add_tag' else 'removed'}: {tag}"
        )

        return {'tag_updated': True}

    def _process_notify_step(self, enrollment: SequenceEnrollment, step: SequenceStep) -> dict:
        """Send notification to team member"""
        config = step.config

        # Send notification (could be email, Slack, in-app, etc.)
        message = self._personalize_content(
            config.get('message', 'Sequence notification'),
            enrollment.personalization_data
        )

        # Log activity
        SequenceActivity.objects.create(
            enrollment=enrollment,
            step=step,
            activity_type='step_started',
            description=f"Notification sent: {message}",
            metadata={'notification_type': config.get('type', 'email')}
        )

        return {'notified': True}

    def _process_webhook_step(self, enrollment: SequenceEnrollment, step: SequenceStep) -> dict:
        """Call external webhook"""
        import requests

        config = step.config
        url = config.get('url')

        if not url:
            return {}

        payload = {
            'enrollment_id': str(enrollment.id),
            'contact_id': enrollment.contact_id,
            'sequence_id': str(enrollment.sequence_id),
            'step_id': str(step.id),
            'personalization_data': enrollment.personalization_data
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=config.get('headers', {}),
                timeout=10
            )
            response.raise_for_status()

            SequenceActivity.objects.create(
                enrollment=enrollment,
                step=step,
                activity_type='step_started',
                description=f"Webhook called: {url}",
                metadata={'status_code': response.status_code}
            )
        except Exception as e:
            logger.error(f"Webhook failed: {e}")

        return {'webhook_called': True}

    def _process_wait_step(self, enrollment: SequenceEnrollment, step: SequenceStep) -> dict:
        """Process wait step (just advances after wait time)"""
        return {}

    def _select_email_variant(self, step: SequenceStep) -> SequenceEmail | None:
        """Select email variant for A/B testing"""
        emails = list(step.emails.all())

        if not emails:
            return None

        if len(emails) == 1:
            return emails[0]

        # Check if there's a declared winner
        winner = next((e for e in emails if e.is_winner), None)
        if winner:
            return winner

        # Weighted random selection for A/B testing
        total_weight = sum(e.variant_weight for e in emails)
        r = random.randint(1, total_weight)

        cumulative = 0
        for email in emails:
            cumulative += email.variant_weight
            if r <= cumulative:
                return email

        return emails[0]

    def _personalize_content(self, content: str, data: dict[str, Any]) -> str:
        """Personalize content with token replacement"""
        if not content:
            return ''

        try:
            template = Template(content.replace('{', '{{').replace('}', '}}'))
            return template.render(Context(data))
        except Exception:
            # Fallback to simple replacement
            result = content
            for key, value in data.items():
                result = result.replace(f'{{{key}}}', str(value or ''))
            return result

    def _send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        body_html: str,
        body_text: str,
        enrollment: SequenceEnrollment,
        email: SequenceEmail
    ):
        """Send email via configured email backend"""
        from email_tracking.models import TrackedEmail

        # Create tracked email record
        tracked = TrackedEmail.objects.create(
            sender=enrollment.sequence.owner,
            from_email=settings.DEFAULT_FROM_EMAIL,
            from_name=enrollment.sequence.owner.get_full_name(),
            to_email=to_email,
            to_name=to_name,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            contact=enrollment.contact,
            status='sent',
            sent_at=timezone.now(),
            metadata={
                'sequence_id': str(enrollment.sequence_id),
                'step_id': str(enrollment.current_step_id),
                'email_variant': email.variant_name,
                'enrollment_id': str(enrollment.id)
            }
        )

        # Send actual email
        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email]
        )
        msg.attach_alternative(body_html, "text/html")
        msg.send()

        return tracked

    def _evaluate_condition(self, enrollment: SequenceEnrollment, step: SequenceStep) -> bool:
        """Evaluate step condition"""
        condition_type = step.condition_type
        config = step.condition_config

        evaluators = {
            'email_opened': self._check_email_opened,
            'email_clicked': self._check_email_clicked,
            'email_replied': self._check_email_replied,
            'lead_score_above': self._check_lead_score_above,
            'lead_score_below': self._check_lead_score_below,
            'has_tag': self._check_has_tag,
            'field_equals': self._check_field_equals,
        }

        evaluator = evaluators.get(condition_type)
        if evaluator:
            return evaluator(enrollment, config)

        return False

    def _check_email_opened(self, enrollment: SequenceEnrollment, config: dict) -> bool:
        """Check if previous email was opened"""
        # Check recent activities
        return SequenceActivity.objects.filter(
            enrollment=enrollment,
            activity_type='email_opened'
        ).exists()

    def _check_email_clicked(self, enrollment: SequenceEnrollment, config: dict) -> bool:
        """Check if any link was clicked"""
        return SequenceActivity.objects.filter(
            enrollment=enrollment,
            activity_type='email_clicked'
        ).exists()

    def _check_email_replied(self, enrollment: SequenceEnrollment, config: dict) -> bool:
        """Check if email was replied to"""
        return SequenceActivity.objects.filter(
            enrollment=enrollment,
            activity_type='email_replied'
        ).exists()

    def _check_lead_score_above(self, enrollment: SequenceEnrollment, config: dict) -> bool:
        """Check if lead score is above threshold"""
        if enrollment.lead:
            return enrollment.lead.lead_score >= config.get('threshold', 50)
        return False

    def _check_lead_score_below(self, enrollment: SequenceEnrollment, config: dict) -> bool:
        """Check if lead score is below threshold"""
        if enrollment.lead:
            return enrollment.lead.lead_score < config.get('threshold', 50)
        return True

    def _check_has_tag(self, enrollment: SequenceEnrollment, config: dict) -> bool:
        """Check if contact has a specific tag"""
        tag = config.get('tag')
        return tag in (enrollment.contact.tags or [])

    def _check_field_equals(self, enrollment: SequenceEnrollment, config: dict) -> bool:
        """Check if a field equals a value"""
        field = config.get('field')
        value = config.get('value')

        if hasattr(enrollment.contact, field):
            return getattr(enrollment.contact, field) == value
        return False

    def _should_exit(self, enrollment: SequenceEnrollment) -> bool:
        """Check if enrollment should exit"""
        exit_conditions = enrollment.sequence.exit_conditions

        # Check if contact replied
        if exit_conditions.get('on_reply') and enrollment.emails_replied > 0:
            return True

        # Check if converted
        if exit_conditions.get('on_conversion'):
            if enrollment.contact.contact_type == 'customer':
                return True

        # Check if unsubscribed
        if exit_conditions.get('on_unsubscribe'):
            # Check unsubscribe status
            pass

        return False

    def _advance_to_next_step(self, enrollment: SequenceEnrollment):
        """Advance enrollment to next step"""
        current_step = enrollment.current_step

        if not current_step:
            self._complete_enrollment(enrollment)
            return

        # Find next step
        next_step = enrollment.sequence.steps.filter(
            step_number__gt=current_step.step_number,
            is_active=True
        ).order_by('step_number').first()

        if next_step:
            enrollment.current_step = next_step
            enrollment.next_action_at = self._calculate_next_action_time(
                next_step,
                enrollment.sequence.settings
            )
            enrollment.save(update_fields=['current_step', 'next_action_at'])

            SequenceActivity.objects.create(
                enrollment=enrollment,
                step=next_step,
                activity_type='step_started',
                description=f"Advanced to step {next_step.step_number}"
            )
        else:
            self._complete_enrollment(enrollment)

    def _complete_enrollment(self, enrollment: SequenceEnrollment):
        """Mark enrollment as completed"""
        enrollment.status = 'completed'
        enrollment.completed_at = timezone.now()
        enrollment.next_action_at = None
        enrollment.save(update_fields=['status', 'completed_at', 'next_action_at'])

        # Update sequence stats
        enrollment.sequence.total_completed = F('total_completed') + 1
        enrollment.sequence.save(update_fields=['total_completed'])

        SequenceActivity.objects.create(
            enrollment=enrollment,
            activity_type='completed',
            description="Sequence completed"
        )

    def _exit_enrollment(self, enrollment: SequenceEnrollment, reason: str):
        """Exit enrollment before completion"""
        enrollment.status = 'exited'
        enrollment.exit_reason = reason
        enrollment.exited_at = timezone.now()
        enrollment.next_action_at = None
        enrollment.save(update_fields=['status', 'exit_reason', 'exited_at', 'next_action_at'])

        SequenceActivity.objects.create(
            enrollment=enrollment,
            activity_type='exited',
            description=f"Exited: {reason}"
        )

    def _calculate_next_action_time(
        self,
        step: SequenceStep | None,
        settings: dict
    ) -> datetime:
        """Calculate when next action should occur"""
        if not step:
            return None

        now = timezone.now()

        # Add step wait time
        wait_minutes = step.wait_total_minutes
        next_time = now + timedelta(minutes=wait_minutes)

        # Apply send window if configured
        send_window = settings.get('send_window', {})
        if send_window:
            next_time = self._apply_send_window(next_time, send_window)

        return next_time

    def _apply_send_window(self, dt: datetime, window: dict) -> datetime:
        """Apply send window restrictions"""
        start_hour = window.get('start_hour', 9)
        end_hour = window.get('end_hour', 17)
        allowed_days = window.get('days', [0, 1, 2, 3, 4])  # Mon-Fri default

        # Adjust if outside hours
        if dt.hour < start_hour:
            dt = dt.replace(hour=start_hour, minute=0)
        elif dt.hour >= end_hour:
            dt = (dt + timedelta(days=1)).replace(hour=start_hour, minute=0)

        # Adjust if not an allowed day
        while dt.weekday() not in allowed_days:
            dt = (dt + timedelta(days=1)).replace(hour=start_hour, minute=0)

        return dt

    def _build_personalization_data(self, contact, lead) -> dict[str, Any]:
        """Build personalization data dictionary"""
        data = {
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'full_name': contact.full_name,
            'email': contact.email,
            'company': contact.company_name,
            'company_name': contact.company_name,
            'job_title': contact.job_title,
            'phone': contact.phone,
            'city': contact.city,
            'state': contact.state,
            'country': contact.country,
        }

        if lead:
            data.update({
                'lead_source': lead.lead_source,
                'lead_score': lead.lead_score,
                'estimated_value': str(lead.estimated_value) if lead.estimated_value else '',
            })

        return data


class ABTestingService:
    """Service for managing A/B tests"""

    def create_test(
        self,
        step: SequenceStep,
        name: str,
        metric: str = 'open_rate',
        sample_size: int = 100,
        auto_select: bool = True
    ) -> ABTest:
        """Create a new A/B test"""
        return ABTest.objects.create(
            step=step,
            name=name,
            test_metric=metric,
            sample_size=sample_size,
            auto_select_winner=auto_select
        )

    def evaluate_test(self, test: ABTest) -> dict[str, Any]:
        """Evaluate A/B test results"""
        emails = test.step.emails.all()

        results = []
        for email in emails:
            metric_value = self._get_metric_value(email, test.test_metric)
            results.append({
                'variant': email.variant_name,
                'email_id': str(email.id),
                'total_sent': email.total_sent,
                test.test_metric: metric_value,
            })

        # Statistical significance check
        if len(results) >= 2 and all(r['total_sent'] >= test.sample_size / len(results) for r in results):
            winner = self._determine_winner(results, test.test_metric, test.confidence_level)

            test.results = {
                'variants': results,
                'winner': winner,
                'confidence': float(test.confidence_level)
            }
            test.save(update_fields=['results'])

            if winner and test.auto_select_winner:
                self._select_winner(test, winner)

        return {
            'status': test.status,
            'variants': results,
            'winner': test.results.get('winner'),
            'ready_to_declare': test.status == 'winner_selected'
        }

    def _get_metric_value(self, email: SequenceEmail, metric: str) -> float:
        """Get metric value for an email"""
        metrics = {
            'open_rate': email.open_rate,
            'click_rate': email.click_rate,
            'reply_rate': email.reply_rate,
        }
        return metrics.get(metric, 0)

    def _determine_winner(
        self,
        results: list[dict],
        metric: str,
        confidence: Decimal
    ) -> dict | None:
        """Determine winner using statistical significance"""
        if len(results) < 2:
            return None

        # Sort by metric value
        sorted_results = sorted(results, key=lambda x: x[metric], reverse=True)

        best = sorted_results[0]
        second = sorted_results[1]

        # Simple significance check (would use proper statistical test in production)
        if best[metric] > 0 and best[metric] > second[metric] * 1.1:
            return {
                'variant': best['variant'],
                'email_id': best['email_id'],
                'metric_value': best[metric],
                'improvement': ((best[metric] - second[metric]) / max(second[metric], 0.01)) * 100
            }

        return None

    def _select_winner(self, test: ABTest, winner: dict):
        """Select and apply winning variant"""
        winning_email = SequenceEmail.objects.get(id=winner['email_id'])

        # Mark as winner
        winning_email.is_winner = True
        winning_email.variant_weight = 100
        winning_email.save(update_fields=['is_winner', 'variant_weight'])

        # Reduce weight of losers
        test.step.emails.exclude(id=winner['email_id']).update(variant_weight=0)

        # Update test
        test.winning_variant = winning_email
        test.winner_selected_at = timezone.now()
        test.status = 'winner_selected'
        test.completed_at = timezone.now()
        test.save(update_fields=['winning_variant', 'winner_selected_at', 'status', 'completed_at'])


class TriggerEvaluationService:
    """Service for evaluating and executing automated triggers"""

    def __init__(self):
        self.execution_service = SequenceExecutionService()

    def evaluate_triggers(self, event_type: str, event_data: dict[str, Any]) -> list[str]:
        """Evaluate all active triggers for an event"""
        enrolled_sequences = []

        # Get matching triggers
        triggers = AutomatedTrigger.objects.filter(
            trigger_type=event_type,
            is_active=True
        ).select_related('sequence')

        for trigger in triggers:
            if self._matches_trigger(trigger, event_data):
                contact_id = event_data.get('contact_id')
                if contact_id:
                    try:
                        enrollment, created = self.execution_service.enroll_contact(
                            sequence_id=str(trigger.sequence_id),
                            contact_id=contact_id,
                            trigger=f"trigger_{trigger.id}",
                            lead_id=event_data.get('lead_id')
                        )

                        if created:
                            enrolled_sequences.append(str(trigger.sequence_id))

                            # Update trigger stats
                            trigger.total_triggered = F('total_triggered') + 1
                            trigger.total_enrolled = F('total_enrolled') + 1
                            trigger.last_triggered_at = timezone.now()
                            trigger.save(update_fields=['total_triggered', 'total_enrolled', 'last_triggered_at'])

                    except Exception as e:
                        logger.error(f"Failed to enroll from trigger {trigger.id}: {e}")

        return enrolled_sequences

    def _matches_trigger(self, trigger: AutomatedTrigger, event_data: dict) -> bool:
        """Check if event data matches trigger configuration"""
        config = trigger.trigger_config

        # Type-specific matching
        matchers = {
            'lead_score': self._match_lead_score,
            'stage_change': self._match_stage_change,
            'inactivity': self._match_inactivity,
            'form_submission': self._match_form_submission,
            'tag_change': self._match_tag_change,
            'field_change': self._match_field_change,
        }

        matcher = matchers.get(trigger.trigger_type)
        if matcher and not matcher(config, event_data):
            return False

        # Check additional conditions
        for condition in trigger.conditions:
            if not self._evaluate_condition(condition, event_data):
                return False

        # Check re-enrollment prevention
        if trigger.prevent_re_enrollment:
            contact_id = event_data.get('contact_id')
            if SequenceEnrollment.objects.filter(
                sequence=trigger.sequence,
                contact_id=contact_id
            ).exists():
                return False

        return True

    def _match_lead_score(self, config: dict, event_data: dict) -> bool:
        """Match lead score threshold"""
        threshold = config.get('threshold', 50)
        operator = config.get('operator', 'gte')
        score = event_data.get('lead_score', 0)

        if operator == 'gte':
            return score >= threshold
        elif operator == 'lte':
            return score <= threshold
        elif operator == 'eq':
            return score == threshold

        return False

    def _match_stage_change(self, config: dict, event_data: dict) -> bool:
        """Match deal stage change"""
        target_stage = config.get('stage')
        new_stage = event_data.get('new_stage')

        return new_stage == target_stage

    def _match_inactivity(self, config: dict, event_data: dict) -> bool:
        """Match inactivity period"""
        days = config.get('days', 7)
        last_activity = event_data.get('last_activity_at')

        if last_activity:
            inactive_days = (timezone.now() - last_activity).days
            return inactive_days >= days

        return False

    def _match_form_submission(self, config: dict, event_data: dict) -> bool:
        """Match form submission"""
        target_form = config.get('form_id')
        submitted_form = event_data.get('form_id')

        return target_form is None or target_form == submitted_form

    def _match_tag_change(self, config: dict, event_data: dict) -> bool:
        """Match tag added/removed"""
        target_tag = config.get('tag')
        added_tags = event_data.get('added_tags', [])
        removed_tags = event_data.get('removed_tags', [])

        action = config.get('action', 'added')

        if action == 'added':
            return target_tag in added_tags
        elif action == 'removed':
            return target_tag in removed_tags

        return False

    def _match_field_change(self, config: dict, event_data: dict) -> bool:
        """Match field value change"""
        field = config.get('field')
        target_value = config.get('value')
        new_value = event_data.get('new_value')

        if field != event_data.get('field'):
            return False

        if target_value is not None:
            return new_value == target_value

        return True

    def _evaluate_condition(self, condition: dict, event_data: dict) -> bool:
        """Evaluate a single condition"""
        field = condition.get('field')
        operator = condition.get('operator', 'eq')
        value = condition.get('value')

        actual_value = event_data.get(field)

        if operator == 'eq':
            return actual_value == value
        elif operator == 'neq':
            return actual_value != value
        elif operator == 'contains':
            return value in str(actual_value)
        elif operator == 'in':
            return actual_value in value

        return True


class AnalyticsService:
    """Service for sequence analytics"""

    def get_sequence_stats(self, sequence_id: str) -> dict[str, Any]:
        """Get comprehensive stats for a sequence"""
        sequence = EmailSequence.objects.get(id=sequence_id)

        enrollments = SequenceEnrollment.objects.filter(sequence=sequence)

        return {
            'sequence_id': str(sequence_id),
            'total_enrolled': sequence.total_enrolled,
            'total_completed': sequence.total_completed,
            'total_converted': sequence.total_converted,
            'active_enrollments': enrollments.filter(status='active').count(),
            'avg_open_rate': float(sequence.avg_open_rate),
            'avg_click_rate': float(sequence.avg_click_rate),
            'avg_reply_rate': float(sequence.avg_reply_rate),
            'conversion_rate': sequence.conversion_rate,
            'steps': self._get_step_stats(sequence),
        }

    def _get_step_stats(self, sequence: EmailSequence) -> list[dict]:
        """Get stats for each step"""
        stats = []

        for step in sequence.steps.all():
            step_stat = {
                'step_number': step.step_number,
                'name': step.name,
                'type': step.step_type,
                'total_executed': step.total_executed,
                'total_completed': step.total_completed,
            }

            if step.step_type == 'email':
                emails = step.emails.all()
                step_stat['email_variants'] = [
                    {
                        'variant': e.variant_name,
                        'total_sent': e.total_sent,
                        'open_rate': e.open_rate,
                        'click_rate': e.click_rate,
                        'reply_rate': e.reply_rate,
                    }
                    for e in emails
                ]

            stats.append(step_stat)

        return stats

    def record_daily_analytics(self, sequence_id: str):
        """Record daily analytics snapshot"""
        sequence = EmailSequence.objects.get(id=sequence_id)
        today = timezone.now().date()

        enrollments = SequenceEnrollment.objects.filter(sequence=sequence)
        emails = SequenceEmail.objects.filter(step__sequence=sequence)

        # Calculate daily metrics
        new_enrollments = enrollments.filter(enrolled_at__date=today).count()

        analytics, _ = SequenceAnalytics.objects.update_or_create(
            sequence=sequence,
            date=today,
            defaults={
                'new_enrollments': new_enrollments,
                'active_enrollments': enrollments.filter(status='active').count(),
                'completed_enrollments': enrollments.filter(
                    status='completed',
                    completed_at__date=today
                ).count(),
                'emails_sent': emails.aggregate(total=Count('total_sent'))['total'] or 0,
            }
        )

        return analytics
