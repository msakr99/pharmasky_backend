# 🚀 Quick Deploy Guide for Your DigitalOcean Droplet

**Droplet IP:** 164.90.217.81  
**Password:** sAkr4601#a

## Method 1: Upload from your local machine

### 1. Upload files to droplet
Run this on your Windows machine in the project directory:

```bash
# Make upload script executable
chmod +x upload_to_droplet.sh

# Run upload script (will prompt for password)
./upload_to_droplet.sh
```

### 2. SSH into droplet and deploy
```bash
# Connect to droplet
ssh root@164.90.217.81

# Navigate to project directory
cd /opt/pharmasky

# Run deployment script
./deploy.sh
```

## Method 2: Direct deployment on droplet

If Method 1 doesn't work, SSH into your droplet and run these commands:

### 1. Connect to your droplet
```bash
ssh root@164.90.217.81
# Password: sAkr4601#a
```

### 2. Install git and clone your repository
```bash
# Update system
apt update && apt upgrade -y

# Install git
apt install -y git

# Create project directory
mkdir -p /opt/pharmasky
cd /opt/pharmasky

# If you have your code in a repository, clone it:
# git clone https://github.com/yourusername/pharmasky.git .

# Or create files manually (copy from your local machine)
```

### 3. Create essential deployment files on droplet

Create the deployment script:
```bash
cat > deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Installing Docker and dependencies..."

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install other dependencies
apt install -y nginx certbot python3-certbot-nginx ufw curl wget

# Configure firewall
ufw --force enable
ufw allow ssh
ufw allow 80
ufw allow 443

echo "✅ Docker and dependencies installed!"
echo "📁 Please upload your project files to /opt/pharmasky"
echo "📝 Next steps:"
echo "  1. Upload your project files"
echo "  2. Configure .env.production"
echo "  3. Run: docker-compose up -d"
EOF

chmod +x deploy.sh
```

### 4. Create Docker configuration files

Create Dockerfile:
```bash
cat > Dockerfile << 'EOF'
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
EOF
```

Create docker-compose.yml:
```bash
cat > docker-compose.yml << 'EOF'
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

  celery:
    build: .
    container_name: pharmasky_celery
    command: celery -A project worker --loglevel=info
    volumes:
      - .:/app
      - media_volume:/app/media
    env_file:
      - .env.production
    depends_on:
      - web
      - redis
    restart: unless-stopped

volumes:
  static_volume:
  media_volume:
  redis_data:
EOF
```

### 5. Configure environment
```bash
cat > .env.production << 'EOF'
# Django Settings
SECRET_KEY=pharmasky-super-secret-key-change-this-in-production-2024
DEBUG=False
ALLOWED_HOSTS=164.90.217.81,localhost,127.0.0.1

# Database Configuration (Your existing DO database)
DATABASE_URL=postgresql://doadmin:AVNS_g62jyoo4mcu0BkfRsdM@pharmasky-db-do-user-17921548-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require

# Firebase Configuration
FIREBASE_CREDENTIALS=pharmasky-2a5a3-firebase-adminsdk-fbsvc-4aa69c05c7.json

# DigitalOcean Spaces Configuration (Update with your actual keys)
AWS_ACCESS_KEY_ID=your-spaces-access-key
AWS_SECRET_ACCESS_KEY=your-spaces-secret-key
AWS_STORAGE_BUCKET_NAME=pharmasky-media
AWS_S3_ENDPOINT_URL=https://pharmasky-media.fra1.digitaloceanspaces.com
AWS_S3_REGION_NAME=fra1
AWS_LOCATION=media

# Redis Configuration
CELERY_BROKER=redis://redis:6379/0
CELERY_BACKEND=redis://redis:6379/0

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://164.90.217.81
CSRF_TRUSTED_ORIGINS=http://164.90.217.81

# SSL Configuration (set to False initially, enable after SSL setup)
SECURE_SSL_REDIRECT=False
EOF
```

### 6. Upload your project files

You need to copy your project files to the droplet. You can:

**Option A: Use SCP from your local machine:**
```bash
# From your local project directory
scp -r . root@164.90.217.81:/opt/pharmasky/
```

**Option B: Create a minimal version manually and upload key files**

### 7. Install and run the application
```bash
# Make sure you're in the project directory
cd /opt/pharmasky

# Run the setup script
./deploy.sh

# Start the application
docker-compose up -d

# Wait a moment for containers to start
sleep 30

# Run database migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Check status
docker-compose ps
```

## 🔍 Verify Deployment

1. **Check if containers are running:**
   ```bash
   docker-compose ps
   ```

2. **Check application logs:**
   ```bash
   docker-compose logs web
   ```

3. **Test the application:**
   - Open browser: `http://164.90.217.81:8000`
   - Admin panel: `http://164.90.217.81:8000/admin/`

## 🚨 Troubleshooting

If something goes wrong:

1. **Check logs:**
   ```bash
   docker-compose logs
   ```

2. **Restart services:**
   ```bash
   docker-compose restart
   ```

3. **Rebuild if needed:**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

## 📝 Important Notes

1. **Update your DigitalOcean Spaces credentials** in `.env.production`
2. **Change the SECRET_KEY** to a secure random string
3. **Upload your Firebase credentials file** (`pharmasky-2a5a3-firebase-adminsdk-fbsvc-4aa69c05c7.json`)
4. **Consider setting up a domain name** and SSL certificate for production

Your application should be accessible at: **http://164.90.217.81:8000**
