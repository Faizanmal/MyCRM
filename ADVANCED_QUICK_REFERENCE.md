# Advanced Features Quick Reference

## 🚀 8 NEW ENTERPRISE FEATURES

### 1. 📊 Analytics Dashboard
```bash
# Sales forecast
GET /api/v1/analytics/forecast/?periods=30

# Conversion funnel
GET /api/v1/analytics/funnel/

# Cohort analysis
GET /api/v1/analytics/cohort/?metric=retention&period=month

# Custom metrics
GET /api/v1/analytics/metrics/?metrics=win_rate,avg_deal_size
```

### 2. 📧 Email Campaigns
```bash
# Templates
GET/POST /api/v1/email-templates/
PUT /api/v1/email-templates/{id}/

# Campaigns
GET/POST /api/v1/email-campaigns/
POST /api/v1/email-campaigns/{id}/send/
GET /api/v1/email-campaigns/{id}/stats/
```

### 3. 🔍 Audit Trail
```bash
# View audit logs
GET /api/v1/audit-trail/?model=lead&object_id=123

# Field history
GET /api/v1/field-history/?model=opportunity&field_name=amount

# Statistics
GET /api/v1/audit-trail/stats/
```

### 4. 📱 Dashboard Widgets
```bash
# Widgets
GET/POST /api/v1/widgets/
GET /api/v1/widgets/{id}/data/

# Dashboards
GET/POST /api/v1/dashboards/
POST /api/v1/dashboards/{id}/add_widget/
POST /api/v1/dashboards/{id}/set_default/
```

### 5. ⚡ Real-time WebSockets
```javascript
// Connect
const ws = new WebSocket('ws://localhost:8000/ws/notifications/');

// Receive notifications
ws.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log(data.notification);
};

// Mark as read
ws.send(JSON.stringify({
  type: 'mark_read',
  notification_id: 123
}));
```

### 6. 🔧 Custom Fields
```bash
# Create field
POST /api/v1/custom-fields/
{
  "name": "revenue",
  "label": "Annual Revenue",
  "field_type": "decimal",
  "content_type": 5
}

# Set values
POST /api/v1/custom-field-values/bulk_update/
{
  "model": "lead",
  "object_id": 1,
  "values": {"1": 100000}
}

# Get values
GET /api/v1/custom-field-values/for_object/?model=lead&object_id=1
```

### 7. 📅 Activity Timeline
```bash
# Unified timeline
GET /api/v1/timeline/?limit=50

# Entity timeline
GET /api/v1/timeline/lead/123/

# User activity
GET /api/v1/timeline/user/
GET /api/v1/timeline/user/{id}/
```

### 8. 🔎 Advanced Search
```bash
# Full-text search
GET /api/v1/leads/?search=acme&status=qualified

# Date range filter
GET /api/v1/opportunities/?close_date__gte=2024-01-01

# Ordering
GET /api/v1/contacts/?ordering=-created_at

# Pagination
GET /api/v1/tasks/?page=2&page_size=50
```

---

## 📦 Widget Types (12 Available)

1. **metric_card** - Single KPI with trend
2. **line_chart** - Time series visualization
3. **bar_chart** - Comparative bar chart
4. **pie_chart** - Distribution pie chart
5. **table** - Tabular data display
6. **funnel** - Conversion funnel chart
7. **goal** - Progress towards goal
8. **leaderboard** - Rankings/top performers
9. **timeline** - Activity timeline
10. **heatmap** - Density visualization
11. **map** - Geographic visualization
12. **list** - Simple list display

---

## 🔢 Custom Field Types (14 Available)

1. **text** - Single-line text input
2. **textarea** - Multi-line text area
3. **number** - Integer numbers
4. **decimal** - Decimal numbers
5. **boolean** - Yes/No checkbox
6. **date** - Date picker
7. **datetime** - Date & time picker
8. **email** - Email with validation
9. **url** - URL with validation
10. **phone** - Phone number
11. **select** - Dropdown list
12. **multiselect** - Multi-select dropdown
13. **radio** - Radio button group
14. **checkbox** - Checkbox group

---

## 🚦 Setup Checklist

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Update Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Start Redis
```bash
redis-server
```

### 4. Start Services
```bash
# Terminal 1: Django + WebSockets
python manage.py runserver
# OR
daphne -b 0.0.0.0 -p 8000 backend.asgi:application

# Terminal 2: Celery Worker
celery -A backend worker -l info

# Terminal 3: Celery Beat
celery -A backend beat -l info
```

### 5. Access Documentation
```
http://localhost:8000/api/docs/
```

---

## 🎯 Common Use Cases

### Create Sales Dashboard
```python
# 1. Create widgets
widget1 = requests.post('/api/v1/widgets/', {
    'name': 'Total Revenue',
    'widget_type': 'metric_card',
    'data_source': 'opportunities_value'
})

widget2 = requests.post('/api/v1/widgets/', {
    'name': 'Pipeline',
    'widget_type': 'funnel',
    'data_source': 'pipeline_stages'
})

# 2. Create dashboard
dashboard = requests.post('/api/v1/dashboards/', {
    'name': 'Sales Dashboard',
    'is_default': True
})

# 3. Add widgets
requests.post(f'/api/v1/dashboards/{dashboard_id}/add_widget/', {
    'widget_id': widget1_id,
    'row': 0, 'column': 0, 'width': 6, 'height': 2
})
```

### Send Email Campaign
```python
# 1. Create template
template = requests.post('/api/v1/email-templates/', {
    'name': 'Product Launch',
    'subject': 'New Product: {{product_name}}',
    'body_html': '<h1>Introducing {{product_name}}</h1>'
})

# 2. Create campaign
campaign = requests.post('/api/v1/email-campaigns/', {
    'name': 'Q1 Launch',
    'template': template_id,
    'segment_filter': {'industry': 'technology'}
})

# 3. Send campaign
requests.post(f'/api/v1/email-campaigns/{campaign_id}/send/')

# 4. Check stats
stats = requests.get(f'/api/v1/email-campaigns/{campaign_id}/stats/')
```

### Add Custom Fields
```python
# 1. Define field
field = requests.post('/api/v1/custom-fields/', {
    'name': 'company_size',
    'label': 'Company Size',
    'field_type': 'select',
    'content_type': 5,  # Lead
    'options': [
        {'value': 'small', 'label': 'Small (1-50)'},
        {'value': 'medium', 'label': 'Medium (51-200)'},
        {'value': 'large', 'label': 'Large (201+)'}
    ]
})

# 2. Set value
requests.post('/api/v1/custom-field-values/bulk_update/', {
    'model': 'lead',
    'object_id': 123,
    'values': {field_id: 'medium'}
})
```

### Track Activity
```python
# Get all activity for a lead
timeline = requests.get('/api/v1/timeline/lead/123/')

# Get user's recent activity
user_activity = requests.get('/api/v1/timeline/user/')

# Get audit trail
audit = requests.get('/api/v1/audit-trail/?model=lead&object_id=123')
```

---

## 🛠️ Troubleshooting

### WebSocket Won't Connect
```bash
# Check Redis
redis-cli ping

# Check Daphne
ps aux | grep daphne

# Test connection
curl --include \
     --no-buffer \
     --header "Connection: Upgrade" \
     --header "Upgrade: websocket" \
     --header "Host: localhost:8000" \
     --header "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
     --header "Sec-WebSocket-Version: 13" \
     http://localhost:8000/ws/notifications/
```

### Celery Not Processing
```bash
# Check worker
celery -A backend inspect active

# Check queue
celery -A backend inspect reserved

# Purge queue
celery -A backend purge
```

### Database Issues
```bash
# Reset migrations
python manage.py migrate --fake-initial

# Create superuser
python manage.py createsuperuser

# Shell access
python manage.py shell
```

---

## 📊 Performance Tips

1. **Widget Caching**: Set appropriate `refresh_interval` (300-3600s)
2. **Timeline Pagination**: Use `limit` parameter (max 500)
3. **Audit Retention**: Configure `AuditConfiguration` per model
4. **WebSocket Pooling**: Use connection pooling for Redis
5. **Database Indexing**: All models have optimized indexes

---

## 🔒 Security Notes

- All endpoints require JWT authentication
- WebSockets require authenticated connections
- Audit trail logs all data changes
- Custom fields support role-based visibility
- Email campaigns validate recipients

---

## 📚 Documentation Files

1. **ADVANCED_FEATURES.md** - Complete feature guide
2. **ADVANCED_IMPLEMENTATION_SUMMARY.md** - Technical summary
3. **advanced_features_examples.py** - API test scripts
4. **ADVANCED_QUICK_REFERENCE.md** - This file
5. **FEATURES.md** - First batch features (Batch 1)
6. **IMPLEMENTATION_SUMMARY.md** - Batch 1 summary

---

## 🎓 Learn More

- API Docs: http://localhost:8000/api/docs/
- Swagger UI: http://localhost:8000/api/docs/swagger/
- ReDoc: http://localhost:8000/api/docs/redoc/

---

## ⚡ Quick Start

```bash
# Clone and setup
cd /workspaces/MyCRM/backend

# Install
pip install -r requirements.txt

# Database
python manage.py migrate

# Create admin
python manage.py createsuperuser

# Start everything (use tmux/screen)
redis-server &
celery -A backend worker -l info &
celery -A backend beat -l info &
python manage.py runserver

# Test
python ../advanced_features_examples.py
```

---

## 🎉 You're Ready!

All 8 advanced features are now available in your MyCRM system:

✅ Analytics Dashboard  
✅ Email Campaigns  
✅ Audit Trail  
✅ Dashboard Widgets  
✅ Real-time WebSockets  
✅ Custom Fields  
✅ Activity Timeline  
✅ Advanced Search  

Start building amazing CRM experiences! 🚀
