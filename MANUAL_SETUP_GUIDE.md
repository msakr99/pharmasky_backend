# 🔧 دليل الإعداد اليدوي للنشر التلقائي

في حالة عدم عمل SSH connection، يمكنك اتباع هذا الدليل للإعداد اليدوي.

## 🚨 مشكلة SSH Connection

إذا واجهت الخطأ التالي:
```
ssh: connect to host 164.90.217.81 port 22: Connection refused
```

فهذا يعني أن:
- SSH service غير مفعل على الدروبليت
- Firewall يحجب SSH port (22)
- الدروبليت غير جاهز بعد

## ✅ الحلول البديلة

### الحل الأول: تفعيل SSH عبر DigitalOcean Console

1. **اذهب إلى DigitalOcean Dashboard:**
   ```
   https://cloud.digitalocean.com/
   ```

2. **اختر Droplet الخاص بك**

3. **انقر على "Console" أو "Access Console"**

4. **تسجيل الدخول باستخدام:**
   - Username: `root`
   - Password: `sAkr4601#a`

5. **تشغيل الأوامر التالية:**

```bash
# تثبيت وتفعيل SSH
apt update
apt install -y openssh-server
systemctl enable ssh
systemctl start ssh

# إعداد Firewall
ufw allow ssh
ufw --force enable

# إضافة SSH public key
mkdir -p ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDQH0MsW1lzkRkpbOspKXb1dlpA1hHD8AONnpDGSFtld pharmasky-github-deploy" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# تثبيت Git و Docker
apt install -y git curl wget
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# إنشاء مجلد المشروع واستنساخه
mkdir -p /opt/pharmasky
git clone https://github.com/msakr99/pharmasky_backend.git /opt/pharmasky
cd /opt/pharmasky
chmod +x *.sh

echo "✅ تم الإعداد بنجاح!"
```

### الحل الثاني: استخدام DigitalOcean Droplets API

إذا كان لديك API token، يمكنك إعادة إنشاء الدروبليت:

```bash
# إنشاء دروبليت جديد مع SSH key
curl -X POST "https://api.digitalocean.com/v2/droplets" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_API_TOKEN" \
-d '{
  "name": "pharmasky-backend",
  "region": "fra1",
  "size": "s-2vcpu-2gb",
  "image": "ubuntu-20-04-x64",
  "ssh_keys": ["SSH_KEY_ID"],
  "backups": false,
  "ipv6": true,
  "user_data": "#!/bin/bash\napt update && apt install -y git curl docker.io docker-compose"
}'
```

### الحل الثالث: إعداد Droplet جديد

إذا كان الدروبليت الحالي لا يعمل:

1. **إنشاء Droplet جديد في DigitalOcean:**
   - اختر Ubuntu 20.04 LTS
   - الحجم: 2GB RAM, 2 vCPUs (أو أكبر)
   - المنطقة: Frankfurt أو أقرب منطقة
   - أضف SSH key عند الإنشاء

2. **عند إنشاء SSH key في DigitalOcean:**
   ```
   ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDQH0MsW1lzkRkpbOspKXb1dlpA1hHD8AONnpDGSFtld pharmasky-github-deploy
   ```

## 📋 بعد حل مشكلة SSH

### 1. تحديث GitHub Secrets

إذا تغير IP الدروبليت:
```
DROPLET_IP = NEW_IP_ADDRESS
DROPLET_SSH_KEY = [نفس المفتاح الخاص]
```

### 2. اختبار SSH Connection

```bash
# من جهازك المحلي
ssh -i pharmasky_deploy_key root@NEW_IP_ADDRESS
```

### 3. إعداد المشروع على الدروبليت

```bash
# الاتصال بالدروبليت
ssh root@NEW_IP_ADDRESS

# تشغيل setup script
curl -o github_deploy.sh https://raw.githubusercontent.com/msakr99/pharmasky_backend/main/github_deploy.sh
chmod +x github_deploy.sh
./github_deploy.sh
```

## 🔐 إعداد GitHub Secrets (بعد حل مشكلة SSH)

### الطريقة السهلة:
افتح ملف `github_secrets_copy.html` في المتصفح وانسخ البيانات المطلوبة.

### الطريقة اليدوية:
1. اذهب إلى: https://github.com/msakr99/pharmasky_backend/settings/secrets/actions
2. أضف Secret جديد:
   - **Name:** `DROPLET_IP`
   - **Value:** `164.90.217.81` (أو IP الجديد)
3. أضف Secret آخر:
   - **Name:** `DROPLET_SSH_KEY`
   - **Value:** المفتاح الخاص كاملاً (من ملف `pharmasky_deploy_key`)

## ✅ اختبار النشر التلقائي

### النشر التلقائي:
قم بأي تغيير في الكود و push إلى main branch

### النشر اليدوي:
1. اذهب إلى: https://github.com/msakr99/pharmasky_backend/actions
2. اختر "Deploy to DigitalOcean"
3. انقر "Run workflow"

## 📊 مراقبة النشر

### GitHub Actions Logs:
```
https://github.com/msakr99/pharmasky_backend/actions
```

### فحص التطبيق:
```bash
# على الدروبليت
cd /opt/pharmasky
docker-compose ps
docker-compose logs -f web
curl http://localhost/health/
```

### عناوين التطبيق:
- **التطبيق:** http://YOUR_DROPLET_IP
- **الإدارة:** http://YOUR_DROPLET_IP/admin/
- **الصحة:** http://YOUR_DROPLET_IP/health/

## 🛠️ أوامر الإدارة السريعة

```bash
# تحديث التطبيق يدوياً
cd /opt/pharmasky
git pull
docker-compose up --build -d

# عرض السجلات
docker-compose logs -f

# إعادة تشغيل الخدمات
docker-compose restart

# فحص الحالة
docker-compose ps

# استخدام الأوامر السريعة
./quick_commands.sh status
./quick_commands.sh health
./quick_commands.sh logs
```

## 🚨 حل المشاكل الشائعة

### 1. Connection refused:
- تحقق من تشغيل SSH service
- تحقق من Firewall settings
- استخدم DigitalOcean Console

### 2. Permission denied:
- تحقق من SSH key في authorized_keys
- تحقق من صلاحيات الملفات (chmod 600)

### 3. Docker errors:
```bash
# تنظيف Docker
docker system prune -a
docker-compose down
docker-compose up --build -d
```

### 4. Database errors:
```bash
# إعادة تشغيل الخدمات
docker-compose restart
# أو فحص اتصال قاعدة البيانات
docker-compose exec web python manage.py check --database default
```

---

## 📞 الدعم الإضافي

إذا واجهت أي مشاكل أخرى:

1. **تحقق من DigitalOcean Dashboard** للتأكد من حالة الدروبليت
2. **استخدم Console** للوصول المباشر للدروبليت
3. **راجع documentation** الخاصة بـ DigitalOcean SSH setup
4. **تحقق من GitHub Actions logs** لمعرفة تفاصيل الأخطاء

**عند حل مشكلة SSH، ستتمكن من استخدام النشر التلقائي بسهولة!** 🎉
