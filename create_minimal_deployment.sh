#!/bin/bash
# This script creates the minimal files needed on the droplet for deployment

cat << 'EOF'
# Copy and paste this entire block into your droplet terminal at /opt/pharmasky

# Create requirements.txt
cat > requirements.txt << 'REQUIREMENTS_EOF'
Django>=5.2.6
django-environ
django-cors-headers
django-storages
djangorestframework
django-phonenumber-field
phonenumbers
django-filter
django-debug-toolbar
django-rosetta
django-import-export
drf-spectacular
django-celery-beat
django-push-notifications
celery
redis
psycopg2-binary
boto3
firebase-admin
Pillow
python-decouple
num2words
python-magic
pandas
weasyprint
drf-excel
drf-nested-routers
gunicorn
whitenoise
django-health-check
sentry-sdk
fuzzywuzzy
REQUIREMENTS_EOF

# Create Dockerfile
cat > Dockerfile << 'DOCKERFILE_EOF'
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libmagic1 \
    gettext \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY . /app/

RUN mkdir -p /app/staticfiles
RUN mkdir -p /app/media

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "project.wsgi:application"]
DOCKERFILE_EOF

# Create docker-compose.yml
cat > docker-compose.yml << 'COMPOSE_EOF'
version: '3.8'

services:
  web:
    build: .
    container_name: pharmasky_web
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    environment:
      - DEBUG=False
    env_file:
      - .env.production
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: pharmasky_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  static_volume:
  media_volume:
  redis_data:
COMPOSE_EOF

# Create environment file
cat > .env.production << 'ENV_EOF'
SECRET_KEY=pharmasky-super-secret-key-change-this-to-something-very-long-and-random-2024
DEBUG=False
ALLOWED_HOSTS=164.90.217.81,localhost,127.0.0.1

# Database Configuration (Your existing DO database)
DATABASE_URL=postgresql://doadmin:AVNS_g62jyoo4mcu0BkfRsdM@pharmasky-db-do-user-17921548-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require

# Redis Configuration
CELERY_BROKER=redis://redis:6379/0
CELERY_BACKEND=redis://redis:6379/0

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://164.90.217.81:8000
CSRF_TRUSTED_ORIGINS=http://164.90.217.81:8000

# SSL Configuration
SECURE_SSL_REDIRECT=False
ENV_EOF

echo "✅ Basic deployment files created!"
echo "📝 Now you need to copy your Django project files here."
echo "💡 You can do this by copying files one by one or using git clone if your code is in a repository."

EOF
