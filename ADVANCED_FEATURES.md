# Advanced Features Documentation - Batch 2

## Overview
This document covers the 8 advanced features added to MyCRM in the second implementation phase.

## Table of Contents
1. [Advanced Analytics Dashboard](#advanced-analytics-dashboard)
2. [Email Campaign Management](#email-campaign-management)
3. [Comprehensive Audit Trail](#comprehensive-audit-trail)
4. [Customizable Dashboard Widgets](#customizable-dashboard-widgets)
5. [Real-time WebSocket Notifications](#real-time-websocket-notifications)
6. [Custom Field Builder](#custom-field-builder)
7. [Unified Activity Timeline](#unified-activity-timeline)
8. [Advanced Search & Filtering](#advanced-search--filtering)

---

## 1. Advanced Analytics Dashboard

### Features
- **Sales Forecasting**: Predict future revenue using machine learning
- **Conversion Funnel Analysis**: Track drop-off rates at each stage
- **Cohort Analysis**: Analyze customer behavior over time
- **Custom Metrics**: Build and track your own KPIs

### API Endpoints

#### Sales Forecast
```http
GET /api/v1/analytics/forecast/
```

Query Parameters:
- `start_date` (optional): Forecast start date
- `end_date` (optional): Forecast end date
- `periods` (default: 30): Number of periods to forecast

Response:
```json
{
  "forecast": [
    {"date": "2024-02-01", "predicted_value": 125000, "confidence_low": 110000, "confidence_high": 140000},
    {"date": "2024-02-02", "predicted_value": 127500, "confidence_low": 112000, "confidence_high": 143000}
  ],
  "model_accuracy": 0.85,
  "trend": "upward"
}
```

#### Conversion Funnel
```http
GET /api/v1/analytics/funnel/
```

Query Parameters:
- `start_date` (optional)
- `end_date` (optional)
- `stages` (optional): Comma-separated list of stages

Response:
```json
{
  "stages": [
    {"stage": "lead", "count": 1000, "conversion_rate": 100},
    {"stage": "qualified", "count": 450, "conversion_rate": 45},
    {"stage": "proposal", "count": 180, "conversion_rate": 18},
    {"stage": "won", "count": 75, "conversion_rate": 7.5}
  ],
  "overall_conversion": 7.5,
  "bottleneck_stage": "qualified"
}
```

#### Cohort Analysis
```http
GET /api/v1/analytics/cohort/
```

Query Parameters:
- `metric` (required): "retention", "revenue", or "activity"
- `period` (default: "month"): "day", "week", or "month"
- `cohorts` (default: 12): Number of cohorts to analyze

Response:
```json
{
  "cohorts": [
    {
      "cohort": "2024-01",
      "periods": [100, 85, 72, 65, 60, 58],
      "retention_rate": 58
    }
  ],
  "average_retention": 62.5,
  "best_cohort": "2024-01"
}
```

#### Custom Metrics
```http
GET /api/v1/analytics/metrics/
```

Query Parameters:
- `metrics` (required): Comma-separated list of metric names
- `start_date` (optional)
- `end_date` (optional)
- `group_by` (optional): "day", "week", "month"

Example:
```http
GET /api/v1/analytics/metrics/?metrics=avg_deal_size,win_rate,sales_velocity&group_by=month
```

---

## 2. Email Campaign Management

### Features
- Template management with variable substitution
- Campaign scheduling and tracking
- Email open/click tracking
- Unsubscribe management
- A/B testing support

### API Endpoints

#### Email Templates
```http
GET    /api/v1/email-templates/
POST   /api/v1/email-templates/
GET    /api/v1/email-templates/{id}/
PUT    /api/v1/email-templates/{id}/
DELETE /api/v1/email-templates/{id}/
```

Create Template:
```json
POST /api/v1/email-templates/
{
  "name": "Welcome Email",
  "subject": "Welcome to {{company_name}}, {{first_name}}!",
  "body_html": "<h1>Welcome!</h1><p>Hi {{first_name}},</p>...",
  "body_text": "Welcome! Hi {{first_name}},...",
  "variables": ["first_name", "company_name", "activation_link"],
  "category": "onboarding"
}
```

#### Email Campaigns
```http
GET    /api/v1/email-campaigns/
POST   /api/v1/email-campaigns/
GET    /api/v1/email-campaigns/{id}/
PUT    /api/v1/email-campaigns/{id}/
DELETE /api/v1/email-campaigns/{id}/
POST   /api/v1/email-campaigns/{id}/send/
POST   /api/v1/email-campaigns/{id}/schedule/
GET    /api/v1/email-campaigns/{id}/stats/
```

Create Campaign:
```json
POST /api/v1/email-campaigns/
{
  "name": "Q1 Product Launch",
  "template": 5,
  "segment_filter": {"industry": "technology", "size": "enterprise"},
  "scheduled_send": "2024-02-15T09:00:00Z",
  "from_email": "sales@company.com",
  "from_name": "Sales Team"
}
```

Send Campaign:
```http
POST /api/v1/email-campaigns/{id}/send/
```

Get Campaign Stats:
```json
GET /api/v1/email-campaigns/{id}/stats/

Response:
{
  "total_recipients": 1500,
  "sent": 1485,
  "delivered": 1470,
  "opened": 735,
  "clicked": 220,
  "bounced": 15,
  "unsubscribed": 8,
  "open_rate": 50.0,
  "click_rate": 14.97,
  "bounce_rate": 1.01
}
```

---

## 3. Comprehensive Audit Trail

### Features
- Track all CRUD operations
- Field-level change history
- Data snapshots for recovery
- Configurable retention policies
- Search and filter audit logs

### API Endpoints

#### Audit Trail
```http
GET /api/v1/audit-trail/
GET /api/v1/audit-trail/{id}/
GET /api/v1/audit-trail/stats/
```

Query Parameters:
- `action`: Filter by action (create, update, delete, view)
- `user`: Filter by user ID
- `model`: Filter by model name (e.g., "lead", "opportunity")
- `object_id`: Filter by specific object
- `start_date`: Filter by date range
- `end_date`: Filter by date range

Example:
```http
GET /api/v1/audit-trail/?model=lead&object_id=123&start_date=2024-01-01

Response:
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "user": "john@company.com",
      "user_name": "John Doe",
      "action": "update",
      "model_name": "lead",
      "object_id": "123",
      "object_repr": "Acme Corp Lead",
      "description": "Updated lead status",
      "changes": ["status"],
      "old_values": {"status": "new"},
      "new_values": {"status": "qualified"},
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Field History
```http
GET /api/v1/field-history/
GET /api/v1/field-history/{id}/
```

Query Parameters:
- `model`: Model name
- `object_id`: Object ID
- `field_name`: Specific field name

Example:
```http
GET /api/v1/field-history/?model=opportunity&object_id=456&field_name=amount

Response:
{
  "count": 8,
  "results": [
    {
      "id": 1,
      "field_name": "amount",
      "field_label": "Deal Amount",
      "old_value": "50000.00",
      "new_value": "75000.00",
      "old_value_display": "$50,000",
      "new_value_display": "$75,000",
      "changed_by": "Jane Smith",
      "changed_at": "2024-01-15T14:20:00Z"
    }
  ]
}
```

---

## 4. Customizable Dashboard Widgets

### Features
- 12 widget types (metrics, charts, tables, etc.)
- Drag-and-drop grid layout
- Real-time data updates
- Widget sharing and permissions
- Data caching for performance

### Widget Types
1. **metric_card**: Single KPI with trend
2. **line_chart**: Time series data
3. **bar_chart**: Comparative data
4. **pie_chart**: Distribution data
5. **table**: Tabular data
6. **funnel**: Conversion funnels
7. **goal**: Progress towards goals
8. **leaderboard**: Rankings
9. **timeline**: Activity timeline
10. **heatmap**: Density visualization
11. **map**: Geographic data
12. **list**: Simple lists

### API Endpoints

#### Widgets
```http
GET    /api/v1/widgets/
POST   /api/v1/widgets/
GET    /api/v1/widgets/{id}/
PUT    /api/v1/widgets/{id}/
DELETE /api/v1/widgets/{id}/
GET    /api/v1/widgets/{id}/data/
```

Create Widget:
```json
POST /api/v1/widgets/
{
  "name": "Sales This Month",
  "widget_type": "metric_card",
  "data_source": "opportunities_value",
  "query_params": {"stage": "won", "this_month": true},
  "size": "medium",
  "color_scheme": "blue",
  "icon": "currency-dollar",
  "value_prefix": "$",
  "refresh_interval": 300
}
```

Get Widget Data:
```http
GET /api/v1/widgets/{id}/data/

Response:
{
  "data": {
    "value": 125000,
    "label": "Sales This Month",
    "trend": "+15%",
    "comparison": "vs last month"
  },
  "cached": false
}
```

#### Dashboards
```http
GET    /api/v1/dashboards/
POST   /api/v1/dashboards/
GET    /api/v1/dashboards/{id}/
PUT    /api/v1/dashboards/{id}/
DELETE /api/v1/dashboards/{id}/
POST   /api/v1/dashboards/{id}/set_default/
POST   /api/v1/dashboards/{id}/add_widget/
DELETE /api/v1/dashboards/{id}/remove_widget/
```

Create Dashboard:
```json
POST /api/v1/dashboards/
{
  "name": "Sales Dashboard",
  "description": "Key sales metrics and pipeline",
  "layout_config": {"columns": 12, "rowHeight": 100},
  "is_default": true
}
```

Add Widget to Dashboard:
```json
POST /api/v1/dashboards/{id}/add_widget/
{
  "widget_id": 5,
  "row": 0,
  "column": 0,
  "width": 6,
  "height": 2
}
```

---

## 5. Real-time WebSocket Notifications

### Features
- Live notifications without polling
- Activity feed updates
- Task/lead/opportunity updates
- Connection status monitoring
- Mark notifications as read

### WebSocket Endpoints

#### Notifications Channel
```
ws://your-domain/ws/notifications/
```

Connection (requires authentication):
```javascript
const socket = new WebSocket('ws://localhost:8000/ws/notifications/');

socket.onopen = () => {
  console.log('Connected to notifications');
};

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Notification:', data);
};
```

Message Types:
1. **connection_established**: Confirms connection
2. **notification**: New notification
3. **activity**: Activity update
4. **task_update**: Task changed
5. **lead_update**: Lead changed

Mark Notification as Read:
```javascript
socket.send(JSON.stringify({
  type: 'mark_read',
  notification_id: 123
}));
```

#### Activity Feed Channel
```
ws://your-domain/ws/activity/
```

Receives real-time activity feed updates for all entities.

### Backend Integration

Send notification to user:
```python
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()
async_to_sync(channel_layer.group_send)(
    f'notifications_{user_id}',
    {
        'type': 'notification_message',
        'notification': {
            'id': notification.id,
            'title': 'New Lead Assigned',
            'message': 'You have been assigned a new lead',
            'url': '/leads/123',
            'timestamp': timezone.now().isoformat()
        }
    }
)
```

---

## 6. Custom Field Builder

### Features
- Add custom fields to any entity
- 14 field types
- Validation rules (required, min/max, regex)
- Field groups for organization
- Role-based visibility

### Field Types
1. **text**: Single-line text
2. **textarea**: Multi-line text
3. **number**: Integer values
4. **decimal**: Decimal values
5. **boolean**: Yes/No
6. **date**: Date picker
7. **datetime**: Date & time picker
8. **email**: Email validation
9. **url**: URL validation
10. **phone**: Phone number
11. **select**: Dropdown
12. **multiselect**: Multiple selection
13. **radio**: Radio buttons
14. **checkbox**: Checkboxes

### API Endpoints

#### Custom Fields
```http
GET    /api/v1/custom-fields/
POST   /api/v1/custom-fields/
GET    /api/v1/custom-fields/{id}/
PUT    /api/v1/custom-fields/{id}/
DELETE /api/v1/custom-fields/{id}/
POST   /api/v1/custom-fields/{id}/validate_value/
```

Create Custom Field:
```json
POST /api/v1/custom-fields/
{
  "name": "annual_revenue",
  "label": "Annual Revenue",
  "field_type": "decimal",
  "content_type": 5,  // Lead content type
  "is_required": true,
  "min_value": 0,
  "max_value": 999999999,
  "help_text": "Company's annual revenue in USD",
  "placeholder": "e.g., 1000000",
  "is_searchable": true,
  "is_filterable": true
}
```

Create Select Field with Options:
```json
POST /api/v1/custom-fields/
{
  "name": "company_size",
  "label": "Company Size",
  "field_type": "select",
  "content_type": 5,
  "options": [
    {"value": "1-10", "label": "1-10 employees"},
    {"value": "11-50", "label": "11-50 employees"},
    {"value": "51-200", "label": "51-200 employees"},
    {"value": "201+", "label": "201+ employees"}
  ]
}
```

#### Custom Field Values
```http
GET  /api/v1/custom-field-values/
POST /api/v1/custom-field-values/
GET  /api/v1/custom-field-values/for_object/
POST /api/v1/custom-field-values/bulk_update/
```

Get Values for Object:
```http
GET /api/v1/custom-field-values/for_object/?model=lead&object_id=123

Response:
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "custom_field": 5,
      "field_label": "Annual Revenue",
      "field_type": "decimal",
      "display_value": 2500000.00
    }
  ]
}
```

Bulk Update Values:
```json
POST /api/v1/custom-field-values/bulk_update/
{
  "model": "lead",
  "object_id": 123,
  "values": {
    "5": 2500000,
    "6": "51-200",
    "7": true
  }
}

Response:
{
  "updated": [
    {"field_id": "5", "field_name": "annual_revenue", "value": 2500000},
    {"field_id": "6", "field_name": "company_size", "value": "51-200"},
    {"field_id": "7", "field_name": "is_partner", "value": true}
  ],
  "errors": []
}
```

---

## 7. Unified Activity Timeline

### Features
- Consolidated view of all activities
- Multiple data sources (activity feed, audit trail, tasks, opportunities)
- Advanced filtering
- Entity-specific timelines
- User activity tracking

### API Endpoints

#### General Timeline
```http
GET /api/v1/timeline/
```

Query Parameters:
- `start_date`: Filter start date
- `end_date`: Filter end date
- `entity_type`: Filter by entity (lead, contact, opportunity, task)
- `entity_id`: Filter by specific entity
- `activity_types`: Comma-separated list
- `user_id`: Filter by user
- `limit`: Max results (default 50, max 500)

Example:
```http
GET /api/v1/timeline/?start_date=2024-01-01&entity_type=lead&limit=100

Response:
{
  "count": 45,
  "results": [
    {
      "id": "activity_123",
      "type": "activity",
      "action": "status_change",
      "description": "Lead status changed to Qualified",
      "entity_type": "lead",
      "entity_id": 123,
      "entity_name": "Acme Corp",
      "user": {
        "id": 5,
        "name": "John Doe",
        "email": "john@company.com"
      },
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Entity Timeline
```http
GET /api/v1/timeline/{entity_type}/{entity_id}/
```

Example:
```http
GET /api/v1/timeline/lead/123/

Response:
{
  "entity_type": "lead",
  "entity_id": 123,
  "count": 28,
  "timeline": [
    {
      "id": "activity_456",
      "type": "activity",
      "action": "created",
      "description": "Lead created",
      "user": "Jane Smith",
      "timestamp": "2024-01-10T09:00:00Z"
    },
    {
      "id": "audit_789",
      "type": "audit",
      "action": "update",
      "description": "Updated lead status",
      "user": "John Doe",
      "changes": ["status"],
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### User Activity
```http
GET /api/v1/timeline/user/
GET /api/v1/timeline/user/{user_id}/
```

Returns all activities performed by a user.

---

## 8. Advanced Search & Filtering

### Features (Built into all ViewSets)
- Full-text search across multiple fields
- Filter by any field
- Date range filtering
- Nested relationship filtering
- Ordering/sorting
- Pagination

### Available on All Resources

Query Parameters:
- `search`: Full-text search
- `ordering`: Sort by field (prefix with `-` for descending)
- `page`: Page number
- `page_size`: Results per page (default 20, max 100)
- Any model field for filtering

Examples:

#### Search Leads
```http
GET /api/v1/leads/?search=acme&status=qualified&ordering=-created_at&page=1&page_size=20
```

#### Filter Opportunities
```http
GET /api/v1/opportunities/?stage=proposal&amount__gte=50000&close_date__gte=2024-01-01&owner=5
```

#### Search with Multiple Filters
```http
GET /api/v1/contacts/?search=smith&company=Acme&tags=enterprise,vip&ordering=last_name
```

---

## Running the Features

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Start Redis (for Celery & WebSockets)
```bash
redis-server
```

### 4. Start Celery Worker
```bash
celery -A backend worker -l info
```

### 5. Start Celery Beat (for scheduled tasks)
```bash
celery -A backend beat -l info
```

### 6. Start Daphne (WebSocket support)
```bash
daphne -b 0.0.0.0 -p 8000 backend.asgi:application
```

Or use Django development server:
```bash
python manage.py runserver
```

---

## Frontend Integration Examples

### React Example: WebSocket Notifications
```javascript
import { useEffect, useState } from 'react';

function NotificationCenter() {
  const [notifications, setNotifications] = useState([]);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/notifications/');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'notification') {
        setNotifications(prev => [data.notification, ...prev]);
      }
    };
    
    setSocket(ws);
    
    return () => ws.close();
  }, []);

  const markAsRead = (notificationId) => {
    socket.send(JSON.stringify({
      type: 'mark_read',
      notification_id: notificationId
    }));
  };

  return (
    <div className="notifications">
      {notifications.map(notif => (
        <div key={notif.id} onClick={() => markAsRead(notif.id)}>
          <h4>{notif.title}</h4>
          <p>{notif.message}</p>
        </div>
      ))}
    </div>
  );
}
```

### React Example: Dashboard Widget
```javascript
import { useEffect, useState } from 'react';
import axios from 'axios';

function DashboardWidget({ widgetId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const response = await axios.get(`/api/v1/widgets/${widgetId}/data/`);
      setData(response.data.data);
      setLoading(false);
    };

    fetchData();
    
    // Refresh based on widget's refresh_interval
    const interval = setInterval(fetchData, 300000); // 5 min
    
    return () => clearInterval(interval);
  }, [widgetId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="widget">
      <h3>{data.label}</h3>
      <div className="value">{data.value}</div>
      <div className="trend">{data.trend}</div>
    </div>
  );
}
```

### React Example: Custom Fields Form
```javascript
import { useEffect, useState } from 'react';
import axios from 'axios';

function CustomFieldsForm({ entityType, entityId }) {
  const [fields, setFields] = useState([]);
  const [values, setValues] = useState({});

  useEffect(() => {
    // Load field definitions
    axios.get(`/api/v1/custom-fields/?model=${entityType}`)
      .then(res => setFields(res.data.results));

    // Load existing values
    axios.get(`/api/v1/custom-field-values/for_object/?model=${entityType}&object_id=${entityId}`)
      .then(res => {
        const vals = {};
        res.data.results.forEach(v => {
          vals[v.custom_field] = v.display_value;
        });
        setValues(vals);
      });
  }, [entityType, entityId]);

  const handleSave = async () => {
    await axios.post('/api/v1/custom-field-values/bulk_update/', {
      model: entityType,
      object_id: entityId,
      values: values
    });
  };

  return (
    <form>
      {fields.map(field => (
        <div key={field.id}>
          <label>{field.label}</label>
          {field.field_type === 'text' && (
            <input
              type="text"
              value={values[field.id] || ''}
              onChange={e => setValues({...values, [field.id]: e.target.value})}
              placeholder={field.placeholder}
            />
          )}
          {field.field_type === 'select' && (
            <select
              value={values[field.id] || ''}
              onChange={e => setValues({...values, [field.id]: e.target.value})}
            >
              {field.options.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          )}
        </div>
      ))}
      <button type="button" onClick={handleSave}>Save</button>
    </form>
  );
}
```

---

## Security Considerations

1. **WebSockets**: Require authentication for all WebSocket connections
2. **Audit Trail**: Configure appropriate retention policies
3. **Custom Fields**: Validate all user input, especially for regex patterns
4. **Email Campaigns**: Implement rate limiting for sending
5. **Dashboard Widgets**: Enforce permission checks for data access
6. **API Access**: Use JWT tokens for authentication
7. **Data Privacy**: Ensure audit logs comply with privacy regulations

---

## Performance Optimization

1. **Widget Caching**: Widgets cache data based on `refresh_interval`
2. **Database Indexing**: All models include appropriate indexes
3. **Query Optimization**: Use `select_related()` and `prefetch_related()`
4. **Pagination**: All list endpoints support pagination
5. **Redis**: Used for Celery, Channels, and caching

---

## Troubleshooting

### WebSockets Not Connecting
```bash
# Check Redis is running
redis-cli ping

# Check Daphne is running
ps aux | grep daphne

# Check channels configuration
python manage.py shell
>>> from channels.layers import get_channel_layer
>>> channel_layer = get_channel_layer()
>>> print(channel_layer)
```

### Custom Fields Not Saving
```python
# Validate field configuration
field = CustomField.objects.get(id=1)
field.full_clean()  # Will raise ValidationError if invalid

# Test value validation
field.validate_value("test value")
```

### Email Campaigns Not Sending
```bash
# Check Celery worker is running
celery -A backend inspect active

# Check Celery logs
tail -f celery.log
```

---

## Next Steps

1. Configure email backend for campaigns
2. Set up monitoring (Sentry, Prometheus)
3. Configure production WebSocket server (Daphne/Nginx)
4. Implement frontend components
5. Set up automated backups
6. Configure CDN for static assets
7. Enable SSL/TLS for WebSockets

---

## Support

For issues or questions:
- Check API documentation: http://localhost:8000/api/docs/
- View logs: `tail -f backend.log`
- Run tests: `python manage.py test`
