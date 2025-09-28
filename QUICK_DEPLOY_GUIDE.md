# 🚀 دليل النشر السريع لـ PharmasSky

## للبدء السريع:

### 1. إعداد أولي (مرة واحدة):
```bash
./setup_ssh.sh
./setup_deployment.sh
```

### 2. النشر اليومي:
```bash
./auto_deploy.sh
```

**أو مع رسالة commit:**
```bash
./auto_deploy.sh "إضافة ميزة جديدة للمنتجات"
```

## الـ Scripts المتاحة:

| Script | الوصف | متى تستخدمه |
|--------|-------|------------|
| `auto_deploy.sh` ⭐ | النشر الذكي السريع | **الاستخدام اليومي** |
| `setup_ssh.sh` | إعداد SSH key | مرة واحدة فقط |
| `setup_deployment.sh` | التحقق من الإعدادات | مرة واحدة فقط |
| `quick_update.sh` | تحديث بسيط | بديل سريع |
| `update_and_deploy.sh` | تحديث مفصل | عند الحاجة لتفاصيل |

## معلومات السيرفر:
- **IP:** 129.212.140.152
- **المستخدم:** root
- **SSH Key:** ~/.ssh/pharmasky-github-deploy
- **مسار المشروع:** /opt/pharmasky

## لو عندك مشاكل:

### مشكلة SSH:
```bash
./setup_ssh.sh
```

### اختبار الاتصال:
```bash
ssh -i ~/.ssh/pharmasky-github-deploy root@129.212.140.152
```

### إعادة تشغيل يدوي:
```bash
ssh -i ~/.ssh/pharmasky-github-deploy root@129.212.140.152
cd /opt/pharmasky
git pull origin main
docker-compose restart
```

---
**💡 نصيحة:** استخدم `./auto_deploy.sh` دائماً للنشر اليومي - هو الأسرع والأذكى!
