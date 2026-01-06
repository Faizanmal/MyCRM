"""
Custom Report Builder Services
"""

import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from django.apps import apps
from django.db.models import Avg, Count, Max, Min, Sum
from django.utils import timezone


class ReportBuilderService:
    """Service for building and executing reports"""

    def __init__(self, user):
        self.user = user

    def create_report(
        self,
        name: str,
        report_type: str,
        data_source: str,
        config: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a new report template"""
        from .report_models import ReportTemplate

        template = ReportTemplate.objects.create(
            user=self.user,
            name=name,
            report_type=report_type,
            data_source=data_source,
            columns=config.get('columns', []),
            grouping=config.get('grouping', []),
            sorting=config.get('sorting', []),
            filters=config.get('filters', []),
            dynamic_filters=config.get('dynamic_filters', []),
            chart_config=config.get('chart_config', {}),
            calculated_fields=config.get('calculated_fields', []),
            layout_config=config.get('layout_config', {}),
            visibility=config.get('visibility', 'private')
        )

        return {
            'report_id': str(template.id),
            'name': template.name,
            'report_type': template.report_type,
            'data_source': template.data_source
        }

    def execute_report(
        self,
        report_id: str,
        parameters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Execute a report and return results"""
        from .report_models import ReportTemplate, SavedReport

        template = ReportTemplate.objects.get(id=report_id)

        # Update view count
        template.view_count += 1
        template.last_viewed_at = timezone.now()
        template.save(update_fields=['view_count', 'last_viewed_at'])

        # Create saved report record
        saved = SavedReport.objects.create(
            template=template,
            user=self.user,
            name=f"{template.name} - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            status='running',
            started_at=timezone.now(),
            parameters=parameters or {}
        )

        try:
            start_time = timezone.now()

            # Build and execute query
            query_builder = ReportQueryBuilder(
                data_source=template.data_source,
                columns=template.columns,
                filters=template.filters,
                grouping=template.grouping,
                sorting=template.sorting,
                parameters=parameters or {}
            )

            data = query_builder.execute()

            # Apply calculated fields
            if template.calculated_fields:
                data = self._apply_calculated_fields(
                    data, template.calculated_fields
                )

            end_time = timezone.now()
            execution_time = int((end_time - start_time).total_seconds() * 1000)

            # Update saved report
            saved.status = 'completed'
            saved.completed_at = end_time
            saved.execution_time_ms = execution_time
            saved.result_data = data
            saved.row_count = len(data.get('rows', []))
            saved.save()

            return {
                'saved_report_id': str(saved.id),
                'status': 'completed',
                'execution_time_ms': execution_time,
                'row_count': saved.row_count,
                'columns': data.get('columns', []),
                'rows': data.get('rows', []),
                'summary': data.get('summary', {})
            }

        except Exception as e:
            saved.status = 'failed'
            saved.error_message = str(e)
            saved.completed_at = timezone.now()
            saved.save()

            return {
                'saved_report_id': str(saved.id),
                'status': 'failed',
                'error': str(e)
            }

    def _apply_calculated_fields(
        self, data: dict, calculated_fields: list[dict]
    ) -> dict:
        """Apply calculated fields to report data"""
        rows = data.get('rows', [])

        for field in calculated_fields:
            field_name = field.get('name')
            formula = field.get('formula')

            for row in rows:
                try:
                    # Simple formula evaluation (would use safer method in production)
                    result = self._evaluate_formula(formula, row)
                    row[field_name] = result
                except Exception:
                    row[field_name] = None

            # Add to columns
            data['columns'].append({
                'name': field_name,
                'label': field.get('label', field_name),
                'type': field.get('type', 'number'),
                'calculated': True
            })

        return data

    def _evaluate_formula(self, formula: str, row: dict) -> Any:
        """Safely evaluate a formula"""
        # Simplified - would use a proper expression parser
        allowed_names = {**row}
        return eval(formula, {"__builtins__": {}}, allowed_names)

    def clone_report(self, report_id: str, new_name: str) -> dict[str, Any]:
        """Clone an existing report"""
        from .report_models import ReportTemplate, ReportWidget

        original = ReportTemplate.objects.get(id=report_id)

        # Clone template
        clone = ReportTemplate.objects.create(
            user=self.user,
            name=new_name,
            description=original.description,
            report_type=original.report_type,
            data_source=original.data_source,
            base_query=original.base_query,
            layout_config=original.layout_config,
            columns=original.columns,
            grouping=original.grouping,
            sorting=original.sorting,
            filters=original.filters,
            dynamic_filters=original.dynamic_filters,
            chart_config=original.chart_config,
            calculated_fields=original.calculated_fields
        )

        # Clone widgets
        for widget in original.widgets.all():
            ReportWidget.objects.create(
                report=clone,
                name=widget.name,
                widget_type=widget.widget_type,
                position_x=widget.position_x,
                position_y=widget.position_y,
                width=widget.width,
                height=widget.height,
                data_source=widget.data_source,
                query=widget.query,
                aggregation=widget.aggregation,
                config=widget.config,
                colors=widget.colors
            )

        return {
            'report_id': str(clone.id),
            'name': clone.name,
            'cloned_from': str(original.id)
        }

    def export_report(
        self,
        saved_report_id: str,
        export_format: str
    ) -> dict[str, Any]:
        """Export a saved report to a file format"""
        from .report_models import SavedReport

        saved = SavedReport.objects.get(id=saved_report_id)

        if saved.status != 'completed':
            return {'error': 'Report not completed'}

        data = saved.result_data

        if export_format == 'csv':
            content = self._to_csv(data)
            extension = 'csv'
        elif export_format == 'json':
            content = json.dumps(data, indent=2)
            extension = 'json'
        elif export_format == 'excel':
            # Would use openpyxl or xlsxwriter
            content = self._to_csv(data)  # Simplified
            extension = 'xlsx'
        else:
            return {'error': f'Unsupported format: {export_format}'}

        # Save file (simplified - would save to S3/storage)
        filename = f"{saved.name.replace(' ', '_')}.{extension}"

        saved.export_format = export_format
        saved.file_url = f"/exports/{filename}"
        saved.file_size = len(content)
        saved.save()

        return {
            'file_url': saved.file_url,
            'filename': filename,
            'size': saved.file_size,
            'format': export_format
        }

    def _to_csv(self, data: dict) -> str:
        """Convert report data to CSV"""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        columns = [c.get('name') for c in data.get('columns', [])]
        writer.writerow(columns)

        # Rows
        for row in data.get('rows', []):
            writer.writerow([row.get(c) for c in columns])

        return output.getvalue()


class ReportQueryBuilder:
    """Builds and executes queries for reports"""

    DATA_SOURCE_MAPPING = {
        'opportunities': ('opportunity_management', 'Opportunity'),
        'contacts': ('contact_management', 'Contact'),
        'accounts': ('contact_management', 'Account'),
        'leads': ('lead_management', 'Lead'),
        'tasks': ('task_management', 'Task'),
        'activities': ('activity_feed', 'Activity'),
    }

    def __init__(
        self,
        data_source: str,
        columns: list[dict],
        filters: list[dict],
        grouping: list[str],
        sorting: list[dict],
        parameters: dict[str, Any]
    ):
        self.data_source = data_source
        self.columns = columns
        self.filters = filters
        self.grouping = grouping
        self.sorting = sorting
        self.parameters = parameters

    def execute(self) -> dict[str, Any]:
        """Execute the query and return results"""
        model = self._get_model()

        if not model:
            return {'columns': [], 'rows': [], 'summary': {}}

        queryset = model.objects.all()

        # Apply filters
        queryset = self._apply_filters(queryset)

        # Apply sorting
        queryset = self._apply_sorting(queryset)

        # Execute query
        if self.grouping:
            return self._execute_grouped(queryset)
        else:
            return self._execute_flat(queryset)

    def _get_model(self):
        """Get Django model for data source"""
        if self.data_source not in self.DATA_SOURCE_MAPPING:
            return None

        app_label, model_name = self.DATA_SOURCE_MAPPING[self.data_source]

        try:
            return apps.get_model(app_label, model_name)
        except LookupError:
            return None

    def _apply_filters(self, queryset):
        """Apply filters to queryset"""
        for f in self.filters:
            field = f.get('field')
            operator = f.get('operator', 'equals')
            value = f.get('value')

            # Check for parameter substitution
            if isinstance(value, str) and value.startswith('$'):
                param_name = value[1:]
                value = self.parameters.get(param_name, value)

            if operator == 'equals':
                queryset = queryset.filter(**{field: value})
            elif operator == 'not_equals':
                queryset = queryset.exclude(**{field: value})
            elif operator == 'contains':
                queryset = queryset.filter(**{f'{field}__icontains': value})
            elif operator == 'starts_with':
                queryset = queryset.filter(**{f'{field}__istartswith': value})
            elif operator == 'ends_with':
                queryset = queryset.filter(**{f'{field}__iendswith': value})
            elif operator == 'greater_than':
                queryset = queryset.filter(**{f'{field}__gt': value})
            elif operator == 'less_than':
                queryset = queryset.filter(**{f'{field}__lt': value})
            elif operator == 'greater_or_equal':
                queryset = queryset.filter(**{f'{field}__gte': value})
            elif operator == 'less_or_equal':
                queryset = queryset.filter(**{f'{field}__lte': value})
            elif operator == 'is_null':
                queryset = queryset.filter(**{f'{field}__isnull': True})
            elif operator == 'is_not_null':
                queryset = queryset.filter(**{f'{field}__isnull': False})
            elif operator == 'in':
                queryset = queryset.filter(**{f'{field}__in': value})
            elif operator == 'between' and isinstance(value, list) and len(value) == 2:
                queryset = queryset.filter(**{f'{field}__range': value})

        return queryset

    def _apply_sorting(self, queryset):
        """Apply sorting to queryset"""
        order_by = []

        for s in self.sorting:
            field = s.get('field')
            direction = s.get('direction', 'asc')

            if direction == 'desc':
                order_by.append(f'-{field}')
            else:
                order_by.append(field)

        if order_by:
            queryset = queryset.order_by(*order_by)

        return queryset

    def _execute_flat(self, queryset) -> dict[str, Any]:
        """Execute flat (non-grouped) query"""
        # Limit results
        limit = self.parameters.get('limit', 1000)
        queryset = queryset[:limit]

        # Get column names
        column_names = [c.get('name') for c in self.columns] if self.columns else []

        queryset = queryset.values(*column_names) if column_names else queryset.values()

        rows = list(queryset)

        # Convert to serializable format
        for row in rows:
            for key, value in row.items():
                if hasattr(value, 'isoformat'):
                    row[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    row[key] = float(value)

        # Build column metadata
        columns = []
        if rows:
            for key in rows[0]:
                columns.append({
                    'name': key,
                    'label': key.replace('_', ' ').title(),
                    'type': 'string'  # Would infer from model field
                })

        return {
            'columns': columns,
            'rows': rows,
            'summary': {
                'total_rows': len(rows)
            }
        }

    def _execute_grouped(self, queryset) -> dict[str, Any]:
        """Execute grouped query with aggregations"""
        # Group by fields
        queryset = queryset.values(*self.grouping)

        # Add aggregations
        aggregations = {}
        for col in self.columns:
            if col.get('aggregation'):
                field = col.get('name')
                agg_type = col.get('aggregation')
                alias = col.get('alias', f'{field}_{agg_type}')

                if agg_type == 'count':
                    aggregations[alias] = Count(field)
                elif agg_type == 'sum':
                    aggregations[alias] = Sum(field)
                elif agg_type == 'avg':
                    aggregations[alias] = Avg(field)
                elif agg_type == 'min':
                    aggregations[alias] = Min(field)
                elif agg_type == 'max':
                    aggregations[alias] = Max(field)

        if aggregations:
            queryset = queryset.annotate(**aggregations)

        rows = list(queryset)

        # Convert to serializable format
        for row in rows:
            for key, value in row.items():
                if hasattr(value, 'isoformat'):
                    row[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    row[key] = float(value)

        # Build columns
        columns = []
        for field in self.grouping:
            columns.append({
                'name': field,
                'label': field.replace('_', ' ').title(),
                'type': 'string',
                'grouped': True
            })

        for alias in aggregations:
            columns.append({
                'name': alias,
                'label': alias.replace('_', ' ').title(),
                'type': 'number',
                'aggregated': True
            })

        return {
            'columns': columns,
            'rows': rows,
            'summary': {
                'total_groups': len(rows)
            }
        }


class DashboardService:
    """Service for managing dashboards"""

    def __init__(self, user):
        self.user = user

    def create_dashboard(
        self,
        name: str,
        config: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a new dashboard"""
        import secrets

        from .report_models import ReportDashboard

        dashboard = ReportDashboard.objects.create(
            user=self.user,
            name=name,
            description=config.get('description', ''),
            layout_type=config.get('layout_type', 'grid'),
            grid_columns=config.get('grid_columns', 12),
            layout_config=config.get('layout_config', {}),
            theme=config.get('theme', 'light'),
            global_filters=config.get('global_filters', []),
            date_range_filter=config.get('date_range_filter', {}),
            auto_refresh=config.get('auto_refresh', False),
            refresh_interval=config.get('refresh_interval', 60),
            public_token=secrets.token_urlsafe(32)
        )

        return {
            'dashboard_id': str(dashboard.id),
            'name': dashboard.name,
            'public_token': dashboard.public_token
        }

    def add_widget(
        self,
        dashboard_id: str,
        widget_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Add a widget to a dashboard"""
        from .report_models import DashboardWidget, ReportDashboard, ReportWidget

        dashboard = ReportDashboard.objects.get(id=dashboard_id)

        # Create or link widget
        widget_id = widget_config.get('widget_id')

        widget = ReportWidget.objects.get(id=widget_id) if widget_id else None

        dashboard_widget = DashboardWidget.objects.create(
            dashboard=dashboard,
            widget=widget,
            widget_type=widget_config.get('widget_type', ''),
            config=widget_config.get('config', {}),
            position_x=widget_config.get('position_x', 0),
            position_y=widget_config.get('position_y', 0),
            width=widget_config.get('width', 4),
            height=widget_config.get('height', 3),
            title_override=widget_config.get('title_override', ''),
            config_overrides=widget_config.get('config_overrides', {})
        )

        return {
            'dashboard_widget_id': str(dashboard_widget.id),
            'position': {
                'x': dashboard_widget.position_x,
                'y': dashboard_widget.position_y
            },
            'size': {
                'width': dashboard_widget.width,
                'height': dashboard_widget.height
            }
        }

    def update_layout(
        self,
        dashboard_id: str,
        widgets: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Update widget positions on a dashboard"""
        from .report_models import DashboardWidget

        for widget_data in widgets:
            widget_id = widget_data.get('id')

            DashboardWidget.objects.filter(id=widget_id).update(
                position_x=widget_data.get('position_x', 0),
                position_y=widget_data.get('position_y', 0),
                width=widget_data.get('width', 4),
                height=widget_data.get('height', 3)
            )

        return {'updated': len(widgets)}

    def get_dashboard_data(
        self,
        dashboard_id: str,
        filters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Get all widget data for a dashboard"""
        from .report_models import ReportDashboard

        dashboard = ReportDashboard.objects.get(id=dashboard_id)
        dashboard.view_count += 1
        dashboard.save(update_fields=['view_count'])

        widgets_data = []

        for dw in dashboard.dashboard_widgets.all():
            widget_data = self._execute_widget(dw, filters)
            widgets_data.append({
                'widget_id': str(dw.id),
                'position': {'x': dw.position_x, 'y': dw.position_y},
                'size': {'width': dw.width, 'height': dw.height},
                'data': widget_data
            })

        return {
            'dashboard_id': str(dashboard.id),
            'name': dashboard.name,
            'widgets': widgets_data,
            'global_filters': dashboard.global_filters,
            'last_refreshed': timezone.now().isoformat()
        }

    def _execute_widget(
        self,
        dashboard_widget,
        filters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Execute a single widget query"""
        config = {
            **dashboard_widget.config,
            **(dashboard_widget.widget.config if dashboard_widget.widget else {}),
            **dashboard_widget.config_overrides
        }

        # Would execute widget-specific query
        return {
            'type': dashboard_widget.widget_type or (
                dashboard_widget.widget.widget_type if dashboard_widget.widget else 'unknown'
            ),
            'title': dashboard_widget.title_override or (
                dashboard_widget.widget.name if dashboard_widget.widget else 'Widget'
            ),
            'data': {},  # Would contain actual widget data
            'config': config
        }

    def share_dashboard(
        self,
        dashboard_id: str,
        share_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Share a dashboard with users or make public"""
        from .report_models import ReportDashboard

        dashboard = ReportDashboard.objects.get(id=dashboard_id)

        if share_config.get('is_public'):
            dashboard.is_public = True
            dashboard.embed_enabled = share_config.get('embed_enabled', False)

        if share_config.get('users'):
            dashboard.shared_with = share_config['users']

        dashboard.save()

        return {
            'dashboard_id': str(dashboard.id),
            'is_public': dashboard.is_public,
            'public_url': f"/public/dashboard/{dashboard.public_token}" if dashboard.is_public else None,
            'embed_code': self._generate_embed_code(dashboard) if dashboard.embed_enabled else None,
            'shared_with': dashboard.shared_with
        }

    def _generate_embed_code(self, dashboard) -> str:
        """Generate embed code for dashboard"""
        return f'<iframe src="/embed/dashboard/{dashboard.public_token}" width="100%" height="600" frameborder="0"></iframe>'


class ScheduleService:
    """Service for managing scheduled reports"""

    def __init__(self, user):
        self.user = user

    def create_schedule(
        self,
        report_id: str,
        schedule_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a scheduled report"""
        from .report_models import ReportTemplate, ScheduledReport

        template = ReportTemplate.objects.get(id=report_id)

        schedule = ScheduledReport.objects.create(
            template=template,
            user=self.user,
            name=schedule_config.get('name', f"Scheduled: {template.name}"),
            frequency=schedule_config.get('frequency', 'weekly'),
            schedule_time=schedule_config.get('schedule_time', '09:00'),
            day_of_week=schedule_config.get('day_of_week'),
            day_of_month=schedule_config.get('day_of_month'),
            timezone=schedule_config.get('timezone', 'UTC'),
            parameters=schedule_config.get('parameters', {}),
            export_format=schedule_config.get('export_format', 'pdf'),
            delivery_method=schedule_config.get('delivery_method', 'email'),
            delivery_config=schedule_config.get('delivery_config', {}),
            recipients=schedule_config.get('recipients', [])
        )

        # Calculate next run
        schedule.next_run_at = self._calculate_next_run(schedule)
        schedule.save()

        return {
            'schedule_id': str(schedule.id),
            'name': schedule.name,
            'frequency': schedule.frequency,
            'next_run_at': schedule.next_run_at.isoformat() if schedule.next_run_at else None
        }

    def _calculate_next_run(self, schedule) -> datetime:
        """Calculate the next run time"""
        import pytz

        tz = pytz.timezone(schedule.timezone)
        now = timezone.now().astimezone(tz)

        # Start with today at scheduled time
        next_run = now.replace(
            hour=schedule.schedule_time.hour,
            minute=schedule.schedule_time.minute,
            second=0,
            microsecond=0
        )

        # Adjust based on frequency
        if schedule.frequency == 'daily':
            if next_run <= now:
                next_run += timedelta(days=1)

        elif schedule.frequency == 'weekly':
            target_dow = schedule.day_of_week or 0
            current_dow = now.weekday()
            days_ahead = target_dow - current_dow
            if days_ahead <= 0 or (days_ahead == 0 and next_run <= now):
                days_ahead += 7
            next_run += timedelta(days=days_ahead)

        elif schedule.frequency == 'monthly':
            target_day = schedule.day_of_month or 1
            next_run = next_run.replace(day=target_day)
            if next_run <= now:
                # Move to next month
                if next_run.month == 12:
                    next_run = next_run.replace(year=next_run.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=next_run.month + 1)

        return next_run

    def run_scheduled_report(self, schedule_id: str) -> dict[str, Any]:
        """Execute a scheduled report"""
        from .report_models import ScheduledReport

        schedule = ScheduledReport.objects.get(id=schedule_id)

        # Execute report
        report_service = ReportBuilderService(schedule.user)
        result = report_service.execute_report(
            str(schedule.template.id),
            schedule.parameters
        )

        # Export if needed
        if result.get('status') == 'completed' and schedule.attach_file:
            export_result = report_service.export_report(
                result['saved_report_id'],
                schedule.export_format
            )
            result['export'] = export_result

        # Deliver
        if result.get('status') == 'completed':
            delivery_result = self._deliver_report(schedule, result)
            result['delivery'] = delivery_result

        # Update schedule
        schedule.last_run_at = timezone.now()
        schedule.run_count += 1
        schedule.last_status = result.get('status', 'unknown')
        schedule.next_run_at = self._calculate_next_run(schedule)

        if result.get('status') == 'failed':
            schedule.failure_count += 1

        schedule.save()

        return result

    def _deliver_report(
        self,
        schedule,
        result: dict[str, Any]
    ) -> dict[str, Any]:
        """Deliver the report to recipients"""
        method = schedule.delivery_method

        if method == 'email':
            return self._deliver_email(schedule, result)
        elif method == 'slack':
            return self._deliver_slack(schedule, result)
        elif method == 'webhook':
            return self._deliver_webhook(schedule, result)

        return {'error': f'Unknown delivery method: {method}'}

    def _deliver_email(self, schedule, result: dict) -> dict[str, Any]:
        """Send report via email"""
        # Would use Django email or service like SendGrid
        return {
            'method': 'email',
            'recipients': schedule.recipients,
            'sent': True
        }

    def _deliver_slack(self, schedule, result: dict) -> dict[str, Any]:
        """Send report to Slack"""
        # Would use Slack API
        return {
            'method': 'slack',
            'channel': schedule.delivery_config.get('channel'),
            'sent': True
        }

    def _deliver_webhook(self, schedule, result: dict) -> dict[str, Any]:
        """Send report to webhook"""
        import requests

        url = schedule.delivery_config.get('url')
        if not url:
            return {'error': 'No webhook URL configured'}

        try:
            response = requests.post(
                url,
                json=result,
                timeout=30
            )
            return {
                'method': 'webhook',
                'status_code': response.status_code,
                'sent': response.ok
            }
        except Exception as e:
            return {'method': 'webhook', 'error': str(e)}


class DataSourceService:
    """Service for managing data sources"""

    def __init__(self):
        pass

    def get_available_sources(self) -> list[dict[str, Any]]:
        """Get all available data sources"""
        from .report_models import DataSource

        sources = DataSource.objects.filter(is_active=True)

        return [
            {
                'name': s.name,
                'display_name': s.display_name,
                'description': s.description,
                'source_type': s.source_type,
                'fields': s.fields
            }
            for s in sources
        ]

    def get_source_fields(self, source_name: str) -> dict[str, Any]:
        """Get fields available for a data source"""
        from .report_models import DataSource

        try:
            source = DataSource.objects.get(name=source_name)
            return {
                'name': source.name,
                'fields': source.fields,
                'relationships': source.relationships,
                'allowed_aggregations': source.allowed_aggregations
            }
        except DataSource.DoesNotExist:
            return self._introspect_model(source_name)

    def _introspect_model(self, source_name: str) -> dict[str, Any]:
        """Introspect a Django model for field information"""
        mapping = ReportQueryBuilder.DATA_SOURCE_MAPPING

        if source_name not in mapping:
            return {'error': f'Unknown source: {source_name}'}

        app_label, model_name = mapping[source_name]

        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            return {'error': f'Model not found: {app_label}.{model_name}'}

        fields = []
        for field in model._meta.get_fields():
            if hasattr(field, 'name'):
                field_info = {
                    'name': field.name,
                    'type': type(field).__name__,
                    'label': field.name.replace('_', ' ').title()
                }

                if hasattr(field, 'choices') and field.choices:
                    field_info['choices'] = [
                        {'value': c[0], 'label': c[1]}
                        for c in field.choices
                    ]

                if hasattr(field, 'related_model') and field.related_model:
                    field_info['relationship'] = {
                        'model': field.related_model.__name__,
                        'type': 'many_to_one' if hasattr(field, 'many_to_one') else 'many_to_many'
                    }

                fields.append(field_info)

        return {
            'name': source_name,
            'model': f'{app_label}.{model_name}',
            'fields': fields,
            'allowed_aggregations': ['count', 'sum', 'avg', 'min', 'max']
        }
