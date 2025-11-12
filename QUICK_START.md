# 🚀 Quick Start Guide - New Features

## Overview
Your CRM now includes 4 major new feature modules:
1. **Email Campaign Management** - Create and track marketing campaigns
2. **Pipeline Analytics & Forecasting** - AI-powered sales insights
3. **Document Management** - File storage with OCR and versioning
4. **Integration Hub** - Webhooks and third-party integrations

---

## 📋 Installation Steps

### 1. Install Required Dependencies

```bash
cd /workspaces/MyCRM/backend

# Optional: For OCR functionality
pip install PyPDF2 pytesseract pillow

# Optional: For document generation
pip install reportlab python-docx
```

### 2. Run Database Migrations

```bash
python manage.py makemigrations campaign_management
python manage.py makemigrations document_management
python manage.py makemigrations integration_hub

python manage.py migrate
```

### 3. Create Media Directory (for document uploads)

```bash
mkdir -p /workspaces/MyCRM/backend/media/documents
mkdir -p /workspaces/MyCRM/backend/media/document_templates
mkdir -p /workspaces/MyCRM/backend/media/template_thumbnails
```

### 4. Start Celery Workers (for background tasks)

Open a new terminal and run:

```bash
cd /workspaces/MyCRM/backend

# Start Celery worker
celery -A backend worker -l info

# In another terminal, start Celery beat (for scheduled tasks)
celery -A backend beat -l info
```

### 5. Configure Environment Variables

Add to your `.env` file or `settings.py`:

```python
# SendGrid for email campaigns
SENDGRID_API_KEY = 'your-sendgrid-api-key'
DEFAULT_FROM_EMAIL = 'noreply@yourcompany.com'

# Celery (if not already configured)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## 🎯 Quick Test - API Endpoints

### Test Campaign Management
```bash
curl -X GET http://localhost:8000/api/campaigns/campaigns/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Pipeline Analytics
```bash
curl -X GET http://localhost:8000/api/core/analytics/pipeline_analytics/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Document Management
```bash
curl -X GET http://localhost:8000/api/documents/documents/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Integration Hub
```bash
curl -X GET http://localhost:8000/api/integrations/webhooks/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Feature Highlights

### 1. Email Campaigns
- Create campaigns with segments
- Schedule or send immediately
- Track opens, clicks, bounces
- A/B testing support
- Reusable templates

### 2. Pipeline Analytics
- Real-time pipeline health score
- Sales forecasting (1-12 months)
- Conversion funnel analysis
- Deal velocity metrics
- Bottleneck detection

### 3. Document Management
- Upload files (PDF, DOC, XLS, images)
- Automatic OCR text extraction
- Version control
- Secure sharing with expiration
- Approval workflows

### 4. Integration Hub
- Webhook notifications for all CRM events
- Third-party integrations (Slack, Teams, etc.)
- Custom API endpoints
- Delivery retry logic
- Activity logging

---

## 🔧 Configuration Examples

### Create an Email Campaign

```python
import requests

response = requests.post('http://localhost:8000/api/campaigns/campaigns/', {
    'name': 'Q4 2025 Launch',
    'subject': 'Exciting Product Update!',
    'content_html': '<h1>Hello {{first_name}}</h1><p>Check out our new product!</p>',
    'campaign_type': 'email',
}, headers={'Authorization': 'Bearer YOUR_TOKEN'})

print(response.json())
```

### Create a Webhook

```python
response = requests.post('http://localhost:8000/api/integrations/webhooks/', {
    'name': 'Slack Notifications',
    'url': 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
    'events': ['lead.created', 'opportunity.won'],
    'secret_key': 'your-secret-key-here'
}, headers={'Authorization': 'Bearer YOUR_TOKEN'})

print(response.json())
```

### Upload a Document

```python
with open('proposal.pdf', 'rb') as f:
    response = requests.post('http://localhost:8000/api/documents/documents/', 
        data={
            'name': 'Client Proposal',
            'category': 'proposal',
            'access_level': 'confidential'
        },
        files={'file': f},
        headers={'Authorization': 'Bearer YOUR_TOKEN'}
    )

print(response.json())
```

---

## 📈 Next Steps

1. **Test the Features**: Use Postman or curl to explore the API
2. **Configure SendGrid**: Add your API key for email campaigns
3. **Set Up Webhooks**: Connect to Slack or other services
4. **Upload Documents**: Start organizing files by lead/opportunity
5. **Review Analytics**: Check pipeline health and forecasts

---

## 🐛 Troubleshooting

### Redis not running?
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
redis-server

# Test connection
redis-cli ping
# Should return: PONG
```

### Migrations failing?
```bash
# Reset migrations (CAUTION: Development only!)
python manage.py migrate campaign_management zero
python manage.py migrate document_management zero
python manage.py migrate integration_hub zero

# Then run migrations again
python manage.py makemigrations
python manage.py migrate
```

### OCR not working?
```bash
# Install Tesseract OCR
sudo apt-get install tesseract-ocr

# Install Python packages
pip install pytesseract pillow PyPDF2
```

---

## 📚 Additional Documentation

- Full feature documentation: `/workspaces/MyCRM/FEATURES.md`
- API endpoints: Access Django admin or `/api/docs/`
- Models: Check each module's `models.py` file

---

## 🎉 You're All Set!

Your CRM now has:
- ✅ Email campaign management
- ✅ Advanced pipeline analytics
- ✅ Document management system
- ✅ Integration hub with webhooks

Start exploring these powerful new features! 🚀
