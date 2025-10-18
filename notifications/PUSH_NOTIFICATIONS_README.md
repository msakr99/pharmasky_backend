# 🔔 نظام Push Notifications - Firebase Cloud Messaging (FCM)

## نظرة عامة

نظام متكامل لإرسال Push Notifications باستخدام Firebase Cloud Messaging (FCM) في مشروع يستخدم Django كـ Backend و Next.js كـ Frontend.

**الميزات:**
- ✅ إرسال إشعارات حتى لو كان المتصفح مغلقًا (Background Notifications)
- ✅ دعم Web, Android, iOS
- ✅ إدارة FCM Tokens في قاعدة البيانات
- ✅ API endpoints جاهزة في Django
- ✅ React Hooks جاهزة في Next.js
- ✅ Service Worker لاستقبال الإشعارات في الخلفية
- ✅ إرسال إشعارات لمستخدم واحد أو عدة مستخدمين
- ✅ أمثلة عملية وتوثيق كامل

---

## 📁 بنية الملفات

### Backend (Django)
```
sky/notifications/
├── models.py                          # موديل FCMToken
├── serializers.py                     # FCMTokenSerializer
├── views.py                          # SaveFCMTokenAPIView
├── urls.py                           # مسارات API
├── utils.py                          # دوال إرسال الإشعارات
├── admin.py                          # إدارة Django Admin
├── FCM_SETUP_GUIDE.md               # دليل الإعداد الكامل
├── FCM_EXAMPLE_USAGE.py             # أمثلة الاستخدام
├── PUSH_NOTIFICATIONS_README.md     # هذا الملف
└── management/
    └── commands/
        └── test_fcm.py               # أمر اختبار النظام
```

### Frontend (Next.js)
```
pharmacy-app/
├── app/
│   ├── lib/
│   │   └── firebase.ts               # إعداد Firebase
│   ├── hooks/
│   │   └── useNotifications.ts       # React Hook
│   └── components/
│       └── NotificationSetup.tsx     # مكون UI
└── public/
    └── firebase-messaging-sw.js      # Service Worker
```

---

## 🚀 الإعداد السريع

### 1. تثبيت المكتبات

#### Django:
```bash
cd sky
pip install pyfcm
```

#### Next.js:
```bash
cd pharmacy-app
npm install firebase
```

### 2. إعداد Firebase

احصل على هذه القيم من [Firebase Console](https://console.firebase.google.com/):

**للـ Backend (Django):**
- `FCM_SERVER_KEY` من: Project Settings > Cloud Messaging > Server key

**للـ Frontend (Next.js):**
- `firebaseConfig` من: Project Settings > General > Your apps
- `VAPID_KEY` من: Project Settings > Cloud Messaging > Web Push certificates

### 3. إضافة المفاتيح

#### في Django (`sky/project/settings/base.py`):
```python
# FCM Server Key
FCM_SERVER_KEY = "AAAAxxxxxxx:APA91bHxxxxxxxxxx..."
```

#### في Next.js (`pharmacy-app/app/lib/firebase.ts`):
```typescript
// استبدل VAPID_KEY
export const VAPID_KEY = "YOUR_VAPID_KEY_HERE";
```

#### في `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. عمل Migrations

```bash
cd sky
python manage.py makemigrations notifications
python manage.py migrate
```

### 5. تشغيل المشروع

```bash
# Django Backend
cd sky
python manage.py runserver

# Next.js Frontend (نافذة أخرى)
cd pharmacy-app
npm run dev
```

---

## 📖 كيفية الاستخدام

### من Frontend (المستخدم النهائي)

1. افتح المتصفح: http://localhost:3000
2. سجل الدخول
3. اضغط على زر "تفعيل الإشعارات"
4. وافق على طلب الإذن
5. تم! 🎉

### من Backend (المطور)

#### اختبار سريع:

```bash
python manage.py test_fcm --test
```

#### إرسال إشعار لمستخدم:

```python
from notifications.utils import send_push_to_user

result = send_push_to_user(
    user_id=1,
    title="طلب جديد",
    message="تم استلام طلبك بنجاح!",
    data={"order_id": 123}
)
```

#### إرسال لعدة مستخدمين:

```python
from notifications.utils import send_push_notification

result = send_push_notification(
    title="عرض خاص",
    message="خصم 20% اليوم فقط!",
    user_ids=[1, 2, 3, 4, 5]
)
```

#### إرسال لجميع المستخدمين:

```python
from notifications.utils import send_push_to_all_users

result = send_push_to_all_users(
    title="إعلان مهم",
    message="سيتم إيقاف الخدمة للصيانة غدًا"
)
```

---

## 🔧 API Endpoints

### 1. حفظ FCM Token

**POST** `/api/notifications/save-fcm-token/`

```json
{
    "fcm_token": "eLxBu5Z8QoWx...",
    "device_type": "web",
    "device_name": "Chrome on Windows"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "message": "FCM Token saved successfully",
        "device_type": "web",
        "is_active": true
    }
}
```

### 2. عرض Tokens المستخدم

**GET** `/api/notifications/fcm-tokens/`

### 3. حذف Token

**DELETE** `/api/notifications/fcm-tokens/{id}/delete/`

---

## 💡 أمثلة عملية

### مثال 1: إشعار عند إنشاء طلب

```python
# في views.py
from notifications.utils import send_notification_with_push

def create_order(request):
    order = Order.objects.create(...)
    
    send_notification_with_push(
        user_id=order.user.id,
        title="طلب جديد",
        message=f"تم إنشاء طلبك رقم {order.order_number}",
        extra={
            "order_id": order.id,
            "url": f"/orders/{order.id}"
        }
    )
    
    return Response({"success": True})
```

### مثال 2: إشعار مُجدول بـ Celery

```python
# في tasks.py
from celery import shared_task
from notifications.utils import send_push_to_user

@shared_task
def send_payment_reminder(user_id):
    send_push_to_user(
        user_id=user_id,
        title="تذكير بالدفع",
        message="لديك فاتورة مستحقة الدفع"
    )
```

### مثال 3: إشعار من Signal

```python
# في signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.utils import send_push_to_user

@receiver(post_save, sender=Invoice)
def invoice_created(sender, instance, created, **kwargs):
    if created:
        send_push_to_user(
            user_id=instance.user.id,
            title="فاتورة جديدة",
            message=f"تم إنشاء فاتورة بمبلغ {instance.total}"
        )
```

---

## 🧪 الاختبار

### 1. من Terminal:

```bash
# عرض جميع الـ tokens
python manage.py test_fcm --list-tokens

# إرسال إشعار تجريبي
python manage.py test_fcm --test

# إرسال لمستخدم محدد
python manage.py test_fcm --user-id 1
```

### 2. من Django Shell:

```bash
python manage.py shell
```

```python
from notifications.utils import test_push_notification

# اختبار سريع
result = test_push_notification(user_id=1)
print(result)
```

### 3. من Django Admin:

1. افتح: http://localhost:8000/admin/
2. اذهب إلى **Notifications** > **FCM Tokens**
3. راقب الـ tokens المسجلة

---

## 🔍 استكشاف الأخطاء

### ❌ الإشعارات لا تصل

**المشكلة:** FCM Server Key غير صحيح

**الحل:**
```python
# تحقق من settings.py
print(settings.FCM_SERVER_KEY)

# يجب أن يبدأ بـ AAAAxxxx
```

**المشكلة:** Service Worker لا يعمل

**الحل:**
```
1. افتح DevTools > Application > Service Workers
2. تأكد من تسجيل firebase-messaging-sw.js
3. إذا لم يكن مسجلًا، تأكد من وجود الملف في public/
```

### ❌ خطأ "FCM service not available"

**المشكلة:** pyfcm غير مثبت

**الحل:**
```bash
pip install pyfcm
```

### ❌ خطأ "Notification permission denied"

**المشكلة:** المستخدم رفض الإذن

**الحل:**
```
Chrome: Settings > Privacy and security > Site Settings > Notifications
أزل الموقع من "Blocked" وأضفه في "Allowed"
```

---

## 📊 بنية قاعدة البيانات

### موديل FCMToken

```python
class FCMToken(models.Model):
    user = ForeignKey(User)              # المستخدم
    token = TextField(unique=True)        # FCM Token
    device_type = CharField(              # نوع الجهاز
        choices=[("web", "Web"), ("android", "Android"), ("ios", "iOS")]
    )
    device_name = CharField()             # اسم الجهاز
    is_active = BooleanField()            # نشط؟
    created_at = DateTimeField()          # تاريخ الإنشاء
    updated_at = DateTimeField()          # تاريخ التحديث
    last_used = DateTimeField()           # آخر استخدام
```

---

## 🛡️ ملاحظات الأمان

### 1. لا ترفع المفاتيح على GitHub

```bash
# أضف في .gitignore
.env
.env.local
*.key
```

### 2. استخدم Environment Variables

```python
# في settings.py
import os
FCM_SERVER_KEY = os.environ.get("FCM_SERVER_KEY")
```

```bash
# في .env
FCM_SERVER_KEY=AAAAxxxxxxx...
```

### 3. HTTPS في Production

- Service Workers تعمل فقط على HTTPS (أو localhost)
- استخدم SSL certificate في الإنتاج

---

## 📚 دوال مهمة

| الدالة | الوصف |
|--------|-------|
| `send_push_to_user()` | إرسال لمستخدم واحد |
| `send_push_notification()` | إرسال لعدة مستخدمين |
| `send_push_to_all_users()` | إرسال لجميع المستخدمين |
| `send_notification_with_push()` | إنشاء في DB + إرسال Push |
| `test_push_notification()` | اختبار سريع |

---

## 📄 ملفات إضافية

- **`FCM_SETUP_GUIDE.md`**: دليل إعداد مفصل خطوة بخطوة
- **`FCM_EXAMPLE_USAGE.py`**: 10 أمثلة عملية للاستخدام
- **`management/commands/test_fcm.py`**: أمر اختبار من Terminal

---

## 🔗 روابط مفيدة

- [Firebase Console](https://console.firebase.google.com/)
- [Firebase Docs - Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- [pyfcm GitHub](https://github.com/olucurious/PyFCM)
- [Web Push Notifications](https://web.dev/notifications/)

---

## ✅ Checklist

قبل البدء، تأكد من:

- [ ] تثبيت `pyfcm` في Django
- [ ] تثبيت `firebase` في Next.js
- [ ] إضافة `FCM_SERVER_KEY` في Django settings
- [ ] إضافة `VAPID_KEY` في firebase.ts
- [ ] عمل migrations للموديل
- [ ] تسجيل Service Worker
- [ ] اختبار من Django shell
- [ ] اختبار من المتصفح

---

## 🎯 الخطوة التالية

بعد إكمال الإعداد:

1. ✅ سجل الدخول في التطبيق
2. ✅ فعّل الإشعارات من المتصفح
3. ✅ شغل: `python manage.py test_fcm --test`
4. ✅ تحقق من وصول الإشعار في المتصفح
5. 🎉 **النظام يعمل بنجاح!**

---

## 💬 الدعم

إذا واجهت أي مشاكل:

1. تحقق من Console في المتصفح
2. تحقق من Django logs
3. راجع `FCM_SETUP_GUIDE.md`
4. شغل `python manage.py test_fcm --list-tokens`

---

**تم إعداد النظام بواسطة PharmaSkY Team 🚀**

**الإصدار:** 1.0.0
**التاريخ:** 2024
**الحالة:** ✅ جاهز للإنتاج

