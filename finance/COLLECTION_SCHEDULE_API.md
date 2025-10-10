# دليل API جدول مواعيد التحصيلات
# Collection Schedule API Guide

---

## 🎯 نظرة عامة

هذا الـ API يرجع قائمة بمواعيد التحصيلات المتوقعة لكل صيدلية حسب الشريحة (مدة الأجل) الخاصة بها.

---

## 📡 الـ Endpoint

```http
GET http://129.212.140.152/finance/collection-schedule/
Authorization: Token your-token-here
```

---

## ✅ الاستجابة

### مثال كامل

```json
{
  "count": 3,
  "total_outstanding_amount": "45000.00",
  "results": [
    {
      "user_id": 12,
      "customer_name": "صيدلية الأمل",
      "username": "+201234567893",
      "payment_period_name": "15 يوم",
      "period_in_days": 15,
      "latest_invoice_date": "2025-09-25T10:00:00Z",
      "expected_collection_date": "2025-10-10T10:00:00Z",
      "days_until_collection": 0,
      "outstanding_balance": "22000.00",
      "is_overdue": false,
      "penalty_percentage": "0.20",
      "penalty_amount": "0.00",
      "total_with_penalty": "22000.00",
      "cashback_percentage": "0.10",
      "cashback_amount": "0.00",
      "total_with_cashback": "22000.00"
    },
    {
      "user_id": 5,
      "customer_name": "صيدلية النور",
      "username": "+201234567890",
      "payment_period_name": "30 يوم",
      "period_in_days": 30,
      "latest_invoice_date": "2025-09-05T14:30:00Z",
      "expected_collection_date": "2025-10-05T14:30:00Z",
      "days_until_collection": 5,
      "outstanding_balance": "15000.00",
      "is_overdue": false,
      "penalty_percentage": "0.20",
      "penalty_amount": "0.00",
      "total_with_penalty": "15000.00",
      "cashback_percentage": "0.10",
      "cashback_amount": "75.00",
      "total_with_cashback": "14925.00"
    },
    {
      "user_id": 7,
      "customer_name": "صيدلية الشفاء",
      "username": "+201234567891",
      "payment_period_name": "7 أيام",
      "period_in_days": 7,
      "latest_invoice_date": "2025-10-01T11:00:00Z",
      "expected_collection_date": "2025-10-08T11:00:00Z",
      "days_until_collection": -2,
      "outstanding_balance": "8000.00",
      "is_overdue": true,
      "penalty_percentage": "0.20",
      "penalty_amount": "32.00",
      "total_with_penalty": "8032.00",
      "cashback_percentage": "0.10",
      "cashback_amount": "0.00",
      "total_with_cashback": "8000.00"
    }
  ]
}
```

---

## 📊 البيانات المُرجعة

### على مستوى الاستجابة العامة

| الحقل | النوع | الوصف |
|------|------|-------|
| `count` | Integer | عدد الصيدليات المديونة |
| `total_outstanding_amount` | Decimal | إجمالي المبالغ المستحقة |
| `results` | Array | قائمة الصيدليات |

---

### على مستوى كل صيدلية (results)

| الحقل | النوع | الوصف |
|------|------|-------|
| `user_id` | Integer | رقم معرّف الصيدلية |
| `customer_name` | String | اسم الصيدلية |
| `username` | String | رقم الهاتف |
| `payment_period_name` | String | اسم الشريحة (مثل "15 يوم") |
| `period_in_days` | Integer | مدة الأجل بالأيام |
| `latest_invoice_date` | DateTime | تاريخ آخر فاتورة |
| `expected_collection_date` | DateTime | تاريخ التحصيل المتوقع |
| `days_until_collection` | Integer | عدد الأيام المتبقية للتحصيل |
| `outstanding_balance` | Decimal | المبلغ المستحق |
| `is_overdue` | Boolean | هل متأخر عن الموعد؟ |
| **`penalty_percentage`** | Decimal | **نسبة الغرامة اليومية (%)** |
| **`penalty_amount`** | Decimal | **مبلغ الغرامة** |
| **`total_with_penalty`** | Decimal | **الإجمالي مع الغرامة** |
| **`cashback_percentage`** | Decimal | **نسبة الكاش باك اليومية (%)** |
| **`cashback_amount`** | Decimal | **مبلغ الكاش باك** |
| **`total_with_cashback`** | Decimal | **الإجمالي بعد الكاش باك** |

---

## 💰 الغرامة والكاش باك (Penalty & Cashback)

### 🔴 غرامة التأخير (Late Payment Penalty)

**متى تُطبق؟**
- عندما `is_overdue = true` (days_until_collection < 0)

**كيف تُحسب؟**
```
penalty_amount = outstanding_balance × penalty_percentage × late_days ÷ 100
total_with_penalty = outstanding_balance + penalty_amount
```

**مثال:**
```
المبلغ المستحق: 8,000 ج
نسبة الغرامة: 0.20% يومياً
عدد أيام التأخير: 2 يوم

penalty_amount = 8,000 × 0.20 × 2 ÷ 100 = 32 ج
total_with_penalty = 8,000 + 32 = 8,032 ج
```

---

### 🟢 كاش باك الدفع المبكر (Early Payment Cashback)

**متى يُطبق؟**
- عندما `is_overdue = false` وَ `days_until_collection > 0`

**كيف يُحسب؟**
```
cashback_amount = outstanding_balance × cashback_percentage × early_days ÷ 100
total_with_cashback = outstanding_balance - cashback_amount
```

**مثال:**
```
المبلغ المستحق: 15,000 ج
نسبة الكاش باك: 0.10% يومياً
عدد الأيام قبل الموعد: 5 أيام

cashback_amount = 15,000 × 0.10 × 5 ÷ 100 = 75 ج
total_with_cashback = 15,000 - 75 = 14,925 ج
```

---

### ⚪ الدفع في الموعد (On-Time Payment)

**متى؟**
- عندما `days_until_collection = 0`

**الحساب:**
```
penalty_amount = 0
cashback_amount = 0
total_with_penalty = outstanding_balance
total_with_cashback = outstanding_balance
```

---

### 📊 جدول مقارنة

| الحالة | الأيام | الغرامة | الكاش باك | الإجمالي |
|--------|--------|---------|----------|----------|
| متأخر يومين | -2 | 32 ج | 0 ج | 8,032 ج |
| في الموعد | 0 | 0 ج | 0 ج | 8,000 ج |
| مبكر 5 أيام | +5 | 0 ج | 75 ج | 7,925 ج |

---

### ⚙️ إعدادات النسب

النسب الافتراضية:
- **غرامة التأخير:** 0.20% يومياً
- **كاش باك الدفع المبكر:** 0.10% يومياً

يمكن تغيير هذه النسب لكل صيدلية من البروفايل:
- `late_payment_penalty_percentage`
- `early_payment_cashback_percentage`

---

## 🔍 فهم البيانات

### تاريخ التحصيل المتوقع

```
expected_collection_date = latest_invoice_date + period_in_days
```

**مثال:**
```
آخر فاتورة: 2025-09-25
مدة الأجل: 15 يوم
التاريخ المتوقع: 2025-10-10
```

---

### الأيام المتبقية

```
days_until_collection = expected_collection_date - اليوم
```

**الحالات:**
- `0` = الموعد اليوم
- `> 0` = باقي X أيام
- `< 0` = متأخر بـ X أيام

---

### حالة التأخير

```json
{
  "is_overdue": true   // متأخر (days_until_collection < 0)
  "is_overdue": false  // في الموعد أو قبله
}
```

---

## 📋 الترتيب

القائمة مرتبة تلقائياً:
1. **المتأخرون أولاً** (is_overdue = true)
2. **ثم حسب التاريخ الأقرب**

---

## 🎯 حالات الاستخدام

### المثال 1: عرض القائمة

```http
GET http://129.212.140.152/finance/collection-schedule/
```

**النتيجة:**
```json
{
  "count": 3,
  "total_outstanding_amount": "45000.00",
  "results": [...]
}
```

---

### المثال 2: تحليل البيانات

```javascript
// الصيدليات المتأخرة
const overdue = results.filter(item => item.is_overdue);

// الصيدليات اللي موعدها اليوم
const today = results.filter(item => item.days_until_collection === 0);

// الأولوية العالية (متأخر أو موعده اليوم أو غداً)
const highPriority = results.filter(item => 
  item.days_until_collection <= 1
);
```

---

### المثال 3: طباعة تقرير

```
═══════════════════════════════════════════════════════
         جدول مواعيد التحصيلات
              تاريخ: 2025/10/10
═══════════════════════════════════════════════════════

إجمالي المبالغ المستحقة:  45,000 جنيه
عدد الصيدليات:             3

───────────────────────────────────────────────────────

🔴 متأخر

1. صيدلية الشفاء
   المبلغ: 8,000 ج
   الموعد المتوقع: 2025-10-08
   متأخر بـ: 2 يوم
   الشريحة: 7 أيام
   
───────────────────────────────────────────────────────

🟢 في الموعد

2. صيدلية الأمل
   المبلغ: 22,000 ج
   الموعد المتوقع: 2025-10-10 (اليوم)
   الشريحة: 15 يوم
   
3. صيدلية النور
   المبلغ: 15,000 ج
   الموعد المتوقع: 2025-10-10 (اليوم)
   الشريحة: 30 يوم

═══════════════════════════════════════════════════════
```

---

## 🎨 مثال واجهة مستخدم

### جدول HTML

```html
<table>
  <thead>
    <tr>
      <th>الصيدلية</th>
      <th>الموعد المتوقع</th>
      <th>المبلغ</th>
      <th>الحالة</th>
      <th>إجراء</th>
    </tr>
  </thead>
  <tbody>
    <tr class="overdue">
      <td>صيدلية الشفاء</td>
      <td>2025-10-08</td>
      <td>8,000 ج</td>
      <td><span class="badge red">متأخر بـ 2 يوم</span></td>
      <td><button>اتصل الآن</button></td>
    </tr>
    <tr class="today">
      <td>صيدلية الأمل</td>
      <td>2025-10-10 (اليوم)</td>
      <td>22,000 ج</td>
      <td><span class="badge yellow">موعد اليوم</span></td>
      <td><button>حصّل</button></td>
    </tr>
    <tr class="upcoming">
      <td>صيدلية النور</td>
      <td>2025-10-10 (اليوم)</td>
      <td>15,000 ج</td>
      <td><span class="badge green">في الموعد</span></td>
      <td><button>حصّل</button></td>
    </tr>
  </tbody>
</table>
```

---

## 🔐 الصلاحيات

### الأدوار المسموحة

- ✅ **Manager** - يرى كل الصيدليات التابعة له
- ✅ **Area Manager** - يرى الصيدليات في منطقته
- ✅ **Sales** - يرى عملاءه فقط
- ✅ **Admin** - يرى الكل

### الأدوار غير المسموحة

- ❌ **Pharmacy** - لا يستطيع رؤية باقي الصيدليات
- ❌ **Delivery** - لا صلاحية له

---

## 📝 ملاحظات مهمة

### 1. الصيدليات المعروضة

يظهر فقط الصيدليات التي:
- ✅ لديها رصيد سالب (مديونة)
- ✅ لديها شريحة محددة (payment_period)
- ✅ لديها آخر تاريخ فاتورة (latest_invoice_date)

---

### 2. الصيدليات المخفية

لن تظهر الصيدليات التي:
- ❌ رصيدها صفر أو موجب (مسددة)
- ❌ ليس لديها شريحة
- ❌ ليس لديها أي فواتير

---

### 3. حساب التاريخ

```
التاريخ المتوقع = آخر فاتورة + مدة الأجل
```

**مثال:**
- آخر فاتورة: 2025-09-25
- الشريحة: 15 يوم
- التاريخ المتوقع: 2025-10-10

---

## 🎯 أمثلة استخدام عملية

### Python Example

```python
import requests

# Get collection schedule
url = "http://129.212.140.152/finance/collection-schedule/"
headers = {"Authorization": "Token your-token-here"}
response = requests.get(url, headers=headers)
data = response.json()

print(f"إجمالي المستحق: {data['total_outstanding_amount']} جنيه")
print(f"عدد الصيدليات: {data['count']}")

# Print overdue pharmacies
overdue = [item for item in data['results'] if item['is_overdue']]
print(f"\nالصيدليات المتأخرة: {len(overdue)}")
for item in overdue:
    print(f"- {item['customer_name']}: {item['outstanding_balance']} ج")
```

---

### JavaScript Example

```javascript
// Fetch collection schedule
fetch('http://129.212.140.152/finance/collection-schedule/', {
  headers: {
    'Authorization': 'Token your-token-here'
  }
})
.then(response => response.json())
.then(data => {
  console.log(`Total Outstanding: ${data.total_outstanding_amount}`);
  
  // Group by priority
  const overdue = data.results.filter(item => item.is_overdue);
  const today = data.results.filter(item => 
    item.days_until_collection === 0 && !item.is_overdue
  );
  const upcoming = data.results.filter(item => 
    item.days_until_collection > 0
  );
  
  console.log(`Overdue: ${overdue.length}`);
  console.log(`Today: ${today.length}`);
  console.log(`Upcoming: ${upcoming.length}`);
});
```

---

## 📊 تحليل البيانات

### إحصائيات مفيدة

```javascript
const stats = {
  total_count: data.count,
  total_amount: data.total_outstanding_amount,
  overdue_count: data.results.filter(i => i.is_overdue).length,
  today_count: data.results.filter(i => i.days_until_collection === 0).length,
  this_week: data.results.filter(i => i.days_until_collection <= 7).length,
  average_amount: data.total_outstanding_amount / data.count,
};
```

---

### ترتيب حسب الأولوية

```javascript
// الأولوية القصوى (متأخر)
const critical = data.results.filter(item => item.is_overdue);

// أولوية عالية (اليوم أو غداً)
const high = data.results.filter(item => 
  !item.is_overdue && item.days_until_collection <= 1
);

// أولوية متوسطة (خلال 7 أيام)
const medium = data.results.filter(item => 
  item.days_until_collection > 1 && item.days_until_collection <= 7
);

// أولوية منخفضة (أكثر من 7 أيام)
const low = data.results.filter(item => 
  item.days_until_collection > 7
);
```

---

## 🔄 التكامل مع APIs أخرى

### 1. بعد عرض القائمة → تسجيل تحصيل

```http
# 1. احصل على القائمة
GET /finance/collection-schedule/

# 2. اتصل بالصيدلية وحصّل

# 3. سجل التحصيل
POST /finance/sale-payments/create/
{
  "user": 5,
  "method": "cash",
  "amount": 5000,
  "at": "2025-10-10"
}
```

---

### 2. التحقق من رصيد صيدلية معينة

```http
# من القائمة
GET /finance/collection-schedule/
# → user_id: 5, outstanding_balance: 15000

# التفاصيل الكاملة
GET /accounts/users/5/
# → account.balance: -15000
```

---

### 3. عرض فواتير الصيدلية

```http
# من القائمة
GET /finance/collection-schedule/
# → user_id: 5

# فواتير الصيدلية المعلقة
GET /invoices/sale-invoices/?status=placed&user=5
```

---

## ✅ أفضل الممارسات

### 1. راجع القائمة يومياً

```bash
# صباح كل يوم
curl -H "Authorization: Token xxx" \
  http://129.212.140.152/finance/collection-schedule/
```

---

### 2. ابدأ بالمتأخرين

```javascript
// المتأخرون أولاً (موجودون في بداية القائمة)
const overdue = data.results.filter(item => item.is_overdue);
overdue.forEach(item => {
  console.log(`اتصل بـ ${item.customer_name} - متأخر ${Math.abs(item.days_until_collection)} يوم`);
});
```

---

### 3. خطط للأسبوع

```javascript
// التحصيلات المتوقعة خلال 7 أيام
const thisWeek = data.results.filter(item => 
  item.days_until_collection >= 0 && item.days_until_collection <= 7
);

// رتب حسب اليوم
const byDay = {};
thisWeek.forEach(item => {
  const day = item.days_until_collection;
  if (!byDay[day]) byDay[day] = [];
  byDay[day].push(item);
});
```

---

## 🐛 استكشاف الأخطاء

### المشكلة: القائمة فارغة

**الأسباب المحتملة:**
1. ✅ كل الصيدليات مسددة (رصيد = 0)
2. ✅ لا توجد صيدليات لها شرائح
3. ✅ لا توجد فواتير سابقة

**الحل:**
- تحقق من رصيد الصيدليات: `GET /accounts/users/?role=pharmacy`
- تحقق من الشرائح: هل كل صيدلية لها `payment_period`؟

---

### المشكلة: تاريخ غير دقيق

**السبب:**
- `latest_invoice_date` غير محدّث

**الحل:**
- تأكد من تحديث `latest_invoice_date` عند إنشاء فاتورة جديدة

---

### المشكلة: صيدلية مديونة لا تظهر

**الأسباب المحتملة:**
1. ليس لديها `payment_period`
2. ليس لديها `latest_invoice_date`
3. رصيدها موجب أو صفر

**الحل:**
- تحقق من بيانات الصيدلية: `GET /accounts/users/{id}/`

---

## 🎯 الخلاصة

### الـ API

```http
GET http://129.212.140.152/finance/collection-schedule/
```

---

### ما يرجعه

```json
{
  "count": 3,
  "total_outstanding_amount": "45000.00",
  "results": [
    {
      "customer_name": "صيدلية الأمل",
      "expected_collection_date": "2025-10-10",
      "outstanding_balance": "22000.00",
      "is_overdue": false
    }
  ]
}
```

---

### الاستخدام

1. **صباح كل يوم:** احصل على القائمة
2. **ابدأ بالمتأخرين:** `is_overdue = true`
3. **اتصل بالصيدليات:** حسب الأولوية
4. **حصّل الفلوس:** استخدم `POST /finance/sale-payments/create/`
5. **راجع التقدم:** احصل على القائمة مرة أخرى

---

**آخر تحديث**: 2025-10-10  
**الإصدار**: 1.0.0  
**الحالة**: ✅ جاهز ويعمل

