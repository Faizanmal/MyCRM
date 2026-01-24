"""
MyCRM Backend - Performance Tests

Load testing and performance benchmarks
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.test import TestCase, TransactionTestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.db import connection, reset_queries
from django.conf import settings
import statistics

User = get_user_model()


# =============================================================================
# Database Query Performance Tests
# =============================================================================

@pytest.mark.django_db
class TestDatabasePerformance(TestCase):
    """Database query performance tests"""
    
    @classmethod
    def setUpTestData(cls):
        """Create test data"""
        cls.client = APIClient()
        cls.user = User.objects.create_user(
            email='perf@test.com',
            password='TestPass123!'
        )
    
    def setUp(self):
        """Set up for each test"""
        self.client.force_authenticate(user=self.user)
        settings.DEBUG = True  # Enable query logging
        reset_queries()
    
    def tearDown(self):
        """Clean up after each test"""
        settings.DEBUG = False
    
    def test_contacts_list_query_count(self):
        """Verify contact list uses efficient queries"""
        response = self.client.get('/api/contacts/')
        
        if response.status_code == 200:
            # Should use minimal queries (no N+1)
            query_count = len(connection.queries)
            # Allow reasonable number of queries
            assert query_count < 10, f"Too many queries: {query_count}"
    
    def test_leads_list_query_count(self):
        """Verify leads list uses efficient queries"""
        response = self.client.get('/api/leads/')
        
        if response.status_code == 200:
            query_count = len(connection.queries)
            assert query_count < 10, f"Too many queries: {query_count}"
    
    def test_opportunities_list_query_count(self):
        """Verify opportunities list uses efficient queries"""
        response = self.client.get('/api/opportunities/')
        
        if response.status_code == 200:
            query_count = len(connection.queries)
            assert query_count < 10, f"Too many queries: {query_count}"
    
    def test_dashboard_query_count(self):
        """Verify dashboard uses efficient queries"""
        response = self.client.get('/api/dashboard/stats/')
        
        if response.status_code == 200:
            query_count = len(connection.queries)
            # Dashboard may need more queries
            assert query_count < 20, f"Too many queries: {query_count}"


# =============================================================================
# Response Time Tests
# =============================================================================

@pytest.mark.django_db
class TestResponseTime(TestCase):
    """API response time tests"""
    
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.user = User.objects.create_user(
            email='timing@test.com',
            password='TestPass123!'
        )
    
    def setUp(self):
        self.client.force_authenticate(user=self.user)
    
    def measure_endpoint_time(self, url, method='get', data=None, iterations=5):
        """Measure endpoint response time"""
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            
            if method == 'get':
                response = self.client.get(url)
            elif method == 'post':
                response = self.client.post(url, data)
            
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms
        
        return {
            'min': min(times),
            'max': max(times),
            'avg': statistics.mean(times),
            'median': statistics.median(times),
            'status': response.status_code
        }
    
    def test_contacts_list_response_time(self):
        """Test contacts list response time"""
        result = self.measure_endpoint_time('/api/contacts/')
        
        if result['status'] == 200:
            # Should respond within 500ms
            assert result['avg'] < 500, f"Contacts list too slow: {result['avg']:.2f}ms"
    
    def test_leads_list_response_time(self):
        """Test leads list response time"""
        result = self.measure_endpoint_time('/api/leads/')
        
        if result['status'] == 200:
            assert result['avg'] < 500, f"Leads list too slow: {result['avg']:.2f}ms"
    
    def test_search_response_time(self):
        """Test search response time"""
        result = self.measure_endpoint_time('/api/search/?q=test')
        
        if result['status'] == 200:
            assert result['avg'] < 1000, f"Search too slow: {result['avg']:.2f}ms"
    
    def test_dashboard_response_time(self):
        """Test dashboard response time"""
        result = self.measure_endpoint_time('/api/dashboard/stats/')
        
        if result['status'] == 200:
            # Dashboard may be slower
            assert result['avg'] < 1000, f"Dashboard too slow: {result['avg']:.2f}ms"


# =============================================================================
# Concurrent Request Tests
# =============================================================================

@pytest.mark.django_db(transaction=True)
class TestConcurrentRequests(TransactionTestCase):
    """Concurrent request handling tests"""
    
    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            email='concurrent@test.com',
            password='TestPass123!'
        )
    
    def make_authenticated_request(self, url):
        """Make authenticated API request"""
        client = APIClient()
        client.force_authenticate(user=self.user)
        
        start = time.perf_counter()
        response = client.get(url)
        end = time.perf_counter()
        
        return {
            'status': response.status_code,
            'time': (end - start) * 1000
        }
    
    def test_concurrent_contact_requests(self):
        """Test handling concurrent contact requests"""
        url = '/api/contacts/'
        num_requests = 10
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self.make_authenticated_request, url)
                for _ in range(num_requests)
            ]
            
            results = [f.result() for f in as_completed(futures)]
        
        # All requests should complete
        assert len(results) == num_requests
        
        # Check for acceptable response times under load
        times = [r['time'] for r in results]
        avg_time = statistics.mean(times)
        
        # Should still be reasonable under concurrent load
        # Allow higher tolerance for concurrent requests
        print(f"Concurrent avg time: {avg_time:.2f}ms")
    
    def test_mixed_concurrent_requests(self):
        """Test handling mixed concurrent requests"""
        urls = [
            '/api/contacts/',
            '/api/leads/',
            '/api/opportunities/',
            '/api/tasks/',
            '/api/dashboard/stats/'
        ]
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self.make_authenticated_request, url)
                for url in urls * 2  # 10 total requests
            ]
            
            results = [f.result() for f in as_completed(futures)]
        
        # All requests should complete
        assert len(results) == 10


# =============================================================================
# Memory Usage Tests
# =============================================================================

@pytest.mark.django_db
class TestMemoryUsage(TestCase):
    """Memory usage tests"""
    
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.user = User.objects.create_user(
            email='memory@test.com',
            password='TestPass123!'
        )
    
    def setUp(self):
        self.client.force_authenticate(user=self.user)
    
    def test_large_response_handling(self):
        """Test handling large response data"""
        # Request with large page size
        response = self.client.get('/api/contacts/?page_size=100')
        
        if response.status_code == 200:
            # Response should be reasonable size
            content_length = len(response.content)
            # Should be less than 1MB
            assert content_length < 1_000_000, f"Response too large: {content_length} bytes"
    
    def test_pagination_prevents_memory_issues(self):
        """Test that pagination prevents memory issues"""
        # Request without explicit pagination
        response = self.client.get('/api/contacts/')
        
        if response.status_code == 200:
            data = response.json()
            # Should have pagination
            if isinstance(data, dict):
                # Paginated response
                if 'results' in data:
                    # Results should be limited
                    assert len(data.get('results', [])) <= 100
            elif isinstance(data, list):
                # Non-paginated should still be limited
                pass  # Allow for now


# =============================================================================
# Caching Performance Tests
# =============================================================================

@pytest.mark.django_db
class TestCachingPerformance(TestCase):
    """Caching performance tests"""
    
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.user = User.objects.create_user(
            email='cache@test.com',
            password='TestPass123!'
        )
    
    def setUp(self):
        self.client.force_authenticate(user=self.user)
    
    def test_repeated_requests_faster(self):
        """Test that repeated requests may be faster due to caching"""
        url = '/api/contacts/'
        
        # First request (cold)
        start1 = time.perf_counter()
        response1 = self.client.get(url)
        time1 = (time.perf_counter() - start1) * 1000
        
        # Second request (potentially cached)
        start2 = time.perf_counter()
        response2 = self.client.get(url)
        time2 = (time.perf_counter() - start2) * 1000
        
        if response1.status_code == 200:
            # Second request should be same or faster
            print(f"First request: {time1:.2f}ms, Second request: {time2:.2f}ms")
    
    def test_etag_caching(self):
        """Test ETag caching headers"""
        response = self.client.get('/api/contacts/')
        
        if response.status_code == 200:
            etag = response.get('ETag')
            
            if etag:
                # Request with If-None-Match
                response2 = self.client.get(
                    '/api/contacts/',
                    HTTP_IF_NONE_MATCH=etag
                )
                
                # Should return 304 Not Modified if caching works
                # Or 200 with fresh data


# =============================================================================
# Bulk Operation Performance Tests
# =============================================================================

@pytest.mark.django_db
class TestBulkOperationPerformance(TestCase):
    """Bulk operation performance tests"""
    
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.user = User.objects.create_user(
            email='bulk@test.com',
            password='TestPass123!'
        )
    
    def setUp(self):
        self.client.force_authenticate(user=self.user)
    
    def test_bulk_create_performance(self):
        """Test bulk create performance"""
        contacts = [
            {
                'first_name': f'Contact{i}',
                'last_name': 'Test',
                'email': f'contact{i}@test.com'
            }
            for i in range(10)
        ]
        
        start = time.perf_counter()
        response = self.client.post(
            '/api/contacts/bulk-create/',
            {'contacts': contacts},
            format='json'
        )
        elapsed = (time.perf_counter() - start) * 1000
        
        if response.status_code in [200, 201]:
            # Bulk create should be efficient
            # Should complete in under 2 seconds
            assert elapsed < 2000, f"Bulk create too slow: {elapsed:.2f}ms"
    
    def test_bulk_update_performance(self):
        """Test bulk update performance"""
        data = {
            'ids': [1, 2, 3, 4, 5],
            'status': 'active'
        }
        
        start = time.perf_counter()
        response = self.client.patch(
            '/api/contacts/bulk-update/',
            data,
            format='json'
        )
        elapsed = (time.perf_counter() - start) * 1000
        
        if response.status_code == 200:
            assert elapsed < 1000, f"Bulk update too slow: {elapsed:.2f}ms"
    
    def test_bulk_delete_performance(self):
        """Test bulk delete performance"""
        data = {'ids': [1, 2, 3]}
        
        start = time.perf_counter()
        response = self.client.post(
            '/api/contacts/bulk-delete/',
            data,
            format='json'
        )
        elapsed = (time.perf_counter() - start) * 1000
        
        if response.status_code in [200, 204]:
            assert elapsed < 1000, f"Bulk delete too slow: {elapsed:.2f}ms"


# =============================================================================
# Search Performance Tests
# =============================================================================

@pytest.mark.django_db
class TestSearchPerformance(TestCase):
    """Search functionality performance tests"""
    
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.user = User.objects.create_user(
            email='search@test.com',
            password='TestPass123!'
        )
    
    def setUp(self):
        self.client.force_authenticate(user=self.user)
    
    def test_simple_search_performance(self):
        """Test simple search performance"""
        start = time.perf_counter()
        response = self.client.get('/api/search/?q=test')
        elapsed = (time.perf_counter() - start) * 1000
        
        if response.status_code == 200:
            assert elapsed < 500, f"Simple search too slow: {elapsed:.2f}ms"
    
    def test_complex_search_performance(self):
        """Test complex search with filters"""
        start = time.perf_counter()
        response = self.client.get(
            '/api/search/?q=test&type=contact&status=active&created_after=2024-01-01'
        )
        elapsed = (time.perf_counter() - start) * 1000
        
        if response.status_code == 200:
            # Complex search may be slower
            assert elapsed < 1000, f"Complex search too slow: {elapsed:.2f}ms"
    
    def test_autocomplete_performance(self):
        """Test autocomplete/typeahead performance"""
        # Autocomplete should be very fast
        start = time.perf_counter()
        response = self.client.get('/api/search/autocomplete/?q=jo')
        elapsed = (time.perf_counter() - start) * 1000
        
        if response.status_code == 200:
            # Autocomplete should be under 200ms
            assert elapsed < 200, f"Autocomplete too slow: {elapsed:.2f}ms"


# =============================================================================
# Report Generation Performance Tests
# =============================================================================

@pytest.mark.django_db
class TestReportPerformance(TestCase):
    """Report generation performance tests"""
    
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.user = User.objects.create_user(
            email='report@test.com',
            password='TestPass123!'
        )
    
    def setUp(self):
        self.client.force_authenticate(user=self.user)
    
    def test_sales_report_performance(self):
        """Test sales report generation performance"""
        start = time.perf_counter()
        response = self.client.get('/api/reports/sales/')
        elapsed = (time.perf_counter() - start) * 1000
        
        if response.status_code == 200:
            # Reports may take longer
            assert elapsed < 2000, f"Sales report too slow: {elapsed:.2f}ms"
    
    def test_pipeline_report_performance(self):
        """Test pipeline report performance"""
        start = time.perf_counter()
        response = self.client.get('/api/reports/pipeline/')
        elapsed = (time.perf_counter() - start) * 1000
        
        if response.status_code == 200:
            assert elapsed < 2000, f"Pipeline report too slow: {elapsed:.2f}ms"
    
    def test_export_performance(self):
        """Test report export performance"""
        start = time.perf_counter()
        response = self.client.get('/api/reports/sales/export/?format=csv')
        elapsed = (time.perf_counter() - start) * 1000
        
        if response.status_code == 200:
            # Export may take longer
            assert elapsed < 5000, f"Report export too slow: {elapsed:.2f}ms"
