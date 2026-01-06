"""
Workflow Automation Engine
Automates business processes with triggers and actions
"""

import json
import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

User = get_user_model()
logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Central workflow automation engine"""

    @staticmethod
    def execute_workflow(workflow, trigger_data=None):
        """Execute a workflow with given trigger data"""
        from .models import WorkflowExecution

        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            trigger_data=trigger_data or {},
            total_steps=len(workflow.actions),
            status='running'
        )

        try:
            for idx, action in enumerate(workflow.actions):
                WorkflowEngine._execute_action(action, trigger_data, execution)
                execution.steps_completed = idx + 1
                execution.save()

            execution.status = 'completed'
            execution.completed_at = timezone.now()
            execution.save()

            logger.info(f"Workflow {workflow.name} completed successfully")
            return True

        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.completed_at = timezone.now()
            execution.save()

            logger.error(f"Workflow {workflow.name} failed: {str(e)}")
            return False

    @staticmethod
    def _execute_action(action, trigger_data, execution):
        """Execute a single workflow action"""
        action_type = action.get('type')
        action_params = action.get('params', {})

        # Add to execution log
        log_entry = {
            'timestamp': timezone.now().isoformat(),
            'action_type': action_type,
            'params': action_params
        }

        try:
            if action_type == 'send_email':
                WorkflowActions.send_email(action_params, trigger_data)
            elif action_type == 'create_task':
                WorkflowActions.create_task(action_params, trigger_data)
            elif action_type == 'update_field':
                WorkflowActions.update_field(action_params, trigger_data)
            elif action_type == 'assign_record':
                WorkflowActions.assign_record(action_params, trigger_data)
            elif action_type == 'send_notification':
                WorkflowActions.send_notification(action_params, trigger_data)
            elif action_type == 'create_record':
                WorkflowActions.create_record(action_params, trigger_data)
            elif action_type == 'webhook':
                WorkflowActions.call_webhook(action_params, trigger_data)
            elif action_type == 'wait':
                WorkflowActions.wait(action_params)
            else:
                raise ValueError(f"Unknown action type: {action_type}")

            log_entry['status'] = 'success'

        except Exception as e:
            log_entry['status'] = 'failed'
            log_entry['error'] = str(e)
            raise

        finally:
            # Update execution log
            execution.execution_log.append(log_entry)
            execution.save()

    @staticmethod
    def check_trigger_conditions(workflow, record, field_changes=None):
        """Check if trigger conditions are met"""
        conditions = workflow.trigger_conditions

        if not conditions:
            return True

        # Evaluate each condition
        for condition in conditions.get('rules', []):
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')

            if not WorkflowEngine._evaluate_condition(record, field, operator, value, field_changes):
                return False

        return True

    @staticmethod
    def _evaluate_condition(record, field, operator, value, field_changes=None):
        """Evaluate a single condition"""
        record_value = getattr(record, field, None)

        if operator == 'equals':
            return record_value == value
        elif operator == 'not_equals':
            return record_value != value
        elif operator == 'contains':
            return value in str(record_value)
        elif operator == 'greater_than':
            return record_value > value
        elif operator == 'less_than':
            return record_value < value
        elif operator == 'changed':
            return field_changes and field in field_changes
        elif operator == 'changed_to':
            return field_changes and field in field_changes and field_changes[field]['new'] == value
        elif operator == 'is_empty':
            return not record_value
        elif operator == 'is_not_empty':
            return bool(record_value)

        return False


class WorkflowActions:
    """Collection of workflow actions"""

    @staticmethod
    def send_email(params, trigger_data):
        """Send email action"""
        recipient = params.get('recipient')
        subject = WorkflowActions._replace_variables(params.get('subject'), trigger_data)
        message = WorkflowActions._replace_variables(params.get('message'), trigger_data)

        send_mail(
            subject=subject,
            message=message,
            from_email='noreply@mycrm.com',
            recipient_list=[recipient],
            fail_silently=False
        )

        logger.info(f"Email sent to {recipient}")

    @staticmethod
    def create_task(params, trigger_data):
        """Create task action"""
        from task_management.models import Task

        title = WorkflowActions._replace_variables(params.get('title'), trigger_data)
        description = WorkflowActions._replace_variables(params.get('description', ''), trigger_data)
        assigned_to_id = params.get('assigned_to')
        priority = params.get('priority', 'medium')
        due_date = params.get('due_date')

        task = Task.objects.create(
            title=title,
            description=description,
            assigned_to_id=assigned_to_id,
            priority=priority,
            due_date=due_date,
            status='pending'
        )

        logger.info(f"Task created: {task.title}")

    @staticmethod
    def update_field(params, trigger_data):
        """Update field action"""
        model_name = params.get('model')
        record_id = trigger_data.get('record_id')
        field = params.get('field')
        value = WorkflowActions._replace_variables(params.get('value'), trigger_data)

        # Get model class dynamically
        from django.apps import apps
        model = apps.get_model(model_name)

        record = model.objects.get(pk=record_id)
        setattr(record, field, value)
        record.save()

        logger.info(f"Updated {field} on {model_name} {record_id}")

    @staticmethod
    def assign_record(params, trigger_data):
        """Assign record action"""
        model_name = params.get('model')
        record_id = trigger_data.get('record_id')
        user_id = params.get('user_id')

        from django.apps import apps
        model = apps.get_model(model_name)

        record = model.objects.get(pk=record_id)
        if hasattr(record, 'assigned_to'):
            record.assigned_to_id = user_id
            record.save()
            logger.info(f"Assigned {model_name} {record_id} to user {user_id}")

    @staticmethod
    def send_notification(params, trigger_data):
        """Send in-app notification action"""
        from .models import Notification

        user_id = params.get('user_id')
        title = WorkflowActions._replace_variables(params.get('title'), trigger_data)
        message = WorkflowActions._replace_variables(params.get('message'), trigger_data)
        notification_type = params.get('notification_type', 'info')

        Notification.objects.create(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type
        )

        logger.info(f"Notification sent to user {user_id}")

    @staticmethod
    def create_record(params, trigger_data):
        """Create new record action"""
        model_name = params.get('model')
        fields = params.get('fields', {})

        # Replace variables in field values
        for field, value in fields.items():
            if isinstance(value, str):
                fields[field] = WorkflowActions._replace_variables(value, trigger_data)

        from django.apps import apps
        model = apps.get_model(model_name)

        record = model.objects.create(**fields)
        logger.info(f"Created {model_name} record: {record.pk}")

    @staticmethod
    def call_webhook(params, trigger_data):
        """Call external webhook action"""
        import requests

        url = params.get('url')
        method = params.get('method', 'POST')
        headers = params.get('headers', {})
        payload = params.get('payload', {})

        # Replace variables in payload
        payload_str = json.dumps(payload)
        payload_str = WorkflowActions._replace_variables(payload_str, trigger_data)
        payload = json.loads(payload_str)

        response = requests.request(
            method=method,
            url=url,
            json=payload,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()
        logger.info(f"Webhook called: {url} - Status: {response.status_code}")

    @staticmethod
    def wait(params):
        """Wait/delay action"""
        import time
        seconds = params.get('seconds', 0)
        time.sleep(seconds)
        logger.info(f"Waited for {seconds} seconds")

    @staticmethod
    def _replace_variables(text, trigger_data):
        """Replace variables in text with actual values from trigger data"""
        if not isinstance(text, str):
            return text

        for key, value in trigger_data.items():
            placeholder = f"{{{{{key}}}}}"  # {{variable_name}}
            text = text.replace(placeholder, str(value))

        return text


@shared_task
def execute_workflow_async(workflow_id, trigger_data=None):
    """Execute workflow asynchronously using Celery"""
    from .models import Workflow

    try:
        workflow = Workflow.objects.get(id=workflow_id, status='active')
        WorkflowEngine.execute_workflow(workflow, trigger_data)
    except Workflow.DoesNotExist:
        logger.error(f"Workflow {workflow_id} not found or inactive")
    except Exception as e:
        logger.error(f"Error executing workflow {workflow_id}: {str(e)}")


class WorkflowTriggerManager:
    """Manages workflow triggers"""

    @staticmethod
    def on_record_created(model_name, record):
        """Trigger workflows when a record is created"""
        from .models import Workflow

        workflows = Workflow.objects.filter(
            trigger_type='record_created',
            status='active'
        )

        trigger_data = {
            'model': model_name,
            'record_id': record.pk,
            'action': 'created'
        }

        for workflow in workflows:
            if WorkflowEngine.check_trigger_conditions(workflow, record):
                execute_workflow_async.delay(str(workflow.id), trigger_data)

    @staticmethod
    def on_record_updated(model_name, record, field_changes=None):
        """Trigger workflows when a record is updated"""
        from .models import Workflow

        workflows = Workflow.objects.filter(
            trigger_type__in=['record_updated', 'field_changed'],
            status='active'
        )

        trigger_data = {
            'model': model_name,
            'record_id': record.pk,
            'action': 'updated',
            'changes': field_changes or {}
        }

        for workflow in workflows:
            if WorkflowEngine.check_trigger_conditions(workflow, record, field_changes):
                execute_workflow_async.delay(str(workflow.id), trigger_data)
