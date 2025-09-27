# 🚀 PharmasSky Auto Deployment Scripts

## 📁 الملفات المتوفرة:

### 1. `setup_deployment.sh` - إعداد أولي
**الاستخدام:** مرة واحدة فقط لإعداد المعلومات الأساسية
```bash
./setup_deployment.sh
```

### 2. `update_and_deploy.sh` - تحديث كامل
**الاستخدام:** تحديث شامل مع تفاصيل وإختبارات
```bash
./update_and_deploy.sh
```

### 3. `quick_update.sh` - تحديث سريع
**الاستخدام:** تحديث سريع بدون تفاصيل
```bash
./quick_update.sh
```

## 🔧 الإعداد الأولي:

### 1. على Windows (محلياً):
```bash
# في Git Bash أو WSL
./setup_deployment.sh
```

### 2. المعلومات المطلوبة:
- عنوان IP الخاص بالـ Droplet
- اسم المستخدم (عادة root)
- مسار المشروع في الـ Droplet (عادة /opt/pharmasky)

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

### للتحديث السريع:
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
./setup_deployment.sh

# بعد تعديل الكود
./quick_update.sh

# انتهى! التطبيق محدث على الـ Droplet 🎉
```
