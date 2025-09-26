#!/bin/bash

# Quick Static Files Fix for PharmasSky
# حل سريع لمشكلة Static Files

echo "⚡ حل سريع لمشكلة Static Files..."

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

print_status "الحل السريع لـ Static Files..."

# Just force collect static files - ignore connection errors
print_status "إجبار جمع Static Files..."
if docker-compose exec -T web python manage.py collectstatic --noinput --clear; then
    print_success "✅ تم جمع Static Files"
else
    print_error "❌ فشل جمع Static Files"
    exit 1
fi

# Test if Django can serve static files through the app
print_status "اختبار Static Files عبر Django..."

# Get current IP
CURRENT_IP=$(curl -s ifconfig.me 2>/dev/null || echo "167.71.40.9")

# Test admin CSS through Django
if curl -f -s "http://localhost/static/admin/css/base.css" >/dev/null 2>&1; then
    print_success "✅ Admin CSS يعمل عبر Django!"
    echo ""
    print_status "🔗 Static Files تعمل! اختبر هذه الروابط:"
    print_status "   • Admin Panel: http://$CURRENT_IP/admin/"
    print_status "   • Admin CSS: http://$CURRENT_IP/static/admin/css/base.css"
    
    # Check if it's being served from Spaces or locally
    css_response=$(curl -s -I "http://localhost/static/admin/css/base.css" 2>/dev/null)
    if echo "$css_response" | grep -q "digitaloceanspaces"; then
        print_success "✅ يتم تحميل Static Files من DigitalOcean Spaces"
    else
        print_warning "⚠️ يتم تحميل Static Files محلياً (وهذا مقبول للآن)"
    fi
    
elif curl -f -s "https://pharmasky-media.fra1.digitaloceanspaces.com/static/admin/css/base.css" >/dev/null 2>&1; then
    print_success "✅ Static Files متاحة على DigitalOcean Spaces مباشرة!"
    print_status "🔗 اختبر: https://pharmasky-media.fra1.digitaloceanspaces.com/static/admin/css/base.css"
    
else
    print_warning "⚠️ Static Files قد تحتاج وقت للانتشار"
    print_status "جاري المحاولة مرة أخرى في 10 ثوان..."
    sleep 10
    
    if curl -f -s "http://localhost/static/admin/css/base.css" >/dev/null 2>&1; then
        print_success "✅ Static Files تعمل الآن!"
    else
        print_warning "⚠️ Static Files لم تظهر بعد - لكن هذا طبيعي قد يحتاج وقت"
    fi
fi

# Force restart nginx container to refresh static files
print_status "إعادة تشغيل nginx لتحديث Static Files..."
docker-compose restart nginx

sleep 5

# Final test
print_status "الاختبار النهائي..."
if curl -f -s "http://localhost/admin/" >/dev/null 2>&1; then
    print_success "✅ Admin Panel يعمل!"
else
    print_warning "⚠️ Admin Panel قد يحتاج دقيقة إضافية"
fi

echo ""
print_success "🎉 تم الانتهاء من الإصلاح السريع!"
echo ""
print_status "📊 حالة الخدمات:"
docker-compose ps

echo ""
print_status "🔗 اختبر هذه الروابط في المتصفح:"
print_status "   • التطبيق: http://$CURRENT_IP"
print_status "   • Admin Panel: http://$CURRENT_IP/admin/"
print_status "   • Admin CSS: http://$CURRENT_IP/static/admin/css/base.css"

echo ""
print_status "📝 ملاحظات:"
print_status "1. إذا كان Admin Panel يظهر بدون تنسيق، انتظر دقيقة وأعد تحميل الصفحة"
print_status "2. Static Files قد تحتاج وقت للانتشار على CDN"
print_status "3. إذا استمرت المشكلة، شغّل: ./debug_spaces.sh"
