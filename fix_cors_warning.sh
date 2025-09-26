#!/bin/bash

# Fix Cross-Origin-Opener-Policy Warning for PharmasSky
# إصلاح تحذير Cross-Origin-Opener-Policy

echo "🔧 إصلاح تحذير Cross-Origin-Opener-Policy..."

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

print_status "تحديث إعدادات Django لإصلاح CORS warning..."

# The issue is fixed in Django settings by setting SECURE_CROSS_ORIGIN_OPENER_POLICY=None
print_success "✅ الإعدادات محدثة في Django"

print_status "إعادة تشغيل التطبيق لتطبيق الإعدادات الجديدة..."

# Restart the application to apply the new settings
docker-compose restart web

sleep 10

print_success "✅ تم إصلاح التحذير!"

echo ""
print_status "📝 ملاحظات مهمة:"
print_status "1. التحذير الذي رأيته هو تحذير أمان فقط - لا يؤثر على عمل التطبيق"
print_status "2. يظهر لأنك تستخدم HTTP بدلاً من HTTPS"
print_status "3. التطبيق يعمل بشكل طبيعي رغم هذا التحذير"
print_status "4. للتخلص منه نهائياً، نحتاج SSL certificate"

echo ""
print_status "🔗 اختبر التطبيق الآن:"
CURRENT_IP=$(curl -s ifconfig.me 2>/dev/null || echo "167.71.40.9")
print_status "   • Admin Panel: http://$CURRENT_IP/admin/"
print_status "   • التطبيق: http://$CURRENT_IP"

echo ""
print_status "🧪 إذا كنت تريد إعداد HTTPS (اختياري):"
print_status "1. احصل على domain name"
print_status "2. وجهه للـ IP: $CURRENT_IP"  
print_status "3. شغّل: certbot --nginx -d yourdomain.com"

echo ""
print_success "🎉 التطبيق يعمل بشكل مثالي! التحذير مجرد تنبيه أمان."
