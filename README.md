# MyCRM - Enterprise CRM Solution

A full-stack Customer Relationship Management (CRM) system built with Django REST Framework and Next.js, featuring advanced lead management, contact tracking, opportunity management, and AI-powered analytics.

## 🚀 Features

### Core Functionality
- **Lead Management**: Comprehensive lead tracking with scoring and qualification
- **Contact Management**: Centralized contact database with relationship tracking
- **Opportunity Management**: Sales pipeline management with deal tracking
- **Task Management**: Task assignment and tracking system
- **Communication Management**: Integrated communication tracking (email, calls, meetings)
- **Reporting & Analytics**: Advanced reporting with AI-powered insights

### Enterprise Features
- **Role-Based Access Control (RBAC)**: Granular permission management
- **AI Analytics**: Machine learning-powered lead scoring and predictions
- **Workflow Automation**: Automated business process workflows
- **Email Integration**: SendGrid integration for email communications
- **SMS Integration**: Twilio integration for SMS notifications
- **Data Export**: Excel and PDF report generation
- **Search**: Advanced search capabilities across entities
- **Security**: Enterprise-grade security with rate limiting, OAuth, and API key management

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.2.7
- **API**: Django REST Framework 3.15.2
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL (production), SQLite (development)
- **Task Queue**: Celery with Redis
- **Cache**: Redis
- **Security**: bcrypt, cryptography, 2FA (pyotp)

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
   - Admin Panel: http://localhost:8000/admin

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
│   ├── accounts/              # User account management
│   ├── contact_management/    # Contact CRUD operations
│   ├── lead_management/       # Lead tracking and scoring
│   ├── opportunity_management/# Sales opportunity tracking
│   ├── task_management/       # Task management
│   ├── communication_management/ # Communication logs
│   ├── reporting/             # Reports and analytics
│   ├── core/                  # Core utilities (AI, workflows, security)
│   ├── backend/               # Django settings and configuration
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
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

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

- `/api/contacts/` - Contact management
- `/api/leads/` - Lead management
- `/api/opportunities/` - Opportunity tracking
- `/api/tasks/` - Task management
- `/api/communications/` - Communication logs
- `/api/reports/` - Reporting and analytics
- `/api/users/` - User management

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
