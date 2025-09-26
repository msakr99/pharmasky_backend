#!/bin/bash

# Fix CORS and ALLOWED_HOSTS issues for PharmasSky
# Run this script on the droplet to fix 400 Bad Request errors

echo "🔧 إصلاح مشاكل CORS و ALLOWED_HOSTS..."

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

# Get current IP
CURRENT_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "167.71.40.9")
print_status "Current IP: $CURRENT_IP"

# Navigate to project directory
cd /opt/pharmasky || {
    print_error "مجلد المشروع غير موجود!"
    exit 1
}

# Update environment file
print_status "تحديث ملف .env.production..."

# Create updated environment file
cat > .env.production << EOF
# Django Settings
SECRET_KEY=pharmasky-change-this-to-a-very-long-random-secret-key-in-production-12345
DEBUG=False
ALLOWED_HOSTS=$CURRENT_IP,167.71.40.9,129.212.140.152,164.90.217.81,localhost,127.0.0.1

# Database Configuration (Using your existing DO database)
DATABASE_URL=postgresql://doadmin:AVNS_g62jyoo4mcu0BkfRsdM@pharmasky-db-do-user-17921548-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require

# Firebase Configuration
FIREBASE_CREDENTIALS=pharmasky-2a5a3-firebase-adminsdk-fbsvc-4aa69c05c7.json

# DigitalOcean Spaces Configuration
AWS_ACCESS_KEY_ID=DO00JME92LMKTFP2BBA3
AWS_SECRET_ACCESS_KEY=your-digitalocean-spaces-secret-key
AWS_STORAGE_BUCKET_NAME=pharmasky-media
AWS_S3_ENDPOINT_URL=https://pharmasky-media.fra1.digitaloceanspaces.com
AWS_S3_REGION_NAME=fra1
AWS_LOCATION=media

# Redis Configuration (Using Docker Redis)
CELERY_BROKER=redis://redis:6379/0
CELERY_BACKEND=redis://redis:6379/0

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://$CURRENT_IP,http://167.71.40.9,http://129.212.140.152,http://164.90.217.81,http://localhost
CSRF_TRUSTED_ORIGINS=http://$CURRENT_IP,http://167.71.40.9,http://129.212.140.152,http://164.90.217.81,http://localhost

# SSL Configuration (set to False initially, enable after SSL setup)
SECURE_SSL_REDIRECT=False
EOF

print_success "تم تحديث ملف البيئة"

# Restart containers
print_status "إعادة تشغيل الحاويات..."
docker-compose down
docker-compose up -d

# Wait for services to be ready
print_status "انتظار تشغيل الخدمات..."
sleep 30

# Check container status
print_status "فحص حالة الخدمات..."
docker-compose ps

# Test health endpoint
print_status "فحص صحة التطبيق..."
sleep 10

if curl -f -s http://localhost/health/ >/dev/null; then
    print_success "✅ التطبيق يعمل بشكل طبيعي!"
else
    print_warning "⚠️ فحص الصحة فشل - قد يحتاج وقت إضافي"
    print_status "جاري فحص السجلات..."
    docker-compose logs web | tail -20
fi

print_status "🔗 عناوين التطبيق المحدثة:"
print_status "   • التطبيق الرئيسي: http://$CURRENT_IP"
print_status "   • لوحة الإدارة: http://$CURRENT_IP/admin/"
print_status "   • فحص الصحة: http://$CURRENT_IP/health/"

echo ""
print_success "🎉 تم إصلاح مشاكل CORS!"
print_warning "📝 لا تنس تحديث GitHub Secrets بالـ IP الجديد: $CURRENT_IP"
