"""
Initialize Default Roles Management Command
Creates the default system roles for RBAC
"""

from django.core.management.base import BaseCommand
from core.settings_models import UserRole


class Command(BaseCommand):
    help = 'Initialize default system roles for RBAC'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing roles',
        )

    def handle(self, *args, **options):
        self.stdout.write('Initializing default roles...')
        
        created_count = 0
        updated_count = 0
        
        for role_data in UserRole.get_default_roles():
            role, created = UserRole.objects.update_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  Created role: {role.display_name}")
                )
            else:
                if options['force']:
                    for key, value in role_data.items():
                        setattr(role, key, value)
                    role.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"  Updated role: {role.display_name}")
                    )
                else:
                    self.stdout.write(
                        self.style.NOTICE(f"  Skipped existing role: {role.display_name}")
                    )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done! Created: {created_count}, Updated: {updated_count}'
        ))
        
        # Display role summary
        self.stdout.write('')
        self.stdout.write('Role Summary:')
        self.stdout.write('-' * 60)
        
        for role in UserRole.objects.all().order_by('-level'):
            perms_count = len(role.permissions) if role.permissions else 0
            self.stdout.write(
                f"  Level {role.level}: {role.display_name} ({perms_count} permissions)"
            )
