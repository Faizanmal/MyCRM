# MyCRM Quick Reference Card

## 🚀 Quick Start

```bash
# Setup (one-time)
./setup.sh

# Start services
redis-server                              # Terminal 1
cd backend && python manage.py runserver  # Terminal 2
cd backend && celery -A backend worker -l info  # Terminal 3 (optional)
```

## 🔑 API Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Returns: {"access":"TOKEN","refresh":"REFRESH_TOKEN"}
```

## 📋 Common API Calls

### Leads

```bash
# List leads
GET /api/v1/leads/
GET /api/v1/leads/?status=qualified&priority=high&assigned_to_me=true

# Create lead
POST /api/v1/leads/
{"first_name":"John","last_name":"Doe","email":"john@example.com","company_name":"Acme"}

# Get lead
GET /api/v1/leads/{id}/

# Update lead
PATCH /api/v1/leads/{id}/
{"status":"qualified","lead_score":85}

# Convert to contact/opportunity
POST /api/v1/leads/{id}/convert/

# Get statistics
GET /api/v1/leads/statistics/

# Bulk operations
POST /api/v1/leads/bulk_update/
{"ids":[1,2,3],"action":"update","data":{"status":"contacted"}}
```

### Contacts

```bash
# List contacts
GET /api/v1/contacts/
GET /api/v1/contacts/?contact_type=customer&search=acme

# Create contact
POST /api/v1/contacts/
{"first_name":"Jane","last_name":"Smith","email":"jane@example.com"}

# Get statistics
GET /api/v1/contacts/statistics/
```

### Opportunities

```bash
# List opportunities
GET /api/v1/opportunities/
GET /api/v1/opportunities/?stage=proposal&assigned_to_me=true

# Create opportunity
POST /api/v1/opportunities/
{"name":"Deal","contact":1,"amount":50000,"stage":"proposal","probability":75}

# Get pipeline stats
GET /api/v1/opportunities/pipeline/
```

### Tasks

```bash
# List tasks
GET /api/v1/tasks/
GET /api/v1/tasks/?assigned_to_me=true&overdue=true

# Create task
POST /api/v1/tasks/
{"title":"Follow up","priority":"high","assigned_to":1,"due_date":"2025-12-01"}

# Complete task
POST /api/v1/tasks/{id}/complete/

# Get statistics
GET /api/v1/tasks/statistics/
```

## 📥📤 CSV Import/Export

```bash
# Import leads
POST /api/v1/import/leads/
- file: leads.csv
- mapping: {"Email":"email","Name":"first_name","Company":"company_name"}
- update_existing: false
- skip_errors: true

# Export leads
GET /api/v1/export/leads/?status=qualified
> leads_export.csv

# Get import template
GET /api/v1/import/leads/
> leads_template.csv
```

## 🤖 AI Lead Scoring

```bash
# Score single lead
POST /api/v1/scoring/
{"action":"score","lead_id":123}

# Bulk score leads (background)
POST /api/v1/scoring/
{"action":"bulk_score","lead_ids":[1,2,3]}

# Retrain model (admin only)
POST /api/v1/scoring/
{"action":"retrain"}

# Get scoring statistics
GET /api/v1/scoring/
```

## ⚙️ Workflows

```bash
# List workflows
GET /api/v1/workflows/
GET /api/v1/workflows/?status=active

# Create workflow
POST /api/v1/workflows/
{
  "name":"Auto-assign CA leads",
  "trigger_type":"record_created",
  "trigger_conditions":{"model":"lead","conditions":{"state":"CA"}},
  "actions":[
    {"type":"assign_record","params":{"user_id":5}},
    {"type":"send_email","params":{"template":"welcome"}}
  ],
  "status":"active"
}

# Execute workflow
POST /api/v1/workflows/{id}/execute/
{"trigger_data":{}}

# Activate/Deactivate
POST /api/v1/workflows/{id}/activate/
POST /api/v1/workflows/{id}/deactivate/

# Get execution history
GET /api/v1/workflows/{id}/executions/
```

## 🔔 Notification Templates

```bash
# List templates
GET /api/v1/notification-templates/
GET /api/v1/notification-templates/?type=email&active_only=true

# Create template
POST /api/v1/notification-templates/
{
  "name":"Lead Assignment",
  "notification_type":"email",
  "subject_template":"New Lead: {{lead.company_name}}",
  "body_template":"Hi {{user.first_name}}, you have a new lead...",
  "variables":["user.first_name","lead.company_name"],
  "is_active":true
}
```

## 🔍 Query Parameters

### Common Filters
- `?search=keyword` - Full-text search
- `?status=value` - Filter by status
- `?priority=high` - Filter by priority
- `?assigned_to_me=true` - Show my items
- `?assigned_to=5` - Filter by user ID
- `?ordering=-created_at` - Sort (use `-` for descending)
- `?page=2` - Pagination
- `?page_size=50` - Items per page

### Date Filters
- `?created_at__gte=2025-01-01` - After date
- `?created_at__lte=2025-12-31` - Before date
- `?due_date__isnull=false` - Has due date

## 📊 Statistics Endpoints

```bash
GET /api/v1/leads/statistics/
GET /api/v1/contacts/statistics/
GET /api/v1/opportunities/pipeline/
GET /api/v1/tasks/statistics/
GET /api/v1/scoring/
```

## 🔐 Authentication Headers

```bash
# All authenticated requests need:
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
-H "Content-Type: application/json"
```

## 📚 Documentation

- **Interactive API Docs:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/
- **Feature Guide:** FEATURES.md
- **Python Examples:** api_examples.py

## 🧪 Testing Endpoints

```bash
# Quick test
curl http://localhost:8000/api/v1/leads/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create test lead
curl -X POST http://localhost:8000/api/v1/leads/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name":"Test",
    "last_name":"User",
    "email":"test@example.com",
    "company_name":"Test Co",
    "lead_source":"website"
  }'

# Score test lead
curl -X POST http://localhost:8000/api/v1/scoring/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action":"score","lead_id":1}'
```

## 🐛 Troubleshooting

### Celery not running
```bash
# Check Redis
redis-cli ping  # Should return PONG

# Check Celery worker
celery -A backend inspect active
```

### Database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Import issues
- Check CSV encoding (should be UTF-8)
- Verify field mapping
- Check error_details in response

## 📞 Quick Support

- **GitHub Issues:** https://github.com/Faizanmal/MyCRM/issues
- **Documentation:** FEATURES.md
- **Examples:** api_examples.py

---

**Pro Tip:** Use the interactive Swagger UI at `/api/docs/` for testing without curl!
