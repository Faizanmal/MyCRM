# Quick Start Guide - MyCRM with Full Monitoring

This guide helps you get MyCRM running with the complete monitoring and observability stack in under 10 minutes.

## Prerequisites

- Docker and Docker Compose installed
- 8GB RAM minimum (16GB recommended)
- 20GB free disk space

## Step 1: Clone and Configure

```bash
# Clone the repository
git clone https://github.com/yourusername/MyCRM.git
cd MyCRM

# Create environment file
cp backend/.env.example backend/.env

# Generate a strong SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(50))"
# Copy the output and paste into backend/.env as SECRET_KEY
```

## Step 2: Update Environment Variables

Edit `backend/.env`:

```env
# Minimum required settings
SECRET_KEY=paste-your-generated-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_NAME=mycrm_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your-secure-password
DATABASE_HOST=db
DATABASE_PORT=5432

REDIS_PASSWORD=your-redis-password
```

## Step 3: Start All Services

```bash
# Start the complete stack (backend, frontend, database, redis, celery, monitoring)
docker-compose -f docker-compose.production.yml up -d

# This will start:
# - PostgreSQL database
# - Redis cache
# - Django backend (with Gunicorn)
# - Celery workers
# - Next.js frontend
# - Prometheus
# - Grafana
# - Loki + Promtail
# - All metric exporters
```

## Step 4: Initialize Database

```bash
# Run migrations
docker-compose -f docker-compose.production.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.production.yml exec backend python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput
```

## Step 5: Verify Installation

### Check Service Health

```bash
# Backend health check
curl http://localhost:8000/api/core/health/

# Readiness check (DB + Redis)
curl http://localhost:8000/api/core/health/ready/

# Service status
curl http://localhost:8000/api/core/status/
```

### Access Services

| Service | URL | Default Credentials |
|---------|-----|-------------------|
| **Application** | http://localhost:8000 | Your superuser |
| **Admin Panel** | http://localhost:8000/admin/ | Your superuser |
| **API Docs** | http://localhost:8000/api/docs/ | - |
| **Frontend** | http://localhost:3000 | Your superuser |
| **Grafana** | http://localhost:3001 | admin/admin |
| **Prometheus** | http://localhost:9090 | - |

## Step 6: Configure Grafana

1. **Login to Grafana**
   - URL: http://localhost:3001
   - Username: `admin`
   - Password: `admin` (change immediately!)

2. **Change Default Password**
   - Click on profile icon → Preferences → Change Password

3. **Verify Datasources**
   - Go to Configuration → Data sources
   - Verify Prometheus and Loki are connected (green checkmark)

4. **Import Dashboards**
   - Go to Dashboards → Import
   - Import dashboard IDs:
     - `1860` - Node Exporter Full
     - `763` - Redis Dashboard
     - `9628` - PostgreSQL Database
     - `13639` - Django Monitoring

5. **Set Up Alerts**
   - Go to Alerting → Notification channels
   - Add Slack webhook or email notifications

## Step 7: Test Monitoring

### Generate Some Traffic

```bash
# Create test data
docker-compose exec backend python manage.py shell

# In Python shell:
from lead_management.models import Lead
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.first()
for i in range(100):
    Lead.objects.create(
        name=f"Test Lead {i}",
        email=f"lead{i}@example.com",
        status="new",
        created_by=user
    )
```

### View Metrics in Grafana

1. Go to http://localhost:3001
2. Navigate to Dashboards
3. View real-time metrics:
   - API request rates
   - Database query performance
   - System resources (CPU, memory, disk)
   - Business metrics (leads created)

### View Logs in Loki

1. In Grafana, go to Explore
2. Select Loki datasource
3. Query: `{job="mycrm-backend"}`
4. View application logs in real-time

### Check Prometheus

1. Go to http://localhost:9090
2. Try queries:
   ```promql
   # API request rate
   rate(mycrm_http_requests_total[5m])
   
   # Database query duration
   histogram_quantile(0.95, rate(mycrm_db_query_duration_seconds_bucket[5m]))
   
   # System CPU usage
   100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
   ```

## Step 8: Configure Backups

```bash
# Make backup script executable
chmod +x scripts/backup.sh
chmod +x scripts/restore.sh

# Set backup encryption key
echo "BACKUP_ENCRYPTION_KEY=your-32-character-encryption-key" >> backend/.env

# Test manual backup
./scripts/backup.sh

# Verify backup created
ls -lh backup/
```

### Set Up Automated Backups

```bash
# Add to crontab (Linux/Mac)
crontab -e

# Add this line for daily backups at 2 AM
0 2 * * * /path/to/MyCRM/scripts/backup.sh >> /var/log/mycrm-backup.log 2>&1

# For Windows, use Task Scheduler:
# - Open Task Scheduler
# - Create Basic Task
# - Set trigger: Daily at 2:00 AM
# - Action: Start a program
# - Program: bash.exe
# - Arguments: C:\path\to\MyCRM\scripts\backup.sh
```

## Step 9: Security Audit

```bash
# Run security audit
chmod +x scripts/security-audit.sh
./scripts/security-audit.sh

# Review and fix any issues reported
```

## Step 10: Load Testing (Optional)

```bash
# Install Locust
pip install locust

# Run load test
cd backend
locust -f locustfile.py --host=http://localhost:8000

# Open browser to http://localhost:8089
# Set users: 100, spawn rate: 10
# Start test and monitor in Grafana
```

## Common Commands

### View Logs

```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f backend
docker-compose -f docker-compose.production.yml logs -f grafana
docker-compose -f docker-compose.production.yml logs -f prometheus
```

### Restart Services

```bash
# Restart single service
docker-compose -f docker-compose.production.yml restart backend

# Restart all services
docker-compose -f docker-compose.production.yml restart
```

### Stop Everything

```bash
# Stop all services (keeps data)
docker-compose -f docker-compose.production.yml stop

# Stop and remove containers (keeps data in volumes)
docker-compose -f docker-compose.production.yml down

# Stop and remove everything including volumes (⚠️ destroys all data)
docker-compose -f docker-compose.production.yml down -v
```

### Update Application

```bash
# Pull latest code
git pull

# Rebuild containers
docker-compose -f docker-compose.production.yml build

# Restart with new code
docker-compose -f docker-compose.production.yml up -d

# Run migrations
docker-compose -f docker-compose.production.yml exec backend python manage.py migrate
```

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Missing SECRET_KEY - check .env file
# 2. Database not ready - wait 30 seconds and retry
# 3. Port 8000 in use - stop other services
```

### Database Connection Error

```bash
# Verify database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection
docker-compose exec db psql -U postgres -d mycrm_db -c "SELECT 1;"
```

### Redis Connection Error

```bash
# Verify Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return "PONG"
```

### Grafana Shows No Data

```bash
# Verify Prometheus is scraping
# Go to http://localhost:9090/targets
# All targets should show "UP"

# Check datasource in Grafana
# Configuration → Data sources → Prometheus
# Click "Test" button - should show green checkmark
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# If memory is high, you can:
# 1. Reduce Prometheus retention: --storage.tsdb.retention.time=15d
# 2. Reduce Gunicorn workers in docker-compose.yml
# 3. Add swap space to your system
```

## Next Steps

1. **Configure SSL/HTTPS**
   - Set up reverse proxy (Nginx)
   - Obtain SSL certificate (Let's Encrypt)
   - Update ALLOWED_HOSTS and CORS settings

2. **Set Up Alerting**
   - Configure Slack webhook in Grafana
   - Set up email notifications
   - Configure PagerDuty (for critical alerts)

3. **Production Hardening**
   - Review PRODUCTION_CHECKLIST.md
   - Change all default passwords
   - Enable firewall rules
   - Set up fail2ban

4. **Performance Tuning**
   - Review PERFORMANCE_OPTIMIZATION.md
   - Add database indexes for your queries
   - Configure CDN for static assets
   - Enable caching strategies

5. **Backup Strategy**
   - Test restore procedure
   - Configure cloud storage upload
   - Set up monitoring for backup success/failure
   - Document recovery procedures

## Support

- **Documentation**: Check `/docs` directory
- **Issues**: Open GitHub issue
- **Security**: Report to security@yourcompany.com

## Success! 🎉

Your MyCRM installation is now running with:
- ✓ Full application stack
- ✓ Complete monitoring (Prometheus + Grafana)
- ✓ Centralized logging (Loki)
- ✓ Error tracking ready (Sentry)
- ✓ Automated backups configured
- ✓ Security hardened

You're ready to start using MyCRM in production!
