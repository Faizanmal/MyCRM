# MyCRM - Developer-First CRM

A modern, API-first Customer Relationship Management system built with Django REST Framework and Next.js. Designed for engineering teams who need a flexible, customizable CRM that integrates seamlessly with their tech stack.

## 🚀 Features

### Core CRM Functionality
- **Lead Management**: Track and qualify leads with automated scoring
- **Contact Management**: Centralized contact database with relationship mapping
- **Opportunity Management**: Sales pipeline management with deal tracking
- **Task Management**: Task assignment, tracking, and automation
- **Communication Tracking**: Multi-channel communication logging
- **Document Management**: Secure document storage and organization

### Advanced Features
- **AI-Powered Lead Scoring**: Machine learning-based lead prioritization
- **Multi-Tenant Architecture**: Organization-based data isolation
- **SSO Integration**: OAuth 2.0 and SAML 2.0 support
- **GDPR Compliance Tools**: Data export, erasure, and consent management
- **Real-time Collaboration**: WebSocket-based notifications and updates
- **Advanced Reporting**: Custom dashboards and analytics
- **Email Campaigns**: Template-based email automation with tracking
- **API-First Design**: Comprehensive REST API with OpenAPI documentation
- **Third-Party Integrations**: Slack, Google Workspace, and webhook support

### Enterprise Security
- **Role-Based Access Control**: Granular permission management
- **Audit Logging**: Complete activity tracking for compliance
- **Data Encryption**: At-rest and in-transit encryption
- **Two-Factor Authentication**: TOTP-based 2FA
- **Rate Limiting**: API rate limiting and throttling

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.2 + Django REST Framework
- **Authentication**: JWT tokens
- **Database**: PostgreSQL (production) / SQLite (development)
- **Real-time**: Django Channels + WebSockets
- **Task Queue**: Celery + Redis
- **AI/ML**: scikit-learn, pandas, OpenAI API
- **Security**: bcrypt, cryptography, 2FA

### Frontend
- **Framework**: Next.js 14 + React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query
- **UI Components**: Radix UI

### DevOps
- **Containerization**: Docker & Docker Compose
- **Web Server**: Gunicorn + Daphne
- **Reverse Proxy**: Nginx
- **Monitoring**: Prometheus + Grafana
- **Logging**: Loki + Promtail

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 15+ (or Docker)
- Redis (or Docker)

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/mycrm.git
cd mycrm

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

### Manual Setup

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

# Frontend setup
cd ../frontend
npm install
npm run dev
```

## 📚 API Documentation

Once running, visit:
- **API Docs**: http://localhost:8000/api/docs/
- **Frontend**: http://localhost:3000

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
