# 🔐 إعداد GitHub Secrets للنشر التلقائي

هذا الدليل يوضح كيفية إعداد GitHub Secrets لتفعيل النشر التلقائي لمشروع PharmasSky.

## 🔑 المعلومات المطلوبة

### 1. SSH Keys

**المفتاح العام (يتم إضافته للدروبليت):**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDQH0MsW1lzkRkpbOspKXb1dlpA1hHD8AONnpDGSFtld pharmasky-github-deploy
```

**المفتاح الخاص (يتم إضافته لـ GitHub Secrets):**
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACA0B9DLFtZc5EZKWzrKSl29XZaQNYRw/ADjZ6QxkhbZXQAAAKCSLXNwki1z
cAAAAAtzc2gtZWQyNTUxOQAAACA0B9DLFtZc5EZKWzrKSl29XZaQNYRw/ADjZ6QxkhbZXQ
AAAECDe22c8t/OUYlRCpg9GqvF4YM+LfpbkBWKZrFeJMwGPDQH0MsW1lzkRkpbOspKXb1d
lpA1hHD8AONnpDGSFtldAAAAF3BoYXJtYXNreS1naXRodWItZGVwbG95AQIDBAUG
-----END OPENSSH PRIVATE KEY-----
```

### 2. بيانات الخادم

- **DROPLET_IP:** `164.90.217.81`
- **Password:** `sAkr4601#a`

---

## 📋 خطوات الإعداد

### الخطوة الأولى: إعداد SSH Key على الدروبليت

#### الطريقة الأولى: استخدام Script جاهز
```bash
# الاتصال بالدروبليت
ssh root@164.90.217.81

# تحميل وتشغيل setup script
curl -o setup_ssh_key.sh https://raw.githubusercontent.com/msakr99/pharmasky_backend/main/setup_ssh_key.sh
chmod +x setup_ssh_key.sh
./setup_ssh_key.sh
```

#### الطريقة الثانية: إعداد يدوي
```bash
# الاتصال بالدروبليت
ssh root@164.90.217.81

# إضافة المفتاح العام
mkdir -p ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDQH0MsW1lzkRkpbOspKXb1dlpA1hHD8AONnpDGSFtld pharmasky-github-deploy" >> ~/.ssh/authorized_keys

# تعيين الصلاحيات الصحيحة
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# تثبيت git إذا لم يكن موجوداً
apt update && apt install -y git

# إنشاء مجلد المشروع
mkdir -p /opt/pharmasky
git clone https://github.com/msakr99/pharmasky_backend.git /opt/pharmasky
chown -R root:root /opt/pharmasky
```

### الخطوة الثانية: إعداد GitHub Secrets

1. **اذهب إلى GitHub Repository:**
   ```
   https://github.com/msakr99/pharmasky_backend
   ```

2. **انقر على Settings (الإعدادات)**

3. **من القائمة الجانبية، اختر "Secrets and variables" > "Actions"**

4. **أضف Secret جديد بالنقر على "New repository secret"**

5. **أضف الـ Secrets التالية:**

   **Secret الأول:**
   - **Name:** `DROPLET_IP`
   - **Secret:** `164.90.217.81`

   **Secret الثاني:**
   - **Name:** `DROPLET_SSH_KEY`
   - **Secret:** 
   ```
   -----BEGIN OPENSSH PRIVATE KEY-----
   b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
   QyNTUxOQAAACA0B9DLFtZc5EZKWzrKSl29XZaQNYRw/ADjZ6QxkhbZXQAAAKCSLXNwki1z
   cAAAAAtzc2gtZWQyNTUxOQAAACA0B9DLFtZc5EZKWzrKSl29XZaQNYRw/ADjZ6QxkhbZXQ
   AAAECDe22c8t/OUYlRCpg9GqvF4YM+LfpbkBWKZrFeJMwGPDQH0MsW1lzkRkpbOspKXb1d
   lpA1hHD8AONnpDGSFtldAAAAF3BoYXJtYXNreS1naXRodWItZGVwbG95AQIDBAUG
   -----END OPENSSH PRIVATE KEY-----
   ```

### الخطوة الثالثة: اختبار الإعداد

1. **تحقق من أن SSH key يعمل:**
   ```bash
   # من جهازك المحلي (إذا كان لديك المفتاح الخاص)
   ssh -i pharmasky_deploy_key root@164.90.217.81
   ```

2. **تحقق من أن GitHub Actions workflow موجود:**
   - تأكد من وجود الملف: `.github/workflows/deploy.yml`

3. **قم بـ push أي تغيير إلى main branch لاختبار النشر التلقائي**

---

## 🚀 كيفية عمل النشر التلقائي

### متى يتم تشغيل النشر:
- عند كل `push` إلى branch `main` أو `master`
- يمكن تشغيله يدوياً من GitHub Actions tab

### ما يحدث خلال النشر:
1. **Checkout:** سحب أحدث إصدار من الكود
2. **Setup SSH:** إعداد اتصال SSH مع الدروبليت
3. **Deploy:** تشغيل أوامر النشر على الخادم:
   - سحب أحدث التحديثات من GitHub
   - بناء وتشغيل Docker containers
   - تشغيل database migrations
   - جمع الملفات الثابتة
   - فحص صحة التطبيق

---

## 🔍 مراقبة النشر

### عرض سجلات GitHub Actions:
1. اذهب إلى GitHub Repository
2. انقر على tab "Actions"
3. اختر آخر workflow run
4. شاهد التفاصيل والسجلات

### فحص التطبيق بعد النشر:
```bash
# الاتصال بالدروبليت
ssh root@164.90.217.81

# فحص حالة الخدمات
cd /opt/pharmasky
docker-compose ps

# عرض السجلات
docker-compose logs -f web

# فحص صحة التطبيق
curl http://localhost/health/
```

---

## 🛠️ أوامر مفيدة للإدارة

### على الدروبليت:
```bash
# الانتقال لمجلد المشروع
cd /opt/pharmasky

# تحديث يدوي من GitHub
git pull origin main
docker-compose up --build -d

# عرض حالة الخدمات
docker-compose ps

# إعادة تشغيل الخدمات
docker-compose restart

# عرض السجلات
docker-compose logs -f

# استخدام الأوامر السريعة
./quick_commands.sh status
./quick_commands.sh health
./quick_commands.sh logs
```

---

## 🚨 حل المشاكل الشائعة

### 1. فشل في SSH connection
```bash
# تحقق من SSH key
ssh-keygen -l -f ~/.ssh/authorized_keys

# تحقق من الصلاحيات
ls -la ~/.ssh/
```

### 2. فشل في GitHub Actions
- تحقق من GitHub Secrets
- تحقق من صيغة المفتاح الخاص
- راجع سجلات GitHub Actions

### 3. فشل في Docker build
```bash
# على الدروبليت
cd /opt/pharmasky
docker-compose down
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

### 4. مشاكل في قاعدة البيانات
```bash
# فحص اتصال قاعدة البيانات
docker-compose exec web python manage.py check --database default

# إعادة تشغيل الخدمات
docker-compose restart
```

---

## 📊 معلومات إضافية

### الملفات المهمة:
- `.github/workflows/deploy.yml` - GitHub Actions workflow
- `production.env` - متغيرات البيئة للإنتاج
- `docker-compose.yml` - إعداد Docker services
- `quick_commands.sh` - أوامر سريعة للإدارة

### عناوين التطبيق بعد النشر:
- **التطبيق الرئيسي:** `http://164.90.217.81`
- **لوحة الإدارة:** `http://164.90.217.81/admin/`
- **فحص الصحة:** `http://164.90.217.81/health/`
- **API Documentation:** `http://164.90.217.81/api/`

---

## ✅ قائمة التحقق

- [ ] إعداد SSH key على الدروبليت
- [ ] إضافة GitHub Secrets
- [ ] اختبار SSH connection
- [ ] تشغيل أول deployment
- [ ] التحقق من عمل التطبيق
- [ ] إنشاء superuser
- [ ] اختبار النشر التلقائي

---

🎉 **بعد إكمال هذه الخطوات، ستكون قادراً على النشر التلقائي بمجرد عمل push إلى GitHub!**
