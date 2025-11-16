# MyCRM - Enterprise CRM Solution

A full-stack Customer Relationship Management (CRM) system built with Django REST Framework and Next.js, featuring advanced lead management, contact tracking, opportunity management, and AI-powered analytics.

## 🚀 Features

### Core CRM Functionality
- **Lead Management**: Comprehensive lead tracking with AI scoring and qualification
- **Contact Management**: Centralized contact database with relationship tracking
- **Opportunity Management**: Sales pipeline management with deal tracking
- **Task Management**: Task assignment, tracking, and automation
- **Communication Management**: Integrated multi-channel communication tracking
- **Document Management**: Centralized document storage and organization

### 🆕 Foundation Features (v1.0)
- **Unified REST API (v1)**: Comprehensive, versioned API with filtering, search, and bulk operations
- **CSV Import/Export**: Bulk data import/export with field mapping and validation
- **AI Lead Scoring**: Machine learning-based lead prioritization with automatic retraining
- **Workflow Automation**: Visual workflow builder with triggers and actions
- **Background Jobs**: Celery-based async task processing for heavy operations
- **Smart Notifications**: Multi-channel notifications with user preferences and digests
- **API Documentation**: Interactive Swagger UI and ReDoc documentation

### ⚡ Advanced Features (v2.0)
1. **📊 Advanced Analytics Dashboard**
   - Sales forecasting with ML predictions
   - Conversion funnel analysis with bottleneck detection
   - Cohort analysis for retention tracking
   - Custom metrics builder for KPI tracking

2. **📧 Email Campaign Management**
   - Template builder with variable substitution
   - Campaign scheduling and automation
   - Email tracking (opens, clicks, bounces)
   - Unsubscribe management and compliance
   - A/B testing support

3. **🔍 Comprehensive Audit Trail**
   - Track all CRUD operations with full context
   - Field-level change history and version control
   - Data snapshots for point-in-time recovery
   - Configurable retention policies per model
   - Advanced search and filtering

4. **📱 Customizable Dashboard Widgets**
   - 12 widget types (metrics, charts, tables, timelines, maps)
   - Drag-and-drop grid layout system
   - Real-time data with intelligent caching
   - Widget sharing and role-based permissions
   - Auto-refresh intervals

5. **⚡ Real-time WebSocket Notifications**
   - Live notifications without polling
   - Activity feed updates in real-time
   - Task/lead/opportunity change notifications
   - Connection monitoring and auto-reconnect
   - Mark as read functionality

6. **🔧 Custom Field Builder**
   - 14 field types with full validation
   - Add custom fields to any entity
   - Field groups for better organization
   - Role-based field visibility
   - Dynamic form generation

7. **📅 Unified Activity Timeline**
   - Consolidated view across all entities
   - Multiple data sources (activities, audit, tasks, opportunities)
   - Advanced filtering by entity, user, date range
   - Entity-specific timeline views
   - Export capabilities

8. **🔎 Advanced Search & Filtering**
   - Full-text search across all fields
   - Complex filter combinations
   - Date range filtering
   - Nested relationship filtering
   - Saved search templates

### Enterprise Security & Compliance
- **Role-Based Access Control (RBAC)**: Granular permission management
- **Audit Logging**: Complete activity tracking for compliance
- **Data Encryption**: At-rest and in-transit encryption
- **2FA Support**: Two-factor authentication with TOTP
- **Rate Limiting**: API rate limiting and throttling
- **OAuth Integration**: Third-party authentication support
- **Security Middleware**: Enterprise-grade security layers

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.2.7
- **API**: Django REST Framework 3.15.2
- **WebSockets**: Django Channels 4.0 + Daphne 4.0
- **Authentication**: JWT (djangorestframework-simplejwt 5.3.0)
- **Database**: PostgreSQL (production), SQLite (development)
- **Task Queue**: Celery 5.3.4 with Redis 5.0.1
- **Message Broker**: Redis + channels-redis 4.1.0
- **Cache**: Redis with django-redis 5.4.0
- **ML/AI**: scikit-learn 1.3.2, pandas 2.2.2, numpy 1.25.2
- **Security**: bcrypt 4.1.2, cryptography 42.0.5, 2FA (pyotp 2.9.0)
- **Documentation**: drf-spectacular 0.27.0

### Frontend
- **Framework**: Next.js 14+ (React 19)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI
- **State Management**: TanStack Query
- **Forms**: React Hook Form
- **Animation**: Framer Motion
- **Charts**: D3.js, Recharts

### DevOps
- **Containerization**: Docker & Docker Compose
- **Web Server**: Gunicorn
- **Static Files**: WhiteNoise
- **Monitoring**: Prometheus, Sentry

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+ and npm/yarn
- Docker & Docker Compose (optional but recommended)
- PostgreSQL 15+ (if not using Docker)
- Redis (if not using Docker)

## 🚀 Getting Started

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Faizanmal/MyCRM.git
   cd mycrm
   ```

2. **Set up environment variables**
   
   Create `.env` file in the backend directory:
   ```bash
   cp backend/.env.example backend/.env
   ```
   
   Edit `backend/.env` with your configuration:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://postgres:password@db:5432/mycrm_db
   REDIS_URL=redis://redis:6379
   
   # Email Configuration
   SENDGRID_API_KEY=your-sendgrid-api-key
   DEFAULT_FROM_EMAIL=noreply@yourcrm.com
   
   # SMS Configuration
   TWILIO_ACCOUNT_SID=your-twilio-sid
   TWILIO_AUTH_TOKEN=your-twilio-token
   TWILIO_PHONE_NUMBER=your-twilio-phone
   
   # Security
   ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=http://localhost:3000
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Run migrations**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api
   - API Documentation: http://localhost:8000/api/docs
   - Admin Panel: http://localhost:8000/admin

### Quick Setup Script

For fast local development setup:

```bash
# Run the automated setup script
./setup.sh

# Start Redis (required for Celery)
redis-server

# Terminal 1: Django server
cd backend && python manage.py runserver

# Terminal 2: Celery worker (for background tasks)
cd backend && celery -A backend worker --loglevel=info

# Terminal 3: Celery beat (for scheduled tasks)
cd backend && celery -A backend beat --loglevel=info
```

### Manual Setup

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

8. **Start Celery (in separate terminal)**
   ```bash
   celery -A backend worker -l info
   celery -A backend beat -l info
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Create environment file**
   ```bash
   cp .env.example .env.local
   ```
   
   Edit `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```

4. **Start development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000

## 📁 Project Structure

```
MyCRM/
├── backend/                    # Django backend
│   ├── api/                   # 🆕 Unified REST API v1
│   │   └── v1/                # API version 1 endpoints
│   ├── accounts/              # User account management
│   ├── contact_management/    # Contact CRUD operations
│   ├── lead_management/       # Lead tracking and scoring
│   ├── opportunity_management/# Sales opportunity tracking
│   ├── task_management/       # Task management
│   ├── communication_management/ # Communication logs
│   ├── activity_feed/         # Activity feed & notifications
│   ├── reporting/             # Reports and analytics
│   ├── core/                  # Core utilities (AI, workflows, security)
│   │   ├── lead_scoring.py    # 🆕 ML-based lead scoring
│   │   ├── workflows.py       # 🆕 Workflow automation
│   │   └── tasks.py           # 🆕 Celery background tasks
│   ├── backend/               # Django settings and configuration
│   │   └── celery.py          # 🆕 Celery configuration
│   ├── requirements.txt       # Python dependencies
│   └── manage.py             # Django management script
│
├── frontend/                  # Next.js frontend
│   ├── src/
│   │   ├── app/              # Next.js app directory
│   │   ├── components/       # Reusable React components
│   │   ├── lib/              # Utility functions
│   │   └── styles/           # Global styles
│   ├── public/               # Static assets
│   └── package.json          # Node dependencies
│
├── docker-compose.yml        # Docker composition
├── setup.sh                 # 🆕 Quick setup script
├── FEATURES.md              # 🆕 Complete feature documentation
├── IMPLEMENTATION_SUMMARY.md # 🆕 Implementation details
├── api_examples.py          # 🆕 Python API usage examples
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 📚 Documentation

- **[FEATURES.md](FEATURES.md)** - Complete feature documentation with API reference
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Implementation details and architecture
- **[api_examples.py](api_examples.py)** - Python code examples for all API endpoints
- **API Docs** - Interactive documentation at http://localhost:8000/api/docs/

## 🔧 Configuration

### Backend Configuration

Key settings in `backend/backend/settings.py`:

- **Database**: Configure PostgreSQL connection
- **Redis**: Set up Redis for caching and Celery
- **CORS**: Configure allowed origins for frontend
- **Email**: SendGrid API configuration
- **SMS**: Twilio API configuration
- **Security**: JWT settings, API key management

### Frontend Configuration

Environment variables in `frontend/.env.local`:

- `NEXT_PUBLIC_API_URL`: Backend API URL

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm run test
# or
yarn test
```

## 📊 API Documentation

Once the backend is running, access the API documentation at:
- Browsable API: http://localhost:8000/api/
- Admin Panel: http://localhost:8000/admin/

### Main API Endpoints

### Unified API v1 (Recommended)
- `/api/v1/leads/` - Lead management with scoring
- `/api/v1/contacts/` - Contact management
- `/api/v1/opportunities/` - Opportunity tracking with pipeline
- `/api/v1/tasks/` - Task management
- `/api/v1/workflows/` - Workflow automation
- `/api/v1/import/{resource}/` - CSV import
- `/api/v1/export/{resource}/` - CSV export
- `/api/v1/scoring/` - AI lead scoring

### Legacy Endpoints
- `/api/contacts/` - Contact management
- `/api/leads/` - Lead management
- `/api/opportunities/` - Opportunity tracking
- `/api/tasks/` - Task management
- `/api/communications/` - Communication logs
- `/api/reports/` - Reporting and analytics
- `/api/users/` - User management

### Quick API Examples

```bash
# Get JWT token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# List leads (with filtering)
curl http://localhost:8000/api/v1/leads/?status=qualified \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create a lead
curl -X POST http://localhost:8000/api/v1/leads/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","email":"john@example.com"}'

# Import leads from CSV
curl -X POST http://localhost:8000/api/v1/import/leads/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@leads.csv" \
  -F 'mapping={"Email":"email","Name":"first_name"}'

# Get pipeline statistics
curl http://localhost:8000/api/v1/opportunities/pipeline/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Obtain token**:
   ```bash
   POST /api/token/
   {
     "username": "your_username",
     "password": "your_password"
   }
   ```

2. **Refresh token**:
   ```bash
   POST /api/token/refresh/
   {
     "refresh": "your_refresh_token"
   }
   ```

3. **Use token in requests**:
   ```
   Authorization: Bearer your_access_token
   ```

## 🚀 Deployment

### Production Checklist

1. Set `DEBUG=False` in backend settings
2. Configure proper `SECRET_KEY`
3. Set up PostgreSQL database
4. Configure static file serving
5. Set up SSL/HTTPS
6. Configure allowed hosts and CORS
7. Set up environment variables
8. Run `python manage.py collectstatic`
9. Set up proper logging and monitoring
10. Configure backup strategy

### Deployment Options

- **Docker**: Use docker-compose.prod.yml for production
- **Cloud Platforms**: AWS, Google Cloud, Azure
- **PaaS**: Heroku, DigitalOcean App Platform
- **Frontend**: Vercel, Netlify

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

Please check the [Issues](https://github.com/yourusername/mycrm/issues) page for known bugs and feature requests.

## 📧 Support

For support, email support@yourcrm.com or open an issue on GitHub.

## 👥 Authors

- Your Name - [GitHub Profile](https://github.com/yourusername)

## 🙏 Acknowledgments

- Django REST Framework team
- Next.js team
- All open-source contributors

## 📈 Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced AI predictions
- [ ] Integration with more third-party services
- [ ] Multi-tenant support
- [ ] Advanced workflow builder UI
- [ ] Real-time collaboration features
- [ ] Enhanced reporting dashboards

---

Made with ❤️ by Your Team
