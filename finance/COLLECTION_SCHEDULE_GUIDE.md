# 📋 دليل استخدام قائمة التحصيلات (Collection Schedule)

## نظرة عامة

Endpoint مخصص لعرض قائمة بجميع العملاء المديونين مع تفاصيل التحصيل المتوقع، الغرامات، والخصومات.

---

## 🔗 Endpoint

```
GET /finance/collection-schedule/
```

**الصلاحيات**: Staff (Sales, Manager, AreaManager)

---

## 🔍 الفلاتر والبحث

### 1. البحث باسم العميل أو رقم الهاتف

```bash
GET /finance/collection-schedule/?search=محمد
GET /finance/collection-schedule/?search=01234567890
GET /finance/collection-schedule/?search=pharmacy
```

**يبحث في**:
- `name`: الاسم بالعربي
- `e_name`: الاسم بالإنجليزي
- `username`: رقم الهاتف

---

### 2. فلتر بالتاريخ (نطاق تاريخ التحصيل المتوقع)

#### من تاريخ معين
```bash
GET /finance/collection-schedule/?date_from=2024-10-01
```

#### إلى تاريخ معين
```bash
GET /finance/collection-schedule/?date_to=2024-10-31
```

#### نطاق كامل
```bash
GET /finance/collection-schedule/?date_from=2024-10-01&date_to=2024-10-31
```

**ملاحظة**: التنسيق المطلوب `YYYY-MM-DD`

---

### 3. فلتر المتأخرين فقط

```bash
GET /finance/collection-schedule/?overdue_only=true
```

**يعرض فقط**: العملاء الذين تجاوزوا موعد السداد

---

### 4. دمج الفلاتر

```bash
# البحث عن "محمد" من المتأخرين فقط
GET /finance/collection-schedule/?search=محمد&overdue_only=true

# المتأخرين في شهر أكتوبر
GET /finance/collection-schedule/?overdue_only=true&date_from=2024-10-01&date_to=2024-10-31

# بحث مع نطاق تاريخ
GET /finance/collection-schedule/?search=pharmacy&date_from=2024-10-15&date_to=2024-10-30

# كل الفلاتر معاً
GET /finance/collection-schedule/?search=أحمد&date_from=2024-10-01&date_to=2024-10-31&overdue_only=true
```

---

## 📊 Response Structure

```json
{
  "count": 25,
  "total_outstanding_amount": "125000.00",
  "results": [
    {
      "user_id": 123,
      "customer_name": "صيدلية الشفاء",
      "username": "+201234567890",
      "payment_period_name": "15 يوم",
      "period_in_days": 15,
      "latest_invoice_date": "2024-10-01",
      "expected_collection_date": "2024-10-16",
      "days_until_collection": -5,
      "outstanding_balance": "5000.00",
      "is_overdue": true,
      
      "penalty_percentage": "0.20",
      "penalty_amount": "50.00",
      "total_with_penalty": "5050.00",
      
      "cashback_percentage": "0.10",
      "cashback_amount": "0.00",
      "total_with_cashback": "5000.00"
    }
  ]
}
```

---

## 🎯 حالات الاستخدام

### 1. عرض المتأخرين اليوم
```bash
GET /finance/collection-schedule/?overdue_only=true
```

### 2. التحصيلات المتوقعة هذا الأسبوع
```bash
GET /finance/collection-schedule/?date_from=2024-10-11&date_to=2024-10-18
```

### 3. البحث عن عميل معين
```bash
GET /finance/collection-schedule/?search=صيدلية الشفاء
```

### 4. المتأخرين من عميل معين
```bash
GET /finance/collection-schedule/?search=محمد&overdue_only=true
```

### 5. تحصيلات شهر أكتوبر
```bash
GET /finance/collection-schedule/?date_from=2024-10-01&date_to=2024-10-31
```

---

## 📱 أمثلة JavaScript/TypeScript

### React/Next.js

```typescript
interface CollectionScheduleParams {
  search?: string;
  date_from?: string;
  date_to?: string;
  overdue_only?: boolean;
}

async function getCollectionSchedule(params: CollectionScheduleParams) {
  const url = new URL('/finance/collection-schedule/', 'http://129.212.140.152');
  
  if (params.search) {
    url.searchParams.append('search', params.search);
  }
  
  if (params.date_from) {
    url.searchParams.append('date_from', params.date_from);
  }
  
  if (params.date_to) {
    url.searchParams.append('date_to', params.date_to);
  }
  
  if (params.overdue_only) {
    url.searchParams.append('overdue_only', 'true');
  }
  
  const response = await fetch(url.toString(), {
    headers: {
      'Authorization': `Token ${token}`,
    },
  });
  
  return response.json();
}

// الاستخدام
// المتأخرين فقط
const overdue = await getCollectionSchedule({ overdue_only: true });

// البحث
const results = await getCollectionSchedule({ search: 'محمد' });

// نطاق تاريخ
const thisWeek = await getCollectionSchedule({
  date_from: '2024-10-11',
  date_to: '2024-10-18'
});

// دمج الفلاتر
const filtered = await getCollectionSchedule({
  search: 'صيدلية',
  overdue_only: true,
  date_from: '2024-10-01'
});
```

---

## 📋 حقول الاستجابة

| الحقل | النوع | الوصف |
|------|------|-------|
| `user_id` | Integer | معرف العميل |
| `customer_name` | String | اسم العميل |
| `username` | String | رقم الهاتف |
| `payment_period_name` | String | اسم فترة السداد |
| `period_in_days` | Integer | عدد أيام فترة السداد |
| `latest_invoice_date` | Date | تاريخ آخر فاتورة |
| `expected_collection_date` | Date | تاريخ التحصيل المتوقع |
| `days_until_collection` | Integer | أيام متبقية (سالب = متأخر) |
| `outstanding_balance` | Decimal | المبلغ المستحق |
| `is_overdue` | Boolean | هل متأخر؟ |
| `penalty_percentage` | Decimal | نسبة الغرامة اليومية |
| `penalty_amount` | Decimal | مبلغ الغرامة |
| `total_with_penalty` | Decimal | الإجمالي مع الغرامة |
| `cashback_percentage` | Decimal | نسبة الخصم للدفع المبكر |
| `cashback_amount` | Decimal | مبلغ الخصم |
| `total_with_cashback` | Decimal | الإجمالي مع الخصم |

---

## 🎨 UI Suggestions

### 1. عرض حالة التأخير
```javascript
function getStatusBadge(item) {
  if (item.is_overdue) {
    return <Badge color="red">متأخر {Math.abs(item.days_until_collection)} يوم</Badge>;
  } else if (item.days_until_collection <= 3) {
    return <Badge color="orange">مستعجل</Badge>;
  } else {
    return <Badge color="green">{item.days_until_collection} يوم</Badge>;
  }
}
```

### 2. عرض المبلغ المناسب
```javascript
function getDisplayAmount(item) {
  if (item.is_overdue) {
    return `${item.total_with_penalty} ج.م (شامل غرامة ${item.penalty_amount})`;
  } else if (item.days_until_collection > 0) {
    return `${item.total_with_cashback} ج.م (مع خصم ${item.cashback_amount})`;
  } else {
    return `${item.outstanding_balance} ج.م`;
  }
}
```

---

## ⚠️ ملاحظات مهمة

1. **الترتيب التلقائي**: النتائج مرتبة بـ:
   - المتأخرين أولاً
   - ثم حسب تاريخ التحصيل المتوقع

2. **الصلاحيات**:
   - **Sales**: يرى عملاءه فقط
   - **Manager**: يرى عملاء المندوبين تحته
   - **AreaManager**: يرى جميع عملاء المنطقة
   - **Admin**: يرى الكل

3. **الفلترة بالتاريخ**: تطبق على `expected_collection_date` فقط

4. **البحث**: غير حساس لحالة الأحرف (case-insensitive)

5. **العملاء المعروضين**: فقط من لديهم رصيد سالب (مديونين)

---

## 🚀 نصائح للأداء

1. **استخدم الفلاتر**: بدلاً من جلب كل البيانات وتصفيتها على الـ Frontend
2. **Cache النتائج**: للمدة المناسبة (مثلاً 5 دقائق)
3. **Pagination**: إذا كانت النتائج كبيرة (يمكن إضافتها لاحقاً)
4. **الفلاتر المتعددة**: استخدمها لتقليل حجم البيانات المرسلة

---

## 📞 للدعم

للاستفسارات أو الإبلاغ عن مشاكل، يرجى التواصل مع فريق التطوير.

**آخر تحديث**: 11 أكتوبر 2025

