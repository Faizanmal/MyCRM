"""
Load Testing Scripts for MyCRM
Run these scripts to test system capacity and performance under load
"""

import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict
import statistics


@dataclass
class LoadTestResult:
    """Result of a single request"""
    success: bool
    response_time: float
    status_code: int
    error: str = None


class LoadTester:
    """Load testing utility for API endpoints"""
    
    def __init__(self, base_url: str, auth_token: str = None):
        self.base_url = base_url
        self.auth_token = auth_token
        self.headers = {}
        if auth_token:
            self.headers['Authorization'] = f'Bearer {auth_token}'
    
    def make_request(self, method: str, endpoint: str, data: dict = None) -> LoadTestResult:
        """Make a single HTTP request"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=self.headers, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=self.headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            
            return LoadTestResult(
                success=response.status_code < 400,
                response_time=elapsed,
                status_code=response.status_code
            )
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            return LoadTestResult(
                success=False,
                response_time=elapsed,
                status_code=0,
                error=str(e)
            )
    
    def run_load_test(
        self,
        method: str,
        endpoint: str,
        num_users: int = 10,
        requests_per_user: int = 10,
        data: dict = None
    ) -> Dict:
        """Run a load test with concurrent users"""
        print(f"\n{'='*60}")
        print(f"Starting Load Test")
        print(f"{'='*60}")
        print(f"Endpoint: {method.upper()} {endpoint}")
        print(f"Concurrent Users: {num_users}")
        print(f"Requests per User: {requests_per_user}")
        print(f"Total Requests: {num_users * requests_per_user}")
        print(f"{'='*60}\n")
        
        results: List[LoadTestResult] = []
        start_time = time.time()
        
        def user_session(user_id: int):
            """Simulate a user session"""
            session_results = []
            for i in range(requests_per_user):
                result = self.make_request(method, endpoint, data)
                session_results.append(result)
                # Small delay between requests to simulate real usage
                time.sleep(0.1)
            return session_results
        
        # Execute concurrent user sessions
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user_session, i) for i in range(num_users)]
            for future in as_completed(futures):
                results.extend(future.result())
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        response_times = [r.response_time for r in successful]
        
        stats = {
            'total_requests': len(results),
            'successful_requests': len(successful),
            'failed_requests': len(failed),
            'success_rate': (len(successful) / len(results)) * 100 if results else 0,
            'total_time': total_time,
            'requests_per_second': len(results) / total_time if total_time > 0 else 0,
        }
        
        if response_times:
            stats.update({
                'avg_response_time': statistics.mean(response_times),
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                'median_response_time': statistics.median(response_times),
                'p95_response_time': self._percentile(response_times, 95),
                'p99_response_time': self._percentile(response_times, 99),
            })
        
        self._print_results(stats)
        return stats
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of a list"""
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _print_results(self, stats: Dict):
        """Print test results"""
        print(f"\n{'='*60}")
        print(f"Load Test Results")
        print(f"{'='*60}")
        print(f"Total Requests:       {stats['total_requests']}")
        print(f"Successful:           {stats['successful_requests']}")
        print(f"Failed:               {stats['failed_requests']}")
        print(f"Success Rate:         {stats['success_rate']:.2f}%")
        print(f"Total Time:           {stats['total_time']:.2f}s")
        print(f"Requests/Second:      {stats['requests_per_second']:.2f}")
        
        if 'avg_response_time' in stats:
            print(f"\nResponse Times:")
            print(f"  Average:            {stats['avg_response_time']:.2f}ms")
            print(f"  Minimum:            {stats['min_response_time']:.2f}ms")
            print(f"  Maximum:            {stats['max_response_time']:.2f}ms")
            print(f"  Median:             {stats['median_response_time']:.2f}ms")
            print(f"  95th Percentile:    {stats['p95_response_time']:.2f}ms")
            print(f"  99th Percentile:    {stats['p99_response_time']:.2f}ms")
        print(f"{'='*60}\n")


def run_comprehensive_load_tests(base_url: str, auth_token: str = None):
    """Run comprehensive load tests on all major endpoints"""
    tester = LoadTester(base_url, auth_token)
    
    # Test scenarios with increasing load
    scenarios = [
        # Light load
        {'name': 'Light Load', 'users': 5, 'requests': 10},
        # Medium load
        {'name': 'Medium Load', 'users': 20, 'requests': 10},
        # Heavy load
        {'name': 'Heavy Load', 'users': 50, 'requests': 10},
        # Stress test
        {'name': 'Stress Test', 'users': 100, 'requests': 5},
    ]
    
    endpoints = [
        {'method': 'GET', 'endpoint': '/api/contacts/', 'name': 'List Contacts'},
        {'method': 'GET', 'endpoint': '/api/leads/', 'name': 'List Leads'},
        {'method': 'GET', 'endpoint': '/api/opportunities/', 'name': 'List Opportunities'},
    ]
    
    results = {}
    
    for scenario in scenarios:
        print(f"\n{'#'*60}")
        print(f"# {scenario['name']}")
        print(f"{'#'*60}")
        
        for endpoint_config in endpoints:
            test_name = f"{scenario['name']} - {endpoint_config['name']}"
            print(f"\nTesting: {test_name}")
            
            result = tester.run_load_test(
                method=endpoint_config['method'],
                endpoint=endpoint_config['endpoint'],
                num_users=scenario['users'],
                requests_per_user=scenario['requests']
            )
            
            results[test_name] = result
            
            # Wait between tests
            time.sleep(2)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*60}")
    for test_name, result in results.items():
        print(f"\n{test_name}:")
        print(f"  Success Rate: {result['success_rate']:.2f}%")
        print(f"  Req/Sec: {result['requests_per_second']:.2f}")
        if 'avg_response_time' in result:
            print(f"  Avg Response: {result['avg_response_time']:.2f}ms")
    
    return results


if __name__ == '__main__':
    # Configuration
    BASE_URL = 'http://localhost:8000'
    
    # You'll need to get an auth token first
    # AUTH_TOKEN = 'your-jwt-token-here'
    AUTH_TOKEN = None
    
    print("MyCRM Load Testing Suite")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print("=" * 60)
    
    # Run basic load test
    tester = LoadTester(BASE_URL, AUTH_TOKEN)
    
    # Example: Test contact list endpoint
    print("\nRunning basic load test on contacts endpoint...")
    tester.run_load_test(
        method='GET',
        endpoint='/api/contacts/',
        num_users=10,
        requests_per_user=5
    )
    
    # Uncomment to run comprehensive tests
    # print("\nRunning comprehensive load tests...")
    # run_comprehensive_load_tests(BASE_URL, AUTH_TOKEN)
