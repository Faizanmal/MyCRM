# Backend API Documentation

## Settings & Preferences API

### Base URL
All endpoints are prefixed with `/api/v1/settings/`

---

## User Preferences

### GET `/preferences/`
Get current user's preferences.

**Response:**
```json
{
  "id": 1,
  "theme": "system",
  "accent_color": "#3b82f6",
  "font_size": 14,
  "compact_mode": false,
  "animations_enabled": true,
  "high_contrast": false,
  "default_view": "overview",
  "sidebar_collapsed": false,
  "show_welcome_message": true,
  "auto_refresh_enabled": true,
  "auto_refresh_interval": 30,
  "dashboard_layout": {},
  "share_activity_with_team": true,
  "show_online_status": true,
  "allow_mentions": true,
  "data_export_enabled": true,
  "sound_enabled": true,
  "sound_volume": 70,
  "keyboard_shortcuts": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### PATCH `/preferences/me/`
Update user preferences.

**Request Body:**
```json
{
  "theme": "dark",
  "compact_mode": true
}
```

### POST `/preferences/reset/`
Reset preferences to defaults.

### PATCH `/preferences/layout/`
Update dashboard layout.

**Request Body:**
```json
{
  "layout": {
    "widgets": ["stats", "chart", "tasks"]
  }
}
```

### PATCH `/preferences/shortcuts/`
Update keyboard shortcuts.

**Request Body:**
```json
{
  "shortcuts": {
    "search": "⌘+K",
    "newContact": "⌘+Shift+C"
  }
}
```

---

## Notification Preferences

### GET `/notifications/`
Get notification preferences.

**Response:**
```json
{
  "id": 1,
  "email_enabled": true,
  "push_enabled": true,
  "in_app_enabled": true,
  "sms_enabled": false,
  "quiet_hours_enabled": false,
  "quiet_hours_start": "22:00:00",
  "quiet_hours_end": "08:00:00",
  "quiet_hours_days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
  "digest_enabled": true,
  "digest_frequency": "daily",
  "digest_time": "09:00:00",
  "digest_include_ai": true,
  "digest_include_metrics": true,
  "type_settings": [...]
}
```

### PATCH `/notifications/me/`
Update notification preferences.

### PATCH `/notifications/channel/`
Toggle a notification channel.

**Request Body:**
```json
{
  "channel": "push",
  "enabled": false
}
```

### PATCH `/notifications/type/`
Update settings for a notification type.

**Request Body:**
```json
{
  "notification_type": "deal_won",
  "email_enabled": true,
  "push_enabled": true,
  "frequency": "instant",
  "priority": "high"
}
```

### PATCH `/notifications/quiet-hours/`
Update quiet hours settings.

**Request Body:**
```json
{
  "enabled": true,
  "start_time": "22:00",
  "end_time": "07:00",
  "days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
}
```

### PATCH `/notifications/digest/`
Update digest settings.

**Request Body:**
```json
{
  "enabled": true,
  "frequency": "daily",
  "time": "09:00",
  "include_ai": true,
  "include_metrics": true
}
```

---

## Data Export

### POST `/export/`
Create a new export job.

**Request Body:**
```json
{
  "format": "csv",
  "entities": ["contacts", "deals", "tasks"],
  "date_range": "month",
  "include_archived": false,
  "include_deleted": false
}
```

**Response (202 Accepted):**
```json
{
  "id": 1,
  "format": "csv",
  "entities": ["contacts", "deals", "tasks"],
  "status": "processing",
  "progress": 0
}
```

### GET `/export/{id}/status/`
Get export job status.

**Response:**
```json
{
  "id": 1,
  "status": "completed",
  "progress": 100,
  "error": null
}
```

### GET `/export/{id}/download/`
Download export file (after completion).

### GET `/export/history/`
Get export history.

**Response:**
```json
{
  "exports": [
    {
      "id": 1,
      "format": "csv",
      "entities": ["contacts"],
      "status": "completed",
      "file_size_formatted": "2.4 MB",
      "download_url": "/api/v1/settings/export/1/download/",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### DELETE `/export/{id}/cancel/`
Cancel a pending export job.

---

## Role-Based Access Control (RBAC)

### GET `/roles/`
List all available roles.

**Response:**
```json
[
  {
    "id": 1,
    "name": "admin",
    "display_name": "Administrator",
    "description": "Full system access",
    "level": 4,
    "permissions": ["view_dashboard", "access_admin", ...],
    "permissions_count": 35,
    "color": "bg-purple-100 text-purple-700",
    "is_system_role": true
  }
]
```

### POST `/roles/initialize/`
Initialize default system roles (admin only).

### GET `/role-assignments/`
List role assignments.

### POST `/role-assignments/`
Assign a role to a user (admin only).

**Request Body:**
```json
{
  "user": 1,
  "role_id": 1,
  "team_id": null,
  "organization_id": null
}
```

### GET `/permissions/me/`
Get current user's roles and permissions.

**Response:**
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "roles": [...],
  "permissions": ["view_contacts", "create_contacts", ...],
  "is_admin": false,
  "highest_role_level": 2
}
```

### POST `/permissions/check/`
Check if current user has a permission.

**Request Body:**
```json
{
  "permission": "view_contacts"
}
```

**Response:**
```json
{
  "has_permission": true
}
```

---

## Analytics Dashboard

### GET `/analytics/dashboard/`
Get admin analytics dashboard data.

**Query Parameters:**
- `range`: `week` | `month` | `quarter` | `year` (default: `year`)

**Response:**
```json
{
  "overview": {
    "total_revenue": 1250750,
    "revenue_growth": 18.5,
    "total_deals": 234,
    "deals_growth": 12.3,
    "conversion_rate": 24.5,
    "conversion_growth": 5.2,
    "active_leads": 1567,
    "leads_growth": -3.8
  },
  "revenue_by_month": [
    {"month": "Jan", "revenue": 85000, "deals_count": 15}
  ],
  "deals_by_stage": [
    {"stage": "Prospecting", "count": 145, "value": 1450000}
  ],
  "team_performance": [
    {"id": 1, "name": "Alex Chen", "deals_count": 45, "deals_value": 256000, ...}
  ],
  "funnel": [
    {"stage": "Website Visits", "count": 10000, "conversion_rate": 100}
  ],
  "lead_sources": [
    {"source": "Organic Search", "count": 350, "percentage": 35}
  ]
}
```

---

## Available Permissions

### Dashboard
- `view_dashboard` - View main dashboard
- `view_admin_dashboard` - View admin dashboard
- `view_analytics` - View analytics pages

### Contacts
- `view_contacts` - View contacts
- `create_contacts` - Create new contacts
- `edit_contacts` - Edit existing contacts
- `delete_contacts` - Delete contacts
- `export_contacts` - Export contacts
- `import_contacts` - Import contacts

### Deals
- `view_deals` - View deals/opportunities
- `create_deals` - Create new deals
- `edit_deals` - Edit existing deals
- `delete_deals` - Delete deals
- `close_deals` - Close deals (won/lost)

### Tasks
- `view_tasks` - View tasks
- `create_tasks` - Create new tasks
- `edit_tasks` - Edit existing tasks
- `delete_tasks` - Delete tasks
- `assign_tasks` - Assign tasks to others

### Team
- `view_team` - View team members
- `manage_team` - Manage team settings
- `invite_users` - Invite new users
- `remove_users` - Remove users
- `assign_roles` - Assign roles to users

### Settings
- `view_settings` - View settings pages
- `manage_settings` - Modify settings
- `manage_integrations` - Manage integrations
- `view_billing` - View billing info
- `manage_billing` - Manage billing

### Reports
- `view_reports` - View reports
- `create_reports` - Create new reports
- `export_reports` - Export reports

### Admin
- `access_admin` - Access admin area
- `manage_organization` - Manage organization settings
- `view_audit_log` - View audit logs

---

## Role Hierarchy

| Role | Level | Description |
|------|-------|-------------|
| Admin | 4 | Full system access |
| Manager | 3 | Team management + full CRM |
| Sales Rep | 2 | Standard CRM user |
| Viewer | 1 | Read-only access |
| Guest | 0 | Minimal access |

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request data",
  "details": {...}
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "error": "Permission denied",
  "required": "access_admin"
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 410 Gone
```json
{
  "error": "Export has expired"
}
```
