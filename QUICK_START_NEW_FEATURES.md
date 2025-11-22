# 🚀 Quick Start Guide - New Features

## Overview
Three major feature sets have been added to MyCRM:
1. **Integration Hub** - Connect with Slack, Google, Zapier
2. **AI Insights** - Churn prediction, recommendations, content generation
3. **Gamification** - Points, achievements, leaderboards, challenges

---

## ⚡ Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
cd /workspaces/MyCRM/backend
pip install openai textblob
```

### Step 2: Run Migrations
```bash
python manage.py makemigrations integration_hub
python manage.py makemigrations ai_insights
python manage.py makemigrations gamification
python manage.py migrate
```

### Step 3: Set Environment Variables (Optional but Recommended)
Create or update `.env`:
```bash
# For AI content generation
OPENAI_API_KEY=your-key-here

# For Slack integration
SLACK_CLIENT_ID=your-client-id
SLACK_CLIENT_SECRET=your-client-secret

# For Google integration
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

### Step 4: Create Initial Data
```bash
python manage.py shell
```

```python
# Create integration providers
from integration_hub.models import IntegrationProvider

IntegrationProvider.objects.create(
    name='Slack',
    slug='slack',
    category='communication',
    description='Team collaboration platform',
    auth_type='oauth2',
    supports_webhooks=True,
    is_active=True
)

IntegrationProvider.objects.create(
    name='Google Workspace',
    slug='google-workspace',
    category='productivity',
    description='Google productivity suite',
    auth_type='oauth2',
    supports_webhooks=False,
    is_active=True
)

IntegrationProvider.objects.create(
    name='Zapier',
    slug='zapier',
    category='automation',
    description='Workflow automation',
    auth_type='api_key',
    supports_webhooks=True,
    is_active=True
)

# Create sample achievements
from gamification.models import Achievement

Achievement.objects.bulk_create([
    Achievement(
        name='First Deal',
        description='Close your first deal',
        category='sales',
        difficulty='bronze',
        criteria_type='deals_won',
        criteria_value=1,
        points=50,
        badge_icon='🎯'
    ),
    Achievement(
        name='Deal Machine',
        description='Close 10 deals',
        category='sales',
        difficulty='silver',
        criteria_type='deals_won',
        criteria_value=10,
        points=200,
        badge_icon='🏆'
    ),
    Achievement(
        name='Revenue King',
        description='Generate $100K in revenue',
        category='sales',
        difficulty='gold',
        criteria_type='revenue_target',
        criteria_value=100000,
        points=500,
        badge_icon='💰'
    ),
    Achievement(
        name='Task Master',
        description='Complete 50 tasks',
        category='activity',
        difficulty='silver',
        criteria_type='tasks_completed',
        criteria_value=50,
        points=150,
        badge_icon='✅'
    ),
    Achievement(
        name='Week Streak',
        description='7 days activity streak',
        category='activity',
        difficulty='bronze',
        criteria_type='streak_days',
        criteria_value=7,
        points=75,
        badge_icon='🔥'
    ),
])

# Create leaderboards
from gamification.models import Leaderboard

Leaderboard.objects.bulk_create([
    Leaderboard(
        name='Top Performers - Monthly',
        metric='total_points',
        period='monthly',
        display_count=10,
        is_public=True
    ),
    Leaderboard(
        name='Sales Leaders - This Week',
        metric='deals_won',
        period='weekly',
        display_count=5,
        is_public=True
    ),
    Leaderboard(
        name='Revenue Champions - All Time',
        metric='revenue_generated',
        period='all_time',
        display_count=10,
        is_public=True
    ),
])

print("✅ Setup complete!")
exit()
```

### Step 5: Start the Server
```bash
python manage.py runserver
```

---

## 🧪 Test the Features

### Test 1: Integration Hub
```bash
# Get your auth token first
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access'])")

# List available providers
curl http://localhost:8000/api/v1/integration-hub/providers/ \
  -H "Authorization: Bearer $TOKEN"
```

### Test 2: AI Churn Prediction
```bash
# Predict churn for a contact (replace contact_id)
curl -X POST http://localhost:8000/api/v1/ai-insights/churn-predictions/predict/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contact_id": 1}'
```

### Test 3: Next Best Actions
```bash
# Generate recommendations
curl -X POST http://localhost:8000/api/v1/ai-insights/next-best-actions/generate/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"limit": 5}'

# View pending actions
curl http://localhost:8000/api/v1/ai-insights/next-best-actions/pending/ \
  -H "Authorization: Bearer $TOKEN"
```

### Test 4: AI Content Generation
```bash
# Generate an email (requires OPENAI_API_KEY)
curl -X POST http://localhost:8000/api/v1/ai-insights/generated-content/generate/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "email",
    "tone": "professional",
    "context": {
      "recipient_name": "John Doe",
      "company_name": "Acme Corp",
      "purpose": "follow up on proposal"
    }
  }'
```

### Test 5: Gamification
```bash
# View achievements
curl http://localhost:8000/api/v1/gamification/achievements/ \
  -H "Authorization: Bearer $TOKEN"

# Check your points (will auto-create)
curl http://localhost:8000/api/v1/gamification/points/ \
  -H "Authorization: Bearer $TOKEN"

# View leaderboards
curl http://localhost:8000/api/v1/gamification/leaderboards/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 Access API Documentation

Visit: http://localhost:8000/api/docs/

Browse all endpoints, try them out interactively!

---

## 🎮 Try the Features

### 1. Connect an Integration
1. Go to `/api/v1/integration-hub/providers/` to see available providers
2. Create an integration: `POST /api/v1/integration-hub/integrations/`
3. For OAuth providers, call `/integrations/{id}/connect/` to get auth URL
4. Test connection: `POST /integrations/{id}/test_connection/`

### 2. Get AI Recommendations
1. Generate recommendations: `POST /api/v1/ai-insights/next-best-actions/generate/`
2. View pending actions: `GET /api/v1/ai-insights/next-best-actions/pending/`
3. Accept an action: `POST /api/v1/ai-insights/next-best-actions/{id}/accept/`
4. Mark complete: `POST /api/v1/ai-insights/next-best-actions/{id}/complete/`

### 3. Generate Content with AI
1. Generate email: `POST /api/v1/ai-insights/generated-content/generate/`
2. Mark as used: `POST /api/v1/ai-insights/generated-content/{id}/mark_used/`
3. Rate content: `POST /api/v1/ai-insights/generated-content/{id}/rate/`

### 4. Check Gamification Progress
1. View your points: `GET /api/v1/gamification/points/`
2. See achievements: `GET /api/v1/gamification/user-achievements/`
3. Check leaderboard: `GET /api/v1/gamification/leaderboards/{id}/rankings/`
4. View challenges: `GET /api/v1/gamification/challenges/`

---

## 🔧 Troubleshooting

### Issue: Migrations fail
**Solution:**
```bash
python manage.py makemigrations --empty integration_hub
python manage.py makemigrations --empty ai_insights
python manage.py makemigrations --empty gamification
python manage.py migrate
```

### Issue: OpenAI API key error
**Solution:** AI content generation requires an OpenAI API key. If not set, it will use fallback templates.

### Issue: No data in leaderboards
**Solution:** Leaderboards require user activity. Create some test data:
```python
from gamification.models import UserPoints
from django.contrib.auth.models import User

for user in User.objects.all():
    points, _ = UserPoints.objects.get_or_create(user=user)
    points.add_points(100, 'sales')
```

### Issue: Churn prediction returns empty
**Solution:** Churn model needs training data. It trains automatically on first use, but needs at least 10 contacts.

---

## 📱 Frontend Integration

Add these components to your React/Next.js frontend:

### Integration Status Widget
```jsx
import { useEffect, useState } from 'react';

export default function IntegrationWidget() {
  const [integrations, setIntegrations] = useState([]);
  
  useEffect(() => {
    fetch('/api/v1/integration-hub/integrations/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => res.json())
    .then(data => setIntegrations(data.results));
  }, []);
  
  return (
    <div className="integration-widget">
      <h3>Integrations</h3>
      {integrations.map(int => (
        <div key={int.id}>
          <span>{int.provider_name}</span>
          <span className={`status-${int.status}`}>{int.status}</span>
        </div>
      ))}
    </div>
  );
}
```

### AI Actions Dashboard
```jsx
export default function ActionsDashboard() {
  const [actions, setActions] = useState([]);
  
  useEffect(() => {
    fetch('/api/v1/ai-insights/next-best-actions/pending/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => res.json())
    .then(data => setActions(data));
  }, []);
  
  return (
    <div>
      <h2>Recommended Actions</h2>
      {actions.map(action => (
        <div key={action.id} className="action-card">
          <h4>{action.title}</h4>
          <p>{action.description}</p>
          <span>Priority: {action.priority_score}</span>
        </div>
      ))}
    </div>
  );
}
```

### Gamification Badge
```jsx
export default function UserBadge() {
  const [points, setPoints] = useState(null);
  
  useEffect(() => {
    fetch('/api/v1/gamification/points/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => res.json())
    .then(data => setPoints(data));
  }, []);
  
  if (!points) return null;
  
  return (
    <div className="user-badge">
      <div>Level {points.level}</div>
      <div>{points.total_points} pts</div>
      <div>🔥 {points.current_streak} days</div>
    </div>
  );
}
```

---

## 🎉 You're All Set!

The new features are now active:
- ✅ Integration Hub
- ✅ AI Insights (Churn, Recommendations, Content)
- ✅ Gamification System

Start exploring at: http://localhost:8000/api/docs/

For detailed documentation, see:
- `NEW_FEATURES_GUIDE.md`
- `IMPLEMENTATION_COMPLETE.md`

---

**Need Help?**
- Check API docs: http://localhost:8000/api/docs/
- View code: `backend/integration_hub/`, `backend/ai_insights/`, `backend/gamification/`
- Test endpoints using the Swagger UI
