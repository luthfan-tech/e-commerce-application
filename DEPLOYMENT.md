# 🚀 ShopHub Deployment Guide

Complete guide for deploying ShopHub to various environments.

## Table of Contents
1. [Development](#development)
2. [Staging](#staging)
3. [Production](#production)
4. [Docker](#docker)
5. [Cloud Platforms](#cloud-platforms)

---

## Development

### Local Setup
```bash
# Clone the repository
git clone <repo-url>
cd shopHub

# Run setup script
./setup.sh  # macOS/Linux
setup.bat   # Windows

# Start the application
python main.py
```

**Access:**
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Staging

### Prerequisites
- Python 3.8+
- PostgreSQL 12+ (recommended over SQLite)
- Nginx (reverse proxy)

### Setup Steps

1. **Install dependencies**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env

# Edit .env with staging values:
# - DATABASE_URL=postgresql+asyncpg://user:pass@localhost/shopdb_staging
# - DEBUG=False
# - CORS_ORIGINS=["https://staging.shopHub.com"]
```

3. **Setup PostgreSQL**
```bash
# Create database
createdb shopdb_staging

# SQLAlchemy will create tables automatically on first run
```

4. **Run with Uvicorn**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

5. **Configure Nginx**
```nginx
server {
    listen 80;
    server_name staging.shophub.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/static;
    }
}
```

---

## Production

### Architecture
```
Client
  ↓
CDN/CloudFlare
  ↓
Load Balancer
  ↓
[Gunicorn + Uvicorn] × N workers
  ↓
PostgreSQL (Primary + Replica)
```

### Prerequisites
- Python 3.8+
- PostgreSQL 12+ (dedicated server or managed service)
- Redis (for caching/sessions)
- Gunicorn + Uvicorn
- Nginx or Apache (reverse proxy)
- SSL Certificate (Let's Encrypt)

### Deployment Steps

1. **Install Production Dependencies**
```bash
pip install -r requirements.txt
pip install gunicorn redis
```

2. **Configure Environment**
```bash
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://prod_user:secure_password@db.prod.internal/shopdb
SECRET_KEY=your-very-secure-random-key-here
DEBUG=False
LOG_LEVEL=INFO
CORS_ORIGINS=["https://shophub.com", "https://www.shophub.com"]
ENABLE_SMS_RECEIPTS=true
SMS_PROVIDER=twilio
SMS_API_KEY=your-production-api-key
EOF
```

3. **Setup PostgreSQL**
```bash
# On your database server
sudo -u postgres psql
CREATE DATABASE shopdb;
CREATE USER shopdb_user WITH PASSWORD 'secure_password';
ALTER ROLE shopdb_user SET client_encoding TO 'utf8';
ALTER ROLE shopdb_user SET default_transaction_isolation TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE shopdb TO shopdb_user;
\q
```

4. **Run Database Migrations**
```bash
# SQLAlchemy will auto-create tables
python -c "from database import db_manager; import asyncio; asyncio.run(db_manager.initialize())"
```

5. **Setup Gunicorn Service**

Create `/etc/systemd/system/shophub.service`:
```ini
[Unit]
Description=ShopHub E-Commerce Application
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/shophub
Environment="PATH=/var/www/shophub/venv/bin"
EnvironmentFile=/var/www/shophub/.env
ExecStart=/var/www/shophub/venv/bin/gunicorn main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/shophub/access.log \
    --error-logfile /var/log/shophub/error.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable shophub
sudo systemctl start shophub
sudo systemctl status shophub
```

6. **Setup Nginx with SSL**

Create `/etc/nginx/sites-available/shophub`:
```nginx
upstream shophub {
    server 127.0.0.1:8000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name shophub.com www.shophub.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name shophub.com www.shophub.com;
    
    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/shophub.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/shophub.com/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Logging
    access_log /var/log/nginx/shophub_access.log;
    error_log /var/log/nginx/shophub_error.log;
    
    # Proxy settings
    location / {
        proxy_pass http://shophub;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "upgrade";
        proxy_set_header Upgrade $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files (with caching)
    location /static {
        alias /var/www/shophub/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # API documentation
    location /docs {
        proxy_pass http://shophub/docs;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/shophub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

7. **Setup SSL with Let's Encrypt**
```bash
sudo certbot certonly --nginx -d shophub.com -d www.shophub.com
sudo certbot renew --dry-run  # Test auto-renewal
```

### Monitoring & Logging

```bash
# View application logs
sudo journalctl -u shophub -f

# View Nginx logs
sudo tail -f /var/log/nginx/shophub_access.log
sudo tail -f /var/log/nginx/shophub_error.log

# Application performance monitoring
pip install prometheus-client
# Add metrics to main.py
```

### Backup & Recovery

```bash
# Database backup
pg_dump shopdb > backup-$(date +%Y%m%d).sql

# Automated backups with cron
0 2 * * * pg_dump shopdb | gzip > /backups/shopdb-$(date +\%Y\%m\%d).sql.gz
```

---

## Docker

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 shophub
USER shophub

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://shopdb:password@postgres:5432/shopdb
      SECRET_KEY: your-secret-key
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: shopdb
      POSTGRES_USER: shopdb
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U shopdb"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  postgres_data:
```

### Run with Docker Compose
```bash
docker-compose up -d
docker-compose logs -f web
docker-compose down
```

---

## Cloud Platforms

### AWS Deployment (EC2 + RDS)

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance: t3.medium or larger
   - Security Group: Allow ports 80, 443, 22

2. **Setup RDS PostgreSQL**
   - Engine: PostgreSQL 15
   - Instance: db.t3.micro (dev) or db.t3.small (prod)
   - Multi-AZ: Yes (production)

3. **Deploy Application**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@ec2-address

# Follow production setup above
# Use RDS endpoint in DATABASE_URL
```

### Heroku Deployment

1. **Install Heroku CLI**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Create Procfile**
```
web: gunicorn main:app -k uvicorn.workers.UvicornWorker
```

3. **Deploy**
```bash
heroku login
heroku create your-app-name
heroku addons:create heroku-postgresql:standard-0
git push heroku main
heroku open
```

### Google Cloud Run

1. **Build and Push Image**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/shophub
```

2. **Deploy**
```bash
gcloud run deploy shophub \
    --image gcr.io/YOUR_PROJECT_ID/shophub \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

---

## Performance Optimization

### Database Optimization
```python
# Enable query logging
echo "log_statement = 'all'" | sudo tee -a /etc/postgresql/15/main/postgresql.conf
sudo systemctl restart postgresql

# Analyze and optimize
ANALYZE;
VACUUM;
```

### Caching Strategy
```python
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

# Cache product listings for 5 minutes
@app.get("/api/products", dependencies=[Depends(fastapi_cache)])
async def list_products():
    pass
```

### Load Testing
```bash
pip install locust

# Create locustfile.py and run
locust -f locustfile.py -u 100 -r 10 -t 5m --headless
```

---

## Troubleshooting

### Database Connection Issues
```bash
# Test connection
psql postgresql://user:password@host:5432/dbname

# Check application logs
sudo journalctl -u shophub -n 100
```

### High Memory Usage
```bash
# Reduce Gunicorn workers
gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker

# Monitor with
watch -n 1 'ps aux | grep gunicorn'
```

### SSL Certificate Renewal
```bash
# Automatic renewal (should be setup)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Manual renewal
sudo certbot renew --force-renewal
```

---

**Last Updated:** 2024
**Version:** 1.0.0
