"""
Management Command: rotate_encryption_keys
==========================================
Scans database models storing encrypted credentials (ThirdPartyIntegration, SSOProvider, SSOSession)
and re-encrypts any records encrypted with an older rotation key or legacy format to the current active key (kid).
"""
import logging
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction

from core.encryption import get_encryption_manager, is_encrypted, is_stale_key

logger = logging.getLogger(__name__)

TARGET_MODELS = [
    {
        'app': 'integration_hub',
        'model': 'ThirdPartyIntegration',
        'fields': ['api_key', 'api_secret', 'access_token', 'refresh_token']
    },
    {
        'app': 'sso_integration',
        'model': 'SSOProvider',
        'fields': ['client_secret']
    },
    {
        'app': 'sso_integration',
        'model': 'SSOSession',
        'fields': ['sso_token', 'refresh_token']
    },
]


class Command(BaseCommand):
    help = "Re-encrypts encrypted model fields using the active encryption key ID (kid)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate key rotation without writing changes to the database.',
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Filter rotation to a specific model name (e.g. ThirdPartyIntegration).',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Number of records to process per batch (default 500).',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        target_model_filter = options.get('model')
        batch_size = options.get('batch_size', 500)

        manager = get_encryption_manager()
        active_kid = manager.active_kid

        self.stdout.write(self.style.NOTICE(
            f"=== Starting Encryption Key Rotation ==="
        ))
        self.stdout.write(f"Active Key ID: {active_kid}")
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE: No database changes will be committed."))

        total_scanned = 0
        total_rotated = 0
        total_current = 0
        total_errors = 0

        for target in TARGET_MODELS:
            model_name = target['model']
            if target_model_filter and target_model_filter.lower() != model_name.lower():
                continue

            try:
                model_class = apps.get_model(target['app'], model_name)
            except LookupError:
                self.stdout.write(self.style.WARNING(f"Model {target['app']}.{model_name} not found. Skipping."))
                continue

            fields = target['fields']
            self.stdout.write(f"\nScanning {model_name} for encrypted fields: {', '.join(fields)}...")

            queryset = model_class.objects.all().order_by('pk')
            model_scanned = 0
            model_rotated = 0

            # Process in batches
            for item in queryset.iterator(chunk_size=batch_size):
                model_scanned += 1
                total_scanned += 1
                dirty_fields = []

                for field_name in fields:
                    val = getattr(item, field_name, None)
                    if not val or not is_encrypted(val):
                        continue

                    if is_stale_key(val):
                        try:
                            new_val, was_rotated = manager.rotate(val)
                            if was_rotated:
                                setattr(item, field_name, new_val)
                                dirty_fields.append(field_name)
                                model_rotated += 1
                                total_rotated += 1
                        except Exception as e:
                            total_errors += 1
                            self.stdout.write(self.style.ERROR(
                                f"  Error rotating {model_name} id={item.pk} field={field_name}: {e}"
                            ))
                    else:
                        total_current += 1

                if dirty_fields and not dry_run:
                    with transaction.atomic():
                        item.save(update_fields=dirty_fields)

            self.stdout.write(f"  {model_name}: {model_scanned} scanned, {model_rotated} rotated fields.")

        self.stdout.write(self.style.SUCCESS(
            f"\n=== Key Rotation Completed ===\n"
            f"Total records scanned: {total_scanned}\n"
            f"Total fields rotated: {total_rotated}\n"
            f"Total fields already current: {total_current}\n"
            f"Total errors: {total_errors}"
        ))
