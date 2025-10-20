# 🚀 ابدأ تجربة الإشعارات من هنا!

## الخطوة 1: تشغيل السيرفر

افتح نافذة Terminal/CMD جديدة وشغل السيرفر:

```bash
# تفعيل البيئة الافتراضية
venv\Scripts\activate

# تشغيل السيرفر
python manage.py runserver
```

✅ السيرفر سيعمل على: **http://127.0.0.1:8000**

اترك هذه النافذة مفتوحة!

---

## الخطوة 2: إنشاء بيانات تجريبية

افتح نافذة Terminal/CMD **جديدة** وشغل:

### الطريقة الأسهل: استخدم الملف الدفعي (Windows)

```bash
test_notifications.bat
```

ثم اختر رقم **2** أو **3** لإنشاء بيانات تجريبية

### أو استخدم الأمر مباشرة:

```bash
# تفعيل البيئة الافتراضية أولاً
venv\Scripts\activate

# إنشاء 20 إشعار تجريبي مع مواضيع
python manage.py create_test_notifications --with-topics --count 20 --mark-some-read
```

---

## الخطوة 3: تجربة الإشعارات

### الطريقة 1: السكريبت التفاعلي (الأسهل) ⭐

```bash
python test_notifications.py
```

سيطلب منك:
1. اختيار طريقة المصادقة (Username/Password أو Token)
2. ثم يعرض لك قائمة بجميع العمليات المتاحة

### الطريقة 2: اختبار سريع

```bash
# استخدم Username وPassword
python quick_test_notifications.py --username admin --password admin

# أو استخدم Token مباشرة
python quick_test_notifications.py --token YOUR_TOKEN_HERE
```

### الطريقة 3: استخدام Postman/Insomnia

1. أولاً احصل على Token:
   ```http
   POST http://127.0.0.1:8000/api/v1/accounts/login/
   Content-Type: application/json
   
   {
       "username": "admin",
       "password": "admin"
   }
   ```

2. استخدم Token في جميع الطلبات:
   ```
   Authorization: Token YOUR_TOKEN
   ```

3. جرب الـ Endpoints:
   - `GET /api/v1/notifications/notifications/` - جميع الإشعارات
   - `GET /api/v1/notifications/notifications/unread/` - غير المقروءة
   - `GET /api/v1/notifications/notifications/stats/` - الإحصائيات

---

## 🎯 أمثلة سريعة

### جلب الإحصائيات

```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://127.0.0.1:8000/api/v1/notifications/notifications/stats/
```

### جلب الإشعارات غير المقروءة

```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://127.0.0.1:8000/api/v1/notifications/notifications/unread/
```

### تحديد إشعار كمقروء

```bash
curl -X PATCH \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"is_read": true}' \
     http://127.0.0.1:8000/api/v1/notifications/notifications/123/update/
```

---

## 📝 ملاحظات مهمة

### إذا كنت لا تعرف Username/Password:

1. أنشئ مستخدم admin جديد:
   ```bash
   python manage.py createsuperuser
   ```

2. أو تحقق من المستخدمين الموجودين:
   ```bash
   python manage.py shell
   ```
   ثم:
   ```python
   from django.contrib.auth import get_user_model
   User = get_user_model()
   
   # عرض جميع المستخدمين
   for user in User.objects.all()[:5]:
       print(f"{user.username} - {user.name or 'No Name'}")
   ```

### إذا واجهت خطأ "Connection refused":

تأكد من أن السيرفر يعمل في نافذة أخرى:
```bash
python manage.py runserver
```

---

## 📚 ملفات مساعدة

- **test_notifications.py** - سكريبت تفاعلي كامل
- **quick_test_notifications.py** - اختبار سريع بدون تفاعل
- **test_notifications.bat** - ملف دفعي للويندوز
- **TEST_NOTIFICATIONS_README.md** - دليل كامل للاختبار
- **PHARMACY_FRONTEND_API.md** - توثيق API الكامل

---

## 🎊 جاهز للبدء؟

1. ✅ شغل السيرفر
2. ✅ أنشئ بيانات تجريبية
3. ✅ شغل السكريبت التفاعلي
4. ✅ استمتع بالتجربة!

```bash
# كل شيء في أمر واحد (في نافذة جديدة بعد تشغيل السيرفر):
python manage.py create_test_notifications --with-topics --count 20 && python test_notifications.py
```

---

**بالتوفيق! 🚀**

