#!/bin/bash

# MyCRM New Features Setup Script
# Run this script to set up all new features

set -e

echo "🚀 MyCRM Advanced Features Setup"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navigate to backend
cd "$(dirname "$0")/backend"

echo -e "${BLUE}Step 1: Installing dependencies...${NC}"
pip install -q openai textblob

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

echo -e "${BLUE}Step 2: Running migrations...${NC}"
python manage.py makemigrations integration_hub
python manage.py makemigrations ai_insights
python manage.py makemigrations gamification
python manage.py migrate

echo -e "${GREEN}✓ Migrations complete${NC}"
echo ""

echo -e "${BLUE}Step 3: Creating initial data...${NC}"
python manage.py shell << 'EOF'
from integration_hub.models import IntegrationProvider
from gamification.models import Achievement, Leaderboard

# Create integration providers
providers = [
    {
        'name': 'Slack',
        'slug': 'slack',
        'category': 'communication',
        'description': 'Team collaboration and messaging platform',
        'auth_type': 'oauth2',
        'supports_webhooks': True,
        'is_active': True
    },
    {
        'name': 'Google Workspace',
        'slug': 'google-workspace',
        'category': 'productivity',
        'description': 'Google productivity and collaboration suite',
        'auth_type': 'oauth2',
        'supports_webhooks': False,
        'is_active': True
    },
    {
        'name': 'Zapier',
        'slug': 'zapier',
        'category': 'automation',
        'description': 'Workflow automation platform',
        'auth_type': 'api_key',
        'supports_webhooks': True,
        'is_active': True
    }
]

for provider_data in providers:
    IntegrationProvider.objects.get_or_create(
        slug=provider_data['slug'],
        defaults=provider_data
    )

print("✓ Integration providers created")

# Create achievements
achievements = [
    {
        'name': 'First Deal',
        'description': 'Close your first deal',
        'category': 'sales',
        'difficulty': 'bronze',
        'criteria_type': 'deals_won',
        'criteria_value': 1,
        'points': 50,
        'badge_icon': '🎯'
    },
    {
        'name': 'Deal Machine',
        'description': 'Close 10 deals',
        'category': 'sales',
        'difficulty': 'silver',
        'criteria_type': 'deals_won',
        'criteria_value': 10,
        'points': 200,
        'badge_icon': '🏆'
    },
    {
        'name': 'Revenue King',
        'description': 'Generate $100,000 in revenue',
        'category': 'sales',
        'difficulty': 'gold',
        'criteria_type': 'revenue_target',
        'criteria_value': 100000,
        'points': 500,
        'badge_icon': '💰'
    },
    {
        'name': 'Task Master',
        'description': 'Complete 50 tasks',
        'category': 'activity',
        'difficulty': 'silver',
        'criteria_type': 'tasks_completed',
        'criteria_value': 50,
        'points': 150,
        'badge_icon': '✅'
    },
    {
        'name': 'Week Warrior',
        'description': 'Maintain 7-day activity streak',
        'category': 'activity',
        'difficulty': 'bronze',
        'criteria_type': 'streak_days',
        'criteria_value': 7,
        'points': 75,
        'badge_icon': '🔥'
    },
    {
        'name': 'Perfect Week',
        'description': 'Complete all tasks in a week',
        'category': 'quality',
        'difficulty': 'silver',
        'criteria_type': 'perfect_week',
        'criteria_value': 1,
        'points': 100,
        'badge_icon': '⭐'
    }
]

for achievement_data in achievements:
    Achievement.objects.get_or_create(
        name=achievement_data['name'],
        defaults=achievement_data
    )

print("✓ Achievements created")

# Create leaderboards
leaderboards = [
    {
        'name': 'Top Performers - This Month',
        'metric': 'total_points',
        'period': 'monthly',
        'display_count': 10,
        'is_public': True
    },
    {
        'name': 'Sales Champions - This Week',
        'metric': 'deals_won',
        'period': 'weekly',
        'display_count': 5,
        'is_public': True
    },
    {
        'name': 'Revenue Leaders - All Time',
        'metric': 'revenue_generated',
        'period': 'all_time',
        'display_count': 10,
        'is_public': True
    },
    {
        'name': 'Activity Stars - Today',
        'metric': 'total_points',
        'period': 'daily',
        'display_count': 5,
        'is_public': True
    }
]

for leaderboard_data in leaderboards:
    Leaderboard.objects.get_or_create(
        name=leaderboard_data['name'],
        defaults=leaderboard_data
    )

print("✓ Leaderboards created")
print("")
print("=" * 50)
print("✅ Setup complete!")
print("=" * 50)
EOF

echo -e "${GREEN}✓ Initial data created${NC}"
echo ""

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "New features are now ready:"
echo "  ✓ Integration Hub"
echo "  ✓ AI Insights (Churn, Recommendations, Content)"
echo "  ✓ Gamification System"
echo ""
echo "Next steps:"
echo "  1. Set environment variables (optional):"
echo "     - OPENAI_API_KEY for AI content generation"
echo "     - SLACK_CLIENT_ID & SLACK_CLIENT_SECRET"
echo "     - GOOGLE_CLIENT_ID & GOOGLE_CLIENT_SECRET"
echo ""
echo "  2. Start the server:"
echo "     python manage.py runserver"
echo ""
echo "  3. Access API documentation:"
echo "     http://localhost:8000/api/docs/"
echo ""
echo "Documentation files:"
echo "  - QUICK_START_NEW_FEATURES.md"
echo "  - FEATURES_SUMMARY.md"
echo "  - NEW_FEATURES_GUIDE.md"
echo "  - IMPLEMENTATION_COMPLETE.md"
echo ""
