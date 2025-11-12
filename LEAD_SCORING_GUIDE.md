# 🎯 Lead Scoring & Qualification System - User Guide

## Overview

The Lead Scoring system automatically evaluates and qualifies leads based on custom rules, helping sales teams prioritize their efforts on the most promising prospects.

---

## 🔢 Lead Scoring Basics

### How It Works:
1. **Rules are evaluated** against lead data
2. **Points are awarded** for matching criteria
3. **Total score** is calculated (0-100)
4. **Qualification stage** is determined
5. **Workflows are triggered** automatically

### Score Categories:
- **Demographic** (20-30 points): Company size, industry, location
- **Behavioral** (25-35 points): Email opens, clicks, website visits
- **Firmographic** (20-30 points): Revenue, employee count, tech stack
- **Engagement** (20-30 points): Form submissions, demo requests

---

## 🎛️ Creating Scoring Rules

### Via Admin Panel:

1. Go to `/admin` → Lead Qualification → Scoring Rules
2. Click "Add Scoring Rule"
3. Fill in:
   - **Name:** "Enterprise company size"
   - **Rule Type:** Firmographic
   - **Field Name:** company_size
   - **Operator:** in_list
   - **Value:** `["Large", "Enterprise"]`
   - **Points:** 15
   - **Priority:** 10
   - **Is Active:** ✓

### Via API:

```bash
POST /api/lead-qualification/scoring-rules/
Content-Type: application/json
Authorization: Bearer <your_token>

{
  "name": "High-value industry",
  "rule_type": "firmographic",
  "field_name": "industry",
  "operator": "in_list",
  "value": "[\"Technology\", \"Finance\", \"Healthcare\"]",
  "points": 15,
  "is_active": true,
  "priority": 10
}
```

---

## 📋 Common Scoring Rules Examples

### 1. Industry-Based Scoring
```json
{
  "name": "Target Industry",
  "rule_type": "firmographic",
  "field_name": "industry",
  "operator": "in_list",
  "value": "[\"SaaS\", \"Enterprise Software\"]",
  "points": 20
}
```

### 2. Company Size Scoring
```json
{
  "name": "Mid to Large Company",
  "rule_type": "firmographic",
  "field_name": "company_size",
  "operator": "in_list",
  "value": "[\"51-200\", \"201-500\", \"500+\"]",
  "points": 15
}
```

### 3. Email Engagement
```json
{
  "name": "Email Engaged",
  "rule_type": "behavioral",
  "field_name": "email_opens_count",
  "operator": "greater_than",
  "value": "3",
  "points": 10
}
```

### 4. Website Activity
```json
{
  "name": "Recent Activity",
  "rule_type": "engagement",
  "field_name": "days_since_creation",
  "operator": "less_than",
  "value": "30",
  "points": 10
}
```

### 5. Job Title
```json
{
  "name": "Decision Maker",
  "rule_type": "demographic",
  "field_name": "title",
  "operator": "contains",
  "value": "director",
  "points": 15
}
```

---

## ✅ Qualification Criteria

### Setting Up MQL Criteria:

```bash
POST /api/lead-qualification/qualification-criteria/

{
  "name": "Marketing Qualified Lead",
  "stage": "mql",
  "minimum_score": 40,
  "required_fields": ["email", "company", "phone"],
  "required_actions": ["email_opened", "form_submitted"],
  "time_constraint_days": 90,
  "is_active": true
}
```

### Setting Up SQL Criteria:

```bash
POST /api/lead-qualification/qualification-criteria/

{
  "name": "Sales Qualified Lead",
  "stage": "sql",
  "minimum_score": 65,
  "required_fields": ["email", "company", "phone", "title", "company_size"],
  "required_actions": ["email_opened", "email_clicked", "demo_requested"],
  "time_constraint_days": 60,
  "is_active": true
}
```

---

## ⚙️ Qualification Workflows

### Workflow Types:

1. **Score Threshold** - Trigger when lead reaches a score
2. **Stage Change** - Trigger when qualification stage changes
3. **Field Update** - Trigger when specific field is updated
4. **Time-Based** - Trigger at scheduled intervals
5. **Manual** - Triggered manually by user

### Action Types:

1. **assign_owner** - Assign lead to a user
2. **change_status** - Update lead status
3. **send_email** - Send notification email
4. **create_task** - Create follow-up task
5. **send_notification** - Send in-app notification
6. **move_to_stage** - Update qualification stage
7. **update_field** - Modify lead field
8. **add_to_campaign** - Add to email campaign

---

## 🔄 Example Workflows

### 1. Auto-Assign Hot Leads

```json
{
  "name": "Assign hot leads to senior rep",
  "trigger_type": "score_threshold",
  "trigger_config": {
    "score": 75
  },
  "action_type": "assign_owner",
  "action_config": {
    "owner_id": 5
  },
  "is_active": true,
  "priority": 10
}
```

### 2. Create Task for Qualified Leads

```json
{
  "name": "Follow up on SQL",
  "trigger_type": "score_threshold",
  "trigger_config": {
    "score": 65
  },
  "action_type": "create_task",
  "action_config": {
    "title": "Call qualified lead",
    "description": "Lead reached SQL qualification",
    "due_in_days": 1,
    "priority": "high"
  },
  "is_active": true
}
```

### 3. Send Notification

```json
{
  "name": "Notify on hot lead",
  "trigger_type": "score_threshold",
  "trigger_config": {
    "score": 80
  },
  "action_type": "send_notification",
  "action_config": {
    "message": "🔥 Hot lead! Score increased to 80+"
  },
  "is_active": true
}
```

### 4. Update Status

```json
{
  "name": "Move to qualified status",
  "trigger_type": "score_threshold",
  "trigger_config": {
    "score": 60
  },
  "action_type": "change_status",
  "action_config": {
    "status": "qualified"
  },
  "is_active": true
}
```

---

## 📊 Using the API

### Calculate Lead Score:

```bash
POST /api/lead-qualification/lead-scores/calculate/
{
  "lead_id": 123
}

# Response:
{
  "id": 456,
  "lead": 123,
  "lead_name": "John Doe",
  "score": 68,
  "previous_score": 45,
  "score_change": 23,
  "score_breakdown": {
    "demographic": 15,
    "behavioral": 20,
    "firmographic": 18,
    "engagement": 15
  },
  "qualification_stage": "sql",
  "calculated_at": "2025-11-12T10:30:00Z"
}
```

### Get Score History:

```bash
GET /api/lead-qualification/lead-scores/history/?lead_id=123

# Response: Array of score changes over time
```

### Test a Rule:

```bash
POST /api/lead-qualification/scoring-rules/5/test_rule/
{
  "lead_id": 123
}

# Response:
{
  "rule": "High-value industry",
  "lead": "Acme Corp",
  "points_awarded": 15,
  "rule_applied": true
}
```

### Bulk Calculate Scores:

```bash
POST /api/lead-qualification/lead-scores/bulk_calculate/
{
  "lead_ids": [123, 124, 125]
}

# Or recalculate all:
{
  "recalculate_all": true
}
```

---

## 🔍 Available Field Names

### Lead Fields:
- `email` - Email address
- `phone` - Phone number
- `company` - Company name
- `title` - Job title
- `industry` - Industry
- `company_size` - Company size
- `status` - Lead status
- `source` - Lead source
- `created_at` - Creation date

### Computed Fields:
- `days_since_creation` - Days since lead was created
- `last_activity_days_ago` - Days since last activity
- `email_opens_count` - Number of email opens
- `email_clicks_count` - Number of email clicks
- `activities_count` - Total activities

### Enrichment Fields:
- `company_revenue` - Company revenue range
- `job_level` - Job level (entry, mid, senior, executive)
- `technologies` - Technologies used
- `social_profiles` - Social media profiles

---

## 🎯 Best Practices

### 1. Start Simple
Begin with 5-10 basic rules covering:
- Industry (15-20 points)
- Company size (10-15 points)
- Job title (10-15 points)
- Email engagement (10 points)
- Recent activity (5-10 points)

### 2. Balance Your Scoring
- Total possible score should exceed 100
- No single rule should be worth more than 25 points
- Use both positive and negative scoring
- Test with sample leads

### 3. Define Clear Stages
- **MQL:** 40-59 points
- **SQL:** 60-79 points
- **Hot Lead:** 80+ points

### 4. Set Up Progressive Workflows
1. Score 40 → Assign to marketing
2. Score 60 → Assign to sales rep
3. Score 75 → Create high-priority task
4. Score 85 → Notify manager

### 5. Monitor and Adjust
- Review score distribution monthly
- Adjust point values based on conversion data
- Update rules as business priorities change
- Track workflow execution success

---

## 📈 Monitoring Lead Scores

### Score Distribution:

```bash
GET /api/lead-qualification/lead-scores/distribution/

# Response:
{
  "score_0_20": 45,
  "score_20_40": 120,
  "score_40_60": 85,
  "score_60_80": 42,
  "score_80_100": 18,
  "avg_score": 47.5
}
```

### Workflow Statistics:

```bash
GET /api/lead-qualification/workflows/statistics/

# Response:
{
  "total_workflows": 8,
  "active_workflows": 6,
  "total_executions": 245,
  "successful_executions": 238,
  "failed_executions": 7
}
```

### Recent Executions:

```bash
GET /api/lead-qualification/workflow-executions/recent/?limit=10
```

---

## 🚀 Advanced Features

### Custom Field Evaluation

Add custom field checks in scoring engine:

```python
# In scoring_engine.py, add to _get_field_value method:

elif field_name == 'custom_metric':
    # Your custom logic here
    return calculate_custom_metric(self.lead)
```

### External Enrichment

Integrate with enrichment APIs:

```python
from lead_qualification.tasks import enrich_lead_data_task

# Trigger enrichment
enrich_lead_data_task.delay(lead_id=123, source='clearbit')
```

### Scheduled Recalculation

Set up Celery Beat schedule:

```python
# In settings.py
CELERY_BEAT_SCHEDULE = {
    'daily-score-recalculation': {
        'task': 'lead_qualification.tasks.daily_score_recalculation',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
}
```

---

## ❓ Troubleshooting

### Lead scores not updating?
- Check Celery worker is running: `celery -A backend worker -l info`
- Verify Redis is running: `redis-cli ping`
- Check logs for errors

### Workflows not executing?
- Verify workflow is active
- Check trigger configuration
- Review workflow execution logs
- Test manually via API

### Rules not matching?
- Use test_rule API endpoint
- Check field name spelling
- Verify operator is correct
- Review field value format

---

## 📚 Additional Resources

- **Admin Panel:** `/admin/lead_qualification/`
- **API Docs:** All endpoints at `/api/lead-qualification/`
- **Code:** `/backend/lead_qualification/`
- **Tests:** Run with `python manage.py test lead_qualification`

---

**Need Help?** Check the Implementation Status document or Django admin for examples!

**Version:** 1.0.0  
**Last Updated:** November 12, 2025
