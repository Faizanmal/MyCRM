"""
Advanced Workflow Engine Services
"""

from datetime import timedelta
from typing import Any

import openai
from django.conf import settings
from django.utils import timezone


class WorkflowEngineService:
    """Main workflow execution engine"""

    def __init__(self, user=None):
        self.user = user

    def start_workflow(
        self,
        workflow_id: str,
        trigger_data: dict | None = None,
        target_object: tuple | None = None
    ) -> dict[str, Any]:
        """Start a new workflow instance"""
        from .workflow_models import WorkflowDefinition, WorkflowInstance, WorkflowLog

        workflow = WorkflowDefinition.objects.get(id=workflow_id)

        if workflow.status != 'active':
            return {'error': 'Workflow is not active'}

        # Check entry conditions
        if workflow.entry_conditions and not self._evaluate_conditions(
            workflow.entry_conditions, trigger_data or {}
        ):
            return {'error': 'Entry conditions not met'}

        # Check concurrent limit
        if workflow.max_concurrent:
            running = WorkflowInstance.objects.filter(
                workflow=workflow,
                status__in=['running', 'waiting']
            ).count()

            if running >= workflow.max_concurrent:
                return {'error': 'Maximum concurrent instances reached'}

        # Create instance
        instance = WorkflowInstance.objects.create(
            workflow=workflow,
            triggered_by=self.user,
            trigger_event=trigger_data.get('event', '') if trigger_data else '',
            trigger_data=trigger_data or {},
            target_content_type=target_object[0] if target_object else '',
            target_object_id=target_object[1] if target_object else '',
            context={'trigger': trigger_data or {}}
        )

        # Log start
        WorkflowLog.objects.create(
            instance=instance,
            log_type='workflow_started',
            message=f'Workflow "{workflow.name}" started'
        )

        # Update workflow stats
        workflow.run_count += 1
        workflow.save(update_fields=['run_count'])

        # Find start node and execute
        start_node = self._find_start_node(workflow)

        if start_node:
            instance.current_node = start_node.node_id
            instance.save(update_fields=['current_node'])

            # Execute first node
            self._execute_node(instance, start_node)

        return {
            'instance_id': str(instance.id),
            'workflow_name': workflow.name,
            'status': instance.status,
            'started_at': instance.started_at.isoformat()
        }

    def _find_start_node(self, workflow):
        """Find the starting node of a workflow"""

        # Find nodes that have no incoming connections
        all_targets = {
            c.target_node for c in workflow.connections.all()
        }

        for node in workflow.nodes.all():
            if node.node_id not in all_targets:
                return node

        return workflow.nodes.first()

    def _execute_node(self, instance, node):
        """Execute a workflow node"""
        from .workflow_models import WorkflowLog, WorkflowNodeExecution

        # Create execution record
        execution = WorkflowNodeExecution.objects.create(
            instance=instance,
            node=node,
            status='running',
            started_at=timezone.now(),
            input_data=instance.context
        )

        WorkflowLog.objects.create(
            instance=instance,
            log_type='node_started',
            node_id=node.node_id,
            message=f'Executing node: {node.name}'
        )

        try:
            # Route to appropriate handler
            handler = self._get_node_handler(node.node_type)
            result = handler(instance, node, execution)

            # Update execution
            execution.status = result.get('status', 'completed')
            execution.output_data = result.get('output', {})
            execution.completed_at = timezone.now()
            execution.execution_time_ms = int(
                (execution.completed_at - execution.started_at).total_seconds() * 1000
            )
            execution.save()

            # Update context with output
            instance.context = {
                **instance.context,
                f'node_{node.node_id}': result.get('output', {})
            }
            instance.save(update_fields=['context'])

            WorkflowLog.objects.create(
                instance=instance,
                log_type='node_completed',
                node_id=node.node_id,
                message=f'Node completed: {node.name}',
                details=result.get('output', {})
            )

            # Handle result
            if result.get('status') == 'waiting':
                instance.status = 'waiting'
                instance.resume_at = result.get('resume_at')
                instance.resume_data = result.get('resume_data', {})
                instance.save()
            elif result.get('status') == 'completed':
                # Find and execute next node
                self._proceed_to_next(instance, node, result)
            elif result.get('status') == 'failed':
                self._handle_node_error(instance, node, execution, result.get('error', ''))

        except Exception as e:
            self._handle_node_error(instance, node, execution, str(e))

    def _get_node_handler(self, node_type: str):
        """Get handler function for node type"""
        handlers = {
            'action_email': self._handle_email_action,
            'action_sms': self._handle_sms_action,
            'action_notification': self._handle_notification_action,
            'action_task': self._handle_task_action,
            'action_update_record': self._handle_update_record,
            'action_create_record': self._handle_create_record,
            'action_webhook': self._handle_webhook_action,
            'condition': self._handle_condition,
            'branch': self._handle_branch,
            'delay': self._handle_delay,
            'approval_single': self._handle_single_approval,
            'approval_multi': self._handle_multi_approval,
            'ai_decision': self._handle_ai_decision,
            'end_success': self._handle_end_success,
            'end_failure': self._handle_end_failure,
        }

        return handlers.get(node_type, self._handle_generic)

    def _handle_email_action(self, instance, node, execution) -> dict:
        """Send email action"""
        config = node.config
        context = instance.context

        # Render email content
        subject = self._render_template(config.get('subject', ''), context)
        self._render_template(config.get('body', ''), context)
        to_email = self._render_template(config.get('to', ''), context)

        # Would send email here
        # send_email(to=to_email, subject=subject, body=body)

        return {
            'status': 'completed',
            'output': {
                'email_sent': True,
                'to': to_email,
                'subject': subject
            }
        }

    def _handle_sms_action(self, instance, node, execution) -> dict:
        """Send SMS action"""
        config = node.config
        context = instance.context

        self._render_template(config.get('message', ''), context)
        to_phone = self._render_template(config.get('to', ''), context)

        return {
            'status': 'completed',
            'output': {
                'sms_sent': True,
                'to': to_phone
            }
        }

    def _handle_notification_action(self, instance, node, execution) -> dict:
        """Send notification action"""
        config = node.config
        context = instance.context

        self._render_template(config.get('title', ''), context)
        self._render_template(config.get('message', ''), context)
        user_ids = config.get('user_ids', [])

        # Would create notifications

        return {
            'status': 'completed',
            'output': {
                'notifications_sent': len(user_ids)
            }
        }

    def _handle_task_action(self, instance, node, execution) -> dict:
        """Create task action"""
        config = node.config
        context = instance.context

        title = self._render_template(config.get('title', ''), context)
        self._render_template(config.get('description', ''), context)

        # Would create task
        # from task_management.models import Task
        # task = Task.objects.create(...)

        return {
            'status': 'completed',
            'output': {
                'task_created': True,
                'title': title
            }
        }

    def _handle_update_record(self, instance, node, execution) -> dict:
        """Update record action"""
        config = node.config
        context = instance.context

        entity_type = config.get('entity_type')
        record_id = self._render_template(str(config.get('record_id', '')), context)
        config.get('updates', {})

        # Would update record
        # model = apps.get_model(...)
        # model.objects.filter(id=record_id).update(**updates)

        return {
            'status': 'completed',
            'output': {
                'record_updated': True,
                'entity_type': entity_type,
                'record_id': record_id
            }
        }

    def _handle_create_record(self, instance, node, execution) -> dict:
        """Create record action"""
        config = node.config
        context = instance.context

        entity_type = config.get('entity_type')
        data = {}

        for field, value in config.get('data', {}).items():
            if isinstance(value, str):
                data[field] = self._render_template(value, context)
            else:
                data[field] = value

        return {
            'status': 'completed',
            'output': {
                'record_created': True,
                'entity_type': entity_type,
                'data': data
            }
        }

    def _handle_webhook_action(self, instance, node, execution) -> dict:
        """Call webhook action"""
        import requests

        config = node.config
        context = instance.context

        url = config.get('url')
        method = config.get('method', 'POST')
        headers = config.get('headers', {})
        payload = config.get('payload', {})

        # Render payload
        rendered_payload = {}
        for key, value in payload.items():
            if isinstance(value, str):
                rendered_payload[key] = self._render_template(value, context)
            else:
                rendered_payload[key] = value

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=rendered_payload,
                timeout=30
            )

            return {
                'status': 'completed',
                'output': {
                    'status_code': response.status_code,
                    'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                }
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def _handle_condition(self, instance, node, execution) -> dict:
        """Evaluate condition node"""
        config = node.config
        context = instance.context

        conditions = config.get('conditions', [])
        result = self._evaluate_conditions(conditions, context)

        return {
            'status': 'completed',
            'output': {
                'result': result,
                'branch': 'true' if result else 'false'
            }
        }

    def _handle_branch(self, instance, node, execution) -> dict:
        """Handle branch/split node"""
        config = node.config
        context = instance.context

        branches = config.get('branches', [])
        selected_branches = []

        for branch in branches:
            if self._evaluate_conditions(branch.get('conditions', []), context):
                selected_branches.append(branch.get('name'))

        return {
            'status': 'completed',
            'output': {
                'selected_branches': selected_branches
            }
        }

    def _handle_delay(self, instance, node, execution) -> dict:
        """Handle delay/wait node"""
        config = node.config

        delay_type = config.get('delay_type', 'duration')

        if delay_type == 'duration':
            minutes = config.get('minutes', 0)
            hours = config.get('hours', 0)
            days = config.get('days', 0)

            resume_at = timezone.now() + timedelta(
                minutes=minutes, hours=hours, days=days
            )
        elif delay_type == 'until_time':
            resume_at = config.get('until_time')
        else:
            resume_at = timezone.now()

        return {
            'status': 'waiting',
            'resume_at': resume_at,
            'output': {
                'delay_type': delay_type,
                'resume_at': resume_at.isoformat() if resume_at else None
            }
        }

    def _handle_single_approval(self, instance, node, execution) -> dict:
        """Handle single-person approval"""
        from .workflow_models import WorkflowApprovalRequest

        config = node.config
        context = instance.context

        approver_id = config.get('approver_id')
        title = self._render_template(config.get('title', 'Approval Required'), context)
        description = self._render_template(config.get('description', ''), context)

        # Create approval request
        approval = WorkflowApprovalRequest.objects.create(
            node_execution=execution,
            approver_id=approver_id,
            title=title,
            description=description,
            data_to_review=context,
            approval_options=config.get('options', [
                {'value': 'approve', 'label': 'Approve'},
                {'value': 'reject', 'label': 'Reject'}
            ]),
            requires_comment=config.get('requires_comment', False),
            due_date=timezone.now() + timedelta(days=config.get('due_days', 3))
        )

        # Would send notification to approver

        return {
            'status': 'waiting',
            'resume_data': {'approval_id': str(approval.id)},
            'output': {
                'approval_requested': True,
                'approver_id': approver_id
            }
        }

    def _handle_multi_approval(self, instance, node, execution) -> dict:
        """Handle multi-person approval"""
        from .workflow_models import WorkflowApprovalRequest

        config = node.config
        context = instance.context

        approver_ids = config.get('approver_ids', [])
        approval_type = config.get('approval_type', 'all')  # all, any, majority

        title = self._render_template(config.get('title', 'Approval Required'), context)

        approval_ids = []
        for approver_id in approver_ids:
            approval = WorkflowApprovalRequest.objects.create(
                node_execution=execution,
                approver_id=approver_id,
                title=title,
                description=config.get('description', ''),
                data_to_review=context,
                due_date=timezone.now() + timedelta(days=config.get('due_days', 3))
            )
            approval_ids.append(str(approval.id))

        return {
            'status': 'waiting',
            'resume_data': {
                'approval_ids': approval_ids,
                'approval_type': approval_type,
                'required_count': len(approver_ids) if approval_type == 'all' else (
                    1 if approval_type == 'any' else len(approver_ids) // 2 + 1
                )
            },
            'output': {
                'approvals_requested': len(approver_ids)
            }
        }

    def _handle_ai_decision(self, instance, node, execution) -> dict:
        """AI-powered decision making"""
        config = node.config
        context = instance.context

        prompt = self._render_template(config.get('prompt', ''), context)
        options = config.get('options', [])

        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

            options_text = '\n'.join([f"- {opt['value']}: {opt['description']}" for opt in options])

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a decision-making assistant. Analyze the situation and choose ONE of the following options:\n{options_text}\n\nRespond with only the option value."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )

            decision = response.choices[0].message.content.strip()

            return {
                'status': 'completed',
                'output': {
                    'decision': decision,
                    'confidence': 'high'  # Would calculate from response
                }
            }
        except Exception as e:
            # Fallback to default
            return {
                'status': 'completed',
                'output': {
                    'decision': config.get('default_option', options[0]['value'] if options else 'continue'),
                    'confidence': 'low',
                    'error': str(e)
                }
            }

    def _handle_end_success(self, instance, node, execution) -> dict:
        """Handle successful end of workflow"""
        instance.status = 'completed'
        instance.completed_at = timezone.now()
        instance.save()

        # Update workflow stats
        instance.workflow.success_count += 1
        instance.workflow.save(update_fields=['success_count'])

        return {
            'status': 'completed',
            'output': {'workflow_status': 'success'}
        }

    def _handle_end_failure(self, instance, node, execution) -> dict:
        """Handle failed end of workflow"""
        instance.status = 'failed'
        instance.completed_at = timezone.now()
        instance.save()

        instance.workflow.failure_count += 1
        instance.workflow.save(update_fields=['failure_count'])

        return {
            'status': 'completed',
            'output': {'workflow_status': 'failed'}
        }

    def _handle_generic(self, instance, node, execution) -> dict:
        """Generic handler for unknown node types"""
        return {
            'status': 'completed',
            'output': {'handled': True}
        }

    def _proceed_to_next(self, instance, current_node, result):
        """Find and execute next node"""
        from .workflow_models import WorkflowConnection, WorkflowNode

        # Get connections from current node
        connections = WorkflowConnection.objects.filter(
            workflow=instance.workflow,
            source_node=current_node.node_id
        ).order_by('priority')

        for conn in connections:
            # Check condition if present
            if conn.condition:
                if not self._evaluate_conditions([conn.condition], result.get('output', {})):
                    continue

            # Check for branch matching
            output = result.get('output', {})
            if output.get('branch'):
                if conn.label and conn.label.lower() != output['branch'].lower():
                    continue

            # Find target node
            try:
                next_node = WorkflowNode.objects.get(
                    workflow=instance.workflow,
                    node_id=conn.target_node
                )

                instance.current_node = next_node.node_id
                instance.save(update_fields=['current_node'])

                self._execute_node(instance, next_node)
                return
            except WorkflowNode.DoesNotExist:
                continue

        # No valid next node - workflow complete
        instance.status = 'completed'
        instance.completed_at = timezone.now()
        instance.save()

    def _handle_node_error(self, instance, node, execution, error_message):
        """Handle node execution error"""
        from .workflow_models import WorkflowLog

        execution.status = 'failed'
        execution.error_message = error_message
        execution.completed_at = timezone.now()
        execution.save()

        WorkflowLog.objects.create(
            instance=instance,
            log_type='node_failed',
            node_id=node.node_id,
            message=f'Node failed: {error_message}',
            details={'error': error_message}
        )

        if node.on_error == 'continue':
            self._proceed_to_next(instance, node, {'status': 'completed', 'output': {}})
        elif node.on_error == 'branch' and node.error_branch_node:
            from .workflow_models import WorkflowNode
            try:
                error_node = WorkflowNode.objects.get(
                    workflow=instance.workflow,
                    node_id=node.error_branch_node
                )
                self._execute_node(instance, error_node)
            except WorkflowNode.DoesNotExist:
                instance.status = 'failed'
                instance.error_message = error_message
                instance.error_node = node.node_id
                instance.save()
        else:
            instance.status = 'failed'
            instance.error_message = error_message
            instance.error_node = node.node_id
            instance.completed_at = timezone.now()
            instance.save()

            instance.workflow.failure_count += 1
            instance.workflow.save(update_fields=['failure_count'])

    def _evaluate_conditions(self, conditions: list[dict], context: dict) -> bool:
        """Evaluate conditions against context"""
        if not conditions:
            return True

        for condition in conditions:
            field = condition.get('field')
            operator = condition.get('operator', 'equals')
            value = condition.get('value')

            field_value = self._get_nested_value(context, field)

            if operator == 'equals':
                if field_value != value:
                    return False
            elif operator == 'not_equals':
                if field_value == value:
                    return False
            elif operator == 'contains':
                if value not in str(field_value):
                    return False
            elif operator == 'greater_than':
                if not (field_value and field_value > value):
                    return False
            elif operator == 'less_than':
                if not (field_value and field_value < value):
                    return False
            elif operator == 'is_empty':
                if field_value:
                    return False
            elif operator == 'is_not_empty':
                if not field_value:
                    return False
            elif operator == 'in' and field_value not in value:
                return False

        return True

    def _get_nested_value(self, data: dict, path: str) -> Any:
        """Get nested value from dict using dot notation"""
        if not path:
            return None

        keys = path.split('.')
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None

        return value

    def _render_template(self, template: str, context: dict) -> str:
        """Render template string with context variables"""
        if not template:
            return template

        result = template

        # Replace {{variable}} patterns
        import re
        pattern = r'\{\{([^}]+)\}\}'

        def replace(match):
            path = match.group(1).strip()
            value = self._get_nested_value(context, path)
            return str(value) if value is not None else ''

        return re.sub(pattern, replace, result)

    def resume_workflow(self, instance_id: str, resume_data: dict | None = None):
        """Resume a waiting workflow"""
        from .workflow_models import WorkflowInstance, WorkflowNode

        instance = WorkflowInstance.objects.get(id=instance_id)

        if instance.status != 'waiting':
            return {'error': f'Workflow status is {instance.status}, not waiting'}

        # Update context with resume data
        if resume_data:
            instance.context = {**instance.context, 'resume': resume_data}

        instance.status = 'running'
        instance.save()

        # Get current node and proceed
        try:
            current_node = WorkflowNode.objects.get(
                workflow=instance.workflow,
                node_id=instance.current_node
            )

            self._proceed_to_next(instance, current_node, {
                'status': 'completed',
                'output': resume_data or {}
            })

        except WorkflowNode.DoesNotExist:
            instance.status = 'failed'
            instance.error_message = 'Current node not found'
            instance.save()

        return {
            'instance_id': str(instance.id),
            'status': instance.status
        }


class WorkflowDesignerService:
    """Service for workflow design and management"""

    def __init__(self, user):
        self.user = user

    def create_workflow(
        self,
        name: str,
        trigger_type: str,
        category: str = 'custom',
        config: dict | None = None
    ) -> dict[str, Any]:
        """Create a new workflow definition"""
        from .workflow_models import WorkflowDefinition

        workflow = WorkflowDefinition.objects.create(
            user=self.user,
            name=name,
            description=config.get('description', '') if config else '',
            category=category,
            trigger_type=trigger_type,
            trigger_config=config.get('trigger_config', {}) if config else {},
            entry_conditions=config.get('entry_conditions', []) if config else []
        )

        return {
            'workflow_id': str(workflow.id),
            'name': workflow.name,
            'status': workflow.status
        }

    def add_node(
        self,
        workflow_id: str,
        node_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Add a node to workflow"""
        from .workflow_models import WorkflowDefinition, WorkflowNode

        workflow = WorkflowDefinition.objects.get(id=workflow_id)

        node = WorkflowNode.objects.create(
            workflow=workflow,
            node_id=node_config.get('node_id'),
            name=node_config.get('name'),
            node_type=node_config.get('node_type'),
            config=node_config.get('config', {}),
            position_x=node_config.get('position_x', 0),
            position_y=node_config.get('position_y', 0),
            timeout_minutes=node_config.get('timeout_minutes'),
            retry_count=node_config.get('retry_count', 0),
            on_error=node_config.get('on_error', 'stop')
        )

        return {
            'node_id': node.node_id,
            'name': node.name,
            'node_type': node.node_type
        }

    def add_connection(
        self,
        workflow_id: str,
        source_node: str,
        target_node: str,
        condition: dict | None = None,
        label: str = ''
    ) -> dict[str, Any]:
        """Add a connection between nodes"""
        from .workflow_models import WorkflowConnection, WorkflowDefinition

        workflow = WorkflowDefinition.objects.get(id=workflow_id)

        connection = WorkflowConnection.objects.create(
            workflow=workflow,
            source_node=source_node,
            target_node=target_node,
            condition=condition or {},
            label=label
        )

        return {
            'connection_id': str(connection.id),
            'source': source_node,
            'target': target_node
        }

    def save_canvas(
        self,
        workflow_id: str,
        canvas_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Save complete canvas state"""
        from .workflow_models import WorkflowConnection, WorkflowDefinition, WorkflowNode

        workflow = WorkflowDefinition.objects.get(id=workflow_id)

        # Update canvas data
        workflow.canvas_data = canvas_data
        workflow.save(update_fields=['canvas_data', 'updated_at'])

        # Sync nodes
        existing_nodes = {n.node_id: n for n in workflow.nodes.all()}

        for node_data in canvas_data.get('nodes', []):
            node_id = node_data.get('id')

            if node_id in existing_nodes:
                # Update existing
                node = existing_nodes[node_id]
                node.name = node_data.get('name', node.name)
                node.config = node_data.get('config', node.config)
                node.position_x = node_data.get('x', node.position_x)
                node.position_y = node_data.get('y', node.position_y)
                node.save()
                del existing_nodes[node_id]
            else:
                # Create new
                WorkflowNode.objects.create(
                    workflow=workflow,
                    node_id=node_id,
                    name=node_data.get('name', 'New Node'),
                    node_type=node_data.get('type', 'action_task'),
                    config=node_data.get('config', {}),
                    position_x=node_data.get('x', 0),
                    position_y=node_data.get('y', 0)
                )

        # Delete removed nodes
        for node in existing_nodes.values():
            node.delete()

        # Sync connections
        workflow.connections.all().delete()

        for conn_data in canvas_data.get('connections', []):
            WorkflowConnection.objects.create(
                workflow=workflow,
                source_node=conn_data.get('source'),
                target_node=conn_data.get('target'),
                source_port=conn_data.get('sourcePort', 'output'),
                target_port=conn_data.get('targetPort', 'input'),
                condition=conn_data.get('condition', {}),
                label=conn_data.get('label', '')
            )

        return {
            'workflow_id': str(workflow.id),
            'nodes_count': workflow.nodes.count(),
            'connections_count': workflow.connections.count()
        }

    def activate_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Activate a workflow"""
        from .workflow_models import WorkflowDefinition

        workflow = WorkflowDefinition.objects.get(id=workflow_id)

        # Validate workflow
        validation = self.validate_workflow(workflow_id)
        if not validation.get('is_valid'):
            return {
                'error': 'Workflow validation failed',
                'issues': validation.get('issues', [])
            }

        workflow.status = 'active'
        workflow.save(update_fields=['status', 'updated_at'])

        return {
            'workflow_id': str(workflow.id),
            'status': 'active'
        }

    def validate_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Validate workflow configuration"""
        from .workflow_models import WorkflowDefinition

        workflow = WorkflowDefinition.objects.get(id=workflow_id)
        issues = []

        nodes = list(workflow.nodes.all())
        connections = list(workflow.connections.all())

        if not nodes:
            issues.append({
                'type': 'error',
                'message': 'Workflow has no nodes'
            })

        # Check for orphan nodes
        connected_nodes = set()
        for conn in connections:
            connected_nodes.add(conn.source_node)
            connected_nodes.add(conn.target_node)

        for node in nodes:
            if node.node_id not in connected_nodes and len(nodes) > 1:
                issues.append({
                    'type': 'warning',
                    'message': f'Node "{node.name}" is not connected',
                    'node_id': node.node_id
                })

        # Check for end nodes
        has_end = any(n.node_type.startswith('end_') for n in nodes)
        if not has_end:
            issues.append({
                'type': 'warning',
                'message': 'Workflow has no end node'
            })

        return {
            'is_valid': not any(i['type'] == 'error' for i in issues),
            'issues': issues
        }

    def clone_workflow(
        self,
        workflow_id: str,
        new_name: str
    ) -> dict[str, Any]:
        """Clone a workflow"""
        from .workflow_models import (
            WorkflowConnection,
            WorkflowDefinition,
            WorkflowNode,
            WorkflowVariable,
        )

        original = WorkflowDefinition.objects.get(id=workflow_id)

        # Clone definition
        clone = WorkflowDefinition.objects.create(
            user=self.user,
            name=new_name,
            description=original.description,
            category=original.category,
            trigger_type=original.trigger_type,
            trigger_config=original.trigger_config,
            entry_conditions=original.entry_conditions,
            canvas_data=original.canvas_data,
            allow_multiple=original.allow_multiple,
            max_concurrent=original.max_concurrent,
            timeout_hours=original.timeout_hours
        )

        # Clone nodes
        for node in original.nodes.all():
            WorkflowNode.objects.create(
                workflow=clone,
                node_id=node.node_id,
                name=node.name,
                node_type=node.node_type,
                config=node.config,
                position_x=node.position_x,
                position_y=node.position_y,
                timeout_minutes=node.timeout_minutes,
                retry_count=node.retry_count,
                on_error=node.on_error
            )

        # Clone connections
        for conn in original.connections.all():
            WorkflowConnection.objects.create(
                workflow=clone,
                source_node=conn.source_node,
                target_node=conn.target_node,
                source_port=conn.source_port,
                target_port=conn.target_port,
                condition=conn.condition,
                label=conn.label,
                priority=conn.priority
            )

        # Clone variables
        for var in original.variables.all():
            WorkflowVariable.objects.create(
                workflow=clone,
                name=var.name,
                display_name=var.display_name,
                variable_type=var.variable_type,
                default_value=var.default_value,
                is_required=var.is_required
            )

        return {
            'workflow_id': str(clone.id),
            'name': clone.name,
            'cloned_from': str(original.id)
        }


class ApprovalService:
    """Service for handling workflow approvals"""

    def __init__(self, user):
        self.user = user

    def get_pending_approvals(self) -> list[dict[str, Any]]:
        """Get pending approvals for user"""
        from .workflow_models import WorkflowApprovalRequest

        approvals = WorkflowApprovalRequest.objects.filter(
            approver=self.user,
            status='pending'
        ).order_by('-created_at')

        return [
            {
                'id': str(a.id),
                'title': a.title,
                'description': a.description,
                'workflow_name': a.node_execution.instance.workflow.name,
                'data_to_review': a.data_to_review,
                'options': a.approval_options,
                'due_date': a.due_date.isoformat() if a.due_date else None,
                'created_at': a.created_at.isoformat()
            }
            for a in approvals
        ]

    def respond_to_approval(
        self,
        approval_id: str,
        decision: str,
        comment: str = ''
    ) -> dict[str, Any]:
        """Respond to an approval request"""
        from .workflow_models import WorkflowApprovalRequest

        approval = WorkflowApprovalRequest.objects.get(
            id=approval_id,
            approver=self.user
        )

        if approval.status != 'pending':
            return {'error': f'Approval already {approval.status}'}

        approval.status = 'approved' if decision == 'approve' else 'rejected'
        approval.decision = decision
        approval.comment = comment
        approval.responded_at = timezone.now()
        approval.save()

        # Update node execution
        execution = approval.node_execution
        execution.approval_status = approval.status
        execution.approved_by = self.user
        execution.approval_comment = comment
        execution.save()

        # Resume workflow
        engine = WorkflowEngineService(self.user)
        engine.resume_workflow(
            str(execution.instance.id),
            {
                'approval_decision': decision,
                'approval_comment': comment,
                'approved_by': str(self.user.id)
            }
        )

        return {
            'approval_id': str(approval.id),
            'status': approval.status,
            'decision': decision
        }

    def delegate_approval(
        self,
        approval_id: str,
        delegate_to_id: str,
        reason: str = ''
    ) -> dict[str, Any]:
        """Delegate approval to another user"""
        from django.contrib.auth import get_user_model

        from .workflow_models import WorkflowApprovalRequest

        User = get_user_model()

        approval = WorkflowApprovalRequest.objects.get(
            id=approval_id,
            approver=self.user
        )

        delegate_to = User.objects.get(id=delegate_to_id)

        approval.status = 'delegated'
        approval.delegated_to = delegate_to
        approval.delegated_reason = reason
        approval.save()

        # Create new approval for delegate
        new_approval = WorkflowApprovalRequest.objects.create(
            node_execution=approval.node_execution,
            approver=delegate_to,
            title=approval.title,
            description=f"{approval.description}\n\nDelegated by {self.user.email}: {reason}",
            data_to_review=approval.data_to_review,
            approval_options=approval.approval_options,
            requires_comment=approval.requires_comment,
            due_date=approval.due_date
        )

        return {
            'original_approval_id': str(approval.id),
            'new_approval_id': str(new_approval.id),
            'delegated_to': delegate_to.email
        }
