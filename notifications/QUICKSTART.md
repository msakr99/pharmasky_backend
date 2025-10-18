# 🚀 Quickstart - Push Notifications في 5 دقائق

## الخطوة 1: التثبيت (دقيقة واحدة)

```bash
# Backend
cd sky
pip install pyfcm

# Frontend
cd pharmacy-app
npm install firebase
```

---

## الخطوة 2: الإعداد (دقيقتان)

### احصل على المفاتيح من Firebase Console

1. افتح: https://console.firebase.google.com/
2. اختر مشروع `pharmasky46`
3. اذهب إلى **⚙️ Project Settings**

**للـ Backend:**
- تبويب **Cloud Messaging** > انسخ **Server key**

**للـ Frontend:**
- تبويب **Cloud Messaging** > قسم **Web Push certificates** > اضغط **Generate key pair**

---

### أضف المفاتيح

**في Django (`sky/project/settings/base.py`):**

```python
# أضف في آخر الملف
FCM_SERVER_KEY = "AAAAxxxxxxx:APA91bHxxxxxxxxxx..."
```

**في Next.js (`pharmacy-app/app/lib/firebase.ts`):**

```typescript
// استبدل السطر 44
export const VAPID_KEY = "BN8xQ_xxxxxxxxxxxxxxxxxxxxxxxxxx";
```

**في `.env.local`:**

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## الخطوة 3: Migrations (30 ثانية)

```bash
cd sky
python manage.py makemigrations notifications
python manage.py migrate
```

---

## الخطوة 4: التشغيل (30 ثانية)

```bash
# Backend
cd sky
python manage.py runserver

# Frontend (نافذة جديدة)
cd pharmacy-app
npm run dev
```

---

## الخطوة 5: الاختبار (دقيقة واحدة)

### من المتصفح:

1. افتح: http://localhost:3000
2. سجل الدخول
3. اضغط "تفعيل الإشعارات"
4. وافق على الإذن

### من Terminal:

```bash
cd sky
python manage.py test_fcm --test
```

✅ **يجب أن يصل الإشعار في المتصفح الآن!**

---

## 🎉 تهانينا!

النظام يعمل الآن. لإرسال إشعار من الكود:

```python
from notifications.utils import send_push_to_user

send_push_to_user(
    user_id=1,
    title="مرحبًا!",
    message="هذا أول إشعار لك 🎊"
)
```

---

## ❓ مشاكل شائعة

### الإشعار لا يصل؟

```bash
# تحقق من وجود tokens
python manage.py test_fcm --list-tokens

# إذا كانت فارغة، فعّل الإشعارات من المتصفح أولاً
```

### خطأ "FCM service not available"?

```bash
pip install pyfcm
# ثم تأكد من إضافة FCM_SERVER_KEY في settings.py
```

---

## 📚 المزيد

- **دليل كامل:** `FCM_SETUP_GUIDE.md`
- **أمثلة:** `FCM_EXAMPLE_USAGE.py`
- **README:** `PUSH_NOTIFICATIONS_README.md`

**تمت بنجاح! 🚀**

