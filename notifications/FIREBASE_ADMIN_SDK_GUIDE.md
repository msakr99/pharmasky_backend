# 🔥 دليل استخدام Firebase Admin SDK للـ Push Notifications

## نظرة عامة

تم تحديث النظام لاستخدام **Firebase Admin SDK** - الطريقة الرسمية والموصى بها من Google لإرسال Push Notifications من Server-side.

---

## ✅ المزايا

### Firebase Admin SDK vs pyfcm

| الميزة | Firebase Admin SDK | pyfcm |
|--------|-------------------|-------|
| **رسمي من Google** | ✅ نعم | ❌ مكتبة third-party |
| **الدعم والتحديثات** | ✅ مستمر | ⚠️ محدود |
| **الأمان** | ✅ Service Account | ⚠️ Server Key فقط |
| **الميزات** | ✅ كاملة | ⚠️ محدودة |
| **معالجة الأخطاء** | ✅ متقدمة | ⚠️ بسيطة |

---

## 📦 ما تم تنفيذه

### 1. ملف Service Account

**الموقع:** `sky/credentials/pharmasky46-firebase-adminsdk.json`

```json
{
  "type": "service_account",
  "project_id": "pharmasky46",
  "private_key_id": "...",
  "private_key": "...",
  ...
}
```

**الحماية:** ✅ الملف محمي في `.gitignore`

---

### 2. الإعدادات في Django

**الملف:** `sky/project/settings/base.py`

```python
# Firebase Cloud Messaging (FCM) Configuration
FIREBASE_CREDENTIALS_PATH = os.path.join(
    BASE_DIR, "credentials", "pharmasky46-firebase-adminsdk.json"
)
```

---

### 3. utils.py المُحدّث

**الملف:** `sky/notifications/utils.py`

#### دوال جديدة:

```python
# تهيئة Firebase
initialize_firebase()

# إرسال لمستخدم واحد
send_push_to_user(user_id, title, message, data=None, image_url=None)

# إرسال لعدة مستخدمين
send_push_notification(title, message, user_ids=[], tokens=[], data=None)

# إرسال للجميع
send_push_to_all_users(title, message, data=None, image_url=None)

# إنشاء في DB + إرسال
send_notification_with_push(user_id, title, message, extra=None)

# اختبار
test_push_notification(user_id)
```

---

### 4. معالجة متقدمة للأخطاء

```python
# إلغاء تفعيل الـ tokens غير الصالحة تلقائياً
if error_code in ['invalid-registration-token', 'registration-token-not-registered']:
    FCMToken.objects.filter(token=tokens[idx]).update(is_active=False)
```

---

### 5. إعدادات متقدمة للـ Web

```python
webpush=messaging.WebpushConfig(
    notification=messaging.WebpushNotification(
        title=title,
        body=message,
        icon="/icon.png",
        badge="/icon.png",
        image=image_url,
    ),
    fcm_options=messaging.WebpushFCMOptions(
        link=click_action,  # URL عند النقر
    ),
)
```

---

## 🚀 الاستخدام

### مثال 1: إرسال إشعار بسيط

```python
from notifications.utils import send_push_to_user

result = send_push_to_user(
    user_id=1,
    title="طلب جديد",
    message="تم استلام طلبك بنجاح!"
)

print(f"Success: {result['success']}")
print(f"Failure: {result['failure']}")
```

---

### مثال 2: إرسال مع بيانات إضافية

```python
result = send_push_to_user(
    user_id=1,
    title="فاتورة جديدة",
    message="تم إنشاء فاتورة بمبلغ 1500 جنيه",
    data={
        "invoice_id": "INV-001",
        "amount": "1500.00",
        "url": "/invoices/INV-001"
    }
)
```

---

### مثال 3: إرسال مع صورة

```python
result = send_push_to_user(
    user_id=1,
    title="منتج جديد",
    message="تم إضافة Aspirin 500mg",
    image_url="https://example.com/aspirin.jpg"
)
```

---

### مثال 4: إرسال لعدة مستخدمين

```python
from notifications.utils import send_push_notification

# قائمة المستخدمين
user_ids = [1, 2, 3, 4, 5]

result = send_push_notification(
    title="عرض خاص",
    message="خصم 20% على جميع الأدوية!",
    user_ids=user_ids,
    data={"type": "offer", "discount": "20"}
)
```

---

### مثال 5: إرسال للجميع

```python
from notifications.utils import send_push_to_all_users

result = send_push_to_all_users(
    title="إعلان مهم",
    message="سيتم إيقاف الخدمة للصيانة غدًا"
)
```

---

### مثال 6: إنشاء في قاعدة البيانات + إرسال

```python
from notifications.utils import send_notification_with_push

notification = send_notification_with_push(
    user_id=1,
    title="تحديث الطلب",
    message="طلبك قيد التجهيز",
    extra={
        "order_id": 123,
        "status": "processing"
    }
)

print(f"Notification ID: {notification.id}")
```

---

## 🧪 الاختبار

### من Django Shell

```bash
python manage.py shell
```

```python
from notifications.utils import test_push_notification

# اختبار لمستخدم محدد
result = test_push_notification(user_id=1)
print(result)
```

---

### من Management Command

```bash
# عرض جميع الـ tokens
python manage.py test_fcm --list-tokens

# إرسال إشعار تجريبي
python manage.py test_fcm --test

# إرسال لمستخدم محدد
python manage.py test_fcm --user-id 1
```

---

## 📊 نتائج الإرسال

### بنية الاستجابة

```python
{
    "success": 3,        # عدد الإشعارات الناجحة
    "failure": 1,        # عدد الفاشلة
    "responses": [       # تفاصيل كل token
        {
            "success": True,
            "message_id": "..."
        },
        {
            "success": False,
            "exception": {
                "code": "invalid-registration-token"
            }
        }
    ]
}
```

---

## 🔍 معالجة الأخطاء

### الأخطاء الشائعة وكيفية التعامل معها

#### 1. Token غير صالح

```
Error: invalid-registration-token
```

**الحل:** يتم إلغاء تفعيل التوكن تلقائياً ✅

---

#### 2. Token غير مسجل

```
Error: registration-token-not-registered
```

**الحل:** يتم إلغاء تفعيل التوكن تلقائياً ✅

---

#### 3. Firebase not initialized

```
Error: Firebase Admin SDK not available
```

**الحل:**
```bash
# تأكد من وجود الملف
ls -la sky/credentials/pharmasky46-firebase-adminsdk.json

# تأكد من المسار في settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.FIREBASE_CREDENTIALS_PATH)
```

---

## 🛡️ الأمان

### 1. حماية ملف Service Account

✅ **محمي في `.gitignore`:**
```gitignore
*firebase-adminsdk*.json
```

---

### 2. في Production

**استخدم Environment Variables:**

```python
# في settings.py
FIREBASE_CREDENTIALS_PATH = os.environ.get(
    'FIREBASE_CREDENTIALS_PATH',
    os.path.join(BASE_DIR, "credentials", "pharmasky46-firebase-adminsdk.json")
)
```

**في Server:**
```bash
export FIREBASE_CREDENTIALS_PATH="/path/to/firebase-adminsdk.json"
```

---

### 3. Permissions

```bash
# تأكد من أن الملف للقراءة فقط
chmod 400 sky/credentials/pharmasky46-firebase-adminsdk.json
```

---

## 📈 المراقبة

### من Django Admin

```
http://localhost:8000/admin/notifications/fcmtoken/
```

راقب:
- ✅ عدد الـ tokens النشطة
- 📅 آخر استخدام لكل token
- 📱 أنواع الأجهزة المسجلة

---

### من Firebase Console

```
https://console.firebase.google.com/project/pharmasky46/notification
```

راقب:
- 📊 إحصائيات الإرسال
- ✅ معدل النجاح
- ❌ الأخطاء

---

## ✅ Checklist

بعد التحديث:

- [x] ✅ ملف Service Account موجود في `credentials/`
- [x] ✅ الملف محمي في `.gitignore`
- [x] ✅ FIREBASE_CREDENTIALS_PATH مضاف في settings
- [x] ✅ utils.py محدّث لاستخدام Firebase Admin SDK
- [x] ✅ Migrations منشأة
- [ ] ⏳ تطبيق Migrations: `python manage.py migrate`
- [ ] ⏳ اختبار النظام: `python manage.py test_fcm --test`

---

## 🎯 الخطوات التالية

### 1. تطبيق Migrations

```bash
# تفعيل virtual environment
source venv/bin/activate  # Linux/Mac
# أو
.\venv\Scripts\Activate.ps1  # Windows

# تطبيق migrations
python manage.py migrate notifications
```

---

### 2. اختبار النظام

```bash
python manage.py test_fcm --test
```

---

### 3. استخدام في الكود

```python
from notifications.utils import send_push_to_user

# في أي مكان في views.py أو signals.py
send_push_to_user(
    user_id=user.id,
    title="مرحباً!",
    message="أهلاً بك في النظام"
)
```

---

## 📚 المراجع

- [Firebase Admin SDK Python](https://firebase.google.com/docs/admin/setup)
- [Cloud Messaging Server](https://firebase.google.com/docs/cloud-messaging/server)
- [Error Codes](https://firebase.google.com/docs/cloud-messaging/http-server-ref#error-codes)

---

**تم التحديث إلى Firebase Admin SDK ✅**

**الإصدار:** 2.0.0 (Firebase Admin SDK)  
**التاريخ:** October 2024  
**الحالة:** ✅ جاهز للإنتاج

