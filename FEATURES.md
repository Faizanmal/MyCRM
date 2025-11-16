# MyCRM - Feature Implementation Guide

## 🚀 New Features Implemented

This document describes the comprehensive features that have been added to MyCRM.

---

## 1. Unified REST API (v1)

A comprehensive, versioned REST API for all CRM resources with consistent patterns.

### Endpoints

#### **Leads API** - `/api/v1/leads/`
- `GET /api/v1/leads/` - List all leads with filtering, search, pagination
- `POST /api/v1/leads/` - Create a new lead
- `GET /api/v1/leads/{id}/` - Get lead details
- `PATCH /api/v1/leads/{id}/` - Update a lead
- `DELETE /api/v1/leads/{id}/` - Delete a lead
- `POST /api/v1/leads/{id}/convert/` - Convert lead to contact & opportunity
- `GET /api/v1/leads/statistics/` - Get lead statistics
- `POST /api/v1/leads/bulk_update/` - Bulk update/delete leads

**Query Parameters:**
- `status` - Filter by status (new, contacted, qualified, etc.)
- `priority` - Filter by priority (low, medium, high, urgent)
- `assigned_to_me=true` - Show only leads assigned to current user
- `search` - Full-text search across name, email, company
- `ordering` - Sort by field (e.g., `-created_at`, `lead_score`)

#### **Contacts API** - `/api/v1/contacts/`
- `GET /api/v1/contacts/` - List all contacts
- `POST /api/v1/contacts/` - Create a new contact
- `GET /api/v1/contacts/{id}/` - Get contact details
- `PATCH /api/v1/contacts/{id}/` - Update a contact
- `DELETE /api/v1/contacts/{id}/` - Delete a contact
- `GET /api/v1/contacts/statistics/` - Get contact statistics
- `POST /api/v1/contacts/bulk_update/` - Bulk operations

#### **Opportunities API** - `/api/v1/opportunities/`
- `GET /api/v1/opportunities/` - List all opportunities
- `POST /api/v1/opportunities/` - Create a new opportunity
- `GET /api/v1/opportunities/{id}/` - Get opportunity details
- `PATCH /api/v1/opportunities/{id}/` - Update an opportunity
- `DELETE /api/v1/opportunities/{id}/` - Delete an opportunity
- `GET /api/v1/opportunities/pipeline/` - Get pipeline statistics
- `POST /api/v1/opportunities/bulk_update/` - Bulk operations

#### **Tasks API** - `/api/v1/tasks/`
- `GET /api/v1/tasks/` - List all tasks
- `POST /api/v1/tasks/` - Create a new task
- `GET /api/v1/tasks/{id}/` - Get task details
- `PATCH /api/v1/tasks/{id}/` - Update a task
- `POST /api/v1/tasks/{id}/complete/` - Mark task as completed
- `GET /api/v1/tasks/statistics/` - Get task statistics

---

## 2. CSV Import/Export

Bulk data import and export with field mapping and validation.

### Import CSV

**Endpoint:** `POST /api/v1/import/{resource_type}/`

**Supported Resources:** `leads`, `contacts`, `opportunities`, `tasks`

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/import/leads/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@leads.csv" \
  -F 'mapping={"first_name":"first_name","last_name":"last_name","email":"email","company":"company_name"}'
```

**Parameters:**
- `file` - CSV file to import
- `mapping` - JSON mapping of CSV columns to model fields
- `update_existing` - Boolean, update existing records by email (default: false)
- `skip_errors` - Boolean, continue on validation errors (default: true)

**Response:**
```json
{
  "success": true,
  "imported": 150,
  "errors": 5,
  "error_details": [
    {
      "row": 23,
      "error": "Invalid email format",
      "data": {...}
    }
  ]
}
```

### Export CSV

**Endpoint:** `GET /api/v1/export/{resource_type}/`

**Example:**
```bash
curl http://localhost:8000/api/v1/export/leads/?status=qualified \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o leads_export.csv
```

### Get Import Template

**Endpoint:** `GET /api/v1/import/{resource_type}/`

Downloads a CSV template with correct field headers.

---

## 3. AI-Powered Lead Scoring

Machine learning-based lead scoring with automatic model retraining.

### Score Leads

**Endpoint:** `POST /api/v1/scoring/`

**Actions:**

#### Score Single Lead
```json
{
  "action": "score",
  "lead_id": 123
}
```

**Response:**
```json
{
  "success": true,
  "lead_id": 123,
  "score": 85,
  "factors": [
    {"factor": "source_score", "importance": 0.25},
    {"factor": "estimated_value", "importance": 0.20}
  ]
}
```

#### Bulk Score Leads (Background)
```json
{
  "action": "bulk_score",
  "lead_ids": [123, 124, 125]
}
```

#### Retrain Model (Admin Only)
```json
{
  "action": "retrain"
}
```

### Get Scoring Statistics

**Endpoint:** `GET /api/v1/scoring/`

**Response:**
```json
{
  "total_leads": 500,
  "high_score": 125,
  "medium_score": 250,
  "low_score": 125,
  "average_score": 62.5
}
```

### Lead Scoring Features

The ML model uses these features:
- Lead source quality
- Lead age (days since creation)
- Company size
- Estimated deal value
- Engagement count (interactions)
- Contact completeness (email, phone)
- Job title/seniority level

**Automatic Retraining:** The model retrains weekly (every Monday at 2 AM) using the latest conversion data.

---

## 4. Workflow Automation

Rule-based workflow automation with triggers and actions.

### Workflows API

**Endpoint:** `/api/v1/workflows/`

#### List Workflows
```bash
GET /api/v1/workflows/
```

#### Create Workflow
```bash
POST /api/v1/workflows/
```

**Example Workflow:**
```json
{
  "name": "Auto-assign leads from CA",
  "description": "Automatically assign leads from California to West Coast team",
  "trigger_type": "record_created",
  "trigger_conditions": {
    "model": "lead",
    "conditions": {
      "state": "CA"
    }
  },
  "actions": [
    {
      "type": "assign_record",
      "params": {
        "user_id": 5
      }
    },
    {
      "type": "send_email",
      "params": {
        "template_id": "welcome_email",
        "to": "{{lead.email}}"
      }
    },
    {
      "type": "create_task",
      "params": {
        "title": "Follow up with {{lead.first_name}}",
        "due_days": 2
      }
    }
  ],
  "status": "active"
}
```

#### Workflow Actions

Supported action types:
- `send_email` - Send email using template
- `create_task` - Create a follow-up task
- `update_field` - Update a field value
- `assign_record` - Assign to user
- `send_notification` - Send in-app notification
- `create_record` - Create related record
- `webhook` - Call external webhook
- `wait` - Delay execution

#### Execute Workflow Manually
```bash
POST /api/v1/workflows/{id}/execute/
```

#### Get Workflow Executions
```bash
GET /api/v1/workflows/{id}/executions/
```

---

## 5. Notification System

Real-time notifications with customizable preferences.

### Notification Preferences

Users can configure notification channels and types:

**Channels:**
- Email
- Push notifications
- In-app notifications
- SMS

**Preferences:**
- Mentions
- Assignments
- Comments
- Updates
- Daily/Weekly digest
- Do Not Disturb hours

### API Endpoints

The notification system is integrated into the activity feed module. Notifications are automatically created for:
- User mentions
- Task assignments
- Comments on followed items
- Status changes
- Reminders

---

## 6. Background Jobs with Celery

Asynchronous task processing for heavy operations.

### Celery Tasks

#### Lead Scoring
- `core.tasks.score_lead(lead_id)` - Score single lead
- `core.tasks.bulk_score_leads(lead_ids)` - Score multiple leads
- `core.tasks.retrain_lead_scoring_model()` - Retrain ML model

#### Workflows
- `core.tasks.execute_workflow(workflow_id, trigger_data)` - Execute workflow

#### Scheduled Tasks
- Model retraining: Every Monday at 2 AM
- Daily digest: Every day at 8 AM
- Overdue task check: Every 30 minutes

### Running Celery

Start Celery worker:
```bash
cd backend
celery -A backend worker --loglevel=info
```

Start Celery beat (scheduler):
```bash
celery -A backend beat --loglevel=info
```

---

## 7. API Documentation

Interactive API documentation with Swagger UI and ReDoc.

### Access Documentation

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

### Features

- Interactive API testing
- Request/response examples
- Authentication support
- Schema validation
- Download OpenAPI spec

---

## Installation & Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Redis (for Celery)

**Option 1: Local Redis**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis
```

**Option 2: Docker Redis**
```bash
docker run -d -p 6379:6379 redis:latest
```

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Start Development Servers

**Terminal 1: Django**
```bash
python manage.py runserver
```

**Terminal 2: Celery Worker**
```bash
celery -A backend worker --loglevel=info
```

**Terminal 3: Celery Beat (optional)**
```bash
celery -A backend beat --loglevel=info
```

---

## API Usage Examples

### Authentication

All API endpoints require JWT authentication:

```bash
# Get JWT token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Use token in requests
curl http://localhost:8000/api/v1/leads/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create a Lead

```bash
curl -X POST http://localhost:8000/api/v1/leads/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "company_name": "Acme Corp",
    "lead_source": "website",
    "priority": "high"
  }'
```

### Search and Filter

```bash
# Search leads
curl "http://localhost:8000/api/v1/leads/?search=Acme&status=qualified" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get high-priority leads assigned to me
curl "http://localhost:8000/api/v1/leads/?priority=high&assigned_to_me=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Convert Lead

```bash
curl -X POST http://localhost:8000/api/v1/leads/123/convert/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Import Leads from CSV

```bash
curl -X POST http://localhost:8000/api/v1/import/leads/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@leads.csv" \
  -F 'mapping={"First Name":"first_name","Last Name":"last_name","Email":"email"}'
```

---

## Configuration

### Settings (backend/settings.py)

```python
# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'

# API Rate Limiting
RATE_LIMIT_ENABLED = True
DEFAULT_RATE_LIMIT = 100  # requests per hour

# Lead Scoring
LEAD_SCORING_MODEL_PATH = BASE_DIR / 'models' / 'lead_scoring_model.pkl'
LEAD_SCORING_RETRAIN_SCHEDULE = '0 2 * * 1'  # Monday 2 AM

# Email Configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

---

## Testing

### Test Lead Scoring

```python
from lead_management.models import Lead
from core.lead_scoring import LeadScoringEngine

# Create test lead
lead = Lead.objects.create(
    first_name="Test",
    last_name="User",
    email="test@example.com",
    company_name="Test Co",
    lead_source="referral",
    estimated_value=10000
)

# Score the lead
engine = LeadScoringEngine()
score, factors = engine.score_lead(lead)
print(f"Lead score: {score}")
print(f"Factors: {factors}")
```

### Test Workflow

```python
from core.models import Workflow
from core.workflows import WorkflowEngine

# Create workflow
workflow = Workflow.objects.create(
    name="Test Workflow",
    trigger_type="record_created",
    actions=[
        {
            "type": "send_notification",
            "params": {
                "message": "New lead created!"
            }
        }
    ],
    status="active"
)

# Execute workflow
WorkflowEngine.execute_workflow(workflow, {"lead_id": 123})
```

---

## Performance Considerations

### Optimization Tips

1. **Use pagination** for large datasets
2. **Filter at the database level** with query parameters
3. **Use bulk operations** for multiple record updates
4. **Process heavy tasks in background** with Celery
5. **Cache frequently accessed data** with Redis
6. **Use select_related/prefetch_related** for efficient queries

### Scaling

- **Horizontal scaling:** Deploy multiple Celery workers
- **Database optimization:** Add indexes for frequently filtered fields
- **Caching:** Use Redis for API response caching
- **CDN:** Serve static files from CDN
- **Load balancing:** Use Nginx/HAProxy for multiple Django instances

---

## Troubleshooting

### Celery not running tasks

```bash
# Check Celery worker status
celery -A backend inspect active

# Check Redis connection
redis-cli ping
```

### Import errors

- Verify CSV encoding is UTF-8
- Check field mapping matches model fields
- Review error_details in response for specific issues

### Lead scoring not working

```bash
# Check if model file exists
ls backend/models/lead_scoring_model.pkl

# Retrain model
python manage.py shell
>>> from core.tasks import retrain_lead_scoring_model
>>> retrain_lead_scoring_model()
```

---

## Future Enhancements

Planned features for next releases:

1. **Real-time notifications** with WebSockets
2. **Advanced analytics** with custom dashboards
3. **Integration marketplace** with pre-built connectors
4. **Mobile app** (React Native)
5. **Multi-tenancy** for SaaS deployment
6. **AI chat assistant** for CRM queries
7. **Document OCR** for automated data extraction
8. **Sales forecasting** with time-series models

---

## Support

For questions or issues:
- GitHub Issues: https://github.com/YourOrg/MyCRM/issues
- Documentation: https://docs.mycrm.com
- API Reference: http://localhost:8000/api/docs/

---

**Version:** 1.0.0  
**Last Updated:** November 2025
