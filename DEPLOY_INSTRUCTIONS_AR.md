# 🚀 تعليمات التطبيق على السيرفر

## ✅ تم رفع التحديثات على Git بنجاح!

الآن اتبع هذه الخطوات على السيرفر:

---

## 📋 الطريقة الأولى: استخدام السكريبت الجاهز (أسهل)

### 1. اتصل بالسيرفر
```bash
ssh root@pharmasky-server
```

### 2. انتقل لمجلد المشروع
```bash
cd /opt/pharmasky
```

### 3. اسحب التحديثات
```bash
git pull origin main
```

### 4. شغل السكريبت
```bash
chmod +x deploy_fixes.sh
bash deploy_fixes.sh
```

✅ السكريبت هيعمل كل حاجة تلقائياً!

---

## 📋 الطريقة الثانية: خطوة بخطوة (يدوي)

إذا فضلت تنفذ الأوامر بنفسك:

### 1️⃣ اتصل بالسيرفر
```bash
ssh root@pharmasky-server
```

### 2️⃣ انتقل لمجلد المشروع
```bash
cd /opt/pharmasky
```

### 3️⃣ إصلاح صلاحيات Migrations
```bash
sudo chown -R 1000:1000 ./market/migrations ./core/migrations
sudo chmod -R 775 ./*/migrations
```

### 4️⃣ اسحب آخر تحديثات
```bash
git pull origin main
```

### 5️⃣ أوقف الحاويات
```bash
docker-compose down
```

### 6️⃣ أعد بناء وتشغيل الحاويات
```bash
docker-compose up -d --build
```

### 7️⃣ انتظر قليلاً (10 ثواني)
```bash
sleep 10
```

### 8️⃣ شغل Migrations
```bash
docker exec -i pharmasky_web python manage.py migrate --noinput
```

### 9️⃣ اجمع الملفات الثابتة
```bash
docker exec -i pharmasky_web python manage.py collectstatic --noinput
```

### 🔟 تحقق من حالة الحاويات
```bash
docker-compose ps
```

---

## ✅ التحقق من نجاح التطبيق

### 1. تحقق من السجلات
```bash
docker logs pharmasky_web --tail 50
```

**يجب أن ترى:**
- ✅ لا توجد أخطاء permission
- ✅ "Migrations completed"
- ✅ الخدمة تعمل بدون مشاكل

### 2. اختبر الـ endpoints
```bash
# اختبر الصفحة الرئيسية
curl http://localhost:8000/

# اختبر robots.txt (الجديد)
curl http://localhost:8000/robots.txt
```

### 3. راقب المحاولات المشبوهة
```bash
# شوف لو في محاولات اختراق اتحظرت
docker logs pharmasky_web | grep -E "Blocked|suspicious"
```

---

## 🎯 النتائج المتوقعة

### ✅ قبل التطبيق (المشاكل):
```
❌ PermissionError: [Errno 13] Permission denied
❌ DisallowedHost: Invalid HTTP_HOST header
❌ Not Found: /robots.txt
❌ محاولات اختراق تزعج السجلات
```

### ✅ بعد التطبيق (الحل):
```
✅ Migrations تعمل بدون مشاكل
✅ محاولات الاختراق تُحظر بهدوء
✅ robots.txt متاح
✅ السجلات نظيفة ومرتبة
```

---

## 🔍 مراقبة مستمرة

### سجلات مباشرة (Live)
```bash
docker logs pharmasky_web -f --tail 100
```

### حالة الخدمات
```bash
docker-compose ps
docker stats pharmasky_web
```

### البحث عن أخطاء
```bash
docker logs pharmasky_web | grep ERROR | tail -20
```

---

## 🆘 إذا حدثت مشكلة

### 1. الحاوية مش شغالة
```bash
docker-compose up -d
docker logs pharmasky_web --tail 50
```

### 2. خطأ في الاتصال بقاعدة البيانات
```bash
docker-compose restart pharmasky_db
sleep 5
docker-compose restart pharmasky_web
```

### 3. لسه في مشكلة permissions
```bash
cd /opt/pharmasky
sudo chown -R 1000:1000 .
sudo chmod -R 755 .
docker-compose restart
```

### 4. إعادة البناء من الصفر
```bash
docker-compose down -v
docker-compose up -d --build
docker exec -i pharmasky_web python manage.py migrate
```

---

## 📞 تواصل معي

إذا واجهت أي مشكلة:
1. أرسل لي ناتج الأمر:
   ```bash
   docker logs pharmasky_web --tail 100
   ```

2. أو أرسل حالة الحاويات:
   ```bash
   docker-compose ps
   ```

---

**جاهز؟ يلا ابدأ! 🚀**

كل اللي عليك:
```bash
ssh root@pharmasky-server
cd /opt/pharmasky
git pull origin main
bash deploy_fixes.sh
```

وخلاص! 🎉

