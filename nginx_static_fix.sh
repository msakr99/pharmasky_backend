#!/bin/bash

# Simple Nginx Static Files Fix for PharmasSky
# حل بسيط عبر nginx لخدمة Static Files

echo "📁 إصلاح Static Files عبر nginx..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

cd /opt/pharmasky || {
    print_error "مجلد المشروع غير موجود!"
    exit 1
}

# Step 1: Force collect static files locally
print_status "جمع Static Files محلياً..."

docker-compose exec -T web python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Force Django to use local static files
import django
django.setup()
from django.conf import settings

# Override settings temporarily
settings.STATIC_URL = '/static/'
settings.USE_S3 = False

print('Forced local static files')
"

# Collect static files
docker-compose exec -T web python manage.py collectstatic --noinput --clear

# Step 2: Update nginx.conf to serve static files directly
print_status "تحديث nginx configuration..."

# Update the existing nginx.conf file
cat > nginx.conf << 'EOF'
upstream django {
    server web:8000;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=admin:10m rate=5r/s;

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # Replace with your actual domain
    client_max_body_size 100M;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy strict-origin-when-cross-origin;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Static files - serve directly from nginx
    location /static/ {
        alias /app/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # Enable directory listing for debugging (remove in production)
        autoindex on;
        
        # Try files with fallback to Django
        try_files $uri $uri/ @django_static;
    }

    # Fallback to Django for static files
    location @django_static {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Media files
    location /media/ {
        alias /app/media/;
        expires 1y;
        add_header Cache-Control "public";
        autoindex on;
        try_files $uri $uri/ @django_media;
    }

    # Fallback to Django for media files
    location @django_media {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin panel with rate limiting
    location /admin/ {
        limit_req zone=admin burst=10 nodelay;
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API endpoints with rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Django application
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

print_success "✅ تم تحديث nginx.conf"

# Step 3: Restart nginx to apply changes
print_status "إعادة تشغيل nginx..."
docker-compose restart nginx

sleep 5

# Step 4: Test static files
print_status "اختبار Static Files..."

CURRENT_IP=$(curl -s ifconfig.me 2>/dev/null || echo "167.71.40.9")

# Test admin CSS
if curl -f -s "http://localhost/static/admin/css/base.css" >/dev/null; then
    print_success "✅ Admin CSS يعمل!"
    
    # Test other static files
    if curl -f -s "http://localhost/static/" >/dev/null; then
        print_success "✅ Static files directory accessible"
    fi
    
    print_success "🎉 Static Files تعمل بنجاح!"
    echo ""
    print_status "🔗 اختبر الروابط التالية:"
    print_status "   • Admin Panel: http://$CURRENT_IP/admin/"
    print_status "   • Static Files List: http://$CURRENT_IP/static/"
    print_status "   • Admin CSS: http://$CURRENT_IP/static/admin/css/base.css"
    
else
    print_warning "⚠️ Static Files لا تعمل بعد، جاري التشخيص..."
    
    # Debug information
    print_status "🔍 معلومات التشخيص:"
    
    # Check if static files exist in container
    docker-compose exec -T web sh -c '
    echo "Static files in container:"
    ls -la /app/staticfiles/ 2>/dev/null | head -5 || echo "Directory not found"
    echo ""
    echo "Admin CSS file:"
    ls -la /app/staticfiles/admin/css/base.css 2>/dev/null || echo "File not found"
    '
    
    # Check nginx access to static files
    docker-compose exec -T nginx sh -c '
    echo "Nginx can access:"
    ls -la /app/staticfiles/ 2>/dev/null | head -5 || echo "Cannot access staticfiles from nginx"
    '
    
    print_status "💡 حلول محتملة:"
    print_status "1. تأكد من وجود مجلد staticfiles في container"
    print_status "2. تحقق من صلاحيات الملفات"
    print_status "3. أعد تشغيل التطبيق كاملاً: docker-compose down && docker-compose up -d"
fi

echo ""
print_status "📊 حالة الخدمات:"
docker-compose ps

echo ""
print_success "🎯 تم الانتهاء من إصلاح nginx static files!"
