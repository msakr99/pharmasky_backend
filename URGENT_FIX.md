# 🚨 إصلاح عاجل - مشكلة 400 Bad Request

## المشكلة الحالية:
```
GET http://167.71.40.9/admin/ 400 (Bad Request)
The Cross-Origin-Opener-Policy header has been ignored
```

**السبب:** الدروبليت IP تغير إلى `167.71.40.9` لكن إعدادات Django لا تشمل هذا الـ IP.

---

## ✅ الحل السريع (دقيقتان):

### 1. اتصل بالدروبليت:
```bash
ssh root@167.71.40.9
```

### 2. شغّل أمر الإصلاح:
```bash
curl -o fix_cors_issue.sh https://raw.githubusercontent.com/msakr99/pharmasky_backend/main/fix_cors_issue.sh && chmod +x fix_cors_issue.sh && ./fix_cors_issue.sh
```

**هذا الأمر سيقوم بـ:**
- ✅ تحديث ALLOWED_HOSTS
- ✅ تحديث CORS settings
- ✅ إعادة تشغيل التطبيق
- ✅ فحص صحة التطبيق

---

## 🛠️ أو الإصلاح اليدوي:

```bash
# الدخول لمجلد المشروع
cd /opt/pharmasky

# تحديث ملف البيئة
nano .env.production

# أضف 167.71.40.9 إلى ALLOWED_HOSTS و CORS_ALLOWED_ORIGINS
ALLOWED_HOSTS=167.71.40.9,129.212.140.152,164.90.217.81,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://167.71.40.9,http://129.212.140.152,http://164.90.217.81,http://localhost
CSRF_TRUSTED_ORIGINS=http://167.71.40.9,http://129.212.140.152,http://164.90.217.81,http://localhost

# إعادة تشغيل التطبيق
docker-compose down
docker-compose up -d
```

---

## 🔐 تحديث GitHub Secrets (مهم للنشر التلقائي):

اذهب إلى: https://github.com/msakr99/pharmasky_backend/settings/secrets/actions

**حدّث:**
- `DROPLET_IP` = `167.71.40.9` (بدلاً من القديم)

---

## ✅ بعد الإصلاح:

التطبيق سيعمل على:
- **التطبيق:** http://167.71.40.9
- **الإدارة:** http://167.71.40.9/admin/
- **الصحة:** http://167.71.40.9/health/

---

## 📊 فحص النجاح:

```bash
# على الدروبليت
docker-compose ps
docker-compose logs web | tail -10
curl http://localhost/health/
```

---

**⏰ وقت الإصلاح المتوقع: دقيقتان**

**🎯 النتيجة: إصلاح كامل لمشاكل CORS و 400 Bad Request**
