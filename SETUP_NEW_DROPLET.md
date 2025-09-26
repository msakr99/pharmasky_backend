# 🚀 إعداد الدروبليت الجديدة - خطوة بخطوة

## 📊 معلومات الدروبليت الجديدة
- **IP Address:** `129.212.140.152`
- **Status:** ✅ متصلة وتعمل
- **SSH:** ⚠️ يحتاج إعداد المفتاح العام

---

## 🔧 الخطوات المطلوبة

### الخطوة 1: إعداد SSH Key عبر DigitalOcean Console

1. **اذهب إلى DigitalOcean Dashboard:**
   ```
   https://cloud.digitalocean.com/
   ```

2. **اختر الدروبليت الجديدة (129.212.140.152)**

3. **انقر على "Console" للوصول المباشر**

4. **تسجيل الدخول:**
   - Username: `root`
   - Password: (كلمة المرور التي أنشأتها)

5. **تشغيل الأوامر التالية في Console:**

```bash
# إعداد SSH key
mkdir -p ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDQH0MsW1lzkRkpbOspKXb1dlpA1hHD8AONnpDGSFtld pharmasky-github-deploy" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# تثبيت المتطلبات الأساسية
apt update
apt install -y git curl wget

# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# تثبيت Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# إعداد Firewall
ufw --force enable
ufw allow ssh
ufw allow 80
ufw allow 443

echo "✅ تم إعداد الدروبليت بنجاح!"
```

---

### الخطوة 2: استنساخ المشروع من GitHub

بعد إعداد SSH، شغّل في Console:

```bash
# إنشاء مجلد المشروع
mkdir -p /opt/pharmasky
cd /opt/pharmasky

# استنساخ المشروع من GitHub
git clone https://github.com/msakr99/pharmasky_backend.git .

# تعيين الصلاحيات
chmod +x *.sh

# نسخ ملف البيئة
cp production.env .env.production

echo "📦 تم استنساخ المشروع بنجاح!"
```

---

### الخطوة 3: تشغيل التطبيق

```bash
# بناء وتشغيل الحاويات
docker-compose build --no-cache
docker-compose up -d

# انتظار تشغيل الخدمات
sleep 30

# تشغيل database migrations
docker-compose exec web python manage.py migrate

# جمع الملفات الثابتة
docker-compose exec web python manage.py collectstatic --noinput

# فحص حالة الخدمات
docker-compose ps

echo "🎉 تم تشغيل التطبيق بنجاح!"
```

---

### الخطوة 4: إنشاء مدير النظام

```bash
# إنشاء superuser
docker-compose exec web python manage.py createsuperuser
```

---

## ✅ فحص التطبيق

بعد إكمال الخطوات:

1. **التطبيق الرئيسي:** http://129.212.140.152
2. **لوحة الإدارة:** http://129.212.140.152/admin/
3. **فحص الصحة:** http://129.212.140.152/health/

---

## 📋 إعداد GitHub Secrets (بعد نجاح SSH)

1. **اذهب إلى:** https://github.com/msakr99/pharmasky_backend/settings/secrets/actions

2. **أضف Secrets جديدة:**

**Secret الأول:**
- **Name:** `DROPLET_IP`
- **Value:** `129.212.140.152`

**Secret الثاني:**
- **Name:** `DROPLET_SSH_KEY`
- **Value:** المفتاح الخاص كاملاً من ملف `pharmasky_deploy_key`

---

## 🚀 أوامر مفيدة للإدارة

```bash
# عرض حالة الخدمات
docker-compose ps

# عرض السجلات
docker-compose logs -f web

# إعادة تشغيل الخدمات
docker-compose restart

# تحديث التطبيق من GitHub
git pull origin main
docker-compose up --build -d

# استخدام الأوامر السريعة
./quick_commands.sh status
./quick_commands.sh health
./quick_commands.sh logs
```

---

## 🛠️ إعداد سريع بأمر واحد

بدلاً من الخطوات السابقة، يمكنك تشغيل الأمر التالي في DigitalOcean Console:

```bash
curl -o setup_complete.sh https://raw.githubusercontent.com/msakr99/pharmasky_backend/main/github_deploy.sh && chmod +x setup_complete.sh && ./setup_complete.sh
```

---

## 📊 حل المشاكل السريع

### إذا فشل Docker:
```bash
systemctl start docker
systemctl enable docker
```

### إذا فشل في الـ build:
```bash
docker system prune -a
docker-compose up --build -d
```

### إذا فشل في Database:
```bash
docker-compose restart
docker-compose logs web
```

---

## 🎯 الخلاصة

بعد إكمال هذه الخطوات ستحصل على:

✅ دروبليت جاهزة للاستخدام  
✅ مشروع PharmasSky مُنصب ويعمل  
✅ Docker containers تعمل  
✅ قاعدة البيانات متصلة  
✅ نشر تلقائي من GitHub جاهز  

**عنوان التطبيق:** http://129.212.140.152
