# 🚀 دليل نشر إصلاحات الصلاحيات على الدروبليت

## 📋 الملفات المحدثة

### ملفات الكود:
- `core/permissions.py` - نظام صلاحيات محدث
- `accounts/permissions.py` - إضافة AdminRoleAuthentication  
- `market/views.py` - تحديث صلاحيات المنتجات
- `API_ENDPOINTS_PERMISSIONS.md` - وثائق محدثة

### ملفات الوثائق:
- `PERMISSION_FIXES.md` - تحليل المشاكل والحلول
- `COMPREHENSIVE_PERMISSION_SOLUTION.md` - الحل الشامل
- `DROPLET_DEPLOYMENT_GUIDE.md` - هذا الملف

## 🔧 خطوات النشر على الدروبليت

### الخطوة 1: رفع الملفات المحدثة
```bash
# الاتصال بالدروبليت
ssh root@129.212.140.152

# الانتقال لمجلد المشروع
cd /path/to/pharmasky-project

# سحب التحديثات من Git
git pull origin main

# أو رفع الملفات يدوياً إذا لم تكن في Git بعد
```

### الخطوة 2: تطبيق التغييرات
```bash
# تفعيل البيئة الافتراضية
source venv/bin/activate

# تطبيق migrations إذا كانت هناك تغييرات في قاعدة البيانات
python manage.py makemigrations
python manage.py migrate

# جمع الملفات الثابتة
python manage.py collectstatic --noinput
```

### الخطوة 3: إعادة تشغيل الخدمات
```bash
# إعادة تشغيل Gunicorn/uWSGI
sudo systemctl restart pharmasky-api
# أو
sudo supervisorctl restart pharmasky-api

# إعادة تشغيل Nginx
sudo systemctl restart nginx

# التحقق من حالة الخدمات
sudo systemctl status pharmasky-api
sudo systemctl status nginx
```

### الخطوة 4: إصلاح قاعدة البيانات (اختياري)
```sql
-- الاتصال بقاعدة البيانات
sudo -u postgres psql pharmasky_db

-- تحديث is_superuser للمدراء
UPDATE accounts_user 
SET is_superuser = TRUE 
WHERE role = 'ADMIN';

-- التحقق من التحديث
SELECT username, role, is_superuser 
FROM accounts_user 
WHERE role = 'ADMIN';

-- الخروج
\q
```

## 🧪 اختبار التحديثات

### اختبار 1: تسجيل الدخول
```bash
curl -X POST "http://129.212.140.152/accounts/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"+201090572414","password":"Sakr4601"}'
```

### اختبار 2: الوصول للمنتجات (يجب أن يعمل الآن)
```bash
curl -X GET "http://129.212.140.152/market/products/" \
  -H "Authorization: Token YOUR_TOKEN"
```

### اختبار 3: endpoints أخرى
```bash
# اختبار الشركات (PHARMACY فقط)
curl -X GET "http://129.212.140.152/market/companies/list" \
  -H "Authorization: Token YOUR_TOKEN"

# اختبار المستخدمين (Staff فقط)  
curl -X GET "http://129.212.140.152/accounts/users/" \
  -H "Authorization: Token YOUR_TOKEN"
```

## 📊 النتائج المتوقعة

### قبل الإصلاح:
- ❌ ADMIN لا يمكنه الوصول للمنتجات
- ❌ رسالة خطأ: "You do not have permission"

### بعد الإصلاح:
- ✅ ADMIN يمكنه الوصول لجميع endpoints
- ✅ نظام صلاحيات موحد وواضح
- ✅ أداء أفضل وكود أنظف

## 🔍 استكشاف الأخطاء

### إذا لم تعمل الإصلاحات:

#### 1. التحقق من اللوجز
```bash
# لوجز التطبيق
sudo journalctl -u pharmasky-api -f

# لوجز Nginx
sudo tail -f /var/log/nginx/error.log
```

#### 2. التحقق من التكوين
```bash
# التحقق من متغيرات البيئة
cat /path/to/.env

# التحقق من إعدادات Django
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DEBUG)
```

#### 3. إعادة تشغيل كاملة
```bash
sudo systemctl restart pharmasky-api nginx postgresql
```

## 📝 ملاحظات مهمة

### 1. النسخ الاحتياطية
- تأكد من عمل نسخة احتياطية من قاعدة البيانات قبل التحديث
- احتفظ بنسخة من الكود القديم

### 2. المراقبة
- راقب اللوجز لمدة ساعة بعد النشر
- تحقق من أداء API endpoints المختلفة

### 3. الرجوع للخلف
- في حالة وجود مشاكل، يمكن الرجوع للكود القديم
- احتفظ بـ commit hash للإصدار السابق

## 🎯 خطة ما بعد النشر

### المرحلة التالية (أسبوع):
- [ ] مراجعة باقي views وتحديثها للنظام الجديد
- [ ] إزالة `accounts/permissions.py` القديم
- [ ] إضافة اختبارات للصلاحيات الجديدة

### المرحلة المتوسطة (شهر):
- [ ] توثيق شامل للنظام الجديد
- [ ] تدريب الفريق على النظام الجديد
- [ ] مراجعة أمنية شاملة

---

**تاريخ الإنشاء**: 2025-09-27  
**المطور**: Mohamed Sakr  
**الحالة**: جاهز للنشر 🚀
