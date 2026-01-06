"""
Django management command to cleanup old audit logs and maintain database health
"""

from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import AuditLog, DataBackup, SystemHealth


class Command(BaseCommand):
    help = 'Cleanup old records and maintain database health'

    def add_arguments(self, parser):
        parser.add_argument(
            '--audit-days',
            type=int,
            default=getattr(settings, 'AUDIT_LOG_RETENTION_DAYS', 365),
            help='Number of days to retain audit logs'
        )
        parser.add_argument(
            '--backup-days',
            type=int,
            default=getattr(settings, 'BACKUP_RETENTION_DAYS', 90),
            help='Number of days to retain backup records'
        )
        parser.add_argument(
            '--health-days',
            type=int,
            default=30,
            help='Number of days to retain health check records'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        audit_days = options['audit_days']
        backup_days = options['backup_days']
        health_days = options['health_days']

        self.stdout.write(
            self.style.SUCCESS(
                f'Starting cleanup process {"(DRY RUN)" if self.dry_run else ""}...'
            )
        )

        # Cleanup audit logs
        self.cleanup_audit_logs(audit_days)

        # Cleanup backup records
        self.cleanup_backup_records(backup_days)

        # Cleanup health check records
        self.cleanup_health_records(health_days)

        self.stdout.write(
            self.style.SUCCESS('Cleanup process completed.')
        )

    def cleanup_audit_logs(self, retention_days):
        """Cleanup old audit logs"""
        cutoff_date = timezone.now() - timedelta(days=retention_days)

        old_logs = AuditLog.objects.filter(timestamp__lt=cutoff_date)
        count = old_logs.count()

        if count > 0:
            if self.dry_run:
                self.stdout.write(
                    f'Would delete {count} audit log records older than {retention_days} days'
                )
            else:
                # Keep critical and high-risk logs longer
                critical_logs = old_logs.filter(risk_level__in=['critical', 'high'])
                regular_logs = old_logs.exclude(risk_level__in=['critical', 'high'])

                regular_count = regular_logs.count()
                if regular_count > 0:
                    regular_logs.delete()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Deleted {regular_count} regular audit log records'
                        )
                    )

                # For critical logs, keep them for twice the retention period
                extended_cutoff = timezone.now() - timedelta(days=retention_days * 2)
                old_critical_logs = critical_logs.filter(timestamp__lt=extended_cutoff)
                critical_count = old_critical_logs.count()

                if critical_count > 0:
                    old_critical_logs.delete()
                    self.stdout.write(
                        self.style.WARNING(
                            f'Deleted {critical_count} critical audit log records '
                            f'older than {retention_days * 2} days'
                        )
                    )
        else:
            self.stdout.write('No old audit logs to cleanup')

    def cleanup_backup_records(self, retention_days):
        """Cleanup old backup records"""
        cutoff_date = timezone.now() - timedelta(days=retention_days)

        old_backups = DataBackup.objects.filter(started_at__lt=cutoff_date)
        count = old_backups.count()

        if count > 0:
            if self.dry_run:
                self.stdout.write(
                    f'Would delete {count} backup records older than {retention_days} days'
                )
            else:
                # TODO: Also delete actual backup files from storage
                deleted_count, _ = old_backups.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Deleted {deleted_count} backup records'
                    )
                )
        else:
            self.stdout.write('No old backup records to cleanup')

    def cleanup_health_records(self, retention_days):
        """Cleanup old health check records, keeping latest for each component"""
        cutoff_date = timezone.now() - timedelta(days=retention_days)

        # Get all unique components
        components = SystemHealth.objects.values_list('component', flat=True).distinct()

        total_deleted = 0

        for component in components:
            # Keep the latest 100 records for each component, regardless of age
            latest_records = SystemHealth.objects.filter(
                component=component
            ).order_by('-checked_at')[:100]

            latest_ids = list(latest_records.values_list('id', flat=True))

            # Delete old records not in the latest 100
            old_records = SystemHealth.objects.filter(
                component=component,
                checked_at__lt=cutoff_date
            ).exclude(id__in=latest_ids)

            count = old_records.count()

            if count > 0:
                if self.dry_run:
                    self.stdout.write(
                        f'Would delete {count} {component} health records '
                        f'older than {retention_days} days'
                    )
                    total_deleted += count
                else:
                    deleted_count, _ = old_records.delete()
                    total_deleted += deleted_count
                    self.stdout.write(
                        f'Deleted {deleted_count} {component} health records'
                    )

        if total_deleted == 0:
            self.stdout.write('No old health check records to cleanup')
        elif self.dry_run:
            self.stdout.write(
                f'Would delete {total_deleted} total health check records'
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Deleted {total_deleted} total health check records'
                )
            )
