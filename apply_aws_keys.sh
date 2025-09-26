#!/bin/bash

# Apply AWS Keys for DigitalOcean Spaces - PharmasSky
# تطبيق مفاتيح AWS للـ DigitalOcean Spaces

echo "🔑 تطبيق مفاتيح DigitalOcean Spaces الجديدة..."

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

# Backup current environment file
print_status "إنشاء نسخة احتياطية..."
cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)

# Get current IP
CURRENT_IP=$(curl -s ifconfig.me 2>/dev/null || echo "167.71.40.9")
print_status "Current IP: $CURRENT_IP"

# Update .env.production with new AWS keys
print_status "تحديث مفاتيح AWS..."

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
AWS_ACCESS_KEY_ID=DO009ZYJD3RNN3PFRRQ3
AWS_SECRET_ACCESS_KEY=q8DX9Ts4+apP95ESQYPBVpuOI8vgN4i1DoSXRj6Inng
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

print_success "✅ تم تحديث ملف البيئة بالمفاتيح الجديدة"

# Restart containers
print_status "إعادة تشغيل الحاويات..."
docker-compose down
docker-compose up -d

# Wait for services to be ready
print_status "انتظار تشغيل الخدمات..."
sleep 30

# Test database connection first
print_status "اختبار اتصال قاعدة البيانات..."
if docker-compose exec -T web python manage.py check --database default; then
    print_success "✅ قاعدة البيانات متصلة"
else
    print_warning "⚠️ مشكلة في اتصال قاعدة البيانات"
fi

# Collect static files
print_status "جمع الملفات الثابتة..."
if docker-compose exec -T web python manage.py collectstatic --noinput --verbosity=2; then
    print_success "✅ تم جمع الملفات الثابتة بنجاح!"
else
    print_error "❌ فشل في جمع الملفات الثابتة"
    print_status "عرض السجلات..."
    docker-compose logs web | tail -20
    exit 1
fi

# Test AWS connection
print_status "اختبار اتصال DigitalOcean Spaces..."
docker-compose exec -T web python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django
django.setup()
from django.conf import settings
import boto3

try:
    s3_client = boto3.client(
        's3',
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    # List objects in the bucket
    response = s3_client.list_objects_v2(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Prefix='static/',
        MaxKeys=5
    )
    
    if 'Contents' in response:
        print(f'✅ Successfully connected to DigitalOcean Spaces!')
        print(f'Found {len(response.get(\"Contents\", []))} static files')
        for obj in response.get('Contents', []):
            print(f'  - {obj[\"Key\"]}')
    else:
        print('⚠️ Connected but no static files found in bucket')
        
except Exception as e:
    print(f'❌ Error connecting to DigitalOcean Spaces: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    print_success "✅ اتصال DigitalOcean Spaces يعمل بشكل صحيح!"
else
    print_error "❌ مشكلة في اتصال DigitalOcean Spaces"
    exit 1
fi

# Test static files access
print_status "اختبار الوصول للملفات الثابتة..."

# Test admin CSS
if curl -f -s "http://localhost/static/admin/css/base.css" >/dev/null; then
    print_success "✅ Admin CSS يعمل (local)"
else
    print_warning "⚠️ Admin CSS لا يعمل محلياً"
fi

# Test direct Spaces access
if curl -f -s "https://pharmasky-media.fra1.digitaloceanspaces.com/static/admin/css/base.css" >/dev/null; then
    print_success "✅ Static files متاحة على DigitalOcean Spaces!"
else
    print_warning "⚠️ لا يمكن الوصول للملفات على Spaces مباشرة"
fi

# Show container status
echo ""
print_status "📊 حالة الحاويات:"
docker-compose ps

# Show final results
echo ""
print_success "🎉 تم تطبيق مفاتيح DigitalOcean Spaces بنجاح!"
echo ""
print_status "🔗 روابط الاختبار:"
print_status "   • التطبيق: http://$CURRENT_IP"
print_status "   • الإدارة: http://$CURRENT_IP/admin/"
print_status "   • Admin CSS: http://$CURRENT_IP/static/admin/css/base.css"
print_status "   • Spaces Direct: https://pharmasky-media.fra1.digitaloceanspaces.com/static/admin/css/base.css"

echo ""
print_status "📝 ملاحظات:"
print_status "1. Static files الآن تُحمل من DigitalOcean Spaces"
print_status "2. يمكنك اختبار Admin panel للتأكد من CSS"
print_status "3. عند كل تحديث، شغّل: docker-compose exec web python manage.py collectstatic --noinput"
