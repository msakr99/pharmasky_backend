# 🔐 دليل الأمان والحلول - PharmaSky

## 📋 المشاكل التي تم حلها

### 1. ✅ مشكلة صلاحيات Migrations

**السبب:** الملفات في مجلد migrations مملوكة لمستخدم مختلف عن المستخدم الذي يشغل Django في الحاوية.

**الحل (على السيرفر):**

```bash
# اتصل بالسيرفر
ssh root@pharmasky-server

# انتقل لمجلد المشروع
cd /opt/pharmasky

# الطريقة 1: إصلاح الصلاحيات من الخارج (مفضل)
sudo chown -R 1000:1000 ./market/migrations
sudo chown -R 1000:1000 ./core/migrations
sudo chmod -R 775 ./*/migrations

# الطريقة 2: إصلاح الصلاحيات من داخل الحاوية
docker exec -u root pharmasky_web chown -R www-data:www-data /app/market/migrations /app/core/migrations
docker exec -u root pharmasky_web chmod -R 775 /app/market/migrations /app/core/migrations
```

**التحقق من الحل:**
```bash
docker exec -i pharmasky_web python manage.py makemigrations
docker exec -i pharmasky_web python manage.py migrate
```

---

### 2. 🛡️ الحماية من محاولات الاختراق

**ما حدث:**
```
DisallowedHost: Invalid HTTP_HOST header: 'bulldog.exchange'
Not Found: /.env
Forbidden (CSRF cookie not set.)
```

**التفسير:**
هذه محاولات تلقائية من روبوتات تحاول:
- الوصول لملفات حساسة (`.env`)
- استخدام نطاقات وهمية (`bulldog.exchange`)
- محاولة هجمات CSRF

**الحماية المطبقة:**

#### أ) Middleware جديد للأمان
تم إضافة `core/middleware/security.py` الذي:
- يحظر المسارات المشبوهة تلقائياً
- يرصد User Agents المشبوهة
- يسجل المحاولات المشبوهة دون إزعاج
- يعيد رسائل خطأ بسيطة

#### ب) ملف robots.txt
تم إضافة `templates/robots.txt` لتوجيه محركات البحث الشرعية.

---

### 3. ⚠️ تحذير WeasyPrint

**التحذير:**
```
WeasyPrint could not import some external libraries.
```

**التفسير:**
- WeasyPrint تحتاج مكتبات نظام خارجية (Cairo, Pango, GDK-PixBuf)
- هذا التحذير غير حرج إذا لم تكن تستخدم توليد PDF

**الحل (إذا كنت تحتاج WeasyPrint):**

في `Dockerfile`:
```dockerfile
# Add system dependencies for WeasyPrint
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*
```

**الحل (إذا لم تحتاجها):**
احذف `WeasyPrint` من `requirements.txt` إذا لم تستخدم توليد PDF.

---

## 🚀 خطوات التطبيق على السيرفر

### الخطوة 1: إصلاح الصلاحيات (مطلوب فوراً)

```bash
ssh root@pharmasky-server
cd /opt/pharmasky

# إصلاح الصلاحيات
sudo chown -R 1000:1000 ./market/migrations ./core/migrations
sudo chmod -R 775 ./*/migrations
```

### الخطوة 2: تحديث الكود (Deploy التحديثات)

```bash
# على جهازك المحلي: ارفع التحديثات
git add .
git commit -m "Add security middleware and robots.txt"
git push origin main

# على السيرفر: اسحب التحديثات
cd /opt/pharmasky
git pull origin main

# أعد بناء وتشغيل الحاوية
docker-compose down
docker-compose up -d --build

# تحقق من السجلات
docker logs pharmasky_web --tail 50
```

### الخطوة 3: التحقق من التشغيل

```bash
# تحقق من أن الخدمة تعمل
curl http://localhost:8000/

# تحقق من robots.txt
curl http://localhost:8000/robots.txt

# تحقق من السجلات
docker logs pharmasky_web --tail 100 | grep -E "Blocked|DisallowedHost"
```

---

## 📊 فهم السجلات (Logs)

### سجلات عادية (لا تقلق منها):
```
Not Found: /robots.txt  → تم الحل بإضافة robots.txt
Not Found: /.env        → محاولة اختراق، محظورة تلقائياً ✅
DisallowedHost          → محاولة اختراق، محظورة تلقائياً ✅
Forbidden (CSRF)        → حماية Django تعمل ✅
```

### سجلات تحتاج انتباه:
```
500 Internal Server Error  → خطأ في الكود
Database connection error  → مشكلة في الاتصال بقاعدة البيانات
Permission denied         → مشكلة في الصلاحيات
```

---

## 🔒 نصائح أمان إضافية

### 1. تأكد من ALLOWED_HOSTS صحيح

في `.env` على السيرفر:
```env
# النطاقات المسموح بها فقط
ALLOWED_HOSTS=pharmasky.com,www.pharmasky.com,api.pharmasky.com

# لا تضع *
# ALLOWED_HOSTS=*  ❌ خطر!
```

### 2. راقب السجلات بانتظام

```bash
# سجلات اليوم
docker logs pharmasky_web --since 24h | grep -E "ERROR|WARNING"

# سجلات محاولات الاختراق
docker logs pharmasky_web | grep -E "Blocked|suspicious"

# سجلات الأداء
docker logs pharmasky_web | grep -E "slow|timeout"
```

### 3. تحديثات دورية

```bash
# تحديث الحاويات شهرياً
docker-compose pull
docker-compose up -d --build

# تحديث التبعيات
pip list --outdated
```

### 4. Backup منتظم

```bash
# نسخة احتياطية من قاعدة البيانات (يومياً)
docker exec pharmasky_db pg_dump -U postgres pharmasky > backup_$(date +%Y%m%d).sql

# نسخة احتياطية من الملفات (أسبوعياً)
tar -czf media_backup_$(date +%Y%m%d).tar.gz /opt/pharmasky/media/
```

---

## 📈 مراقبة الأداء

### أوامر مفيدة:

```bash
# استهلاك الموارد
docker stats pharmasky_web

# عدد الاتصالات
docker exec pharmasky_web netstat -an | grep ESTABLISHED | wc -l

# حجم قاعدة البيانات
docker exec pharmasky_db psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('pharmasky'));"

# الحاويات النشطة
docker-compose ps
```

---

## ✅ Checklist ما بعد التطبيق

- [ ] تم إصلاح صلاحيات migrations
- [ ] تم Deploy التحديثات الجديدة
- [ ] Middleware الأمان يعمل
- [ ] robots.txt متاح
- [ ] السجلات نظيفة من الأخطاء الحرجة
- [ ] ALLOWED_HOSTS محدد بشكل صحيح
- [ ] النسخ الاحتياطية تعمل تلقائياً

---

## 🆘 الدعم

إذا واجهت مشكلة:

1. **تحقق من السجلات:**
   ```bash
   docker logs pharmasky_web --tail 100
   ```

2. **أعد تشغيل الحاوية:**
   ```bash
   docker-compose restart pharmasky_web
   ```

3. **تحقق من الاتصال بقاعدة البيانات:**
   ```bash
   docker exec pharmasky_web python manage.py dbshell
   ```

4. **اختبر الاتصال:**
   ```bash
   curl -I http://localhost:8000/
   ```

---

## 📚 مصادر إضافية

- [Django Security Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Django Best Practices for Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

---

**آخر تحديث:** 20 أكتوبر 2025
**الإصدار:** 1.0.0

