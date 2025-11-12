"""
Django management command to check system health
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection
from django.core.cache import cache
from core.models import SystemHealth
import time
import requests


class Command(BaseCommand):
    help = 'Check system health and update health records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--component',
            type=str,
            help='Check specific component only',
            choices=['database', 'cache', 'email', 'storage', 'api', 'queue']
        )

    def handle(self, *args, **options):
        component = options.get('component')
        
        if component:
            self.check_component(component)
        else:
            self.check_all_components()

    def check_all_components(self):
        """Check all system components"""
        components = ['database', 'cache', 'email', 'storage', 'api', 'queue']
        
        self.stdout.write(
            self.style.SUCCESS('Starting system health check...')
        )
        
        for component in components:
            self.check_component(component)
        
        self.stdout.write(
            self.style.SUCCESS('System health check completed.')
        )

    def check_component(self, component):
        """Check a specific component"""
        self.stdout.write(f'Checking {component}...')
        
        try:
            if component == 'database':
                self.check_database()
            elif component == 'cache':
                self.check_cache()
            elif component == 'email':
                self.check_email()
            elif component == 'storage':
                self.check_storage()
            elif component == 'api':
                self.check_api()
            elif component == 'queue':
                self.check_queue()
                
        except Exception as e:
            self.record_health_status(
                component=component,
                status='critical',
                error_message=str(e),
                response_time=None
            )
            self.stdout.write(
                self.style.ERROR(f'{component} check failed: {str(e)}')
            )

    def check_database(self):
        """Check database connectivity and performance"""
        start_time = time.time()
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if response_time < 100:
                status = 'healthy'
            elif response_time < 500:
                status = 'warning'
            else:
                status = 'critical'
            
            self.record_health_status(
                component='database',
                status=status,
                response_time=response_time,
                metrics={'query_time': response_time}
            )
            
        except Exception as e:
            self.record_health_status(
                component='database',
                status='down',
                error_message=str(e),
                response_time=None
            )
            raise

    def check_cache(self):
        """Check cache connectivity and performance"""
        start_time = time.time()
        
        try:
            # Test cache write and read
            test_key = 'health_check_test'
            test_value = 'test_value'
            
            cache.set(test_key, test_value, 30)
            retrieved_value = cache.get(test_key)
            
            if retrieved_value != test_value:
                raise Exception("Cache read/write test failed")
            
            cache.delete(test_key)
            
            response_time = (time.time() - start_time) * 1000
            
            if response_time < 50:
                status = 'healthy'
            elif response_time < 200:
                status = 'warning'
            else:
                status = 'critical'
            
            self.record_health_status(
                component='cache',
                status=status,
                response_time=response_time,
                metrics={'cache_response_time': response_time}
            )
            
        except Exception as e:
            self.record_health_status(
                component='cache',
                status='down',
                error_message=str(e),
                response_time=None
            )
            raise

    def check_email(self):
        """Check email service connectivity"""
        start_time = time.time()
        
        try:
            # Test email configuration without actually sending
            from django.core.mail import get_connection
            
            connection = get_connection()
            connection.open()
            connection.close()
            
            response_time = (time.time() - start_time) * 1000
            
            self.record_health_status(
                component='email',
                status='healthy',
                response_time=response_time,
                metrics={'connection_time': response_time}
            )
            
        except Exception as e:
            self.record_health_status(
                component='email',
                status='down',
                error_message=str(e),
                response_time=None
            )
            raise

    def check_storage(self):
        """Check file storage accessibility"""
        start_time = time.time()
        
        try:
            from django.core.files.storage import default_storage
            import tempfile
            import os
            
            # Test file write and read
            test_content = b'health check test file'
            test_filename = f'health_check_{timezone.now().timestamp()}.txt'
            
            # Write test file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(test_content)
                temp_file.flush()
                
                # Save to storage
                with open(temp_file.name, 'rb') as file:
                    saved_name = default_storage.save(test_filename, file)
                
                # Read from storage
                if default_storage.exists(saved_name):
                    with default_storage.open(saved_name, 'rb') as stored_file:
                        stored_content = stored_file.read()
                    
                    if stored_content != test_content:
                        raise Exception("Storage read/write test failed")
                    
                    # Clean up
                    default_storage.delete(saved_name)
                else:
                    raise Exception("File was not saved to storage")
                
                # Clean up temp file
                os.unlink(temp_file.name)
            
            response_time = (time.time() - start_time) * 1000
            
            self.record_health_status(
                component='storage',
                status='healthy',
                response_time=response_time,
                metrics={'storage_response_time': response_time}
            )
            
        except Exception as e:
            self.record_health_status(
                component='storage',
                status='down',
                error_message=str(e),
                response_time=None
            )
            raise

    def check_api(self):
        """Check external API connectivity"""
        start_time = time.time()
        
        try:
            # Test a simple HTTP request to verify internet connectivity
            response = requests.get('https://httpbin.org/status/200', timeout=10)
            
            if response.status_code == 200:
                response_time = (time.time() - start_time) * 1000
                
                if response_time < 1000:
                    status = 'healthy'
                elif response_time < 3000:
                    status = 'warning'
                else:
                    status = 'critical'
                
                self.record_health_status(
                    component='api',
                    status=status,
                    response_time=response_time,
                    metrics={'api_response_time': response_time}
                )
            else:
                raise Exception(f"API returned status code: {response.status_code}")
                
        except Exception as e:
            self.record_health_status(
                component='api',
                status='down',
                error_message=str(e),
                response_time=None
            )
            raise

    def check_queue(self):
        """Check task queue connectivity"""
        start_time = time.time()
        
        try:
            # Test Celery/Redis connectivity
            from celery import current_app
            
            # Get broker connection
            with current_app.connection() as conn:
                conn.ensure_connection(max_retries=3)
            
            response_time = (time.time() - start_time) * 1000
            
            self.record_health_status(
                component='queue',
                status='healthy',
                response_time=response_time,
                metrics={'queue_response_time': response_time}
            )
            
        except Exception as e:
            self.record_health_status(
                component='queue',
                status='down',
                error_message=str(e),
                response_time=None
            )
            raise

    def record_health_status(self, component, status, response_time=None, error_message=None, metrics=None):
        """Record health status in database"""
        SystemHealth.objects.create(
            component=component,
            status=status,
            response_time=response_time,
            error_message=error_message,
            metrics=metrics or {},
            checked_at=timezone.now()
        )
        
        status_style = self.style.SUCCESS if status == 'healthy' else (
            self.style.WARNING if status == 'warning' else self.style.ERROR
        )
        
        self.stdout.write(
            status_style(f'{component}: {status.upper()}')
        )