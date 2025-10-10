#!/bin/bash
# سكريبت نشر التحديثات على السيرفر
# Deploy Updates to Server Script

SERVER="129.212.140.152"
PROJECT_PATH="/home/pharmasky/pharmasky_backend"  # ⚠️ عدل المسار حسب السيرفر

echo "=================================="
echo "  نشر التحديثات على السيرفر"
echo "  Deploy Updates to Server"
echo "=================================="
echo ""

echo "📦 التحديثات المرفوعة:"
echo "  ✅ نظام المصاريف الكامل"
echo "  ✅ معلومات المورد في المخزون"
echo "  ✅ مرتجعات الشراء برقم فاتورة المورد"
echo ""

echo "🔗 الاتصال بالسيرفر..."
echo "ssh user@$SERVER"
echo ""

# أوامر السيرفر
cat << 'EOF'

# على السيرفر، شغل الأوامر التالية:

cd /home/pharmasky/pharmasky_backend  # عدل المسار

# 1. سحب التحديثات
echo "1️⃣ سحب التحديثات..."
git pull origin main

# 2. تفعيل البيئة الافتراضية (إذا موجودة)
# source venv/bin/activate  # فك التعليق لو بتستخدم venv

# 3. تشغيل Migration (مهم!)
echo "2️⃣ تشغيل Migration..."
python manage.py migrate

# 4. جمع الملفات الثابتة (اختياري)
# python manage.py collectstatic --noinput

# 5. إعادة تشغيل Django
echo "3️⃣ إعادة تشغيل Django..."
sudo systemctl restart gunicorn

# أو حسب إعدادك:
# sudo systemctl restart uwsgi
# أو: sudo supervisorctl restart pharmasky
# أو: docker-compose restart

echo ""
echo "✅ تم النشر بنجاح!"
echo ""

# 6. التحقق من الحالة
echo "4️⃣ التحقق..."
sudo systemctl status gunicorn

EOF

echo ""
echo "=================================="
echo "📋 ملاحظات:"
echo "  - Migration مطلوب (نموذج Expense جديد)"
echo "  - عدل المسار والأوامر حسب إعداد السيرفر"
echo "=================================="

