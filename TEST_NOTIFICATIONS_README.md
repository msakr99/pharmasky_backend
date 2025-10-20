# 🔔 دليل تجربة نظام الإشعارات

## 🚀 البدء السريع

### 1. تشغيل السيرفر

أولاً، تأكد من تشغيل السيرفر:

```bash
# تفعيل البيئة الافتراضية
venv\Scripts\activate

# تشغيل السيرفر
python manage.py runserver
```

السيرفر سيعمل على: `http://127.0.0.1:8000`

---

### 2. إنشاء بيانات تجريبية

قبل اختبار الإشعارات، أنشئ بيانات تجريبية:

```bash
# إنشاء 10 إشعارات تجريبية لجميع المستخدمين
python manage.py create_test_notifications

# إنشاء 20 إشعار لمستخدم محدد
python manage.py create_test_notifications --users +201234567890 --count 20

# إنشاء إشعارات مع مواضيع
python manage.py create_test_notifications --with-topics --count 15

# إنشاء إشعارات وتحديد بعضها كمقروء
python manage.py create_test_notifications --mark-some-read --count 30
```

---

### 3. اختبار الإشعارات

#### طريقة 1: استخدام السكريبت التفاعلي

```bash
python test_notifications.py
```

ثم اتبع التعليمات على الشاشة:
- اختر طريقة المصادقة (Username/Password أو Token)
- اختر العملية التي تريد تجربتها من القائمة

#### طريقة 2: استخدام Django Shell

```bash
python manage.py shell
```

ثم:

```python
from django.contrib.auth import get_user_model
from notifications.management.commands.create_test_notifications import create_test_notifications_for_user

User = get_user_model()

# جلب مستخدم
user = User.objects.first()

# إنشاء 10 إشعارات تجريبية
create_test_notifications_for_user(user, count=10)

# عرض الإشعارات
from notifications.models import Notification
notifs = Notification.objects.filter(user=user)
for n in notifs:
    print(f"{n.id}: {n.title} - {'مقروء' if n.is_read else 'غير مقروء'}")
```

---

## 📱 واجهات API المتاحة

### 1. جلب الإشعارات

```bash
# جميع الإشعارات
GET http://127.0.0.1:8000/api/v1/notifications/notifications/

# غير المقروءة فقط
GET http://127.0.0.1:8000/api/v1/notifications/notifications/unread/

# الإحصائيات
GET http://127.0.0.1:8000/api/v1/notifications/notifications/stats/
```

### 2. تحديد كمقروء

```bash
# إشعار واحد
PATCH http://127.0.0.1:8000/api/v1/notifications/notifications/{id}/update/
Body: {"is_read": true}

# جميع الإشعارات
POST http://127.0.0.1:8000/api/v1/notifications/notifications/mark-all-read/
```

### 3. حذف إشعار

```bash
DELETE http://127.0.0.1:8000/api/v1/notifications/notifications/{id}/delete/
```

### 4. المواضيع والاشتراكات

```bash
# جلب المواضيع مع حالة الاشتراك
GET http://127.0.0.1:8000/api/v1/notifications/topics/my-topics/

# الاشتراك في موضوع
POST http://127.0.0.1:8000/api/v1/notifications/subscriptions/create/
Body: {"topic": 1, "is_active": true}
```

---

## 🧪 اختبارات Postman

### 1. الحصول على Token

```http
POST http://127.0.0.1:8000/api/v1/accounts/login/
Content-Type: application/json

{
    "username": "+201234567890",
    "password": "your_password"
}
```

استجابة:
```json
{
    "success": true,
    "data": {
        "token": "abc123...",
        "user": { ... }
    }
}
```

### 2. استخدام Token في جميع الطلبات

أضف هذا Header لجميع الطلبات:
```
Authorization: Token abc123...
```

### 3. مثال كامل - جلب الإشعارات

```http
GET http://127.0.0.1:8000/api/v1/notifications/notifications/
Authorization: Token abc123...
```

---

## 🎯 سيناريوهات الاختبار

### السيناريو 1: تجربة أساسية

1. ✅ تسجيل الدخول
2. ✅ جلب جميع الإشعارات
3. ✅ عرض الإحصائيات
4. ✅ تحديد إشعار كمقروء
5. ✅ حذف إشعار

### السيناريو 2: المواضيع والاشتراكات

1. ✅ عرض جميع المواضيع
2. ✅ الاشتراك في موضوع
3. ✅ عرض الإشعارات الخاصة بالموضوع
4. ✅ إلغاء الاشتراك

### السيناريو 3: اختبار الأداء

1. ✅ إنشاء 100 إشعار
2. ✅ جلب الإشعارات مع pagination
3. ✅ تحديد الكل كمقروء
4. ✅ قياس وقت الاستجابة

---

## 🐛 استكشاف الأخطاء

### خطأ: Connection refused

**الحل:** تأكد من تشغيل السيرفر:
```bash
python manage.py runserver
```

### خطأ: Authentication failed

**الحل:** تأكد من:
1. صحة Username/Password
2. أن المستخدم موجود في قاعدة البيانات
3. أن الـ Token صحيح

### خطأ: لا توجد إشعارات

**الحل:** أنشئ بيانات تجريبية:
```bash
python manage.py create_test_notifications
```

---

## 📊 أنواع الإشعارات المتاحة

| النوع | الوصف | Extra Type |
|------|-------|-----------|
| 🛒 | طلب جديد | `sale_invoice` |
| ✅ | تحديث الطلب | `invoice_status_update` |
| 💰 | دفعة مسجلة | `sale_payment` |
| ⏰ | تذكير دفع | `payment_due_reminder` |
| ⚠️ | تأخير دفع | `payment_overdue` |
| ✨ | منتج متوفر | `wishlist_product_available` |
| 🎁 | عرض خاص | `special_offer` |
| 🟢 | نظام متاح | `shift_started` |
| 🔴 | نظام مغلق | `shift_closed` |
| ↩️ | مرتجع | `sale_return` |
| ✅ | موافقة مرتجع | `return_approved` |

---

## 💡 نصائح

1. **استخدم السكريبت التفاعلي** للاختبار السريع
2. **أنشئ بيانات تجريبية** باستخدام Management Command
3. **استخدم Postman** لاختبار API بشكل أكثر تفصيلاً
4. **راجع ملف `PHARMACY_FRONTEND_API.md`** للتوثيق الكامل

---

## 📚 ملفات التوثيق الأخرى

- `PHARMACY_FRONTEND_API.md` - توثيق API كامل للصيدليات
- `ADMIN_FRONTEND_API.md` - توثيق API للمشرفين
- `FCM_SETUP_GUIDE.md` - إعداد Push Notifications
- `COMPLETE_GUIDE.md` - دليل شامل لنظام الإشعارات

---

## 🤝 الدعم

إذا واجهت أي مشاكل:
1. تحقق من أن السيرفر يعمل
2. تحقق من الـ logs في Console
3. راجع ملفات التوثيق
4. استخدم Django Shell للتشخيص

---

**تم إعداده بواسطة فريق PharmaSky 🚀**

