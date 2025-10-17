# 🕐 نظام الوردية (Work Shift System)

نظام ذكي لإدارة أوقات العمل مع إشعارات تلقائية للصيدليات.

---

## 📋 المشكلة والحل

### المشكلة ❌
- العمل من 6 مساءً → 2 صباحاً (ليس وقت ثابت)
- صعوبة حساب إحصائيات دقيقة
- الصيدليات لا تعرف متى النظام متاح

### الحل ✅
- نظام وردية يدوي - تبدأ وتنتهي بضغطة زر
- إشعارات تلقائية لجميع الصيدليات عند البدء والإغلاق
- إحصائيات دقيقة لكل وردية
- مرونة كاملة في أوقات العمل

---

## 🎯 كيف يعمل النظام

### التدفق

```
1. Admin يضغط "ابدأ الوردية" 
   ↓
2. إنشاء WorkShift (status=ACTIVE)
   ↓
3. إرسال إشعار "🟢 النظام متاح الآن" لكل الصيدليات
   ↓
4. العمل يبدأ... (الإحصائيات تتسجل تلقائياً)
   ↓
5. Admin يضغط "إغلاق الوردية"
   ↓
6. تحديث الإحصائيات النهائية
   ↓
7. إرسال إشعار "🔴 تم إغلاق النظام" لكل الصيدليات
```

---

## 🌐 API Endpoints

### 1. بدء وردية جديدة

```bash
POST /core/shifts/start/
```

**Request:**
```json
{
  "send_notifications": true,
  "notification_message": "مرحباً! النظام متاح الآن للطلبات"
}
```

**Response:**
```json
{
  "success": true,
  "message": "تم بدء الوردية بنجاح وإرسال الإشعارات للصيدليات",
  "data": {
    "id": 123,
    "status": "ACTIVE",
    "started_by": {
      "id": 1,
      "username": "admin",
      "name": "Admin"
    },
    "start_time": "2025-10-17T18:00:00Z",
    "total_sale_invoices": 0,
    "total_sales_amount": "0.00"
  }
}
```

**ما يحدث:**
- ✅ إنشاء وردية جديدة
- ✅ إرسال إشعار لـ **جميع الصيدليات النشطة**:
  ```
  🟢 النظام متاح الآن
  مرحباً! بدأت الوردية الآن (06:00 PM). 
  يمكنك تقديم الطلبات والاستفسارات. نحن في خدمتك!
  ```

---

### 2. إغلاق الوردية

```bash
POST /core/shifts/close/
```

**Request:**
```json
{
  "notes": "وردية ممتازة، 50 طلب تم معالجتها",
  "send_notifications": true,
  "notification_message": "شكراً! سنعود غداً في نفس الموعد"
}
```

**Response:**
```json
{
  "success": true,
  "message": "تم إغلاق الوردية بنجاح",
  "data": {
    "id": 123,
    "status": "CLOSED",
    "start_time": "2025-10-17T18:00:00Z",
    "end_time": "2025-10-18T02:00:00Z",
    "duration": "8.0 ساعة",
    "total_sale_invoices": 50,
    "total_sales_amount": "125000.00",
    "total_payments": 30,
    "total_payments_amount": "75000.00",
    "notes": "وردية ممتازة، 50 طلب تم معالجتها"
  }
}
```

**ما يحدث:**
- ✅ تحديث إحصائيات الوردية
- ✅ إغلاق الوردية
- ✅ إرسال إشعار لـ **جميع الصيدليات**:
  ```
  🔴 تم إغلاق النظام
  تم إغلاق الوردية (02:00 AM). مدة الوردية: 8.0 ساعة.
  شكراً لكم! سنكون متاحين في الوردية القادمة.
  ```

---

### 3. الوردية الحالية

```bash
GET /core/shifts/current/
```

**Response:**
```json
{
  "success": true,
  "message": "الوردية النشطة الحالية",
  "data": {
    "id": 123,
    "status": "ACTIVE",
    "started_by": {"id": 1, "name": "Admin"},
    "start_time": "2025-10-17T18:00:00Z",
    "duration": "3.5 ساعة (مستمرة)",
    "total_sale_invoices": 25,
    "total_sales_amount": "62500.00"
  }
}
```

**الاستخدام:**
- للتحقق من وجود وردية نشطة
- لعرض الإحصائيات الحالية (Live)
- متاح لجميع المستخدمين

---

### 4. قائمة الورديات

```bash
GET /core/shifts/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": 123,
        "status": "CLOSED",
        "start_time": "2025-10-17T18:00:00Z",
        "end_time": "2025-10-18T02:00:00Z",
        "duration": "8.0 ساعة",
        "total_sale_invoices": 50,
        "total_sales_amount": "125000.00"
      }
    ],
    "count": 100
  }
}
```

**Filters:**
```bash
# فلترة حسب الحالة
GET /core/shifts/?status=ACTIVE
GET /core/shifts/?status=CLOSED
```

---

### 5. إحصائيات الورديات

```bash
GET /core/shifts/stats/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_shifts": 150,
    "active_shifts": 1,
    "closed_shifts": 149,
    "total_sales_all_shifts": "18750000.00",
    "total_payments_all_shifts": "15000000.00",
    "average_invoices_per_shift": 45.5
  }
}
```

---

## 💡 أمثلة الاستخدام

### مثال 1: بدء يوم عمل عادي

```bash
# الساعة 6 مساءً - Admin جاهز للعمل
curl -X POST http://localhost:8000/core/shifts/start/ \
     -H "Authorization: Token ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "send_notifications": true,
       "notification_message": "مساء الخير! النظام متاح الآن. يمكنكم تقديم طلباتكم 🌙"
     }'

# ✨ جميع الصيدليات (200 صيدلية) تستلم:
# "🟢 النظام متاح الآن"
# "مساء الخير! النظام متاح الآن. يمكنكم تقديم طلباتكم 🌙"
```

---

### مثال 2: إغلاق الوردية

```bash
# الساعة 2 صباحاً - انتهى العمل
curl -X POST http://localhost:8000/core/shifts/close/ \
     -H "Authorization: Token ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "notes": "وردية ممتازة - 75 طلب",
       "send_notifications": true,
       "notification_message": "تصبحون على خير! انتهت الوردية. سنعود غداً 🌙"
     }'

# ✨ جميع الصيدليات تستلم:
# "🔴 تم إغلاق النظام"
# "تصبحون على خير! انتهت الوردية. سنعود غداً 🌙"
```

---

### مثال 3: التحقق من الوردية الحالية

```bash
# أي مستخدم يقدر يشوف الوردية الحالية
curl http://localhost:8000/core/shifts/current/ \
     -H "Authorization: Token ANY_USER_TOKEN"

# Response:
{
  "success": true,
  "data": {
    "status": "ACTIVE",
    "start_time": "2025-10-17T18:00:00Z",
    "duration": "5.5 ساعة (مستمرة)",
    "total_sale_invoices": 45,
    "total_sales_amount": "112500.00"
  }
}
```

---

### مثال 4: مراجعة الورديات السابقة

```bash
# Admin يشوف آخر 10 ورديات
curl http://localhost:8000/core/shifts/?page_size=10 \
     -H "Authorization: Token ADMIN_TOKEN"

# Response: قائمة بجميع الورديات مع الإحصائيات
```

---

## 📊 الإحصائيات المسجلة تلقائياً

### لكل وردية:

| الإحصائية | الوصف |
|-----------|--------|
| `total_sale_invoices` | عدد فواتير البيع (طلبات الصيدليات) |
| `total_purchase_invoices` | عدد فواتير الشراء (للمخازن) |
| `total_payments` | عدد الدفعات |
| `total_returns` | عدد المرتجعات |
| `total_complaints` | عدد الشكاوي |
| `total_new_registrations` | عدد الصيدليات الجديدة |
| `total_sales_amount` | إجمالي المبيعات (بالجنيه) |
| `total_payments_amount` | إجمالي المدفوعات (بالجنيه) |

### حساب تلقائي:
- ✅ يتم حساب الإحصائيات **تلقائياً** عند إغلاق الوردية
- ✅ يمكن تحديثها أثناء الوردية من API الحالية

---

## 🎯 سيناريو عملي كامل

### اليوم الأول:

```python
# الساعة 6:00 مساءً
# 1. Admin يبدأ الوردية
POST /core/shifts/start/
{
  "notification_message": "مساء الخير! بدأنا العمل الآن 🌙"
}

# ✨ 200 صيدلية تستلم: "🟢 النظام متاح الآن"

# خلال الوردية (6 مساءً → 2 صباحاً):
# - 75 صيدلية تطلب طلبات → 75 فاتورة بيع
# - 30 دفعة تم تسجيلها
# - 5 مرتجعات
# - 2 شكوى
# - 3 صيدليات جديدة

# الساعة 2:00 صباحاً
# 2. Admin يغلق الوردية
POST /core/shifts/close/
{
  "notes": "وردية ممتازة - طلبات كثيرة"
}

# ✨ 200 صيدلية تستلم: "🔴 تم إغلاق النظام"

# النتيجة:
{
  "duration": "8.0 ساعة",
  "total_sale_invoices": 75,
  "total_sales_amount": "187500.00",
  "total_payments": 30,
  "total_payments_amount": "90000.00",
  "total_returns": 5,
  "total_complaints": 2,
  "total_new_registrations": 3
}
```

---

## 📱 Integration في Frontend

### Dashboard الرئيسي:

```javascript
// React/Vue/Angular Component

// 1. التحقق من الوردية الحالية
const checkCurrentShift = async () => {
  const response = await fetch('/core/shifts/current/', {
    headers: { 'Authorization': `Token ${token}` }
  });
  const data = await response.json();
  
  if (data.data) {
    // عرض: "الوردية نشطة - بدأت الساعة 6:00 مساءً"
    setShiftStatus('active');
    setShiftData(data.data);
  } else {
    // عرض: "لا توجد وردية نشطة"
    setShiftStatus('inactive');
  }
};

// 2. بدء وردية
const startShift = async () => {
  const response = await fetch('/core/shifts/start/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${adminToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      send_notifications: true,
      notification_message: customMessage || ""
    })
  });
  
  // Success: "تم بدء الوردية وإرسال الإشعارات لـ 200 صيدلية"
};

// 3. إغلاق وردية
const closeShift = async () => {
  const response = await fetch('/core/shifts/close/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${adminToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      notes: shiftNotes,
      send_notifications: true
    })
  });
  
  // Success: عرض إحصائيات الوردية
  console.log(data.data.total_sale_invoices); // 75
  console.log(data.data.total_sales_amount);  // 187500.00
};
```

---

## 📊 Admin Dashboard UI

### مثال واجهة:

```
╔════════════════════════════════════════════════╗
║        🕐 إدارة الوردية                      ║
╠════════════════════════════════════════════════╣
║                                                ║
║  الحالة: 🟢 نشطة                             ║
║  بدأت: 17/10/2025 - 06:00 مساءً              ║
║  المدة: 5.5 ساعة (مستمرة)                    ║
║                                                ║
║  ─────── الإحصائيات الحالية ───────          ║
║  📦 الطلبات: 45                               ║
║  💰 المبيعات: 112,500 جنيه                   ║
║  💳 الدفعات: 25 (62,500 جنيه)                ║
║  ↩️  المرتجعات: 3                             ║
║  📢 الشكاوي: 1                                ║
║                                                ║
║  [ 🔴 إغلاق الوردية ]                        ║
║                                                ║
╚════════════════════════════════════════════════╝
```

عند الضغط على "إغلاق":
```
╔════════════════════════════════════════════════╗
║        إغلاق الوردية                         ║
╠════════════════════════════════════════════════╣
║                                                ║
║  📝 ملاحظات (اختياري):                       ║
║  [__________________________________]          ║
║                                                ║
║  ✅ إرسال إشعارات للصيدليات                 ║
║                                                ║
║  💬 رسالة مخصصة (اختياري):                   ║
║  [__________________________________]          ║
║                                                ║
║  [ إلغاء ]  [ ✅ تأكيد الإغلاق ]             ║
║                                                ║
╚════════════════════════════════════════════════╝
```

---

## 🔔 الإشعارات المرسلة

### عند بدء الوردية:

**للصيدليات:**
```
🟢 النظام متاح الآن

مرحباً! بدأت الوردية الآن (06:00 PM).
يمكنك تقديم الطلبات والاستفسارات. نحن في خدمتك!
```

**Extra Data:**
```json
{
  "type": "shift_started",
  "shift_id": 123,
  "shift_type": "start",
  "timestamp": "2025-10-17T18:00:00Z"
}
```

---

### عند إغلاق الوردية:

**للصيدليات:**
```
🔴 تم إغلاق النظام

تم إغلاق الوردية (02:00 AM). مدة الوردية: 8.0 ساعة.
شكراً لكم! سنكون متاحين في الوردية القادمة.
```

**Extra Data:**
```json
{
  "type": "shift_closed",
  "shift_id": 123,
  "shift_type": "close",
  "timestamp": "2025-10-18T02:00:00Z"
}
```

---

## 🎯 حالات الاستخدام

### حالة 1: وردية عادية

```
06:00 PM → بدء ✅ (200 إشعار)
   ↓
[8 ساعات عمل]
   ↓
02:00 AM → إغلاق ✅ (200 إشعار)
```

### حالة 2: وردية طويلة

```
06:00 PM → بدء ✅
   ↓
[12 ساعة عمل]
   ↓
06:00 AM → إغلاق ✅
```

### حالة 3: ورديتين في يوم

```
08:00 AM → بدء وردية 1 ✅
02:00 PM → إغلاق وردية 1 ✅
   
06:00 PM → بدء وردية 2 ✅
02:00 AM → إغلاق وردية 2 ✅
```

---

## 🔒 الصلاحيات

| Endpoint | Permission |
|----------|------------|
| Start Shift | Admin/Manager only |
| Close Shift | Admin/Manager only |
| Current Shift | All authenticated users |
| List Shifts | Admin/Manager only |
| Stats | Admin/Manager only |

---

## 📊 Django Admin

في Admin Panel:

```
Work Shifts
┌──────┬────────┬───────────────┬──────────────┬─────────┬──────────┐
│ ID   │ Status │ Started By    │ Start Time   │ Duration│ Invoices │
├──────┼────────┼───────────────┼──────────────┼─────────┼──────────┤
│ 123  │ ACTIVE │ Admin         │ 18:00 PM     │ 5.5h    │ 45       │
│ 122  │ CLOSED │ Manager       │ 18:00 PM     │ 8.0h    │ 68       │
│ 121  │ CLOSED │ Admin         │ 18:00 PM     │ 7.5h    │ 52       │
└──────┴────────┴───────────────┴──────────────┴─────────┴──────────┘
```

**Features:**
- عرض جميع الورديات
- تصفية حسب الحالة
- عرض الإحصائيات التفصيلية
- البحث حسب من بدأها/أغلقها
- **منع الإضافة اليدوية** (يجب استخدام API)

---

## 🧪 الاختبار

### من Django Shell:

```python
from core.models import WorkShift
from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.filter(role='ADMIN').first()

# 1. بدء وردية
shift = WorkShift.objects.create(
    started_by=admin,
    status='ACTIVE'
)
print(f"✓ بدأت الوردية #{shift.pk}")

# 2. محاكاة بعض العمليات...
# (إنشاء فواتير، دفعات، إلخ)

# 3. تحديث الإحصائيات
shift.update_statistics()
print(f"✓ فواتير البيع: {shift.total_sale_invoices}")
print(f"✓ المبيعات: {shift.total_sales_amount} جنيه")

# 4. إغلاق الوردية
shift.close_shift(user=admin, notes="وردية تجريبية")
print(f"✓ المدة: {shift.get_duration()}")
```

---

## ⚙️ Migration

### إنشاء Migration:

```bash
docker exec -it pharmasky_web python manage.py makemigrations core
docker exec -it pharmasky_web python manage.py migrate core
```

---

## ✅ المميزات

✅ **مرونة كاملة** - ابدأ وأغلق متى تريد  
✅ **إشعارات تلقائية** - لجميع الصيدليات  
✅ **رسائل مخصصة** - حسب المناسبة  
✅ **إحصائيات دقيقة** - لكل وردية  
✅ **تحديث فوري** - الإحصائيات live  
✅ **سهل الاستخدام** - ضغطة زر واحدة  
✅ **متابعة تاريخية** - جميع الورديات مسجلة  
✅ **Admin Panel** - واجهة سهلة  

---

## 🎊 الخلاصة

### ما تم إنشاؤه:

| الملف | الوصف |
|------|-------|
| ✅ `core/models.py` | WorkShift model |
| ✅ `core/serializers.py` | 3 serializers |
| ✅ `core/views.py` | 5 API views |
| ✅ `core/urls.py` | 5 endpoints |
| ✅ `core/admin.py` | Admin interface |
| ✅ `notifications/tasks.py` | `send_shift_notification` task |

### الاستخدام:

```
1. اضغط "ابدأ" → ✨ إشعار لـ 200 صيدلية
2. العمل... → 📊 الإحصائيات تتسجل تلقائياً
3. اضغط "أغلق" → ✨ إشعار لـ 200 صيدلية + حفظ الإحصائيات
```

**النظام جاهز! 🚀**

