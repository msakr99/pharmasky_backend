#!/bin/bash

# Fix Static Files Issues for PharmasSky
# This script fixes static files serving from DigitalOcean Spaces

echo "🔧 إصلاح مشاكل الملفات الثابتة (Static Files)..."

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

# Navigate to project directory
cd /opt/pharmasky || {
    print_error "مجلد المشروع غير موجود!"
    exit 1
}

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    print_error "ملف .env.production غير موجود!"
    exit 1
fi

print_status "فحص إعدادات DigitalOcean Spaces..."

# Check if AWS keys are configured
if grep -q "your-digitalocean-spaces-secret-key-here" .env.production; then
    print_warning "⚠️ مفتاح DigitalOcean Spaces غير مُحدث!"
    print_status "يجب تحديث AWS_SECRET_ACCESS_KEY في ملف .env.production"
    echo ""
    print_status "الخطوات المطلوبة:"
    print_status "1. اذهب إلى DigitalOcean Dashboard"
    print_status "2. اختر Spaces → pharmasky-media → Settings → API Keys"
    print_status "3. انسخ Secret Access Key"
    print_status "4. حدّث AWS_SECRET_ACCESS_KEY في .env.production"
    echo ""
fi

# Backup current environment file
print_status "إنشاء نسخة احتياطية من ملف البيئة..."
cp .env.production .env.production.backup

# Update environment file with better static settings
print_status "تحديث إعدادات Static Files..."

# Get current IP
CURRENT_IP=$(curl -s ifconfig.me 2>/dev/null || echo "167.71.40.9")

cat > .env.production << EOF
# Django Settings
SECRET_KEY=pharmasky-change-this-to-a-very-long-random-secret-key-in-production-12345
DEBUG=False
ALLOWED_HOSTS=$CURRENT_IP,167.71.40.9,129.212.140.152,164.90.217.81,localhost,127.0.0.1

# Database Configuration (Using your existing DO database)
DATABASE_URL=postgresql://doadmin:AVNS_g62jyoo4mcu0BkfRsdM@pharmasky-db-do-user-17921548-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require

# Firebase Configuration
FIREBASE_CREDENTIALS=pharmasky-2a5a3-firebase-adminsdk-fbsvc-4aa69c05c7.json

# DigitalOcean Spaces Configuration - UPDATE WITH YOUR ACTUAL KEYS!
AWS_ACCESS_KEY_ID=DO00JME92LMKTFP2BBA3
AWS_SECRET_ACCESS_KEY=your-digitalocean-spaces-secret-key-here
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

# Check if AWS_SECRET_ACCESS_KEY is still placeholder
if grep -q "your-digitalocean-spaces-secret-key-here" .env.production; then
    print_warning "⚠️ لا يزال يجب تحديث مفتاح DigitalOcean Spaces!"
    
    # Prompt for the key
    echo ""
    print_status "هل تريد إدخال مفتاح DigitalOcean Spaces الآن؟ (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -n "أدخل AWS_SECRET_ACCESS_KEY: "
        read -r secret_key
        if [ ! -z "$secret_key" ]; then
            sed -i "s/your-digitalocean-spaces-secret-key-here/$secret_key/g" .env.production
            print_success "تم تحديث المفتاح بنجاح"
        fi
    fi
fi

# Restart containers
print_status "إعادة تشغيل الحاويات..."
docker-compose down
docker-compose up -d

# Wait for services to be ready
print_status "انتظار تشغيل الخدمات..."
sleep 30

# Collect static files
print_status "جمع الملفات الثابتة..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Check if static files collection was successful
if [ $? -eq 0 ]; then
    print_success "✅ تم جمع الملفات الثابتة بنجاح!"
else
    print_error "❌ فشل في جمع الملفات الثابتة"
    print_status "فحص السجلات..."
    docker-compose logs web | tail -10
fi

# Test static files
print_status "اختبار الملفات الثابتة..."
if curl -f -s "http://localhost/static/admin/css/base.css" >/dev/null; then
    print_success "✅ الملفات الثابتة تعمل بشكل صحيح!"
elif curl -f -s "https://pharmasky-media.fra1.digitaloceanspaces.com/static/admin/css/base.css" >/dev/null; then
    print_success "✅ الملفات الثابتة متاحة على DigitalOcean Spaces!"
else
    print_warning "⚠️ لا يمكن الوصول للملفات الثابتة"
    print_status "تحقق من إعدادات DigitalOcean Spaces"
fi

# Show final status
echo ""
print_status "📊 ملخص الحالة:"
docker-compose ps

echo ""
print_status "🔗 روابط اختبار الملفات الثابتة:"
print_status "   • Admin CSS (local): http://$CURRENT_IP/static/admin/css/base.css"
print_status "   • Admin CSS (Spaces): https://pharmasky-media.fra1.digitaloceanspaces.com/static/admin/css/base.css"

echo ""
if grep -q "your-digitalocean-spaces-secret-key-here" .env.production; then
    print_warning "⚠️ تحذير: لا يزال يجب تحديث AWS_SECRET_ACCESS_KEY في .env.production"
    print_status "اذهب إلى: https://cloud.digitalocean.com/spaces/pharmasky-media?i=8b5a82"
    print_status "Settings → API → Generate New Key"
else
    print_success "🎉 تم الإعداد بنجاح!"
fi

echo ""
print_status "📝 إذا كانت الملفات الثابتة لا تزال لا تعمل:"
print_status "1. تأكد من تحديث AWS_SECRET_ACCESS_KEY"
print_status "2. تحقق من صلاحيات DigitalOcean Spaces"
print_status "3. تأكد من أن bucket 'pharmasky-media' يحتوي على مجلد 'static'"
