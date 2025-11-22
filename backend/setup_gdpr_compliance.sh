#!/bin/bash

# GDPR Compliance Tools Setup Script

echo "🔒 Setting up GDPR Compliance Tools..."

# Navigate to backend directory
cd "$(dirname "$0")"

# Create migrations
echo "📦 Creating database migrations..."
python manage.py makemigrations gdpr_compliance

# Apply migrations
echo "⚙️ Applying migrations..."
python manage.py migrate gdpr_compliance

echo "✅ GDPR Compliance Tools setup complete!"
echo ""
echo "📝 Available features:"
echo "   - Consent Management: Track and manage user consents"
echo "   - Data Export: Right to data portability"
echo "   - Data Deletion: Right to be forgotten"
echo "   - Processing Activities: Article 30 records"
echo "   - Breach Management: Incident tracking and notifications"
echo "   - Privacy Preferences: User privacy settings"
echo "   - Audit Logging: Data access tracking"
echo ""
echo "🌐 API Endpoints available at:"
echo "   - /api/v1/gdpr/consent-types/"
echo "   - /api/v1/gdpr/user-consents/"
echo "   - /api/v1/gdpr/export-requests/"
echo "   - /api/v1/gdpr/deletion-requests/"
echo "   - /api/v1/gdpr/processing-activities/"
echo "   - /api/v1/gdpr/breach-incidents/"
echo "   - /api/v1/gdpr/access-logs/"
echo "   - /api/v1/gdpr/privacy-notices/"
echo "   - /api/v1/gdpr/privacy-preferences/"
