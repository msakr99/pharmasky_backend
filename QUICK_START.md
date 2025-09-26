# ⚡ التشغيل السريع - PharmasSky Backend

## 🎯 الآن لديك دروبليت جديدة IP: `129.212.140.152`

---

## 🚀 الطريقة الأسرع - أمر واحد فقط!

### 1. اذهب إلى DigitalOcean Console:
```
https://cloud.digitalocean.com/
```

### 2. اختر الدروبليت الجديدة → انقر Console

### 3. تسجيل الدخول بـ root + كلمة المرور

### 4. شغّل الأمر التالي:
```bash
curl -o complete_setup.sh https://raw.githubusercontent.com/msakr99/pharmasky_backend/main/complete_setup.sh && chmod +x complete_setup.sh && ./complete_setup.sh
```

**هذا الأمر سيقوم بـ:**
- ✅ إعداد SSH key
- ✅ تثبيت Docker & Docker Compose  
- ✅ استنساخ المشروع من GitHub
- ✅ تشغيل التطبيق
- ✅ إعداد قاعدة البيانات
- ✅ فحص صحة التطبيق

---

## ⏰ بعد انتهاء الأمر (5-10 دقائق):

### إنشاء مدير النظام:
```bash
cd /opt/pharmasky
docker-compose exec web python manage.py createsuperuser
```

### فحص التطبيق:
- **التطبيق:** http://129.212.140.152
- **الإدارة:** http://129.212.140.152/admin/
- **الصحة:** http://129.212.140.152/health/

---

## 🔐 إعداد GitHub Secrets للنشر التلقائي:

### 1. اذهب إلى:
```
https://github.com/msakr99/pharmasky_backend/settings/secrets/actions
```

### 2. أضف Secrets:
- **DROPLET_IP:** `129.212.140.152`
- **DROPLET_SSH_KEY:** (المفتاح من ملف `pharmasky_deploy_key`)

### 3. أو افتح ملف `github_secrets_copy.html` في المتصفح لنسخ البيانات بسهولة

---

## 🛠️ أوامر مفيدة:

```bash
# فحص حالة الخدمات
docker-compose ps

# عرض السجلات  
docker-compose logs -f web

# إعادة التشغيل
docker-compose restart

# استخدام الأوامر السريعة
./quick_commands.sh status
./quick_commands.sh health
```

---

## 📱 اختبار النشر التلقائي:

بعد إعداد GitHub Secrets، قم بأي تغيير في الكود و push إلى main branch - سيتم النشر تلقائياً!

---

## 🚨 في حالة المشاكل:

### إذا فشل الأمر الأول:
راجع ملف `SETUP_NEW_DROPLET.md` للخطوات التفصيلية

### إذا لم يعمل التطبيق:
```bash
cd /opt/pharmasky
docker-compose logs
docker-compose restart
```

---

**🎉 بعد 10 دقائق ستكون لديك تطبيق يعمل كاملاً مع نشر تلقائي من GitHub!**
