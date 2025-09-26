#!/bin/bash

# Final Static Files Fix for PharmasSky
# الحل النهائي لمشكلة Static Files

echo "🔧 الحل النهائي لمشكلة Static Files..."

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

print_status "فحص الوضع الحالي للـ Static Files..."

# Get current IP
CURRENT_IP=$(curl -s ifconfig.me 2>/dev/null || echo "167.71.40.9")

# Method 1: Check current Django static files setup
print_status "فحص إعدادات Django الحالية..."

docker-compose exec -T web python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django
django.setup()
from django.conf import settings

print(f'DEBUG: {settings.DEBUG}')
print(f'STATIC_URL: {settings.STATIC_URL}')
print(f'STATIC_ROOT: {settings.STATIC_ROOT}')

# Check storages configuration
if hasattr(settings, 'STORAGES'):
    print('STORAGES configuration found')
    print(f'Static storage: {settings.STORAGES.get(\"staticfiles\", {})}')
else:
    print('No STORAGES configuration')

# Check AWS settings
print(f'AWS_ACCESS_KEY_ID: {getattr(settings, \"AWS_ACCESS_KEY_ID\", \"Not set\")[:10]}...')
print(f'AWS_STORAGE_BUCKET_NAME: {getattr(settings, \"AWS_STORAGE_BUCKET_NAME\", \"Not set\")}')
print(f'AWS_S3_ENDPOINT_URL: {getattr(settings, \"AWS_S3_ENDPOINT_URL\", \"Not set\")}')
"

echo ""
print_status "الحل 1: إجبار استخدام Local Static Files..."

# Force local static files by temporarily changing settings
cat > temp_local_static.py << 'EOF'
import os
import sys
import django
from django.conf import settings

# Add project directory to Python path
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Override static files settings to use local storage
from django.conf import settings
settings.STATIC_URL = '/static/'
settings.STORAGES = {
    'default': settings.STORAGES['default'],
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

print('Switched to local static files storage')
EOF

# Copy to container and apply
docker-compose exec -T web python -c "
# Force local static files
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django
django.setup()

# Update settings.py to force local static files
with open('/app/project/settings.py', 'r') as f:
    content = f.read()

# Add local static override
local_static_override = '''
# FORCE LOCAL STATIC FILES FOR DEBUGGING
STATIC_URL = \"/static/\"
STORAGES = {
    \"default\": {
        \"BACKEND\": \"django.core.files.storage.FileSystemStorage\",
    },
    \"staticfiles\": {
        \"BACKEND\": \"django.contrib.staticfiles.storage.StaticFilesStorage\",
    },
}
'''

if 'FORCE LOCAL STATIC FILES' not in content:
    with open('/app/project/settings.py', 'a') as f:
        f.write(local_static_override)
    print('✅ Added local static files override')
else:
    print('✅ Local static files already configured')
"

print_status "إعادة تشغيل التطبيق..."
docker-compose restart web

sleep 15

print_status "جمع Static Files محلياً..."
if docker-compose exec -T web python manage.py collectstatic --noinput --clear; then
    print_success "✅ تم جمع Static Files محلياً"
else
    print_error "❌ فشل جمع Static Files"
fi

# Test local static files
print_status "اختبار Static Files المحلية..."

if curl -f -s "http://localhost/static/admin/css/base.css" >/dev/null 2>&1; then
    print_success "✅ Static Files تعمل محلياً!"
    echo ""
    print_status "🔗 اختبر هذه الروابط:"
    print_status "   • Admin Panel: http://$CURRENT_IP/admin/"
    print_status "   • Admin CSS: http://$CURRENT_IP/static/admin/css/base.css"
    echo ""
    print_success "🎉 تم حل مشكلة Static Files! استخدم التطبيق الآن."
    
else
    print_warning "❌ Static Files المحلية لا تعمل، جاري المحاولة بطريقة أخرى..."
    
    # Method 2: Serve static through nginx directly
    print_status "الحل 2: تكوين nginx لخدمة Static Files مباشرة..."
    
    # Update nginx configuration to serve static files directly
    docker-compose exec -T nginx sh -c '
    # Check if nginx can access static files
    ls -la /app/staticfiles/ 2>/dev/null || echo "Static files directory not found"
    
    # Create basic nginx config for static files
    cat > /etc/nginx/conf.d/static.conf << "EOF"
location /static/ {
    alias /app/staticfiles/;
    expires 1y;
    add_header Cache-Control "public, immutable";
    
    # Try files with fallback
    try_files $uri $uri/ =404;
}

location /media/ {
    alias /app/media/;
    expires 1y;
    add_header Cache-Control "public";
}
EOF
    
    # Reload nginx
    nginx -s reload
    echo "✅ Nginx configuration updated"
    '
    
    sleep 5
    
    # Test again
    if curl -f -s "http://localhost/static/admin/css/base.css" >/dev/null 2>&1; then
        print_success "✅ Static Files تعمل عبر nginx!"
    else
        # Method 3: Symbolic link approach
        print_status "الحل 3: إنشاء symbolic links..."
        
        docker-compose exec -T web sh -c '
        # Create symbolic link in nginx accessible location
        ln -sf /app/staticfiles /app/static 2>/dev/null || echo "Link exists or failed"
        
        # Ensure permissions
        chmod -R 755 /app/staticfiles 2>/dev/null || echo "Permission setting failed"
        
        # List static files
        echo "Static files in /app/staticfiles:"
        ls -la /app/staticfiles/admin/css/ 2>/dev/null | head -5
        '
        
        # Test one more time
        sleep 3
        if curl -f -s "http://localhost/static/admin/css/base.css" >/dev/null 2>&1; then
            print_success "✅ Static Files تعمل بعد symbolic links!"
        else
            print_error "❌ جميع الطرق فشلت"
            
            # Final fallback: Show debugging info
            print_status "🔍 معلومات التشخيص:"
            
            docker-compose exec -T web sh -c '
            echo "=== Django Settings ==="
            python manage.py diffsettings | grep -i static
            
            echo -e "\n=== Static Files Directory ==="
            ls -la /app/staticfiles/ 2>/dev/null | head -10
            
            echo -e "\n=== Admin CSS File ==="
            ls -la /app/staticfiles/admin/css/base.css 2>/dev/null || echo "File not found"
            
            echo -e "\n=== Nginx Access ==="
            ls -la /app/static* 2>/dev/null || echo "No static directories accessible"
            '
        fi
    fi
fi

echo ""
print_status "📊 ملخص النتائج:"
docker-compose ps | grep -E "(web|nginx)"

echo ""
print_status "🧪 اختبارات أخيرة:"
print_status "   • Admin CSS: curl -I http://$CURRENT_IP/static/admin/css/base.css"
print_status "   • Admin Panel: http://$CURRENT_IP/admin/"

# Show final instructions
echo ""
if curl -f -s "http://localhost/static/admin/css/base.css" >/dev/null 2>&1; then
    print_success "🎉 Static Files تعمل! التطبيق جاهز للاستخدام."
else
    print_warning "⚠️ Static Files قد تحتاج إعداد إضافي. راجع معلومات التشخيص أعلاه."
    echo ""
    print_status "💡 نصائح لحل المشكلة:"
    print_status "1. تأكد أن مجلد /app/staticfiles موجود في container"
    print_status "2. تأكد أن nginx يمكنه الوصول لهذا المجلد"
    print_status "3. تحقق من صلاحيات الملفات"
    print_status "4. تأكد أن collectstatic تم بنجاح"
fi
