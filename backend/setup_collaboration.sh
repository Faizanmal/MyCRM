#!/bin/bash

# Advanced Collaboration Tools Setup Script

echo "🚀 Setting up Advanced Collaboration Tools..."

# Navigate to backend directory
cd "$(dirname "$0")"

# Create migrations
echo "📦 Creating database migrations..."
python manage.py makemigrations collaboration

# Apply migrations
echo "⚙️ Applying migrations..."
python manage.py migrate collaboration

echo "✅ Advanced Collaboration Tools setup complete!"
echo ""
echo "📝 Available features:"
echo "   - Deal Rooms: Secure collaboration spaces for opportunities"
echo "   - Team Messaging: Real-time chat with channels and threading"
echo "   - Document Collaboration: Version control, comments, locking"
echo "   - Approval Workflows: Configurable multi-step approvals"
echo ""
echo "🌐 API Endpoints available at:"
echo "   - /api/v1/collaboration/deal-rooms/"
echo "   - /api/v1/collaboration/channels/"
echo "   - /api/v1/collaboration/messages/"
echo "   - /api/v1/collaboration/documents/"
echo "   - /api/v1/collaboration/document-comments/"
echo "   - /api/v1/collaboration/workflows/"
echo "   - /api/v1/collaboration/approval-instances/"
