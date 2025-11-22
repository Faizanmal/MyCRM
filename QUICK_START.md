# 🚀 Quick Start Guide - MyCRM Enterprise Features

## ⚡ Get Started in 5 Minutes

### Step 1: Apply Database Migrations (2 minutes)
```bash
# Run the master setup script
chmod +x setup_all_features.sh
./setup_all_features.sh

# OR manually in backend directory
cd backend
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Create Superuser (1 minute)
```bash
cd backend
python manage.py createsuperuser
# Follow prompts to create admin account
```

### Step 3: Start the Application (1 minute)
```bash
# Terminal 1: Start Django backend
cd backend
python manage.py runserver

# Terminal 2: Start Next.js frontend
cd frontend
npm run dev
```

### Step 4: Access Features (1 minute)
Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **Admin Panel**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/docs/

---

## 🎯 Feature Access URLs

Once logged in, visit these pages to explore each feature:

1. **Integration Hub**: http://localhost:3000/integration-hub
   - Manage webhooks, third-party integrations, API endpoints

2. **AI Insights**: http://localhost:3000/ai-insights
   - Sales forecasting, customer segmentation, churn prediction

3. **Gamification**: http://localhost:3000/gamification
   - Achievements, leaderboards, challenges, points

4. **Organizations (Multi-Tenant)**: http://localhost:3000/organizations
   - Tenant management, user invitations, settings

5. **SSO Settings**: http://localhost:3000/sso-settings
   - Configure OAuth2 and SAML providers

6. **Collaboration**: http://localhost:3000/collaboration
   - Deal rooms, channels, messaging, approvals

7. **GDPR Compliance**: http://localhost:3000/gdpr-compliance
   - Consent management, data exports, deletion requests

---

## 🧪 Quick Testing

### Test API Endpoints
```bash
# Get authentication token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'

# Test Integration Hub
curl -X GET http://localhost:8000/api/v1/integration-hub/webhooks/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test Gamification
curl -X GET http://localhost:8000/api/v1/gamification/points/my_points/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Run Unit Tests
```bash
cd backend
python manage.py test  # All tests
python manage.py test gamification  # Specific app
python manage.py test collaboration.tests.DealRoomModelTest  # Specific test
```

---

## 🔑 Key API Endpoints

### Integration Hub
- `GET /api/v1/integration-hub/webhooks/` - List webhooks
- `POST /api/v1/integration-hub/webhooks/` - Create webhook
- `POST /api/v1/integration-hub/webhooks/{id}/test/` - Test webhook
- `GET /api/v1/integration-hub/integrations/` - List integrations
- `POST /api/v1/integration-hub/integrations/{id}/sync/` - Sync integration

### AI Insights
- `GET /api/core/ai-analytics/sales_forecast/` - Sales forecast
- `GET /api/core/ai-analytics/customer_segmentation/` - Customer segments
- `GET /api/core/ai-analytics/churn_prediction/` - Churn risk
- `POST /api/core/ai-analytics/next_best_action/` - AI recommendations

### Gamification
- `GET /api/v1/gamification/achievements/` - List achievements
- `GET /api/v1/gamification/points/my_points/` - My points
- `GET /api/v1/gamification/leaderboards/{id}/rankings/` - Leaderboard
- `POST /api/v1/gamification/challenges/{id}/join/` - Join challenge

### Multi-Tenant
- `GET /api/v1/multi-tenant/tenants/` - List tenants
- `POST /api/v1/multi-tenant/tenants/{id}/switch/` - Switch tenant
- `GET /api/v1/multi-tenant/users/` - Tenant users
- `POST /api/v1/multi-tenant/invitations/` - Invite user

### SSO Integration
- `GET /api/v1/sso/providers/` - List SSO providers
- `POST /api/v1/sso/providers/` - Create SSO provider
- `GET /api/v1/sso/login/{provider_id}/` - SSO login URL
- `GET /api/v1/sso/connections/my_connections/` - My SSO connections

### Collaboration
- `GET /api/v1/collaboration/deal-rooms/` - List deal rooms
- `POST /api/v1/collaboration/deal-rooms/` - Create deal room
- `POST /api/v1/collaboration/deal-rooms/{id}/add_member/` - Add member
- `GET /api/v1/collaboration/channels/my_channels/` - My channels
- `POST /api/v1/collaboration/messages/` - Send message

### GDPR Compliance
- `GET /api/v1/gdpr/consents/my_consents/` - My consents
- `POST /api/v1/gdpr/consents/{id}/withdraw/` - Withdraw consent
- `POST /api/v1/gdpr/exports/` - Request data export
- `POST /api/v1/gdpr/deletions/` - Request data deletion
- `GET /api/v1/gdpr/breaches/` - List data breaches (staff only)

---

## 📊 Admin Panel Usage

### 1. Access Admin Panel
Navigate to http://localhost:8000/admin/ and login with superuser credentials.

### 2. Explore Features
Each feature has its own section in the admin:
- **Integration Hub** - Manage webhooks, integrations
- **AI Insights** - View AI insights, prediction models
- **Gamification** - Configure achievements, challenges
- **Multi Tenant** - Manage tenants, users
- **SSO Integration** - Configure SSO providers
- **Collaboration** - Manage deal rooms, channels
- **GDPR Compliance** - Review consents, exports, breaches

---

## 🐛 Troubleshooting

### Database Issues
```bash
# Reset database
cd backend
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
```

### Migration Issues
```bash
# Delete migrations and recreate
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

### Frontend Issues
```bash
# Clear cache and reinstall
cd frontend
rm -rf .next node_modules
npm install
npm run dev
```

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

---

## 🎓 Next Steps

### Learn More
1. Read **ADVANCED_FEATURES.md** for detailed feature documentation
2. Check **ADVANCED_QUICK_REFERENCE.md** for API reference
3. Review **MULTI_TENANT_GUIDE.md** for multi-tenancy setup
4. Study **SSO_INTEGRATION_GUIDE.md** for SSO configuration

### Customize & Extend
1. Modify models in `backend/*/models.py`
2. Add custom endpoints in `backend/*/views.py`
3. Create new UI components in `frontend/src/components/`
4. Add custom business logic in `backend/*/services.py`

### Deploy to Production
1. Configure environment variables
2. Set up PostgreSQL and Redis
3. Configure Celery workers
4. Enable SSL/TLS
5. Set up OAuth/SAML providers
6. Configure email settings
7. Set up monitoring and logging

---

## 🎉 You're Ready!

All 7 enterprise features are now operational. Enjoy building amazing CRM experiences!

For issues or questions, refer to:
- **PROJECT_COMPLETION_SUMMARY.md** - Complete implementation details
- **ADVANCED_FEATURES.md** - Feature documentation
- **Django Admin Panel** - Configuration interface
- **API Docs** - http://localhost:8000/api/docs/

Happy coding! 🚀
