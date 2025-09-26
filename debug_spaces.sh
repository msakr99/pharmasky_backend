#!/bin/bash

# Debug DigitalOcean Spaces Structure for PharmasSky
# فحص بنية DigitalOcean Spaces وإصلاح مشاكل Static Files

echo "🔍 فحص وإصلاح بنية DigitalOcean Spaces..."

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

print_status "فحص بنية DigitalOcean Spaces..."

# Debug Spaces structure using Python
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
    
    print('🔍 فحص بنية Bucket...')
    print(f'Bucket: {settings.AWS_STORAGE_BUCKET_NAME}')
    print(f'Endpoint: {settings.AWS_S3_ENDPOINT_URL}')
    print()
    
    # List all objects in bucket (first 20)
    print('📁 محتويات Bucket الحالية:')
    try:
        response = s3_client.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            MaxKeys=20
        )
        
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f'  - {obj[\"Key\"]} ({obj[\"Size\"]} bytes)')
        else:
            print('  (فارغ - لا توجد ملفات)')
    except Exception as e:
        print(f'  ❌ خطأ في قراءة محتويات Bucket: {e}')
    
    print()
    
    # Try to create static folder if it doesn't exist
    print('🔧 إنشاء مجلد static...')
    try:
        # Upload a test file to create static folder
        s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key='static/.gitkeep',
            Body=b'Static files folder',
            ContentType='text/plain'
        )
        print('✅ تم إنشاء مجلد static/')
    except Exception as e:
        print(f'⚠️ تحذير: لا يمكن إنشاء مجلد static: {e}')
    
    print()
    
    # Test upload a simple file
    print('🧪 اختبار رفع ملف...')
    try:
        test_content = 'body { background: red; } /* Test CSS */'
        s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key='static/test.css',
            Body=test_content.encode(),
            ContentType='text/css',
            CacheControl='max-age=86400'
        )
        print('✅ تم رفع ملف اختبار: static/test.css')
        
        # Test download
        download_response = s3_client.get_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key='static/test.css'
        )
        downloaded_content = download_response['Body'].read().decode()
        if test_content == downloaded_content:
            print('✅ تم تحميل الملف بنجاح')
        else:
            print('⚠️ محتوى الملف مختلف')
            
    except Exception as e:
        print(f'❌ فشل اختبار الرفع/التحميل: {e}')
    
    print()
    print('🔗 روابط الاختبار:')
    print(f'Test CSS: {settings.AWS_S3_ENDPOINT_URL}/static/test.css')
    
except Exception as e:
    print(f'❌ خطأ عام في الاتصال: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
print_status "إعادة جمع Static Files مع verbose output..."

# Force collect static with verbose output
if docker-compose exec -T web python manage.py collectstatic --noinput --clear --verbosity=2; then
    print_success "✅ تم جمع Static Files"
else
    print_error "❌ فشل في جمع Static Files"
fi

echo ""
print_status "فحص الملفات المرفوعة حديثاً..."

# Check uploaded files again
docker-compose exec -T web python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django
django.setup()
from django.conf import settings
import boto3

s3_client = boto3.client(
    's3',
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)

print('📁 Static Files المرفوعة:')
try:
    response = s3_client.list_objects_v2(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Prefix='static/',
        MaxKeys=10
    )
    
    if 'Contents' in response:
        for obj in response['Contents']:
            print(f'  ✅ {obj[\"Key\"]}')
    else:
        print('  ❌ لا توجد static files')
        
    # Try to access admin CSS specifically
    try:
        admin_css = s3_client.head_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key='static/admin/css/base.css'
        )
        print('  ✅ Admin CSS موجود')
    except:
        print('  ❌ Admin CSS غير موجود')
        
except Exception as e:
    print(f'❌ خطأ: {e}')
"

echo ""
print_status "اختبار الروابط في المتصفح..."

# Get current IP
CURRENT_IP=$(curl -s ifconfig.me 2>/dev/null || echo "167.71.40.9")

echo ""
print_status "🔗 روابط للاختبار:"
print_status "   • Test CSS: https://pharmasky-media.fra1.digitaloceanspaces.com/static/test.css"
print_status "   • Admin CSS: https://pharmasky-media.fra1.digitaloceanspaces.com/static/admin/css/base.css"
print_status "   • Local Admin CSS: http://$CURRENT_IP/static/admin/css/base.css"
print_status "   • Admin Panel: http://$CURRENT_IP/admin/"

echo ""
print_success "🎉 تم فحص وإصلاح بنية DigitalOcean Spaces!"
print_status "📝 اختبر الروابط أعلاه للتأكد من عمل Static Files"
