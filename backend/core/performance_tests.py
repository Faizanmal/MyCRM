"""
Performance and Load Testing Suite for MyCRM
This file contains load testing, stress testing, and performance benchmarking tools
"""

import time
import concurrent.futures
import requests
import statistics
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import override_settings
from rest_framework.test import APIClient

User = get_user_model()


class PerformanceTestCase(TestCase):
    """Base class for performance tests"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='perftest',
            email='perf@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def measure_time(self, func, *args, **kwargs):
        """Measure execution time of a function"""
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        return result, (end - start) * 1000  # Return time in milliseconds
    
    def measure_query_count(self, func, *args, **kwargs):
        """Measure number of database queries"""
        from django.test.utils import CaptureQueriesContext
        with CaptureQueriesContext(connection) as context:
            result = func(*args, **kwargs)
        return result, len(context.captured_queries)


class DatabasePerformanceTest(PerformanceTestCase):
    """Test database query performance"""
    
    def test_bulk_create_performance(self):
        """Test bulk create performance"""
        from contact_management.models import Contact
        
        contacts = [
            Contact(
                first_name=f'User{i}',
                last_name=f'Test{i}',
                email=f'user{i}@example.com',
                created_by=self.user
            )
            for i in range(1000)
        ]
        
        _, elapsed = self.measure_time(Contact.objects.bulk_create, contacts)
        print(f"Bulk created 1000 contacts in {elapsed:.2f}ms")
        self.assertLess(elapsed, 5000, "Bulk create took too long")
    
    def test_query_optimization(self):
        """Test query optimization with select_related and prefetch_related"""
        from contact_management.models import Contact
        
        # Create test data
        for i in range(100):
            Contact.objects.create(
                first_name=f'User{i}',
                last_name=f'Test{i}',
                email=f'user{i}@example.com',
                assigned_to=self.user,
                created_by=self.user
            )
        
        # Without optimization
        def query_without_optimization():
            contacts = Contact.objects.all()
            for contact in contacts:
                _ = contact.assigned_to
                _ = contact.created_by
        
        # With optimization
        def query_with_optimization():
            contacts = Contact.objects.select_related('assigned_to', 'created_by').all()
            for contact in contacts:
                _ = contact.assigned_to
                _ = contact.created_by
        
        _, queries_without = self.measure_query_count(query_without_optimization)
        _, queries_with = self.measure_query_count(query_with_optimization)
        
        print(f"Queries without optimization: {queries_without}")
        print(f"Queries with optimization: {queries_with}")
        
        self.assertLess(queries_with, queries_without)
    
    def test_pagination_performance(self):
        """Test pagination performance"""
        from contact_management.models import Contact
        
        # Create test data
        Contact.objects.bulk_create([
            Contact(
                first_name=f'User{i}',
                last_name=f'Test{i}',
                email=f'user{i}@example.com',
                created_by=self.user
            )
            for i in range(1000)
        ])
        
        # Test paginated query
        def paginated_query():
            return list(Contact.objects.all()[:20])
        
        _, elapsed = self.measure_time(paginated_query)
        print(f"Paginated query (20 items) took {elapsed:.2f}ms")
        self.assertLess(elapsed, 100, "Pagination too slow")


class APIPerformanceTest(PerformanceTestCase):
    """Test API endpoint performance"""
    
    def test_list_endpoint_performance(self):
        """Test list endpoint response time"""
        from contact_management.models import Contact
        
        # Create test data
        Contact.objects.bulk_create([
            Contact(
                first_name=f'User{i}',
                last_name=f'Test{i}',
                email=f'user{i}@example.com',
                created_by=self.user
            )
            for i in range(100)
        ])
        
        def test_list():
            response = self.client.get('/api/contacts/')
            return response
        
        response, elapsed = self.measure_time(test_list)
        print(f"List endpoint took {elapsed:.2f}ms")
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed, 1000, "List endpoint too slow")
    
    def test_create_endpoint_performance(self):
        """Test create endpoint performance"""
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testcreate@example.com'
        }
        
        def test_create():
            return self.client.post('/api/contacts/', data)
        
        response, elapsed = self.measure_time(test_create)
        print(f"Create endpoint took {elapsed:.2f}ms")
        self.assertEqual(response.status_code, 201)
        self.assertLess(elapsed, 500, "Create endpoint too slow")


class ConcurrentLoadTest(TransactionTestCase):
    """Test concurrent user load"""
    
    def setUp(self):
        self.base_url = 'http://localhost:8000'
        self.user = User.objects.create_user(
            username='loadtest',
            email='load@example.com',
            password='testpass123'
        )
    
    def make_request(self, endpoint):
        """Make a single API request"""
        try:
            start = time.time()
            # You'll need to authenticate properly for production tests
            response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            elapsed = (time.time() - start) * 1000
            return {
                'status': response.status_code,
                'time': elapsed,
                'success': response.status_code == 200
            }
        except Exception as e:
            return {
                'status': 0,
                'time': 0,
                'success': False,
                'error': str(e)
            }
    
    def test_concurrent_users(self):
        """Test system with concurrent users"""
        num_users = 10
        requests_per_user = 5
        endpoint = '/api/contacts/'
        
        results = []
        
        def user_session(user_id):
            session_results = []
            for _ in range(requests_per_user):
                result = self.make_request(endpoint)
                session_results.append(result)
                time.sleep(0.1)  # Small delay between requests
            return session_results
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user_session, i) for i in range(num_users)]
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        successful = [r for r in results if r['success']]
        response_times = [r['time'] for r in successful]
        
        if response_times:
            print("\n=== Concurrent Load Test Results ===")
            print(f"Total users: {num_users}")
            print(f"Requests per user: {requests_per_user}")
            print(f"Total requests: {len(results)}")
            print(f"Successful requests: {len(successful)}")
            print(f"Failed requests: {len(results) - len(successful)}")
            print(f"Success rate: {len(successful)/len(results)*100:.2f}%")
            print(f"Total time: {total_time:.2f}s")
            print(f"Requests per second: {len(results)/total_time:.2f}")
            print(f"Average response time: {statistics.mean(response_times):.2f}ms")
            print(f"Min response time: {min(response_times):.2f}ms")
            print(f"Max response time: {max(response_times):.2f}ms")
            print(f"Median response time: {statistics.median(response_times):.2f}ms")


class MemoryPerformanceTest(TestCase):
    """Test memory usage and performance"""
    
    def test_memory_efficient_queries(self):
        """Test memory-efficient query patterns"""
        from contact_management.models import Contact
        
        # Create test data
        Contact.objects.bulk_create([
            Contact(
                first_name=f'User{i}',
                last_name=f'Test{i}',
                email=f'user{i}@example.com',
                created_by=User.objects.create_user(
                    username=f'creator{i}',
                    email=f'creator{i}@example.com',
                    password='pass123'
                )
            )
            for i in range(100)
        ])
        
        # Test with iterator for large datasets
        def memory_efficient_iteration():
            contacts = Contact.objects.all().iterator(chunk_size=20)
            count = sum(1 for _ in contacts)
            return count
        
        count = memory_efficient_iteration()
        self.assertEqual(count, 100)


class CachePerformanceTest(PerformanceTestCase):
    """Test caching performance"""
    
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    })
    def test_cache_effectiveness(self):
        """Test cache effectiveness for frequently accessed data"""
        from django.core.cache import cache
        from contact_management.models import Contact
        
        contact = Contact.objects.create(
            first_name='Cache',
            last_name='Test',
            email='cache@example.com',
            created_by=self.user
        )
        
        cache_key = f'contact_{contact.id}'
        
        # First access (no cache)
        def query_without_cache():
            cache.delete(cache_key)
            return Contact.objects.get(id=contact.id)
        
        # Second access (with cache)
        def query_with_cache():
            cached = cache.get(cache_key)
            if cached is None:
                cached = Contact.objects.get(id=contact.id)
                cache.set(cache_key, cached, 300)
            return cached
        
        _, time_without = self.measure_time(query_without_cache)
        
        # Prime the cache
        query_with_cache()
        
        _, time_with = self.measure_time(query_with_cache)
        
        print(f"Query without cache: {time_without:.2f}ms")
        print(f"Query with cache: {time_with:.2f}ms")
        print(f"Cache speedup: {time_without/time_with:.2f}x")
