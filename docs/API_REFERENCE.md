# 📚 MyCRM API Reference

## Overview

MyCRM provides a comprehensive RESTful API built with Django REST Framework. All endpoints follow REST conventions and return JSON responses.

**Base URL:** `https://api.mycrm.io/api/v1`

**API Version:** `v1`

---

## 🔐 Authentication

### JWT Authentication

MyCRM uses JWT (JSON Web Tokens) for API authentication.

#### Obtain Token Pair

```http
POST /api/v1/auth/token/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "admin"
  }
}
```

#### Refresh Token

```http
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Token Configuration

| Setting | Value |
|---------|-------|
| Access Token Lifetime | 15 minutes |
| Refresh Token Lifetime | 7 days |
| Token Rotation | Enabled |
| Blacklisting | Enabled |

### Using the Token

Include the access token in the `Authorization` header:

```http
GET /api/v1/contacts/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### API Key Authentication

For server-to-server integrations, use API keys:

```http
GET /api/v1/contacts/
X-API-Key: sk_live_abc123def456
```

---

## 📋 Response Format

### Success Response

```json
{
  "status": "success",
  "data": { ... },
  "meta": {
    "timestamp": "2024-12-09T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### Paginated Response

```json
{
  "count": 150,
  "next": "https://api.mycrm.io/api/v1/contacts/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

### Error Response

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["Enter a valid email address."]
    }
  },
  "meta": {
    "timestamp": "2024-12-09T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (successful delete) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict (duplicate resource) |
| 422 | Unprocessable Entity |
| 429 | Too Many Requests (rate limited) |
| 500 | Internal Server Error |

---

## 📇 Contacts API

### List Contacts

```http
GET /api/v1/contacts/
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number (default: 1) |
| `page_size` | integer | Items per page (default: 20, max: 100) |
| `search` | string | Search in name, email, company |
| `status` | string | Filter by status (active, inactive) |
| `tags` | string | Filter by tags (comma-separated) |
| `created_after` | datetime | Filter by creation date |
| `created_before` | datetime | Filter by creation date |
| `ordering` | string | Sort field (prefix `-` for descending) |

**Example:**
```http
GET /api/v1/contacts/?search=john&status=active&ordering=-created_at
```

**Response:**
```json
{
  "count": 45,
  "next": "https://api.mycrm.io/api/v1/contacts/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "phone": "+1-555-123-4567",
      "company": "Acme Corp",
      "job_title": "CEO",
      "status": "active",
      "tags": ["enterprise", "decision-maker"],
      "custom_fields": {
        "industry": "Technology",
        "company_size": "500-1000"
      },
      "owner": {
        "id": 5,
        "name": "Jane Smith"
      },
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-12-01T14:22:00Z"
    }
  ]
}
```

### Create Contact

```http
POST /api/v1/contacts/
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1-555-123-4567",
  "company": "Acme Corp",
  "job_title": "CEO",
  "tags": ["enterprise"],
  "custom_fields": {
    "industry": "Technology"
  }
}
```

### Get Contact

```http
GET /api/v1/contacts/{id}/
```

### Update Contact

```http
PATCH /api/v1/contacts/{id}/
Content-Type: application/json

{
  "job_title": "CTO"
}
```

### Delete Contact

```http
DELETE /api/v1/contacts/{id}/
```

### Bulk Operations

#### Bulk Create
```http
POST /api/v1/contacts/bulk/
Content-Type: application/json

{
  "contacts": [
    {"first_name": "John", "last_name": "Doe", "email": "john@example.com"},
    {"first_name": "Jane", "last_name": "Smith", "email": "jane@example.com"}
  ]
}
```

#### Bulk Update
```http
PATCH /api/v1/contacts/bulk/
Content-Type: application/json

{
  "ids": [1, 2, 3],
  "data": {
    "status": "inactive"
  }
}
```

#### Bulk Delete
```http
DELETE /api/v1/contacts/bulk/
Content-Type: application/json

{
  "ids": [1, 2, 3]
}
```

---

## 🎣 Leads API

### List Leads

```http
GET /api/v1/leads/
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | new, contacted, qualified, converted, lost |
| `source` | string | website, referral, cold_call, etc. |
| `score_min` | integer | Minimum lead score (0-100) |
| `score_max` | integer | Maximum lead score (0-100) |
| `owner` | integer | Owner user ID |
| `assigned_to` | integer | Assigned user ID |

**Response:**
```json
{
  "count": 120,
  "results": [
    {
      "id": 1,
      "name": "New Lead - Acme Corp",
      "company": "Acme Corp",
      "email": "contact@acme.com",
      "phone": "+1-555-987-6543",
      "status": "qualified",
      "source": "website",
      "score": 85,
      "estimated_value": 50000.00,
      "probability": 0.65,
      "owner": {
        "id": 5,
        "name": "Jane Smith"
      },
      "assigned_to": {
        "id": 3,
        "name": "Bob Wilson"
      },
      "activities_count": 12,
      "last_activity_at": "2024-12-08T16:45:00Z",
      "created_at": "2024-11-01T09:00:00Z"
    }
  ]
}
```

### Create Lead

```http
POST /api/v1/leads/
Content-Type: application/json

{
  "name": "New Lead - Tech Corp",
  "company": "Tech Corp",
  "email": "info@techcorp.com",
  "phone": "+1-555-111-2222",
  "source": "website",
  "estimated_value": 75000,
  "notes": "Interested in enterprise plan"
}
```

### Score Lead (AI)

```http
POST /api/v1/leads/{id}/score/
```

**Response:**
```json
{
  "id": 1,
  "score": 85,
  "score_breakdown": {
    "company_size": 20,
    "engagement": 25,
    "budget_fit": 20,
    "timeline": 15,
    "decision_maker": 5
  },
  "recommendation": "High priority - schedule discovery call",
  "scored_at": "2024-12-09T10:30:00Z"
}
```

### Convert Lead to Opportunity

```http
POST /api/v1/leads/{id}/convert/
Content-Type: application/json

{
  "opportunity_name": "Acme Corp - Enterprise Deal",
  "pipeline_id": 1,
  "stage_id": 2,
  "value": 75000,
  "close_date": "2025-03-31"
}
```

---

## 💼 Opportunities API

### List Opportunities

```http
GET /api/v1/opportunities/
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `pipeline` | integer | Pipeline ID |
| `stage` | integer | Stage ID |
| `status` | string | open, won, lost |
| `value_min` | decimal | Minimum value |
| `value_max` | decimal | Maximum value |
| `close_date_after` | date | Close date range start |
| `close_date_before` | date | Close date range end |

**Response:**
```json
{
  "count": 45,
  "results": [
    {
      "id": 1,
      "name": "Acme Corp - Enterprise Deal",
      "contact": {
        "id": 1,
        "name": "John Doe",
        "company": "Acme Corp"
      },
      "pipeline": {
        "id": 1,
        "name": "Enterprise Sales"
      },
      "stage": {
        "id": 3,
        "name": "Proposal",
        "probability": 50
      },
      "value": 75000.00,
      "probability": 0.50,
      "weighted_value": 37500.00,
      "expected_close_date": "2025-03-31",
      "products": [
        {
          "id": 1,
          "name": "Enterprise License",
          "quantity": 50,
          "unit_price": 1200.00,
          "total": 60000.00
        }
      ],
      "owner": {
        "id": 5,
        "name": "Jane Smith"
      },
      "created_at": "2024-11-15T10:00:00Z"
    }
  ]
}
```

### Move Stage

```http
POST /api/v1/opportunities/{id}/move-stage/
Content-Type: application/json

{
  "stage_id": 4,
  "notes": "Client approved proposal, moving to negotiation"
}
```

### Close Won

```http
POST /api/v1/opportunities/{id}/close-won/
Content-Type: application/json

{
  "actual_value": 80000,
  "close_date": "2024-12-09",
  "notes": "Deal signed!"
}
```

### Close Lost

```http
POST /api/v1/opportunities/{id}/close-lost/
Content-Type: application/json

{
  "loss_reason": "competitor",
  "competitor_name": "Competitor X",
  "notes": "Lost on price"
}
```

---

## 📋 Tasks API

### List Tasks

```http
GET /api/v1/tasks/
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | pending, in_progress, completed, cancelled |
| `priority` | string | low, medium, high, urgent |
| `type` | string | call, email, meeting, follow_up, other |
| `due_date` | date | Filter by due date |
| `overdue` | boolean | Filter overdue tasks |
| `assigned_to` | integer | Assigned user ID |

**Response:**
```json
{
  "count": 28,
  "results": [
    {
      "id": 1,
      "title": "Follow up with John Doe",
      "description": "Discuss enterprise pricing",
      "type": "call",
      "priority": "high",
      "status": "pending",
      "due_date": "2024-12-10T14:00:00Z",
      "is_overdue": false,
      "related_to": {
        "type": "lead",
        "id": 1,
        "name": "Acme Corp Lead"
      },
      "assigned_to": {
        "id": 5,
        "name": "Jane Smith"
      },
      "created_by": {
        "id": 1,
        "name": "Admin"
      },
      "completed_at": null,
      "created_at": "2024-12-08T09:00:00Z"
    }
  ]
}
```

### Create Task

```http
POST /api/v1/tasks/
Content-Type: application/json

{
  "title": "Schedule demo call",
  "description": "Demo of premium features",
  "type": "call",
  "priority": "high",
  "due_date": "2024-12-12T15:00:00Z",
  "related_to_type": "opportunity",
  "related_to_id": 1,
  "assigned_to_id": 5
}
```

### Complete Task

```http
POST /api/v1/tasks/{id}/complete/
Content-Type: application/json

{
  "notes": "Call completed, client interested",
  "outcome": "positive"
}
```

---

## 📈 Analytics API

### Dashboard Metrics

```http
GET /api/v1/analytics/dashboard/
```

**Response:**
```json
{
  "summary": {
    "total_leads": 150,
    "leads_this_month": 45,
    "leads_change": 12.5,
    "total_opportunities": 65,
    "pipeline_value": 1250000.00,
    "weighted_pipeline": 625000.00,
    "deals_won_this_month": 8,
    "revenue_this_month": 180000.00,
    "win_rate": 32.5,
    "avg_deal_size": 22500.00,
    "avg_sales_cycle": 45
  },
  "pipeline_by_stage": [
    {"stage": "Prospecting", "count": 20, "value": 300000},
    {"stage": "Qualification", "count": 15, "value": 250000},
    {"stage": "Proposal", "count": 12, "value": 400000},
    {"stage": "Negotiation", "count": 8, "value": 200000},
    {"stage": "Closed Won", "count": 8, "value": 180000}
  ],
  "leads_by_source": [
    {"source": "Website", "count": 60},
    {"source": "Referral", "count": 35},
    {"source": "Cold Call", "count": 25},
    {"source": "Event", "count": 20},
    {"source": "Other", "count": 10}
  ],
  "activity_timeline": [
    {"date": "2024-12-08", "calls": 15, "emails": 45, "meetings": 8},
    {"date": "2024-12-07", "calls": 12, "emails": 38, "meetings": 5}
  ]
}
```

### Revenue Forecast

```http
GET /api/v1/analytics/forecast/
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `period` | string | month, quarter, year |
| `start_date` | date | Forecast start date |
| `end_date` | date | Forecast end date |

**Response:**
```json
{
  "forecast": {
    "period": "Q1 2025",
    "predicted_revenue": 450000,
    "confidence_interval": {
      "low": 380000,
      "high": 520000
    },
    "probability": 0.75
  },
  "breakdown": [
    {
      "month": "January 2025",
      "committed": 120000,
      "best_case": 180000,
      "pipeline": 250000
    }
  ],
  "trend": "increasing",
  "recommendations": [
    "Focus on opportunities in Negotiation stage",
    "Follow up on 5 stalled deals"
  ]
}
```

### Pipeline Funnel

```http
GET /api/v1/analytics/funnel/
```

**Response:**
```json
{
  "funnel": [
    {
      "stage": "Leads",
      "count": 150,
      "conversion_rate": null
    },
    {
      "stage": "Qualified",
      "count": 75,
      "conversion_rate": 50.0
    },
    {
      "stage": "Opportunity",
      "count": 45,
      "conversion_rate": 60.0
    },
    {
      "stage": "Proposal",
      "count": 25,
      "conversion_rate": 55.5
    },
    {
      "stage": "Won",
      "count": 12,
      "conversion_rate": 48.0
    }
  ],
  "overall_conversion": 8.0,
  "avg_time_in_stage": {
    "Qualified": 5,
    "Opportunity": 12,
    "Proposal": 8,
    "Negotiation": 10
  }
}
```

---

## 🤖 AI API

### AI Sales Assistant

```http
POST /api/v1/ai/assistant/
Content-Type: application/json

{
  "query": "Help me write a follow-up email for John Doe at Acme Corp",
  "context": {
    "contact_id": 1,
    "last_interaction": "Demo call on Dec 5"
  }
}
```

**Response:**
```json
{
  "response": "Here's a follow-up email draft...",
  "suggestions": [
    "Mention the ROI calculator we discussed",
    "Include case study from similar company"
  ],
  "email_draft": {
    "subject": "Great connecting last week - Next steps for Acme Corp",
    "body": "Hi John,\n\nThank you for taking the time..."
  },
  "confidence": 0.92
}
```

### Lead Enrichment

```http
POST /api/v1/ai/enrich/
Content-Type: application/json

{
  "lead_id": 1
}
```

**Response:**
```json
{
  "enriched_data": {
    "company_info": {
      "industry": "Technology",
      "employee_count": "500-1000",
      "revenue_range": "$50M-$100M",
      "founded": 2010,
      "headquarters": "San Francisco, CA"
    },
    "contact_info": {
      "linkedin_url": "https://linkedin.com/in/johndoe",
      "twitter_handle": "@johndoe",
      "verified_email": true
    },
    "insights": {
      "recent_news": ["Series C funding announced"],
      "technologies_used": ["Salesforce", "Slack", "AWS"],
      "buying_signals": ["Hiring sales team", "Expanding to EMEA"]
    }
  },
  "confidence": 0.88,
  "sources": ["LinkedIn", "Crunchbase", "Company Website"]
}
```

### Churn Prediction

```http
GET /api/v1/ai/churn-prediction/{customer_id}/
```

**Response:**
```json
{
  "customer_id": 1,
  "churn_probability": 0.35,
  "risk_level": "medium",
  "contributing_factors": [
    {"factor": "Decreased login frequency", "impact": 0.25},
    {"factor": "Support ticket increase", "impact": 0.15},
    {"factor": "No feature adoption in 30 days", "impact": 0.10}
  ],
  "recommended_actions": [
    "Schedule check-in call",
    "Send feature adoption guide",
    "Offer training session"
  ],
  "predicted_at": "2024-12-09T10:30:00Z"
}
```

---

## 🔔 Webhooks API

### List Webhooks

```http
GET /api/v1/webhooks/
```

### Create Webhook

```http
POST /api/v1/webhooks/
Content-Type: application/json

{
  "name": "New Lead Notification",
  "url": "https://your-app.com/webhooks/mycrm",
  "events": ["lead.created", "lead.converted"],
  "secret": "your_webhook_secret",
  "active": true
}
```

### Webhook Events

| Event | Description |
|-------|-------------|
| `contact.created` | New contact created |
| `contact.updated` | Contact updated |
| `contact.deleted` | Contact deleted |
| `lead.created` | New lead created |
| `lead.scored` | Lead score updated |
| `lead.converted` | Lead converted to opportunity |
| `opportunity.created` | New opportunity created |
| `opportunity.stage_changed` | Stage changed |
| `opportunity.won` | Deal closed won |
| `opportunity.lost` | Deal closed lost |
| `task.created` | New task created |
| `task.completed` | Task completed |

### Webhook Payload

```json
{
  "event": "lead.created",
  "timestamp": "2024-12-09T10:30:00Z",
  "data": {
    "id": 1,
    "name": "New Lead - Tech Corp",
    "email": "info@techcorp.com"
  },
  "webhook_id": "wh_abc123",
  "signature": "sha256=abc123..."
}
```

---

## 📊 Rate Limiting

### Limits

| Plan | Rate Limit |
|------|------------|
| Free | 100 requests/hour |
| Pro | 1,000 requests/hour |
| Enterprise | 10,000 requests/hour |
| API Key | Custom |

### Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1702123200
```

### Rate Limit Exceeded

```json
{
  "status": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please retry after 60 seconds.",
    "retry_after": 60
  }
}
```

---

## 🔍 Search API

### Global Search

```http
GET /api/v1/search/?q=acme
```

**Response:**
```json
{
  "query": "acme",
  "total_results": 15,
  "results": {
    "contacts": [
      {"id": 1, "name": "John Doe", "company": "Acme Corp", "type": "contact"}
    ],
    "leads": [
      {"id": 1, "name": "Acme Corp Lead", "type": "lead"}
    ],
    "opportunities": [
      {"id": 1, "name": "Acme Corp - Enterprise Deal", "type": "opportunity"}
    ]
  },
  "search_time_ms": 45
}
```

---

## 📦 Import/Export API

### Import Contacts (CSV)

```http
POST /api/v1/import/contacts/
Content-Type: multipart/form-data

file: contacts.csv
mapping: {"first_name": "First Name", "email": "Email Address"}
options: {"skip_duplicates": true, "update_existing": false}
```

**Response:**
```json
{
  "import_id": "imp_abc123",
  "status": "processing",
  "total_rows": 500,
  "processed": 0,
  "succeeded": 0,
  "failed": 0,
  "webhook_url": "/api/v1/import/imp_abc123/status/"
}
```

### Export Contacts

```http
POST /api/v1/export/contacts/
Content-Type: application/json

{
  "format": "csv",
  "filters": {
    "status": "active",
    "tags": ["enterprise"]
  },
  "fields": ["first_name", "last_name", "email", "company"]
}
```

---

## 🛠️ SDK Examples

### Python

```python
from mycrm import Client

client = Client(api_key="sk_live_abc123")

# List contacts
contacts = client.contacts.list(status="active", page_size=50)

# Create lead
lead = client.leads.create(
    name="New Lead",
    email="lead@example.com",
    source="website"
)

# Score lead with AI
score = client.leads.score(lead.id)
```

### JavaScript/TypeScript

```typescript
import { MyCRM } from '@mycrm/sdk';

const client = new MyCRM({ apiKey: 'sk_live_abc123' });

// List contacts
const contacts = await client.contacts.list({ status: 'active' });

// Create opportunity
const opp = await client.opportunities.create({
  name: 'Enterprise Deal',
  value: 50000,
  contactId: 1,
});

// Move stage
await client.opportunities.moveStage(opp.id, { stageId: 3 });
```

---

## 📚 Additional Resources

- [OpenAPI Spec](/api/schema/) - Download OpenAPI 3.0 specification
- [Postman Collection](/api/postman/) - Import into Postman
- [API Changelog](/api/changelog/) - Version history
- [Status Page](https://status.mycrm.io) - API status and incidents

---

*Last Updated: December 2024*
*API Version: v1.2.0*
