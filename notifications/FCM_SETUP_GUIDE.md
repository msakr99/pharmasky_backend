# دليل إعداد Push Notifications مع Firebase Cloud Messaging (FCM)

## 📋 المحتويات
1. [متطلبات التثبيت](#متطلبات-التثبيت)
2. [إعداد Firebase Console](#إعداد-firebase-console)
3. [إعداد Django Backend](#إعداد-django-backend)
4. [إعداد Next.js Frontend](#إعداد-nextjs-frontend)
5. [اختبار النظام](#اختبار-النظام)
6. [أمثلة الاستخدام](#أمثلة-الاستخدام)

---

## 🔧 متطلبات التثبيت

### Django Backend

```bash
# تثبيت Firebase Admin SDK (موجود بالفعل في requirements.txt ✅)
pip install firebase-admin

# أو
pip install -r requirements.txt
```

**ملاحظة:** `firebase-admin` موجود بالفعل في المشروع! ✅

### Next.js Frontend

```bash
# تثبيت Firebase SDK
npm install firebase
# أو
yarn add firebase
```

---

## 🔥 إعداد Firebase Console

### الخطوة 1: إنشاء مشروع Firebase (إذا لم يكن موجودًا)
1. اذهب إلى [Firebase Console](https://console.firebase.google.com/)
2. اضغط على "Add project" أو اختر مشروعك الموجود `pharmasky46`

### الخطوة 2: إضافة تطبيق Web
1. في Project Overview، اضغط على "Add app"
2. اختر "Web" (أيقونة `</>`)
3. سمِّ التطبيق (مثل: "Pharmacy Web App")
4. اضغط "Register app"
5. انسخ `firebaseConfig` - ستحتاجه في Next.js

### الخطوة 3: تفعيل Cloud Messaging
1. اذهب إلى **Project Settings** (الترس ⚙️)
2. اختر تبويب **Cloud Messaging**
3. انسخ **Server key** - ستحتاجه في Django

### الخطوة 4: إنشاء VAPID Key
1. في نفس صفحة **Cloud Messaging**
2. ابحث عن قسم **Web Push certificates**
3. اضغط على **Generate key pair**
4. انسخ **Key pair** - ستحتاجه في Next.js

---

## ⚙️ إعداد Django Backend

### الخطوة 1: إضافة FCM Server Key في Settings

افتح `project/settings/base.py` أو `project/settings.py` وأضف:

```python
# ═══════════════════════════════════════════════════════════════════
# Firebase Cloud Messaging (FCM) Configuration
# ═══════════════════════════════════════════════════════════════════
# احصل على Server Key من Firebase Console > Project Settings > Cloud Messaging
FCM_SERVER_KEY = "AAAAxxxxxxx:APA91bHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**⚠️ مهم جدًا:** لا ترفع المفتاح على GitHub!

### الخطوة 2: عمل Migrations

```bash
python manage.py makemigrations notifications
python manage.py migrate
```

### الخطوة 3: إضافة المسارات

تأكد من إضافة مسارات notifications في `project/urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... المسارات الأخرى
    path("api/notifications/", include("notifications.urls")),
]
```

---

## 🌐 إعداد Next.js Frontend

### الخطوة 1: إضافة Firebase Config

الملف موجود بالفعل في: `pharmacy-app/app/lib/firebase.ts`

**استبدل VAPID_KEY:**

```typescript
// في pharmacy-app/app/lib/firebase.ts
export const VAPID_KEY = "YOUR_VAPID_KEY_HERE"; // ضع الـ Key pair هنا
```

### الخطوة 2: إضافة NEXT_PUBLIC_API_URL

في ملف `.env.local` (أو `.env`):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### الخطوة 3: تحديث next.config.js

تأكد من السماح بـ Service Workers:

```javascript
// pharmacy-app/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // ... الإعدادات الأخرى
  
  // السماح بـ Service Workers
  async headers() {
    return [
      {
        source: '/firebase-messaging-sw.js',
        headers: [
          {
            key: 'Service-Worker-Allowed',
            value: '/',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
```

### الخطوة 4: استخدام المكون في التطبيق

في `pharmacy-app/app/layout.tsx` أو صفحة معينة:

```tsx
import { NotificationSetup } from "./components/NotificationSetup";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        {children}
        
        {/* طلب إذن الإشعارات تلقائيًا */}
        <NotificationSetup autoRequest={false} showButton={true} />
      </body>
    </html>
  );
}
```

---

## 🧪 اختبار النظام

### 1. اختبار من Django Shell

```bash
python manage.py shell
```

```python
# استيراد الدالة
from notifications.utils import test_push_notification

# إرسال إشعار تجريبي
result = test_push_notification(user_id=1)
print(result)

# أو إرسال إشعار مخصص
from notifications.utils import send_push_to_user

result = send_push_to_user(
    user_id=1,
    title="طلب جديد",
    message="تم استلام طلبك بنجاح!",
    data={"order_id": 123, "type": "new_order"}
)
print(result)
```

### 2. اختبار من Django Admin

1. افتح Django Admin: http://localhost:8000/admin/
2. اذهب إلى **Notifications** > **FCM Tokens**
3. تأكد من وجود tokens مسجلة للمستخدمين

### 3. اختبار من Frontend

1. افتح التطبيق في المتصفح
2. سجل الدخول
3. اضغط على زر "تفعيل الإشعارات"
4. وافق على طلب الإذن
5. افتح Console في المتصفح للتأكد من عدم وجود أخطاء

---

## 📖 أمثلة الاستخدام

### مثال 1: إرسال إشعار عند إنشاء طلب جديد

```python
# في views.py أو signals.py
from notifications.utils import send_notification_with_push

def create_order(request):
    # ... إنشاء الطلب
    order = Order.objects.create(...)
    
    # إرسال إشعار للمستخدم
    send_notification_with_push(
        user_id=order.user.id,
        title="طلب جديد",
        message=f"تم استلام طلبك رقم {order.id} بنجاح!",
        extra={
            "order_id": order.id,
            "type": "new_order",
            "url": f"/orders/{order.id}"
        }
    )
    
    return Response({"success": True})
```

### مثال 2: إرسال إشعار لعدة مستخدمين

```python
from notifications.utils import send_push_notification

# إرسال إشعار لجميع الصيادلة
pharmacist_ids = User.objects.filter(role="pharmacist").values_list("id", flat=True)

result = send_push_notification(
    title="عرض جديد",
    message="عرض خاص على الأدوية - خصم 20%",
    user_ids=list(pharmacist_ids),
    data={"type": "offer", "discount": 20}
)

print(f"تم الإرسال بنجاح: {result['success']}")
print(f"فشل: {result['failure']}")
```

### مثال 3: إرسال إشعار لجميع المستخدمين

```python
from notifications.utils import send_push_to_all_users

result = send_push_to_all_users(
    title="إعلان مهم",
    message="سيتم إيقاف الخدمة للصيانة يوم الجمعة من 12 ص إلى 6 ص",
    data={"type": "maintenance"}
)
```

### مثال 4: استخدام في Celery Task (للإرسال المُجدول)

```python
# في tasks.py
from celery import shared_task
from notifications.utils import send_push_notification

@shared_task
def send_payment_reminder(user_id):
    """إرسال تذكير بالدفع"""
    send_push_notification(
        title="تذكير بالدفع",
        message="لديك فاتورة مستحقة الدفع",
        user_ids=[user_id],
        data={"type": "payment_reminder"}
    )
```

---

## 🔍 استكشاف الأخطاء (Troubleshooting)

### 1. الإشعارات لا تصل

**السبب المحتمل:**
- FCM Server Key غير صحيح
- VAPID Key غير صحيح
- Service Worker لا يعمل

**الحل:**
```bash
# تحقق من Console في المتصفح
# تحقق من Django logs
python manage.py runserver --verbosity 3

# تحقق من تسجيل Service Worker
# افتح DevTools > Application > Service Workers
```

### 2. خطأ "FCM service not available"

**السبب:** لم يتم تثبيت pyfcm أو لم يتم إضافة FCM_SERVER_KEY

**الحل:**
```bash
pip install pyfcm
# ثم أضف FCM_SERVER_KEY في settings.py
```

### 3. خطأ "Notification permission denied"

**السبب:** المستخدم رفض إذن الإشعارات

**الحل:**
```
1. اطلب من المستخدم السماح بالإشعارات من إعدادات المتصفح
2. Chrome: Settings > Privacy and security > Site Settings > Notifications
3. قم بإزالة الموقع من "Blocked" وأضفه في "Allowed"
```

### 4. Service Worker لا يتم تسجيله

**السبب:** الملف `firebase-messaging-sw.js` ليس في المكان الصحيح

**الحل:**
```
تأكد أن الملف موجود في: pharmacy-app/public/firebase-messaging-sw.js
```

---

## 📊 مراقبة الإشعارات

### من Django Admin

1. اذهب إلى **Notifications** > **FCM Tokens**
2. راقب `last_used` للتأكد من إرسال الإشعارات
3. تحقق من `is_active` للتأكد من صلاحية الـ tokens

### من Firebase Console

1. اذهب إلى **Cloud Messaging** في Firebase Console
2. راقب إحصائيات الإرسال والاستقبال

---

## 🔒 ملاحظات الأمان

1. **لا ترفع المفاتيح على GitHub:**
   ```bash
   # أضف في .gitignore
   .env
   .env.local
   ```

2. **استخدم Environment Variables:**
   ```python
   # في settings.py
   import os
   FCM_SERVER_KEY = os.environ.get("FCM_SERVER_KEY")
   ```

3. **HTTPS في Production:**
   - Service Workers تعمل فقط على HTTPS (أو localhost)
   - تأكد من استخدام HTTPS في الإنتاج

---

## 📚 مراجع مفيدة

- [Firebase Documentation](https://firebase.google.com/docs/cloud-messaging)
- [pyfcm Documentation](https://github.com/olucurious/PyFCM)
- [Web Push Notifications](https://web.dev/notifications/)
- [Service Workers Guide](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)

---

## ✅ Checklist

- [ ] تثبيت pyfcm في Django
- [ ] إضافة FCM_SERVER_KEY في Django settings
- [ ] عمل migrations للموديل FCMToken
- [ ] إضافة VAPID_KEY في firebase.ts
- [ ] إضافة NEXT_PUBLIC_API_URL في .env
- [ ] تسجيل Service Worker في المتصفح
- [ ] اختبار إرسال إشعار من Django shell
- [ ] اختبار استقبال إشعار في المتصفح
- [ ] اختبار الإشعارات عند إغلاق التطبيق

---

**تم إعداد الدليل بواسطة نظام PharmaSkY للإشعارات 🚀**

