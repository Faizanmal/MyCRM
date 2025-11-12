"""
Django management command to create database backup
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from core.models import DataBackup
import subprocess
import os


class Command(BaseCommand):
    help = 'Create database backup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='full',
            choices=['full', 'incremental', 'differential'],
            help='Type of backup to create'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='backups',
            help='Output directory for backup files'
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Compress the backup file'
        )

    def handle(self, *args, **options):
        backup_type = options['type']
        output_dir = options['output_dir']
        compress = options['compress']

        self.stdout.write(
            self.style.SUCCESS(f'Starting {backup_type} backup...')
        )

        # Create backup record
        backup = DataBackup.objects.create(
            backup_type=backup_type,
            file_path=self.generate_backup_filename(output_dir, backup_type, compress),
            status='running'
        )

        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Perform the backup
            if backup_type == 'full':
                self.create_full_backup(backup, compress)
            elif backup_type == 'incremental':
                self.create_incremental_backup(backup, compress)
            elif backup_type == 'differential':
                self.create_differential_backup(backup, compress)

            # Update backup record
            backup.status = 'completed'
            backup.completed_at = timezone.now()
            
            # Get file size
            if os.path.exists(backup.file_path):
                backup.file_size = os.path.getsize(backup.file_path)
            
            backup.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Backup completed successfully: {backup.file_path}'
                )
            )

        except Exception as e:
            backup.status = 'failed'
            backup.error_message = str(e)
            backup.completed_at = timezone.now()
            backup.save()
            
            self.stdout.write(
                self.style.ERROR(f'Backup failed: {str(e)}')
            )
            raise

    def generate_backup_filename(self, output_dir, backup_type, compress):
        """Generate backup filename"""
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        extension = '.sql.gz' if compress else '.sql'
        
        filename = f"crm_backup_{backup_type}_{timestamp}{extension}"
        return os.path.join(output_dir, filename)

    def create_full_backup(self, backup, compress):
        """Create full database backup"""
        db_config = settings.DATABASES['default']
        
        # Build pg_dump command
        cmd = [
            'pg_dump',
            '--host', db_config['HOST'],
            '--port', str(db_config['PORT']),
            '--username', db_config['USER'],
            '--dbname', db_config['NAME'],
            '--verbose',
            '--clean',
            '--no-owner',
            '--no-privileges'
        ]
        
        if compress:
            cmd.extend(['--compress', '9'])
        
        # Set environment variable for password
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        # Run pg_dump
        with open(backup.file_path, 'wb') as output_file:
            result = subprocess.run(
                cmd,
                stdout=output_file,
                stderr=subprocess.PIPE,
                env=env,
                check=True
            )
            # Log backup process completion
            if result.returncode == 0:
                self.stdout.write('Backup process completed successfully')
        
        self.stdout.write(f'Full backup created: {backup.file_path}')

    def create_incremental_backup(self, backup, compress):
        """Create incremental backup (simplified version)"""
        # In a real implementation, this would use WAL (Write-Ahead Logging)
        # For now, we'll create a full backup with a note
        self.stdout.write(
            self.style.WARNING(
                'Incremental backup not fully implemented. Creating full backup instead.'
            )
        )
        self.create_full_backup(backup, compress)

    def create_differential_backup(self, backup, compress):
        """Create differential backup (simplified version)"""
        # In a real implementation, this would backup changes since last full backup
        # For now, we'll create a full backup with a note
        self.stdout.write(
            self.style.WARNING(
                'Differential backup not fully implemented. Creating full backup instead.'
            )
        )
        self.create_full_backup(backup, compress)