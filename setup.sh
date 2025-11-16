#!/bin/bash

# MyCRM Quick Setup Script
# This script sets up the development environment for MyCRM

set -e

echo "🚀 MyCRM Quick Setup"
echo "===================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "backend/manage.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "📦 Step 1: Installing Python dependencies..."
cd backend
pip install -r requirements.txt

echo ""
echo "🗄️  Step 2: Setting up database..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "👤 Step 3: Creating superuser (optional)..."
echo "You can create a superuser now or skip this step."
read -p "Create superuser? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

echo ""
echo "📚 Step 4: Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "============="
echo ""
echo "1. Start Redis (required for Celery):"
echo "   ${YELLOW}redis-server${NC}"
echo "   OR using Docker:"
echo "   ${YELLOW}docker run -d -p 6379:6379 redis:latest${NC}"
echo ""
echo "2. Start Django development server:"
echo "   ${YELLOW}cd backend && python manage.py runserver${NC}"
echo ""
echo "3. Start Celery worker (in a new terminal):"
echo "   ${YELLOW}cd backend && celery -A backend worker --loglevel=info${NC}"
echo ""
echo "4. Start Celery beat scheduler (optional, in a new terminal):"
echo "   ${YELLOW}cd backend && celery -A backend beat --loglevel=info${NC}"
echo ""
echo "5. Access the application:"
echo "   - Admin: ${GREEN}http://localhost:8000/admin/${NC}"
echo "   - API Docs: ${GREEN}http://localhost:8000/api/docs/${NC}"
echo "   - API v1: ${GREEN}http://localhost:8000/api/v1/${NC}"
echo ""
echo "📖 For more information, see FEATURES.md"
echo ""
