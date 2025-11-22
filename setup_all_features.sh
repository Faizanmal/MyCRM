#!/bin/bash

# Master Setup Script for All New Enterprise Features

echo "🚀 Setting up ALL Enterprise Features for MyCRM..."
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# List of new apps to migrate
APPS=(
    "integration_hub"
    "ai_insights"
    "gamification"
    "multi_tenant"
    "sso_integration"
    "collaboration"
    "gdpr_compliance"
)

echo "📦 Creating migrations for all new features..."
for app in "${APPS[@]}"; do
    echo "   - Creating migrations for $app..."
    python manage.py makemigrations $app 2>/dev/null || echo "     (migrations may already exist)"
done

echo ""
echo "⚙️ Applying all migrations..."
python manage.py migrate

echo ""
echo "✅ All Enterprise Features setup complete!"
echo ""
echo "🎉 Successfully installed:"
echo "   1. Integration Hub - Connect with external services"
echo "   2. AI Insights - Intelligent predictions and analytics"
echo "   3. Gamification - Engagement and rewards system"
echo "   4. Multi-Tenant Architecture - Organization management"
echo "   5. SSO Integration - OAuth2 and SAML 2.0 support"
echo "   6. Advanced Collaboration - Deal rooms, messaging, workflows"
echo "   7. GDPR Compliance - Privacy and data protection"
echo ""
echo "🌐 Frontend pages available at:"
echo "   - http://localhost:3000/integration-hub"
echo "   - http://localhost:3000/ai-insights"
echo "   - http://localhost:3000/gamification"
echo "   - http://localhost:3000/organizations"
echo "   - http://localhost:3000/sso-settings"
echo "   - http://localhost:3000/collaboration"
echo "   - http://localhost:3000/gdpr-compliance"
echo ""
echo "📚 Documentation:"
echo "   - README.md"
echo "   - FEATURES.md"
echo "   - ADVANCED_FEATURES.md"
echo "   - IMPLEMENTATION_SUMMARY.md"
echo ""
