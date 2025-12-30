# 🚀 MyCRM Deployment Guide

## Overview

This comprehensive guide covers deploying MyCRM to production environments. We support multiple deployment targets including Docker, Kubernetes, and traditional server deployments.

---

## 📋 Pre-Deployment Checklist

Before deploying to production, ensure you've completed:

- [ ] All tests pass locally (`python manage.py test`)
- [ ] Frontend builds successfully (`npm run build`)
- [ ] Environment variables configured
- [ ] Database migrations are up to date
- [ ] SSL certificates obtained
- [ ] Domain DNS configured
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Security audit completed

---

## 🔐 Environment Variables

### Backend Environment Variables

Create a `.env.production` file:

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=backend.settings_production
DJANGO_SECRET_KEY=your-super-secret-key-min-50-chars
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# Database
DATABASE_URL=postgres://user:password@db-host:5432/mycrm
DB_HOST=db-host
DB_PORT=5432
DB_NAME=mycrm
DB_USER=mycrm_user
DB_PASSWORD=secure-database-password

# Redis
REDIS_URL=redis://redis-host:6379/0
CELERY_BROKER_URL=redis://redis-host:6379/1
CELERY_RESULT_BACKEND=redis://redis-host:6379/2

# Security
CORS_ALLOWED_ORIGINS=https://yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Email
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# AWS S3 (for file storage)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=mycrm-files
AWS_S3_REGION_NAME=us-east-1

# AI Features (optional)
OPENAI_API_KEY=your-openai-api-key

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
```

### Frontend Environment Variables

Create `.env.production`:

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com/ws
NEXT_PUBLIC_APP_URL=https://yourdomain.com
NEXT_PUBLIC_SENTRY_DSN=https://your-frontend-sentry-dsn
```

---

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
# Clone repository
git clone https://github.com/yourorg/mycrm.git
cd mycrm

# Create production env files
cp .env.example .env.production

# Build and start services
docker-compose -f docker-compose.production.yml up -d

# Run migrations
docker-compose -f docker-compose.production.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.production.yml exec backend python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input
```

### Production Docker Compose

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
    depends_on:
      - backend
      - frontend
    restart: always

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    env_file: .env.production
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - db
      - redis
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    command: celery -A backend worker -l info --concurrency=4
    env_file: .env.production
    depends_on:
      - db
      - redis
    restart: always

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    command: celery -A backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    env_file: .env.production
    depends_on:
      - db
      - redis
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.production
      args:
        NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL}
    restart: always

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    restart: always

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

---

## ☸️ Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (EKS, GKE, AKS, or self-managed)
- `kubectl` configured
- `helm` installed
- Container registry access

### Deploy with Helm

```bash
# Add required Helm repos
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Create namespace
kubectl create namespace mycrm

# Create secrets
kubectl create secret generic mycrm-secrets \
  --namespace mycrm \
  --from-env-file=.env.production

# Install PostgreSQL
helm install mycrm-db bitnami/postgresql \
  --namespace mycrm \
  --set auth.database=mycrm \
  --set auth.username=mycrm_user \
  --set auth.password=your-secure-password \
  --set primary.persistence.size=50Gi

# Install Redis
helm install mycrm-redis bitnami/redis \
  --namespace mycrm \
  --set architecture=standalone \
  --set auth.enabled=false

# Deploy application
kubectl apply -f k8s/base/ --namespace mycrm

# Or with Kustomize overlays
kubectl apply -k k8s/overlays/production/
```

### Kubernetes Manifests

#### Backend Deployment

```yaml
# k8s/base/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mycrm-backend
  labels:
    app: mycrm
    component: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mycrm
      component: backend
  template:
    metadata:
      labels:
        app: mycrm
        component: backend
    spec:
      containers:
        - name: backend
          image: your-registry/mycrm-backend:latest
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: mycrm-secrets
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health/
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready/
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
```

#### Horizontal Pod Autoscaler

```yaml
# k8s/base/backend-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mycrm-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mycrm-backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

---

## 🔒 SSL/TLS Configuration

### Using Let's Encrypt with Certbot

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Obtain certificate
certbot certonly --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal (add to crontab)
0 0 * * * /usr/bin/certbot renew --quiet
```

### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Content-Security-Policy "default-src 'self'";
    
    location / {
        proxy_pass http://frontend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## 📊 Monitoring & Observability

### Prometheus & Grafana Stack

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:v2.45.0
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:10.0.0
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    environment:
      GF_SECURITY_ADMIN_PASSWORD: secure-grafana-password
    ports:
      - "3001:3000"

  alertmanager:
    image: prom/alertmanager:v0.25.0
    volumes:
      - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml
    ports:
      - "9093:9093"

volumes:
  prometheus_data:
  grafana_data:
```

### Django Prometheus Metrics

```python
# backend/backend/settings_production.py
INSTALLED_APPS += ['django_prometheus']

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... other middleware ...
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# Expose metrics at /metrics
urlpatterns += [
    path('', include('django_prometheus.urls')),
]
```

---

## 🔄 Database Migrations & Backup

### Running Migrations

```bash
# Docker
docker-compose exec backend python manage.py migrate

# Kubernetes
kubectl exec -it deployment/mycrm-backend -n mycrm -- python manage.py migrate
```

### Database Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/mycrm_${TIMESTAMP}.sql.gz"

# Create backup
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE

# Upload to S3
aws s3 cp $BACKUP_FILE s3://mycrm-backups/database/

# Keep only last 7 days of local backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

### Automated Backups with CronJob

```yaml
# k8s/base/backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: mycrm-db-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: postgres:15-alpine
              command:
                - /bin/sh
                - -c
                - |
                  pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | gzip | \
                  aws s3 cp - s3://mycrm-backups/db/backup-$(date +%Y%m%d).sql.gz
              envFrom:
                - secretRef:
                    name: mycrm-secrets
          restartPolicy: OnFailure
```

---

## 📈 Scaling Strategies

### Horizontal Scaling

1. **Backend API**: Scale based on CPU/Memory usage
2. **Celery Workers**: Scale based on queue length
3. **Frontend**: Scale based on request rate

### Vertical Scaling Guidelines

| Component | Minimum | Recommended | High Load |
|-----------|---------|-------------|-----------|
| Backend | 512MB / 0.5 CPU | 1GB / 1 CPU | 2GB / 2 CPU |
| Celery Worker | 256MB / 0.25 CPU | 512MB / 0.5 CPU | 1GB / 1 CPU |
| Frontend | 256MB / 0.25 CPU | 512MB / 0.5 CPU | 1GB / 1 CPU |
| PostgreSQL | 1GB / 1 CPU | 4GB / 2 CPU | 16GB / 4 CPU |
| Redis | 256MB | 512MB | 1GB |

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Errors

```bash
# Check database is accessible
docker-compose exec backend python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection(); print('Connected!')"
```

#### 2. Static Files Not Loading

```bash
# Regenerate static files
docker-compose exec backend python manage.py collectstatic --no-input --clear
```

#### 3. Celery Tasks Not Processing

```bash
# Check Celery worker status
docker-compose logs celery

# Check Redis connection
docker-compose exec redis redis-cli ping
```

#### 4. Memory Issues

```bash
# Check container memory usage
docker stats

# Increase limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

---

## 📞 Support

For deployment assistance:

- 📧 Email: support@mycrm.io
- 📖 Docs: https://docs.mycrm.io
- 💬 Discord: https://discord.gg/mycrm

---

*Last Updated: December 2024*
