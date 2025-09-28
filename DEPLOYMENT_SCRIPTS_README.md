# 🚀 PharmasSky Auto Deployment Scripts

## 📁 الملفات المتوفرة:

### 1. `setup_ssh.sh` - إعداد SSH Key (الأهم!)
**الاستخدام:** إعداد SSH key للوصول للسيرفر
```bash
./setup_ssh.sh
```

### 2. `auto_deploy.sh` - النشر السريع المحسّن ⭐
**الاستخدام:** أسرع طريقة للنشر (مستحسن للاستخدام اليومي)
```bash
./auto_deploy.sh
# أو مع رسالة commit مخصصة
./auto_deploy.sh "إضافة ميزة جديدة للمنتجات"
```

### 3. `setup_deployment.sh` - إعداد أولي
**الاستخدام:** مرة واحدة فقط للتحقق من الإعدادات
```bash
./setup_deployment.sh
```

### 4. `update_and_deploy.sh` - تحديث كامل
**الاستخدام:** تحديث شامل مع تفاصيل وإختبارات
```bash
./update_and_deploy.sh
```

### 5. `quick_update.sh` - تحديث سريع بسيط
**الاستخدام:** تحديث سريع بدون تفاصيل
```bash
./quick_update.sh
```

## 🔧 الإعداد الأولي:

### خطوات الإعداد لأول مرة:

1. **إعداد SSH Key:**
```bash
./setup_ssh.sh
```

2. **التحقق من الإعدادات:**
```bash
./setup_deployment.sh
```

3. **جاهز للاستخدام!** 🎉

### المعلومات المستخدمة (من server-config.md):
- **عنوان IP:** 129.212.140.152
- **المستخدم:** root
- **مسار المشروع:** /opt/pharmasky
- **SSH Key:** ~/.ssh/pharmasky-github-deploy

## 📋 ما يفعله كل script:

### `setup_deployment.sh`:
- ✅ يطلب معلومات الـ Droplet
- ✅ يحفظ الإعدادات في `.deploy_config`
- ✅ يحدث الـ scripts الأخرى بالقيم الصحيحة
- ✅ يختبر اتصال SSH

### `update_and_deploy.sh`:
- ✅ يتحقق من التغييرات غير المحفوظة
- ✅ يطلب رسالة commit
- ✅ يرفع التحديثات لـ GitHub
- ✅ يحدث الـ Droplet
- ✅ يعيد تشغيل Docker containers
- ✅ يختبر الـ API

### `quick_update.sh`:
- ✅ يحفظ التغييرات تلقائياً
- ✅ يرفع لـ GitHub
- ✅ يحدث الـ Droplet
- ✅ يعيد تشغيل الخدمات

## 🔑 متطلبات SSH:

### إعداد SSH Key (إذا لم يكن موجود):
```bash
# إنشاء SSH key
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# نسخ المفتاح العام للـ Droplet
ssh-copy-id root@your_droplet_ip

# أو نسخ يدوياً:
cat ~/.ssh/id_rsa.pub
# ثم أضف المحتوى في الـ Droplet في ~/.ssh/authorized_keys
```

## 🚀 الاستخدام اليومي:

### الطريقة المفضلة (سريعة وذكية):
```bash
./auto_deploy.sh
# أو مع رسالة commit
./auto_deploy.sh "إضافة ميزة جديدة"
```

### للتحديث السريع البسيط:
```bash
./quick_update.sh
```

### للتحديث مع تحكم أكبر:
```bash
./update_and_deploy.sh
```

## 🐳 Docker Commands (في حالة المشاكل):

### في الـ Droplet:
```bash
# التحقق من الـ containers
docker-compose ps

# مشاهدة اللوجز
docker-compose logs -f

# إعادة تشغيل container محدد
docker-compose restart web

# إعادة بناء كامل
docker-compose down
docker-compose up --build -d
```

## 🔍 استكشاف الأخطاء:

### مشاكل SSH:
```bash
# اختبار الاتصال
ssh root@your_droplet_ip

# إذا كان يطلب password، أضف SSH key
ssh-copy-id root@your_droplet_ip
```

### مشاكل Git:
```bash
# التحقق من حالة Git
git status

# إعادة تعيين للآخر commit
git reset --hard HEAD

# حل conflicts
git stash
git pull origin main
git stash pop
```

### مشاكل Docker:
```bash
# في الـ Droplet
cd /opt/pharmasky
docker-compose logs
docker system prune -f  # حذف المساحة غير المستخدمة
```

## 📝 ملاحظات مهمة:

- ✅ ملف `.deploy_config` لا يُرفع لـ GitHub (في .gitignore)
- ✅ Scripts تعمل على Linux/Mac/Windows (Git Bash)
- ✅ يتم حفظ backup من nginx.conf تلقائياً
- ✅ Scripts تختبر الاتصال قبل التحديث

## 🎯 مثال على الاستخدام:

```bash
# الإعداد الأولي (مرة واحدة فقط)
./setup_ssh.sh
./setup_deployment.sh

# بعد تعديل الكود - استخدم الطريقة المفضلة
./auto_deploy.sh

# انتهى! التطبيق محدث على الـ Droplet 🎉
```

## ⚡ الفرق بين الـ Scripts:

| Script | السرعة | التفاصيل | الاستخدام |
|--------|---------|----------|-----------|
| `auto_deploy.sh` | ⚡⚡⚡ | متوسط | **اليومي المفضل** |
| `quick_update.sh` | ⚡⚡ | قليل | سريع وبسيط |
| `update_and_deploy.sh` | ⚡ | كثير | تحديث شامل |
| `deploy_to_server.sh` | ⚡⚡ | متوسط | نشر مباشر |

## 🔑 نصائح مهمة:

1. **للمرة الأولى:** شغل `setup_ssh.sh` ثم `setup_deployment.sh`
2. **للاستخدام اليومي:** استخدم `auto_deploy.sh` (الأفضل!)
3. **لو عندك مشاكل SSH:** شغل `setup_ssh.sh` مرة تانية
4. **لو محتاج تفاصيل أكثر:** استخدم `update_and_deploy.sh`

## 📞 لو عندك مشاكل:

1. **تأكد من وجود SSH key:** `ls -la ~/.ssh/pharmasky-github-deploy`
2. **اختبر الاتصال:** `ssh -i ~/.ssh/pharmasky-github-deploy root@129.212.140.152`
3. **شغل الإعداد مرة تانية:** `./setup_ssh.sh`
