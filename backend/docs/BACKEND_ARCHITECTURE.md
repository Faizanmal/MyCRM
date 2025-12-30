# MyCRM Backend Architecture

## Overview

MyCRM is a comprehensive Customer Relationship Management system built with Django and Django REST Framework. This document outlines the complete backend architecture.

## Project Structure

```
backend/
├── config/                     # Django project configuration
│   ├── settings.py             # Main settings
│   ├── urls.py                 # Root URL configuration
│   ├── celery.py               # Celery configuration
│   └── asgi.py                 # ASGI configuration for WebSockets
│
├── core/                       # Core application (Enterprise Features)
│   ├── models.py               # Core enterprise models
│   ├── settings_models.py      # User preferences, RBAC models
│   ├── settings_serializers.py # DRF serializers
│   ├── settings_views.py       # API views
│   ├── settings_urls.py        # URL routing
│   ├── settings_admin.py       # Django admin
│   ├── auth_views.py           # Authentication endpoints
│   ├── auth_urls.py            # Auth URL routing
│   ├── health_views.py         # Health check endpoints
│   ├── health_urls.py          # Health URL routing
│   ├── rbac_middleware.py      # RBAC permission system
│   ├── notification_service.py # Multi-channel notifications
│   ├── notification_templates.py # Email templates
│   ├── notification_signals.py # Auto-notification triggers
│   ├── celery_tasks.py         # Background tasks
│   ├── export_tasks.py         # Export processing tasks
│   ├── export_views.py         # Export API views
│   ├── websocket_consumers.py  # WebSocket handlers
│   ├── throttling.py           # API rate limiting
│   └── ai_recommendation_service.py # AI recommendations
│
├── contact_management/         # Contacts, Companies
├── opportunity_management/     # Deals, Pipeline
├── task_management/            # Tasks, Activities
├── activity_feed/              # Activity tracking
├── campaign_management/        # Email campaigns
├── email_tracking/             # Email tracking
└── analytics/                  # Analytics & reporting
```

## Core Features

### 1. User Preferences

```python
# Get user preferences
GET /api/v1/settings/preferences/

# Update preferences
PATCH /api/v1/settings/preferences/me/
{
    "theme": "dark",
    "compact_mode": true,
    "auto_refresh_interval": 60
}
```

### 2. Notification System

**Channels supported:**
- Email (with HTML templates)
- Push notifications
- In-app notifications
- SMS
- WebSocket real-time

**Usage:**
```python
from core.notification_service import notification_service

notification_service.send(
    user=user,
    notification_type='deal_won',
    title='Deal Won!',
    message='You closed a $50,000 deal',
    action_url='/deals/123',
    priority='high'
)
```

### 3. Role-Based Access Control (RBAC)

**Default Roles:**
| Role | Level | Description |
|------|-------|-------------|
| Admin | 4 | Full system access |
| Manager | 3 | Team management |
| Sales Rep | 2 | Standard CRM user |
| Viewer | 1 | Read-only |
| Guest | 0 | Minimal access |

**Usage in views:**
```python
from core.rbac_middleware import HasPermission, IsAdmin

class MyView(APIView):
    permission_classes = [HasPermission]
    required_permission = 'view_contacts'
```

### 4. Data Export

```python
# Create export job
POST /api/v1/settings/export/
{
    "format": "csv",
    "entities": ["contacts", "deals"],
    "date_range": "month"
}

# Check status
GET /api/v1/settings/export/{id}/status/

# Download
GET /api/v1/settings/export/{id}/download/
```

### 5. Authentication

```python
# Register
POST /api/v1/auth/register/
{
    "email": "user@example.com",
    "password": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
}

# Login
POST /api/v1/auth/login/
{
    "email": "user@example.com",
    "password": "securepass123"
}

# Response
{
    "user": {...},
    "permissions": [...],
    "tokens": {
        "access": "...",
        "refresh": "..."
    }
}
```

### 6. Health Monitoring

```python
# Basic health check
GET /api/v1/healthz/

# Detailed health
GET /api/v1/health/

# Prometheus metrics
GET /api/v1/metrics/
```

## Celery Tasks

### Scheduled Tasks (via Celery Beat)

| Task | Schedule | Description |
|------|----------|-------------|
| `send_daily_digests` | 9:00 AM daily | Email digest |
| `send_weekly_digests` | Monday 9:00 AM | Weekly report |
| `check_overdue_tasks` | Every 30 min | Task reminders |
| `cleanup_old_notifications` | 2:00 AM daily | DB cleanup |
| `generate_ai_recommendations` | 6:00 AM daily | AI insights |

**Start workers:**
```bash
# Main worker
celery -A config worker -l info

# Beat scheduler
celery -A config beat -l info

# With specific queues
celery -A config worker -l info -Q notifications,exports,analytics
```

## WebSocket Events

**Connect:**
```javascript
ws = new WebSocket('wss://api.mycrm.com/ws/notifications/?token=JWT_TOKEN');
```

**Event types:**
- `notification` - General notifications
- `deal_update` - Deal stage changes
- `mention` - @mentions
- `achievement` - Gamification unlocks
- `export_progress` - Export job updates
- `presence` - Team online status

## API Rate Limiting

| Endpoint Type | Rate Limit |
|--------------|------------|
| General | 60/minute, 1000/hour |
| Anonymous | 20/minute, 100/hour |
| Export | 10/hour |
| AI Operations | 30/minute |
| Login | 5/minute |

## Environment Variables

```env
# Database
DATABASE_URL=postgres://user:pass@localhost:5432/mycrm

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CACHE_URL=redis://localhost:6379/1

# Email
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=user@example.com
EMAIL_HOST_PASSWORD=password
DEFAULT_FROM_EMAIL=noreply@example.com

# Frontend
FRONTEND_URL=https://app.mycrm.com

# Security
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=api.mycrm.com
```

## Database Models

### Core Models
- `AuditLog` - Security audit trail
- `SystemConfiguration` - System settings
- `APIKey` - API key management
- `Workflow` - Automated workflows
- `Integration` - External integrations
- `Notification` - In-app notifications

### Settings Models
- `UserPreference` - User settings
- `NotificationPreference` - Channel settings
- `ExportJob` - Export history
- `UserRole` - RBAC roles
- `UserRoleAssignment` - Role assignments

## Running Migrations

```bash
# Generate migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Initialize default roles
python manage.py init_roles
```

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test core.tests_settings

# With coverage
coverage run --source='.' manage.py test
coverage report
```

## Security Features

1. **JWT Authentication** with refresh tokens
2. **RBAC** with permission caching
3. **Audit logging** for critical actions
4. **Rate limiting** per endpoint type
5. **Password reset** with secure tokens
6. **IP-based security alerts**

## Performance Optimizations

1. **Permission caching** (5 minutes)
2. **Query optimization** with select_related
3. **Async task processing** with Celery
4. **Database indexes** on frequently queried fields
5. **Connection pooling** for database

## API Documentation

Full API documentation available at:
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI Schema: `/api/schema/`
