# 🔔 Notifications App - تطبيق الإشعارات

نظام إشعارات متكامل لمشروع Pharmasky يوفر إرسال وإدارة الإشعارات للمستخدمين.

## 📋 جدول المحتويات

- [المميزات](#المميزات)
- [بنية التطبيق](#بنية-التطبيق)
- [الموديلات](#الموديلات)
- [API Endpoints](#api-endpoints)
- [أمثلة الاستخدام](#أمثلة-الاستخدام)
- [Celery Tasks](#celery-tasks)
- [الصلاحيات](#الصلاحيات)
- [الاختبارات](#الاختبارات)

---

## 🎯 المميزات

### ✅ الميزات الأساسية
- ✨ إرسال إشعارات فردية لمستخدم محدد
- 📢 إرسال إشعارات جماعية لعدة مستخدمين
- 🏷️ نظام المواضيع (Topics) للتصنيف
- 🔔 الاشتراك/إلغاء الاشتراك في المواضيع
- 📊 إحصائيات الإشعارات
- ✅ تحديد حالة القراءة (مقروء/غير مقروء)
- 🔍 بحث وتصفية متقدمة
- 🗑️ حذف الإشعارات القديمة تلقائياً

### 🔒 الأمان
- صلاحيات محددة لكل نوع مستخدم
- التحقق من ملكية الإشعارات
- حماية البيانات الشخصية
- Rate limiting على الـ API

---

## 📁 بنية التطبيق

```
notifications/
├── __init__.py
├── admin.py              # إدارة Django Admin
├── apps.py               # إعدادات التطبيق
├── models.py             # الموديلات الأساسية
├── serializers.py        # Django REST Framework Serializers
├── views.py              # API Views
├── urls.py               # URL Configuration
├── filters.py            # Filters للبحث والتصفية
├── permissions.py        # الصلاحيات المخصصة
├── signals.py            # Django Signals
├── tasks.py              # Celery Tasks
├── tests.py              # الاختبارات
├── utils.py              # دوال مساعدة
└── README.md             # التوثيق
```

---

## 🗄️ الموديلات

### 1. Notification (الإشعار)

```python
class Notification(models.Model):
    user = ForeignKey(User)                    # المستخدم المستقبل
    topic = ForeignKey(Topic, null=True)       # الموضوع (اختياري)
    title = CharField(max_length=255)          # العنوان
    message = TextField()                      # المحتوى
    is_read = BooleanField(default=False)      # حالة القراءة
    extra = JSONField(null=True)               # بيانات إضافية
    image_url = URLField()                     # رابط الصورة
    created_at = DateTimeField(auto_now_add=True)
```

**الفهارس:**
- `(user, is_read, created_at)` - لتحسين الأداء

### 2. Topic (الموضوع)

```python
class Topic(models.Model):
    name = CharField(max_length=255, unique=True)  # اسم الموضوع
    description = TextField(null=True)              # الوصف
```

**الفهارس:**
- `name` - للبحث السريع

### 3. TopicSubscription (الاشتراك)

```python
class TopicSubscription(models.Model):
    user = ForeignKey(User)                    # المستخدم
    topic = ForeignKey(Topic)                  # الموضوع
    subscribed_at = DateTimeField(auto_now_add=True)
    is_active = BooleanField(default=True)     # حالة الاشتراك
```

**القيود:**
- `unique_together: (user, topic)` - اشتراك واحد لكل مستخدم في كل موضوع

---

## 🌐 API Endpoints

### 📢 Notifications (الإشعارات)

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/notifications/notifications/` | قائمة جميع الإشعارات | Authenticated |
| GET | `/notifications/notifications/unread/` | الإشعارات غير المقروءة | Authenticated |
| GET | `/notifications/notifications/stats/` | إحصائيات الإشعارات | Authenticated |
| POST | `/notifications/notifications/mark-all-read/` | تحديد الكل كمقروء | Authenticated |
| POST | `/notifications/notifications/create/` | إنشاء إشعار | Admin/Manager |
| POST | `/notifications/notifications/bulk-create/` | إنشاء إشعارات جماعية | Admin/Manager |
| GET | `/notifications/notifications/{id}/` | تفاصيل إشعار | Owner |
| PATCH | `/notifications/notifications/{id}/update/` | تحديث إشعار | Owner |
| DELETE | `/notifications/notifications/{id}/delete/` | حذف إشعار | Owner |

### 🏷️ Topics (المواضيع)

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/notifications/topics/` | قائمة المواضيع | Authenticated |
| GET | `/notifications/topics/my-topics/` | المواضيع مع حالة الاشتراك | Authenticated |
| POST | `/notifications/topics/create/` | إنشاء موضوع | Admin/Manager |
| GET | `/notifications/topics/{id}/` | تفاصيل موضوع | Authenticated |
| PATCH | `/notifications/topics/{id}/update/` | تحديث موضوع | Admin/Manager |
| DELETE | `/notifications/topics/{id}/delete/` | حذف موضوع | Admin/Manager |

### 🔔 Subscriptions (الاشتراكات)

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/notifications/subscriptions/` | قائمة اشتراكاتي | Authenticated |
| POST | `/notifications/subscriptions/create/` | الاشتراك في موضوع | Authenticated |
| PATCH | `/notifications/subscriptions/{id}/update/` | تحديث اشتراك | Owner |
| DELETE | `/notifications/subscriptions/{id}/delete/` | إلغاء الاشتراك | Owner |

---

## 💡 أمثلة الاستخدام

### 1. الحصول على الإشعارات

```bash
curl -X GET http://localhost:8000/notifications/notifications/ \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": {
    "results": [
      {
        "id": 1,
        "user": {
          "id": 1,
          "username": "pharmacy1",
          "name": "صيدلية الأمل"
        },
        "topic": null,
        "title": "عرض جديد",
        "message": "عرض جديد على المنتجات",
        "is_read": false,
        "extra": null,
        "image_url": "",
        "created_at": "2025-10-17T10:00:00Z"
      }
    ],
    "count": 1,
    "next": null,
    "previous": null
  }
}
```

### 2. إنشاء إشعار (Admin)

```bash
curl -X POST http://localhost:8000/notifications/notifications/create/ \
     -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "user": 1,
       "title": "إشعار جديد",
       "message": "لديك رسالة جديدة",
       "extra": {"type": "info"}
     }'
```

### 3. إرسال إشعارات جماعية

```bash
curl -X POST http://localhost:8000/notifications/notifications/bulk-create/ \
     -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "user_ids": [1, 2, 3, 4, 5],
       "title": "إشعار جماعي",
       "message": "هذا إشعار لجميع المستخدمين المحددين"
     }'
```

### 4. تحديث حالة الإشعار

```bash
curl -X PATCH http://localhost:8000/notifications/notifications/1/update/ \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"is_read": true}'
```

### 5. الاشتراك في موضوع

```bash
curl -X POST http://localhost:8000/notifications/subscriptions/create/ \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "topic": 1,
       "is_active": true
     }'
```

### 6. إرسال إشعار لموضوع

```bash
curl -X POST http://localhost:8000/notifications/notifications/create/ \
     -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "topic": 1,
       "title": "عرض جديد",
       "message": "عرض خاص لجميع المشتركين"
     }'
```

---

## ⚙️ Celery Tasks

### 1. `send_notification_to_user`
إرسال إشعار لمستخدم محدد

```python
from notifications.tasks import send_notification_to_user

send_notification_to_user.delay(
    user_id=1,
    title="إشعار جديد",
    message="محتوى الإشعار",
    extra={"key": "value"}
)
```

### 2. `send_notification_to_topic`
إرسال إشعارات لجميع المشتركين في موضوع

```python
from notifications.tasks import send_notification_to_topic

send_notification_to_topic.delay(
    topic_id=1,
    title="إشعار الموضوع",
    message="محتوى الإشعار"
)
```

### 3. `send_bulk_notifications`
إرسال إشعارات جماعية

```python
from notifications.tasks import send_bulk_notifications

send_bulk_notifications.delay(
    user_ids=[1, 2, 3, 4, 5],
    title="إشعار جماعي",
    message="محتوى الإشعار"
)
```

### 4. `delete_old_read_notifications`
حذف الإشعارات المقروءة القديمة

```python
from notifications.tasks import delete_old_read_notifications

# حذف الإشعارات المقروءة الأقدم من 30 يوم
delete_old_read_notifications.delay(days=30)
```

**جدولة تلقائية في Celery Beat:**

```python
# في celery.py
from celery.schedules import crontab

app.conf.beat_schedule = {
    'delete-old-notifications': {
        'task': 'notifications.tasks.delete_old_read_notifications',
        'schedule': crontab(hour=2, minute=0),  # كل يوم الساعة 2 صباحاً
        'args': (30,)  # حذف الأقدم من 30 يوم
    },
}
```

---

## 🔐 الصلاحيات

### Roles في النظام:
- **ADMIN**: جميع الصلاحيات
- **MANAGER**: إنشاء وإدارة الإشعارات والمواضيع
- **PHARMACY**: استقبال وقراءة الإشعارات فقط
- **STORE**: استقبال وقراءة الإشعارات فقط
- **SALES**: استقبال وقراءة الإشعارات فقط

### Permission Classes:

```python
from notifications.permissions import (
    IsNotificationOwner,       # للتحقق من ملكية الإشعار
    IsSubscriptionOwner,       # للتحقق من ملكية الاشتراك
    CanCreateNotification,     # للسماح بإنشاء إشعارات
    CanManageTopics,          # للسماح بإدارة المواضيع
    CanViewAllNotifications   # للسماح بعرض جميع الإشعارات
)
```

---

## 🔍 Filters والبحث

### Notification Filters:

```python
# Filter بالـ ID
?id=1,2,3

# Filter بالمستخدم
?user=1

# Filter بالموضوع
?topic=1

# Filter بحالة القراءة
?is_read=true

# Filter بالتاريخ
?created_at__gte=2025-01-01&created_at__lte=2025-12-31

# البحث في العنوان والمحتوى
?search=عرض

# الترتيب
?ordering=-created_at
```

---

## 🧪 الاختبارات

### تشغيل الاختبارات:

```bash
# تشغيل جميع اختبارات التطبيق
python manage.py test notifications

# تشغيل اختبار محدد
python manage.py test notifications.tests.NotificationAPITest

# مع coverage
coverage run --source='notifications' manage.py test notifications
coverage report
```

### تغطية الاختبارات:
- ✅ Notification Model Tests
- ✅ Topic Model Tests
- ✅ TopicSubscription Model Tests
- ✅ Notification API Tests (10+ test cases)
- ✅ Topic API Tests
- ✅ TopicSubscription API Tests

---

## 📊 Admin Panel

يوفر التطبيق واجهة إدارة متقدمة في Django Admin:

### إدارة الإشعارات:
- عرض جميع الإشعارات
- تحديد كمقروء/غير مقروء (Bulk Actions)
- البحث في العنوان والمحتوى
- فلترة حسب الحالة والتاريخ
- عرض تفاصيل المستخدم والموضوع

### إدارة المواضيع:
- إنشاء وتعديل المواضيع
- عرض عدد المشتركين
- البحث في الأسماء

### إدارة الاشتراكات:
- عرض جميع الاشتراكات
- تفعيل/تعطيل الاشتراكات
- البحث حسب المستخدم أو الموضوع

---

## 🚀 التطوير المستقبلي

### ميزات مخطط لها:
- [ ] تفعيل Firebase Cloud Messaging (FCM)
- [ ] إرسال إشعارات البريد الإلكتروني
- [ ] إرسال إشعارات SMS
- [ ] نظام الأولويات (عادي، متوسط، عاجل)
- [ ] جدولة الإشعارات
- [ ] قوالب الإشعارات
- [ ] إشعارات متعددة اللغات
- [ ] Dashboard للإحصائيات المتقدمة

---

## 📝 ملاحظات مهمة

1. **الأداء**: تم تحسين الاستعلامات باستخدام `select_related` و `prefetch_related`
2. **الفهارس**: تم إضافة فهارس على الحقول الأكثر استخداماً
3. **Bulk Operations**: استخدام `bulk_create` للإشعارات الجماعية
4. **Soft Delete**: يمكن تفعيل Soft Delete للإشعارات في المستقبل
5. **Rate Limiting**: يُنصح بتفعيل Rate Limiting على endpoints الإنشاء

---

## 🤝 المساهمة

للمساهمة في تطوير التطبيق:
1. Fork المشروع
2. إنشاء branch جديد (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push للـ branch (`git push origin feature/amazing-feature`)
5. فتح Pull Request

---

## 📄 License

هذا التطبيق جزء من مشروع Pharmasky.

---

## 📞 الدعم

للحصول على المساعدة أو الإبلاغ عن مشاكل، يرجى التواصل مع فريق التطوير.

**Built with ❤️ by Pharmasky Team**

