# 🐳 إصلاح مشاكل Docker - Quick Fix Guide

## 🚨 المشاكل المكتشفة:

### 1. ⚠️ **كلمة مرور قاعدة البيانات مكشوفة في docker-compose.yml**
**الخطورة:** حرجة 🔴

### 2. Docker build فشل (exit code: 100)
**السبب:** مشاكل في apt-get repositories

### 3. مكتبة openai غير موجودة في Container
**السبب:** Docker image قديم يحتاج rebuild

---

## ✅ الحلول المطبقة:

### 1. تم إصلاح Dockerfile:
- ✅ إضافة `apt-get clean` قبل update
- ✅ إضافة `--fix-missing` لحل مشاكل repositories
- ✅ إضافة `--no-install-recommends` لتقليل الحجم
- ✅ إزالة nginx & supervisor (غير ضرورية داخل container)

### 2. تم إنشاء docker-compose.production.yml آمن:
- ✅ استخدام متغيرات بيئية بدلاً من hardcoded values
- ✅ إخفاء كلمات المرور من الملف

---

## 📋 خطوات الإصلاح (نفذها على السيرفر):

### الخطوة 1️⃣: إنشاء ملف .env للـ Docker
```bash
# على السيرفر (pharmasky-server)
cd /opt/pharmasky

# أنشئ ملف .env.docker
cat > .env.docker << 'EOF'
SECRET_KEY=pharmasky-change-this-to-a-very-long-random-secret-key-in-production-12345
DATABASE_URL=postgresql://doadmin:AVNS_g62jyoo4mcu0BkfRsdM@pharmasky-db-do-user-17921548-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require
OPENAI_API_KEY=your-openai-api-key-here
DIGITALOCEAN_AGENT_URL=https://rh7hum3gky53ykah274mdpkl.agents.do-ai.run
ALLOWED_HOSTS=167.71.40.9,129.212.140.152,164.90.217.81,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://167.71.40.9,http://129.212.140.152,http://164.90.217.81,http://localhost
CSRF_TRUSTED_ORIGINS=http://167.71.40.9,http://129.212.140.152,http://164.90.217.81,http://localhost
EOF
```

### الخطوة 2️⃣: إيقاف الـ Containers القديمة
```bash
docker-compose down
```

### الخطوة 3️⃣: حذف Images القديمة وإعادة البناء
```bash
# حذف الـ images القديمة
docker rmi pharmasky_web pharmasky_celery pharmasky_celery_beat 2>/dev/null || true

# إعادة بناء الـ images مع no-cache
docker-compose build --no-cache
```

### الخطوة 4️⃣: تشغيل الـ Containers
```bash
# باستخدام الملف الآمن الجديد
docker-compose -f docker-compose.production.yml --env-file .env.docker up -d

# أو إذا أردت استخدام الملف القديم (بعد تعديله):
docker-compose up -d
```

### الخطوة 5️⃣: التحقق من النجاح
```bash
# فحص الـ logs
docker-compose logs web --tail=50

# التأكد من عمل الـ containers
docker-compose ps

# اختبار openai import
docker exec pharmasky_web python -c "from openai import OpenAI; print('OpenAI loaded successfully!')"
```

---

## 🔧 حل سريع (إذا كنت متعجلاً):

```bash
# على السيرفر
cd /opt/pharmasky

# إيقاف كل شيء
docker-compose down

# حذف الصور القديمة
docker system prune -a -f

# إعادة البناء والتشغيل
docker-compose build --no-cache && docker-compose up -d

# فحص النتيجة
docker-compose logs web --tail=30
```

---

## ⚠️ تحذيرات أمنية:

### 1. كلمة مرور قاعدة البيانات:
```bash
# ⚠️ كلمة المرور موجودة حالياً في:
# - docker-compose.yml (سطر 22)
# - project/settings.py (تم إصلاحها ✅)

# الحل:
# 1. غيّر كلمة مرور قاعدة البيانات فوراً
# 2. استخدم docker-compose.production.yml الجديد
# 3. ضع كلمة المرور في .env.docker فقط
```

### 2. ملفات حساسة:
```bash
# تأكد من عدم رفع هذه الملفات للـ Git:
.env
.env.docker
production.env
```

---

## 🎯 النتيجة المتوقعة:

بعد تطبيق الخطوات:
- ✅ Docker build ينجح بدون أخطاء
- ✅ مكتبة openai متوفرة
- ✅ AI Agent يعمل بشكل صحيح
- ✅ كلمات المرور محمية

---

## 📞 في حالة وجود مشاكل:

### مشكلة 1: Docker build لا يزال يفشل
```bash
# جرب تغيير base image
# عدل Dockerfile السطر 2:
FROM python:3.11-slim-bullseye
```

### مشكلة 2: openai لا يزال غير موجود
```bash
# تأكد من تثبيته يدوياً
docker exec pharmasky_web pip install openai>=1.0.0
```

### مشكلة 3: permission denied
```bash
# أعط صلاحيات للـ directories
sudo chown -R $USER:$USER /opt/pharmasky
```

---

**آخر تحديث:** 16 أكتوبر 2025  
**الحالة:** ✅ تم إصلاح Dockerfile وإنشاء docker-compose آمن

