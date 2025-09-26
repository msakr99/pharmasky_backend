# 🚀 دليل رفع مشروع PharmasSky من GitHub إلى DigitalOcean

هذا الدليل يوضح كيفية رفع مشروع PharmasSky Backend من GitHub repository إلى DigitalOcean Droplet.

## معلومات الخادم
- **عنوان IP للـ Droplet:** `164.90.217.81`
- **اسم المستخدم:** `root`
- **كلمة المرور:** `sAkr4601#a`
- **GitHub Repository:** `https://github.com/msakr99/pharmasky_backend.git`

## الطريقة الأولى: الرفع التلقائي باستخدام GitHub Actions (موصى بها)

### 1. إعداد GitHub Secrets

اذهب إلى GitHub repository → Settings → Secrets and Variables → Actions وأضف:

```
DROPLET_IP = 164.90.217.81
DROPLET_SSH_KEY = [محتوى المفتاح الخاص SSH]
```

### 2. إنشاء SSH Key (إذا لم يكن موجوداً)

على جهازك المحلي:
```bash
ssh-keygen -t ed25519 -C "pharmasky-deploy"
```

انسخ المفتاح العام إلى الخادم:
```bash
ssh-copy-id root@164.90.217.81
```

انسخ المفتاح الخاص وأضفه كـ Secret في GitHub.

### 3. تفعيل الرفع التلقائي

عند كل push إلى branch `main`، سيتم رفع التطبيق تلقائياً.

لرفع يدوي، اذهب إلى:
GitHub → Actions → Deploy to DigitalOcean → Run workflow

---

## الطريقة الثانية: الرفع اليدوي من الخادم

### 1. الاتصال بالخادم

```bash
ssh root@164.90.217.81
```

### 2. استخدام الـ Script الجديد للـ GitHub

```bash
# تحميل وتشغيل الـ deployment script
curl -o github_deploy.sh https://raw.githubusercontent.com/msakr99/pharmasky_backend/main/github_deploy.sh
chmod +x github_deploy.sh
./github_deploy.sh
```

### 3. أو الطريقة اليدوية الكاملة

```bash
# تحديث النظام وتثبيت المتطلبات
apt update && apt upgrade -y
apt install -y docker.io docker-compose git nginx ufw curl

# تفعيل وإعداد Firewall
ufw --force enable
ufw allow ssh
ufw allow 80
ufw allow 443

# إنشاء مجلد المشروع
mkdir -p /opt/pharmasky
cd /opt/pharmasky

# استنساخ المشروع من GitHub
git clone https://github.com/msakr99/pharmasky_backend.git .

# إعداد ملف البيئة
cp production.env .env.production

# تحرير ملف البيئة (مهم!)
nano .env.production
```

### 4. تحرير ملف البيئة (.env.production)

تأكد من تحديث القيم التالية:

```env
# تحديث الـ ALLOWED_HOSTS
ALLOWED_HOSTS=164.90.217.81,yourdomain.com,localhost

# تعيين مفتاح سري قوي
SECRET_KEY=your-very-long-and-random-secret-key-here

# تحديث بيانات DigitalOcean Spaces
AWS_ACCESS_KEY_ID=your-spaces-access-key
AWS_SECRET_ACCESS_KEY=your-spaces-secret-key

# تحديث CORS settings
CORS_ALLOWED_ORIGINS=http://164.90.217.81,http://yourdomain.com
CSRF_TRUSTED_ORIGINS=http://164.90.217.81,http://yourdomain.com
```

### 5. رفع وتشغيل التطبيق

```bash
# بناء وتشغيل الحاويات
docker-compose build --no-cache
docker-compose up -d

# انتظار تشغيل الخدمات
sleep 30

# تشغيل migrations
docker-compose exec web python manage.py migrate

# جمع الملفات الثابتة
docker-compose exec web python manage.py collectstatic --noinput

# إنشاء حساب مدير
docker-compose exec web python manage.py createsuperuser

# فحص حالة الخدمات
docker-compose ps
```

---

## التحقق من نجاح الرفع

### 1. فحص الخدمات
```bash
docker-compose ps
docker-compose logs web
```

### 2. اختبار التطبيق
- التطبيق الرئيسي: `http://164.90.217.81`
- لوحة الإدارة: `http://164.90.217.81/admin/`
- فحص الصحة: `http://164.90.217.81/health/`

---

## إعداد النشر المستمر (CI/CD)

المشروع يحتوي على GitHub Actions workflow الذي:

1. **يتم تشغيله عند:** Push إلى main branch أو تشغيل يدوي
2. **يقوم بـ:** سحب التحديثات، بناء التطبيق، وتشغيله
3. **يتضمن:** فحص صحة التطبيق بعد الرفع

### ملف الـ Workflow: `.github/workflows/deploy.yml`

```yaml
name: Deploy to DigitalOcean
on:
  push:
    branches: [ main, master ]
  workflow_dispatch:
```

---

## الأوامر المفيدة

### إدارة التطبيق
```bash
# عرض سجلات التطبيق
docker-compose logs -f web

# إعادة تشغيل الخدمات
docker-compose restart

# تحديث التطبيق من GitHub
cd /opt/pharmasky
git pull
docker-compose up --build -d

# تشغيل أوامر Django
docker-compose exec web python manage.py [command]

# فحص استخدام الموارد
docker stats

# تنظيف الحاويات والصور القديمة
docker system prune -a
```

### إدارة قاعدة البيانات
```bash
# إنشاء backup لقاعدة البيانات
docker-compose exec web python manage.py dumpdata > backup_$(date +%Y%m%d).json

# تشغيل migrations جديدة
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

---

## حل المشاكل الشائعة

### 1. فشل في بناء الحاوية
```bash
# حذف الحاويات والصور القديمة
docker-compose down
docker system prune -a
docker-compose build --no-cache
```

### 2. مشاكل في قاعدة البيانات
```bash
# فحص اتصال قاعدة البيانات
docker-compose exec web python manage.py check --database default

# إعادة تشغيل الخدمات
docker-compose restart
```

### 3. مشاكل في الملفات الثابتة
```bash
# جمع الملفات الثابتة مرة أخرى
docker-compose exec web python manage.py collectstatic --clear --noinput
```

### 4. فحص السجلات للأخطاء
```bash
# سجلات التطبيق الرئيسي
docker-compose logs web

# سجلات nginx
docker-compose logs nginx

# سجلات Redis
docker-compose logs redis

# سجلات Celery
docker-compose logs celery
```

---

## إعداد SSL والنطاق (اختياري)

### 1. إعداد النطاق
```bash
# تحديث nginx.conf بالنطاق الخاص بك
sed -i 's/your-domain.com/yourdomain.com/g' nginx.conf

# إعداد SSL مع Let's Encrypt
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 2. تحديث إعدادات Django
```bash
# تحديث .env.production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,164.90.217.81
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SECURE_SSL_REDIRECT=True
```

---

## المراقبة والصيانة

### 1. إعداد مراقبة أساسية
```bash
# إضافة cron job لفحص صحة التطبيق
echo "*/5 * * * * curl -f http://localhost/health/ || systemctl restart docker" | crontab -
```

### 2. نسخ احتياطية تلقائية
```bash
# إنشاء script للنسخ الاحتياطي
cat > /usr/local/bin/pharmasky-backup.sh << 'EOF'
#!/bin/bash
cd /opt/pharmasky
docker-compose exec -T web python manage.py dumpdata > /opt/backups/backup_$(date +%Y%m%d_%H%M).json
find /opt/backups -name "backup_*.json" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/pharmasky-backup.sh

# إضافة إلى cron (نسخة احتياطية يومية)
echo "0 2 * * * /usr/local/bin/pharmasky-backup.sh" | crontab -
```

---

## 📞 الدعم والمساعدة

في حالة مواجهة أي مشاكل:

1. تحقق من سجلات التطبيق: `docker-compose logs`
2. تأكد من تشغيل جميع الخدمات: `docker-compose ps`
3. فحص مساحة القرص: `df -h`
4. فحص استخدام الذاكرة: `free -m`

**عنوان التطبيق النهائي:** `http://164.90.217.81` أو نطاقك المخصص

🎉 **تم إعداد التطبيق بنجاح!**
