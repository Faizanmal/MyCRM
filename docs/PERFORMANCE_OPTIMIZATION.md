# Performance Optimization Guide for MyCRM

This guide provides recommendations and best practices for optimizing MyCRM performance in production environments.

## Table of Contents
- [Database Optimization](#database-optimization)
- [Caching Strategy](#caching-strategy)
- [Application Performance](#application-performance)
- [Frontend Optimization](#frontend-optimization)
- [Infrastructure Scaling](#infrastructure-scaling)
- [Monitoring & Profiling](#monitoring--profiling)

## Database Optimization

### 1. PostgreSQL Configuration

#### Connection Pooling
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # Keep connections open for 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'  # 30 second query timeout
        }
    }
}
```

#### Recommended PostgreSQL Settings
```sql
-- postgresql.conf recommendations for 8GB RAM server
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1  # For SSD storage
effective_io_concurrency = 200
work_mem = 16MB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 4
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
max_connections = 200
```

### 2. Query Optimization

#### Use Select Related and Prefetch Related
```python
# Bad - N+1 queries
leads = Lead.objects.all()
for lead in leads:
    print(lead.user.name)  # Separate query for each user

# Good - Single query with JOIN
leads = Lead.objects.select_related('user', 'assigned_to')

# Good - For many-to-many relationships
leads = Lead.objects.prefetch_related('tags', 'activities')
```

#### Add Database Indexes
```python
# models.py
class Lead(models.Model):
    email = models.EmailField(db_index=True)
    status = models.CharField(max_length=20, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['assigned_to', 'status']),
        ]
```

#### Use Database-Level Aggregation
```python
# Bad - Fetch all records then aggregate in Python
leads = Lead.objects.all()
total_value = sum(lead.value for lead in leads)

# Good - Aggregate at database level
from django.db.models import Sum
total_value = Lead.objects.aggregate(total=Sum('value'))['total']
```

### 3. Slow Query Monitoring

#### Enable Query Logging
```python
# settings.py
if DEBUG:
    LOGGING['loggers']['django.db.backends'] = {
        'level': 'DEBUG',
        'handlers': ['console'],
    }
```

#### Use Django Debug Toolbar
```python
# Only in development
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

## Caching Strategy

### 1. Redis Cache Configuration

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'mycrm',
        'TIMEOUT': 300,  # 5 minutes default
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'session',
        'TIMEOUT': 86400,  # 24 hours
    }
}

# Use Redis for sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'
```

### 2. View-Level Caching

```python
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

# Cache view for 5 minutes
@cache_page(60 * 5)
def my_view(request):
    return Response(data)

# For class-based views
class MyViewSet(viewsets.ModelViewSet):
    @method_decorator(cache_page(60 * 5))
    def list(self, request):
        return super().list(request)
```

### 3. Query Result Caching

```python
from django.core.cache import cache

def get_dashboard_stats(user_id):
    cache_key = f'dashboard_stats_{user_id}'
    stats = cache.get(cache_key)
    
    if stats is None:
        # Expensive query
        stats = {
            'total_leads': Lead.objects.filter(user=user_id).count(),
            'total_opportunities': Opportunity.objects.filter(user=user_id).count(),
            # ... more stats
        }
        cache.set(cache_key, stats, timeout=300)  # Cache for 5 minutes
    
    return stats
```

### 4. Template Fragment Caching

```django
{% load cache %}

{% cache 500 sidebar request.user.username %}
    <!-- Expensive sidebar content -->
{% endcache %}
```

## Application Performance

### 1. Async Task Processing

```python
# Use Celery for heavy operations
from celery import shared_task

@shared_task
def process_large_import(file_path):
    # Heavy processing
    # Don't block HTTP request/response
    pass

# In view
def import_view(request):
    file_path = save_uploaded_file(request.FILES['file'])
    process_large_import.delay(file_path)
    return Response({'message': 'Import started'})
```

### 2. Batch Operations

```python
# Bad - Individual saves
for data in large_dataset:
    Lead.objects.create(**data)

# Good - Bulk create
Lead.objects.bulk_create([Lead(**data) for data in large_dataset], batch_size=1000)

# Bulk update
leads = Lead.objects.filter(status='new')
leads.update(status='contacted', updated_at=timezone.now())
```

### 3. Pagination

```python
# REST Framework pagination settings
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,  # Reasonable default
    'MAX_PAGE_SIZE': 100,  # Prevent abuse
}
```

### 4. API Response Optimization

```python
# Use serializer fields sparingly
class LeadListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'name', 'email', 'status']  # Only essential fields

class LeadDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'  # All fields for detail view

# In ViewSet
class LeadViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'list':
            return LeadListSerializer
        return LeadDetailSerializer
```

## Frontend Optimization

### 1. Code Splitting

```javascript
// Next.js dynamic imports
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('@/components/HeavyComponent'), {
  loading: () => <Spinner />,
  ssr: false  // Disable server-side rendering if not needed
});
```

### 2. Image Optimization

```javascript
// Use Next.js Image component
import Image from 'next/image';

<Image
  src="/avatar.jpg"
  width={200}
  height={200}
  alt="User avatar"
  priority={false}  // Lazy load by default
/>
```

### 3. API Call Optimization

```typescript
// Use TanStack Query for caching
import { useQuery } from '@tanstack/react-query';

const { data, isLoading } = useQuery({
  queryKey: ['leads', filters],
  queryFn: () => fetchLeads(filters),
  staleTime: 5 * 60 * 1000,  // Consider data fresh for 5 minutes
  cacheTime: 30 * 60 * 1000,  // Keep in cache for 30 minutes
});
```

### 4. Bundle Size Optimization

```javascript
// next.config.js
module.exports = {
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.optimization.splitChunks.cacheGroups = {
        ...config.optimization.splitChunks.cacheGroups,
        common: {
          name: 'common',
          minChunks: 2,
          priority: 10,
        },
      };
    }
    return config;
  },
};
```

## Infrastructure Scaling

### 1. Horizontal Scaling

```yaml
# docker-compose.production.yml
services:
  backend:
    deploy:
      replicas: 3  # Run 3 instances
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 2. Gunicorn Workers

```bash
# Calculate workers: (2 x CPU cores) + 1
# For 4 CPU cores: 9 workers
gunicorn backend.wsgi:application \
  --workers 9 \
  --worker-class gthread \
  --threads 2 \
  --worker-tmp-dir /dev/shm \
  --max-requests 1000 \
  --max-requests-jitter 50
```

### 3. Celery Workers

```bash
# CPU-intensive tasks
celery -A backend worker -Q cpu_tasks --concurrency=4 -n worker1@%h

# IO-intensive tasks
celery -A backend worker -Q io_tasks --concurrency=10 -n worker2@%h

# Priority queue
celery -A backend worker -Q priority --concurrency=2 -n worker3@%h
```

### 4. Load Balancing

```nginx
# nginx.conf
upstream backend {
    least_conn;  # Use least connections algorithm
    server backend1:8000 max_fails=3 fail_timeout=30s;
    server backend2:8000 max_fails=3 fail_timeout=30s;
    server backend3:8000 max_fails=3 fail_timeout=30s;
}
```

## Monitoring & Profiling

### 1. Application Performance Monitoring

```python
# Use Django Silk for profiling in development
if DEBUG:
    INSTALLED_APPS += ['silk']
    MIDDLEWARE += ['silk.middleware.SilkyMiddleware']
```

### 2. Prometheus Metrics

```python
# Track custom business metrics
from core.enterprise.observability import MetricsCollector

metrics = MetricsCollector.get_instance()
metrics.increment_counter('leads_created_total', {'source': 'api'})
metrics.observe_histogram('api_request_duration', duration, {'endpoint': '/api/leads'})
```

### 3. Slow Query Alerts

```yaml
# Prometheus alert rules
- alert: SlowDatabaseQueries
  expr: histogram_quantile(0.95, rate(mycrm_db_query_duration_seconds_bucket[5m])) > 1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Database queries are slow"
    description: "95th percentile query time is {{ $value }}s"
```

### 4. Performance Budget

```javascript
// Lighthouse CI configuration
{
  "ci": {
    "collect": {
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "first-contentful-paint": ["error", {"maxNumericValue": 2000}],
        "largest-contentful-paint": ["error", {"maxNumericValue": 2500}],
        "cumulative-layout-shift": ["error", {"maxNumericValue": 0.1}],
        "total-blocking-time": ["error", {"maxNumericValue": 300}]
      }
    }
  }
}
```

## Performance Benchmarks

### Target Metrics

| Metric | Target | Critical |
|--------|--------|----------|
| API Response Time (p95) | < 200ms | < 500ms |
| Database Query Time (p95) | < 100ms | < 300ms |
| Page Load Time | < 2s | < 3s |
| Time to Interactive | < 3s | < 5s |
| Cache Hit Ratio | > 80% | > 60% |
| Error Rate | < 0.1% | < 1% |

### Load Testing

```python
# locustfile.py
from locust import HttpUser, task, between

class CRMUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/auth/login/", {
            "email": "test@example.com",
            "password": "password"
        })
        self.token = response.json()['access']
    
    @task(3)
    def list_leads(self):
        self.client.get("/api/v1/leads/", headers={
            "Authorization": f"Bearer {self.token}"
        })
    
    @task(1)
    def create_lead(self):
        self.client.post("/api/v1/leads/", json={
            "name": "Test Lead",
            "email": "lead@example.com"
        }, headers={
            "Authorization": f"Bearer {self.token}"
        })
```

Run load tests:
```bash
locust -f backend/locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10
```

## Quick Wins Checklist

- [ ] Enable Redis caching
- [ ] Add database indexes on frequently queried fields
- [ ] Use select_related/prefetch_related in querysets
- [ ] Enable Gunicorn with multiple workers
- [ ] Configure connection pooling
- [ ] Enable static file compression
- [ ] Set up CDN for static assets
- [ ] Enable browser caching headers
- [ ] Optimize images (WebP format, compression)
- [ ] Enable database query logging to identify slow queries
- [ ] Set up monitoring dashboards
- [ ] Configure alerting for performance degradation

## Additional Resources

- [Django Performance Tips](https://docs.djangoproject.com/en/stable/topics/performance/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Redis Best Practices](https://redis.io/docs/manual/performance/)
- [Next.js Performance](https://nextjs.org/docs/advanced-features/measuring-performance)

---

**Remember**: Always measure before and after optimization to verify improvements!
