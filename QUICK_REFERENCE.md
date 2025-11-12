# 🚀 MyCRM Quick Reference Card

## Start All Services

```bash
# Terminal 1 - Django Backend
cd /workspaces/MyCRM/backend
source ../.venv/bin/activate
python manage.py runserver

# Terminal 2 - Celery Worker
cd /workspaces/MyCRM/backend
source ../.venv/bin/activate
celery -A backend worker -l info

# Terminal 3 - Redis (if not running)
redis-server

# Terminal 4 - Next.js Frontend
cd /workspaces/MyCRM/frontend
npm run dev
```

## Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Your user account |
| **Backend API** | http://localhost:8000/api | JWT token |
| **Admin Panel** | http://localhost:8000/admin | Superuser account |
| **Redis** | redis://localhost:6379 | No auth (dev) |

## New Features URLs

| Feature | Frontend URL | Backend API |
|---------|-------------|-------------|
| **Campaigns** | `/campaigns` | `/api/campaigns/` |
| **Documents** | `/documents` | `/api/documents/` |
| **Analytics** | `/analytics/pipeline` | `/api/core/analytics/` |
| **Integrations** | `/integrations` | `/api/integrations/` |
| **Activity Feed** | Component in entity pages | `/api/activity/` |
| **Notifications** | Dropdown in header | `/api/activity/notifications/` |

## Common Commands

### Backend (Django)
```bash
# Create superuser
python manage.py createsuperuser

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic

# Django shell
python manage.py shell
```

### Frontend (Next.js)
```bash
# Install dependencies
npm install

# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Type check
npm run type-check
```

### Database
```bash
# Access SQLite (dev)
sqlite3 backend/db.sqlite3

# Show tables
.tables

# Describe table
.schema campaign_management_campaign

# Exit
.exit
```

## Quick Test Checklist

✅ **Backend Test:**
```bash
curl http://localhost:8000/api/campaigns/campaigns/
# Should return JSON (may require auth)
```

✅ **Frontend Test:**
```
Open http://localhost:3000
Login → Navigate to Campaigns
```

✅ **Celery Test:**
```bash
# Check worker is running
# Should see "celery@hostname ready"
```

✅ **Redis Test:**
```bash
redis-cli ping
# Should return: PONG
```

## API Quick Reference

### Campaign API
```bash
# List campaigns
GET /api/campaigns/campaigns/

# Create campaign
POST /api/campaigns/campaigns/
{
  "name": "Test Campaign",
  "subject": "Hello",
  "status": "draft"
}

# Get analytics
GET /api/campaigns/campaigns/{id}/analytics/
```

### Document API
```bash
# List documents
GET /api/documents/documents/

# Upload document
POST /api/documents/documents/
Content-Type: multipart/form-data
file: <file>
title: "Document Name"

# Download document
GET /api/documents/documents/{id}/download/
```

### Analytics API
```bash
# Pipeline analytics
GET /api/core/analytics/pipeline_analytics/

# Sales forecast (3 months)
GET /api/core/analytics/sales_forecast/?months=3

# AI insights
GET /api/core/analytics/ai_insights_dashboard/
```

### Activity API
```bash
# My feed
GET /api/activity/activities/my_feed/

# Entity activities
GET /api/activity/activities/for_entity/?model=lead&id=123

# Add comment
POST /api/activity/comments/
{
  "content": "Great progress!",
  "content_type": "lead",
  "object_id": "123"
}

# Notifications
GET /api/activity/notifications/
GET /api/activity/notifications/unread_count/
POST /api/activity/notifications/{id}/mark_read/
```

## Environment Variables

### Backend (.env)
```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
SENDGRID_API_KEY=your-sendgrid-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Troubleshooting Quick Fixes

### Issue: Port already in use
```bash
# Find process
lsof -i :8000  # or :3000

# Kill process
kill -9 <PID>
```

### Issue: Migrations out of sync
```bash
python manage.py migrate --fake-initial
```

### Issue: Static files not loading
```bash
python manage.py collectstatic --no-input
```

### Issue: Celery not picking up tasks
```bash
# Restart celery worker
# Ctrl+C to stop, then restart
celery -A backend worker -l info
```

### Issue: Redis connection failed
```bash
# Start Redis
redis-server

# Or install if missing
# Ubuntu/Debian:
sudo apt-get install redis-server
```

### Issue: Module not found
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

## Documentation Files

| File | Purpose |
|------|---------|
| `FEATURES.md` | Detailed feature documentation |
| `QUICK_START.md` | Setup and usage guide |
| `FRONTEND_GUIDE.md` | Frontend components guide |
| `INTEGRATION_CHECKLIST.md` | Integration steps |
| `COMPLETE_SUMMARY.md` | Overall summary |
| `FINAL_REPORT.md` | Complete implementation report |

## Key File Locations

### Backend
```
backend/
├── campaign_management/      # Campaign features
├── document_management/       # Document features
├── integration_hub/          # Webhook features
├── activity_feed/            # Activity features
├── core/ai_analytics.py      # Analytics
├── backend/settings.py       # Configuration
├── backend/urls.py           # URL routing
└── requirements.txt          # Dependencies
```

### Frontend
```
frontend/
├── src/app/
│   ├── campaigns/           # Campaign pages
│   ├── documents/           # Document pages
│   ├── analytics/pipeline/  # Analytics page
│   └── integrations/        # Integration page
├── src/components/
│   ├── ActivityFeed.tsx     # Activity component
│   └── NotificationsDropdown.tsx  # Notifications
└── src/lib/api.ts           # API client
```

## Component Usage Examples

### ActivityFeed Component
```tsx
import ActivityFeed from '@/components/ActivityFeed';

// In lead detail page:
<ActivityFeed 
  entityModel="lead" 
  entityId={leadId} 
  showComments={true}
/>
```

### NotificationsDropdown Component
```tsx
import NotificationsDropdown from '@/components/NotificationsDropdown';

// In header:
<NotificationsDropdown />
```

## Database Models Quick Reference

### Campaign Models
- `Campaign` - Main campaign record
- `CampaignSegment` - Audience segments
- `CampaignRecipient` - Individual recipients
- `CampaignClick` - Click tracking
- `EmailTemplate` - Email templates

### Document Models
- `Document` - File records
- `DocumentTemplate` - Document templates
- `DocumentShare` - Sharing permissions
- `DocumentComment` - Comments
- `DocumentApproval` - Approval workflow

### Integration Models
- `Webhook` - Webhook configurations
- `WebhookDelivery` - Delivery logs
- `ThirdPartyIntegration` - OAuth integrations
- `IntegrationLog` - Sync logs
- `APIEndpoint` - API endpoints

### Activity Models
- `Activity` - Activity records
- `Comment` - Comments on entities
- `Mention` - @mentions
- `Notification` - User notifications
- `Follow` - Following entities

## Status Indicators

### Campaign Status
- `draft` - Being edited
- `scheduled` - Scheduled for sending
- `sending` - Currently sending
- `sent` - Completed
- `paused` - Temporarily stopped

### Document Status
- `pending` - Awaiting approval
- `approved` - Approved
- `rejected` - Rejected

### Integration Status
- `connected` - Working
- `error` - Connection failed
- `syncing` - Currently syncing
- `disconnected` - Not connected

### Webhook Status
- `active` - Enabled
- `inactive` - Disabled
- `failed` - Delivery failed

## Performance Tips

### Backend
- Use `select_related()` for ForeignKey queries
- Use `prefetch_related()` for ManyToMany queries
- Cache expensive analytics with Redis
- Use Celery for long-running tasks

### Frontend
- Lazy load components with `next/dynamic`
- Use `React.memo()` for expensive components
- Debounce search inputs
- Paginate long lists

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG=False in production
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS
- [ ] Set up CORS properly
- [ ] Use strong passwords
- [ ] Enable rate limiting
- [ ] Review user permissions

## Monitoring Commands

### Check Celery Tasks
```bash
# Active tasks
celery -A backend inspect active

# Registered tasks
celery -A backend inspect registered

# Stats
celery -A backend inspect stats
```

### Check Redis
```bash
# Info
redis-cli info

# Memory usage
redis-cli info memory

# Keys
redis-cli keys '*'
```

### Check Django
```bash
# Show migrations
python manage.py showmigrations

# Check deployment
python manage.py check --deploy
```

## Support Resources

- **Django Docs:** https://docs.djangoproject.com/
- **DRF Docs:** https://www.django-rest-framework.org/
- **Next.js Docs:** https://nextjs.org/docs
- **Celery Docs:** https://docs.celeryq.dev/
- **Redis Docs:** https://redis.io/documentation

---

## 🎯 Quick Start (First Time)

```bash
# 1. Backend setup
cd backend
python -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

# 2. Start services
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Celery
celery -A backend worker -l info

# Terminal 3: Redis
redis-server

# Terminal 4: Frontend
cd ../frontend
npm install
npm run dev

# 3. Access
# Frontend: http://localhost:3000
# Admin: http://localhost:8000/admin
```

---

**📌 Pin this file for quick reference!**

**Status:** ✅ Ready to use  
**Version:** 1.0.0  
**Last Updated:** 2024
