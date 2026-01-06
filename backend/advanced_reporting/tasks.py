from datetime import timedelta

from celery import shared_task
from django.db.models import Avg, Count, Sum
from django.utils import timezone


@shared_task
def execute_report_task(execution_id):
    """
    Execute a report and save results
    """
    from .models import ReportExecution

    try:
        execution = ReportExecution.objects.get(id=execution_id)
        report = execution.report

        execution.status = 'running'
        execution.started_at = timezone.now()
        execution.save()

        # Generate report data
        data = generate_report_data(report)

        # Save results
        execution.result_data = data
        execution.status = 'completed'
        execution.completed_at = timezone.now()
        execution.save()

        # Send to recipients if configured
        if report.recipients.exists():
            send_report_email.delay(execution.id)

        return {'status': 'success', 'execution_id': execution_id}

    except Exception as e:
        execution.status = 'failed'
        execution.error_message = str(e)
        execution.completed_at = timezone.now()
        execution.save()

        return {'status': 'error', 'message': str(e)}


def generate_report_data(report, limit=None):
    """
    Generate data for a report based on its configuration
    """
    from contact_management.models import Contact
    from lead_management.models import Lead
    from opportunity_management.models import Opportunity
    from task_management.models import Task

    report_type = report.report_type
    data_source = report.data_source
    filters = report.filters or {}
    grouping = report.grouping or []
    # TODO: Implement sorting configuration for dynamic report ordering
    # sorting = report.sorting or []

    # Select model based on data source
    if data_source == 'leads':
        queryset = Lead.objects.all()
        model_name = 'Lead'
    elif data_source == 'opportunities':
        queryset = Opportunity.objects.all()
        model_name = 'Opportunity'
    elif data_source == 'contacts':
        queryset = Contact.objects.all()
        model_name = 'Contact'
    elif data_source == 'tasks':
        queryset = Task.objects.all()
        model_name = 'Task'
    else:
        return {'error': f'Unknown data source: {data_source}'}

    # Apply filters
    for field, value in filters.items():
        if isinstance(value, dict):
            # Complex filter (e.g., date range, comparisons)
            operator = value.get('operator', 'exact')
            filter_value = value.get('value')

            if operator == 'gte':
                queryset = queryset.filter(**{f'{field}__gte': filter_value})
            elif operator == 'lte':
                queryset = queryset.filter(**{f'{field}__lte': filter_value})
            elif operator == 'contains':
                queryset = queryset.filter(**{f'{field}__icontains': filter_value})
            elif operator == 'in':
                queryset = queryset.filter(**{f'{field}__in': filter_value})
        else:
            # Simple exact match
            queryset = queryset.filter(**{field: value})

    # Generate data based on report type
    if report_type == 'tabular':
        # Tabular report - list of records
        if limit:
            queryset = queryset[:limit]

        rows = []
        for obj in queryset:
            row = {'id': obj.id}

            # Add common fields based on model
            if model_name == 'Lead':
                row.update({
                    'name': f"{obj.first_name} {obj.last_name}",
                    'email': obj.email,
                    'status': obj.status,
                    'source': obj.source,
                    'score': getattr(obj, 'score', None)
                })
            elif model_name == 'Opportunity':
                row.update({
                    'name': obj.name,
                    'value': obj.value,
                    'stage': obj.stage,
                    'probability': obj.probability,
                    'close_date': obj.close_date.isoformat() if obj.close_date else None
                })
            elif model_name == 'Contact':
                row.update({
                    'name': f"{obj.first_name} {obj.last_name}",
                    'email': obj.email,
                    'phone': obj.phone,
                    'company': getattr(obj, 'company', None)
                })
            elif model_name == 'Task':
                row.update({
                    'title': obj.title,
                    'status': obj.status,
                    'priority': obj.priority,
                    'due_date': obj.due_date.isoformat() if obj.due_date else None
                })

            rows.append(row)

        return {
            'type': 'tabular',
            'columns': list(rows[0].keys()) if rows else [],
            'rows': rows,
            'total_count': queryset.count()
        }

    elif report_type == 'summary':
        # Summary report - aggregated data
        summary = {}

        # Count
        summary['total_count'] = queryset.count()

        # Additional aggregations based on model
        if model_name == 'Opportunity':
            summary['total_value'] = queryset.aggregate(total=Sum('value'))['total'] or 0
            summary['avg_value'] = queryset.aggregate(avg=Avg('value'))['avg'] or 0
            summary['avg_probability'] = queryset.aggregate(avg=Avg('probability'))['avg'] or 0

        # Group by if specified
        if grouping:
            grouped_data = []
            for group_field in grouping:
                group_results = queryset.values(group_field).annotate(count=Count('id'))
                grouped_data.append({
                    'field': group_field,
                    'groups': list(group_results)
                })
            summary['grouped_data'] = grouped_data

        return {
            'type': 'summary',
            'summary': summary
        }

    elif report_type == 'analytics':
        # Analytics report - time-based trends
        # Group by date
        date_field = filters.get('date_field', 'created_at')
        days = filters.get('days', 30)

        start_date = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(**{f'{date_field}__gte': start_date})

        # Group by day
        from django.db.models.functions import TruncDate
        daily_data = queryset.annotate(
            date=TruncDate(date_field)
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        return {
            'type': 'analytics',
            'period_days': days,
            'date_field': date_field,
            'daily_data': list(daily_data)
        }

    else:
        return {'error': f'Unknown report type: {report_type}'}


@shared_task
def send_report_email(execution_id):
    """
    Send report results to recipients via email
    """
    from core.email_service import send_email

    from .models import ReportExecution

    try:
        execution = ReportExecution.objects.get(id=execution_id)
        report = execution.report

        # Get recipients
        recipients = [user.email for user in report.recipients.all() if user.email]

        if not recipients:
            return {'status': 'skipped', 'reason': 'No recipients'}

        # Prepare email
        subject = f"Report: {report.name}"

        # Format result data for email
        result_summary = execution.result_data
        if isinstance(result_summary, dict):
            if result_summary.get('type') == 'tabular':
                row_count = len(result_summary.get('rows', []))
                body = f"Report '{report.name}' has completed.\n\n"
                body += f"Total rows: {row_count}\n"
                body += f"Executed at: {execution.completed_at}\n\n"
                body += "View full report in CRM dashboard."
            elif result_summary.get('type') == 'summary':
                summary = result_summary.get('summary', {})
                body = f"Report '{report.name}' has completed.\n\n"
                body += "Summary:\n"
                for key, value in summary.items():
                    body += f"  {key}: {value}\n"
            else:
                body = f"Report '{report.name}' has completed.\n\nView results in CRM dashboard."
        else:
            body = f"Report '{report.name}' has completed.\n\nView results in CRM dashboard."

        # Send email
        for recipient in recipients:
            send_email(
                to_email=recipient,
                subject=subject,
                body=body
            )

        return {'status': 'success', 'recipients': len(recipients)}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@shared_task
def calculate_kpi_task(kpi_id):
    """
    Calculate and store current KPI value
    """
    from .models import KPI, KPIValue

    try:
        kpi = KPI.objects.get(id=kpi_id)

        # Execute KPI calculation based on configuration
        value = execute_kpi_calculation(kpi)

        # Store value
        KPIValue.objects.create(
            kpi=kpi,
            value=value,
            timestamp=timezone.now()
        )

        return {'status': 'success', 'kpi_id': kpi_id, 'value': value}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def execute_kpi_calculation(kpi):
    """
    Execute KPI calculation based on its configuration
    """
    from contact_management.models import Contact
    from lead_management.models import Lead
    from opportunity_management.models import Opportunity
    from task_management.models import Task

    data_source = kpi.data_source
    calculation_method = kpi.calculation_method
    query_config = kpi.query_config or {}

    # Select model
    if data_source == 'leads':
        queryset = Lead.objects.all()
    elif data_source == 'opportunities':
        queryset = Opportunity.objects.all()
    elif data_source == 'contacts':
        queryset = Contact.objects.all()
    elif data_source == 'tasks':
        queryset = Task.objects.all()
    else:
        return 0

    # Apply filters from query_config
    filters = query_config.get('filters', {})
    for field, value in filters.items():
        queryset = queryset.filter(**{field: value})

    # Calculate value
    if calculation_method == 'count':
        return queryset.count()

    elif calculation_method == 'sum':
        field = query_config.get('field', 'value')
        result = queryset.aggregate(total=Sum(field))['total']
        return float(result) if result else 0.0

    elif calculation_method == 'avg':
        field = query_config.get('field', 'value')
        result = queryset.aggregate(avg=Avg(field))['avg']
        return float(result) if result else 0.0

    elif calculation_method == 'conversion_rate':
        # Calculate conversion rate (completed / total)
        status_field = query_config.get('status_field', 'status')
        completed_status = query_config.get('completed_status', 'won')

        total = queryset.count()
        completed = queryset.filter(**{status_field: completed_status}).count()

        return (completed / total * 100) if total > 0 else 0.0

    else:
        return 0


@shared_task
def run_scheduled_reports():
    """
    Check and execute scheduled reports
    Runs every hour via Celery beat
    """
    from .models import ReportExecution, ReportSchedule

    now = timezone.now()

    # Find schedules due for execution
    due_schedules = ReportSchedule.objects.filter(
        is_active=True,
        next_run__lte=now
    )

    executed_count = 0

    for schedule in due_schedules:
        # Create execution
        execution = ReportExecution.objects.create(
            report=schedule.report,
            status='pending'
        )

        # Trigger execution
        execute_report_task.delay(execution.id)

        # Update schedule
        schedule.last_run = now
        schedule.next_run = schedule.calculate_next_run()
        schedule.save()

        executed_count += 1

    return {
        'status': 'success',
        'executed_count': executed_count,
        'checked_at': now.isoformat()
    }


@shared_task
def refresh_all_kpis():
    """
    Refresh all active KPIs
    Runs every 15 minutes via Celery beat
    """
    from .models import KPI

    kpis = KPI.objects.filter(is_active=True)

    for kpi in kpis:
        calculate_kpi_task.delay(kpi.id)

    return {
        'status': 'success',
        'kpi_count': kpis.count()
    }
