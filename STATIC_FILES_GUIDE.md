# 📁 دليل إصلاح مشكلة Static Files مع DigitalOcean Spaces

## 🚨 المشكلة الحالية
Static files (CSS, JS, Images) لا تظهر في التطبيق لأنها محملة على DigitalOcean Spaces لكن الإعدادات غير صحيحة.

---

## ⚡ الحل السريع (3 دقائق)

### 1. اتصل بالدروبليت:
```bash
ssh root@167.71.40.9
```

### 2. شغّل script الإصلاح:
```bash
curl -o fix_static_files.sh https://raw.githubusercontent.com/msakr99/pharmasky_backend/main/fix_static_files.sh && chmod +x fix_static_files.sh && ./fix_static_files.sh
```

---

## 🔐 إعداد DigitalOcean Spaces Keys

### الحصول على المفاتيح:

1. **اذهب إلى DigitalOcean Dashboard:**
   ```
   https://cloud.digitalocean.com/spaces
   ```

2. **اختر Space: `pharmasky-media`**

3. **انقر على Settings → API**

4. **انقر "Generate New Key"**

5. **انسخ:**
   - **Access Key ID:** `DO00JME92LMKTFP2BBA3` ✅ (موجود)
   - **Secret Access Key:** (انسخه واحتفظ به)

### تحديث المفاتيح:

```bash
# على الدروبليت
cd /opt/pharmasky
nano .env.production

# حدّث هذا السطر:
AWS_SECRET_ACCESS_KEY=YOUR_ACTUAL_SECRET_KEY_HERE
```

---

## 🔧 الإصلاح اليدوي (إذا فشل الـ Script)

### 1. تحديث ملف البيئة:
```bash
cd /opt/pharmasky
nano .env.production
```

### 2. تأكد من هذه الإعدادات:
```env
# DigitalOcean Spaces Configuration
AWS_ACCESS_KEY_ID=DO00JME92LMKTFP2BBA3
AWS_SECRET_ACCESS_KEY=YOUR_ACTUAL_SECRET_KEY_HERE
AWS_STORAGE_BUCKET_NAME=pharmasky-media
AWS_S3_ENDPOINT_URL=https://pharmasky-media.fra1.digitaloceanspaces.com
AWS_S3_REGION_NAME=fra1
AWS_LOCATION=media
```

### 3. إعادة تشغيل وجمع Static Files:
```bash
docker-compose down
docker-compose up -d
sleep 30
docker-compose exec web python manage.py collectstatic --noinput
```

---

## 📊 فحص Static Files

### اختبار الروابط:

```bash
# فحص admin CSS
curl -I http://167.71.40.9/static/admin/css/base.css

# فحص على Spaces مباشرة
curl -I https://pharmasky-media.fra1.digitaloceanspaces.com/static/admin/css/base.css
```

### في المتصفح:
- **Admin CSS:** http://167.71.40.9/static/admin/css/base.css
- **Direct Spaces:** https://pharmasky-media.fra1.digitaloceanspaces.com/static/admin/css/base.css

---

## 🏗️ بنية DigitalOcean Spaces المطلوبة

يجب أن تكون البنية كالتالي:

```
pharmasky-media/
├── media/          # Media files (uploads)
└── static/         # Static files (CSS, JS)
    ├── admin/
    ├── css/
    └── js/
```

---

## 🚨 المشاكل الشائعة والحلول

### 1. مفتاح Spaces خاطئ:
```bash
# خطأ: 403 Forbidden
# الحل: تحديث AWS_SECRET_ACCESS_KEY
```

### 2. Static files لا تُجمع:
```bash
# فحص السجلات
docker-compose logs web

# إعادة المحاولة
docker-compose exec web python manage.py collectstatic --noinput --verbosity=2
```

### 3. Permissions مشكلة:
```bash
# تحقق من Spaces permissions
# Settings → Permissions → Public Read
```

### 4. CORS مشاكل:
```bash
# في Spaces Settings → CORS
# أضف: Origin: http://167.71.40.9
```

---

## ⚙️ إعدادات Django الحالية

الإعدادات في `settings.py` صحيحة:

```python
# Production static files will use:
STATIC_URL = "https://pharmasky-media.fra1.digitaloceanspaces.com/static/"
STORAGES = {
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3StaticStorage",
        # ... DigitalOcean Spaces configuration
    }
}
```

---

## 🔍 تشخيص المشاكل

### أوامر التشخيص:
```bash
# فحص حالة التطبيق
docker-compose ps

# فحص السجلات
docker-compose logs web | grep -i static

# فحص متغيرات البيئة
docker-compose exec web printenv | grep AWS

# اختبار connection للـ Spaces
docker-compose exec web python -c "
import boto3
from django.conf import settings
s3 = boto3.client('s3', 
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)
print('Connection successful!')
"
```

---

## 📝 خطة العمل المرتبة

### الأولوية الأولى:
1. ✅ تحديث `AWS_SECRET_ACCESS_KEY` 
2. ✅ إعادة تشغيل التطبيق
3. ✅ تشغيل `collectstatic`

### الأولوية الثانية:
1. 🔍 فحص Spaces permissions
2. 🔍 فحص CORS settings
3. 🔍 تحقق من بنية المجلدات

### الأولوية الثالثة:
1. 🧪 اختبار Static files في المتصفح
2. 🧪 فحص Admin panel styling
3. 🧪 اختبار API assets

---

## 💡 نصائح للمستقبل

### للحفاظ على Static Files:
```bash
# دائماً شغّل بعد التحديثات
docker-compose exec web python manage.py collectstatic --noinput

# للنسخ الاحتياطي
aws s3 sync s3://pharmasky-media/static/ ./static_backup/ --endpoint-url=https://fra1.digitaloceanspaces.com
```

### مراقبة الـ Storage:
```bash
# فحص استخدام المساحة
aws s3 ls s3://pharmasky-media/ --recursive --human-readable --summarize --endpoint-url=https://fra1.digitaloceanspaces.com
```

---

**🎯 النتيجة المتوقعة:** بعد تنفيذ هذه الخطوات، ستعمل جميع Static Files بشكل صحيح من DigitalOcean Spaces!
