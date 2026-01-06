"""
Lead Scoring Engine
Calculates lead scores based on rules and updates qualification stages
"""
import json
from datetime import timedelta

from django.utils import timezone

from .models import (
    LeadScore,
    QualificationCriteria,
    QualificationWorkflow,
    ScoringRule,
    WorkflowExecution,
)


class LeadScoringEngine:
    """Engine for calculating lead scores based on rules"""

    def __init__(self, lead):
        self.lead = lead
        self.score_breakdown = {
            'demographic': 0,
            'behavioral': 0,
            'firmographic': 0,
            'engagement': 0,
            'custom': 0
        }
        self.rules_applied = []

    def calculate_score(self):
        """Calculate total score for a lead"""
        rules = ScoringRule.objects.filter(is_active=True).order_by('-priority')

        total_score = 0
        for rule in rules:
            points = self._evaluate_rule(rule)
            if points:
                total_score += points
                self.score_breakdown[rule.rule_type] += points
                self.rules_applied.append({
                    'rule': rule.name,
                    'points': points,
                    'type': rule.rule_type
                })

        # Normalize score to 0-100
        normalized_score = max(0, min(100, total_score))

        # Save score history
        previous_scores = LeadScore.objects.filter(lead=self.lead).order_by('-calculated_at')
        previous_score = previous_scores.first().score if previous_scores.exists() else None

        lead_score = LeadScore.objects.create(
            lead=self.lead,
            score=normalized_score,
            previous_score=previous_score,
            score_breakdown=self.score_breakdown,
            demographic_score=self.score_breakdown['demographic'],
            behavioral_score=self.score_breakdown['behavioral'],
            firmographic_score=self.score_breakdown['firmographic'],
            engagement_score=self.score_breakdown['engagement'],
            qualification_stage=self._determine_stage(normalized_score)
        )

        # Update lead's current score
        self.lead.score = normalized_score
        self.lead.save(update_fields=['score'])

        # Check and execute workflows
        self._check_workflows(normalized_score, previous_score)

        return lead_score

    def _evaluate_rule(self, rule):
        """Evaluate a single scoring rule"""
        try:
            field_value = self._get_field_value(rule.field_name)
            rule_value = self._parse_value(rule.value)

            result = self._apply_operator(field_value, rule.operator, rule_value)
            return rule.points if result else 0
        except Exception as e:
            print(f"Error evaluating rule {rule.name}: {str(e)}")
            return 0

    def _get_field_value(self, field_name):
        """Get field value from lead or related objects"""
        # Check lead fields
        if hasattr(self.lead, field_name):
            return getattr(self.lead, field_name)

        # Check enrichment data
        enrichment = self.lead.enrichment_data.filter(is_verified=True).first()
        if enrichment and hasattr(enrichment, field_name):
            return getattr(enrichment, field_name)

        # Check engagement metrics (activities, emails, etc.)
        if field_name == 'email_opens_count':
            return self.lead.email_interactions.filter(opened=True).count()
        elif field_name == 'email_clicks_count':
            return self.lead.email_interactions.filter(clicked=True).count()
        elif field_name == 'activities_count':
            return self.lead.activities.count()
        elif field_name == 'days_since_creation':
            return (timezone.now() - self.lead.created_at).days
        elif field_name == 'last_activity_days_ago':
            last_activity = self.lead.activities.order_by('-created_at').first()
            if last_activity:
                return (timezone.now() - last_activity.created_at).days
            return 999

        return None

    def _apply_operator(self, field_value, operator, rule_value):
        """Apply comparison operator"""
        if field_value is None:
            return False

        if operator == 'equals':
            return field_value == rule_value
        elif operator == 'not_equals':
            return field_value != rule_value
        elif operator == 'contains':
            return rule_value in str(field_value).lower()
        elif operator == 'not_contains':
            return rule_value not in str(field_value).lower()
        elif operator == 'greater_than':
            return float(field_value) > float(rule_value)
        elif operator == 'less_than':
            return float(field_value) < float(rule_value)
        elif operator == 'in_list':
            return field_value in rule_value
        elif operator == 'not_in_list':
            return field_value not in rule_value
        elif operator == 'between':
            if isinstance(rule_value, list) and len(rule_value) == 2:
                return rule_value[0] <= float(field_value) <= rule_value[1]

        return False

    def _parse_value(self, value):
        """Parse rule value (handle JSON)"""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def _determine_stage(self, score):
        """Determine qualification stage based on score"""
        criteria = QualificationCriteria.objects.filter(
            is_active=True,
            minimum_score__lte=score
        ).order_by('-minimum_score').first()

        if criteria:
            return criteria.stage
        return 'unqualified'

    def _check_workflows(self, current_score, previous_score):
        """Check and execute qualification workflows"""
        workflows = QualificationWorkflow.objects.filter(
            is_active=True,
            trigger_type='score_threshold'
        ).order_by('-priority')

        for workflow in workflows:
            trigger_score = workflow.trigger_config.get('score', 0)

            # Check if score crossed threshold
            if current_score >= trigger_score:
                if previous_score is None or previous_score < trigger_score:
                    self._execute_workflow(workflow, {
                        'current_score': current_score,
                        'previous_score': previous_score,
                        'threshold': trigger_score
                    })

    def _execute_workflow(self, workflow, trigger_data):
        """Execute a qualification workflow"""
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            lead=self.lead,
            status='running',
            trigger_data=trigger_data
        )

        try:
            result = self._perform_action(workflow.action_type, workflow.action_config)

            execution.status = 'completed'
            execution.result_data = result
            execution.completed_at = timezone.now()
            execution.save()

            workflow.execution_count += 1
            workflow.last_executed_at = timezone.now()
            workflow.save(update_fields=['execution_count', 'last_executed_at'])

        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.completed_at = timezone.now()
            execution.save()

    def _perform_action(self, action_type, action_config):
        """Perform workflow action"""
        result = {}

        if action_type == 'assign_owner':
            owner_id = action_config.get('owner_id')
            if owner_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                owner = User.objects.get(id=owner_id)
                self.lead.assigned_to = owner
                self.lead.save(update_fields=['assigned_to'])
                result['assigned_to'] = owner.email

        elif action_type == 'change_status':
            new_status = action_config.get('status')
            if new_status:
                self.lead.status = new_status
                self.lead.save(update_fields=['status'])
                result['new_status'] = new_status

        elif action_type == 'create_task':
            from task_management.models import Task
            task = Task.objects.create(
                title=action_config.get('title', f'Follow up on {self.lead.name}'),
                description=action_config.get('description', ''),
                lead=self.lead,
                assigned_to=self.lead.assigned_to,
                due_date=timezone.now() + timedelta(days=action_config.get('due_in_days', 7)),
                priority=action_config.get('priority', 'medium')
            )
            result['task_id'] = task.id

        elif action_type == 'send_notification':
            # Create notification via activity feed
            from activity_feed.models import Notification
            if self.lead.assigned_to:
                Notification.objects.create(
                    user=self.lead.assigned_to,
                    notification_type='lead_qualified',
                    message=action_config.get('message', f'Lead {self.lead.name} has been qualified'),
                    metadata={'lead_id': self.lead.id}
                )
                result['notification_sent'] = True

        elif action_type == 'move_to_stage':
            new_stage = action_config.get('stage')
            if new_stage and hasattr(self.lead, 'stage'):
                self.lead.stage = new_stage
                self.lead.save(update_fields=['stage'])
                result['new_stage'] = new_stage

        elif action_type == 'update_field':
            field_name = action_config.get('field')
            field_value = action_config.get('value')
            if field_name and hasattr(self.lead, field_name):
                setattr(self.lead, field_name, field_value)
                self.lead.save(update_fields=[field_name])
                result['field_updated'] = field_name

        return result


class LeadQualificationChecker:
    """Check if lead meets qualification criteria"""

    @staticmethod
    def check_qualification(lead, stage):
        """Check if lead meets criteria for a stage"""
        criteria = QualificationCriteria.objects.filter(
            stage=stage,
            is_active=True
        ).first()

        if not criteria:
            return False, "No criteria defined for this stage"

        # Check score
        if lead.score < criteria.minimum_score:
            return False, f"Score {lead.score} below minimum {criteria.minimum_score}"

        # Check required fields
        for field_name in criteria.required_fields:
            if not getattr(lead, field_name, None):
                return False, f"Required field '{field_name}' is missing"

        # Check time constraint
        if criteria.time_constraint_days:
            days_since_creation = (timezone.now() - lead.created_at).days
            if days_since_creation > criteria.time_constraint_days:
                return False, f"Lead is too old ({days_since_creation} days)"

        # Check required actions
        for action in criteria.required_actions:
            if not LeadQualificationChecker._check_action(lead, action):
                return False, f"Required action '{action}' not completed"

        return True, "All criteria met"

    @staticmethod
    def _check_action(lead, action):
        """Check if lead has completed a specific action"""
        if action == 'email_opened':
            return lead.email_interactions.filter(opened=True).exists()
        elif action == 'email_clicked':
            return lead.email_interactions.filter(clicked=True).exists()
        elif action == 'form_submitted':
            return lead.activities.filter(activity_type='form_submission').exists()
        elif action == 'website_visited':
            return lead.activities.filter(activity_type='website_visit').exists()
        elif action == 'demo_requested':
            return lead.activities.filter(activity_type='demo_request').exists()

        return False


def recalculate_all_leads():
    """Utility function to recalculate scores for all leads"""
    from lead_management.models import Lead

    leads = Lead.objects.all()
    results = {
        'total': leads.count(),
        'success': 0,
        'failed': 0,
        'errors': []
    }

    for lead in leads:
        try:
            engine = LeadScoringEngine(lead)
            engine.calculate_score()
            results['success'] += 1
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"Lead {lead.id}: {str(e)}")

    return results
