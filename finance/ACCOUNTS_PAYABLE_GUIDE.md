# 💰 دليل استخدام قائمة الحسابات الدائنة (Accounts Payable)

## نظرة عامة

Endpoint مخصص لعرض قائمة بجميع الموردين/المتاجر اللي الشركة مديونة لهم (الفلوس اللي علينا).

---

## 🔗 Endpoint

```
GET /finance/accounts-payable/
```

**الصلاحيات**: Manager فقط

---

## 📊 البيانات المعروضة

يعرض جميع الحسابات ذات الرصيد الموجب (`balance > 0`) أي الشركة مديونة لهم.

---

## 🔍 الفلاتر والبحث

### 1. البحث باسم المورد أو رقم الهاتف

```bash
GET /finance/accounts-payable/?search=شركة الأدوية
GET /finance/accounts-payable/?search=01234567890
GET /finance/accounts-payable/?search=united
```

**يبحث في**:
- `name`: الاسم بالعربي
- `e_name`: الاسم بالإنجليزي  
- `username`: رقم الهاتف

---

### 2. فلتر حسب نوع المستخدم (Role)

```bash
# المتاجر فقط
GET /finance/accounts-payable/?role=STORE

# Sales فقط
GET /finance/accounts-payable/?role=SALES

# الموردين (أي نوع)
GET /finance/accounts-payable/?role=SUPPLIER
```

**الأنواع المتاحة**:
- `STORE`: متاجر
- `SALES`: مندوبين مبيعات
- `PHARMACY`: صيدليات
- `DELIVERY`: مندوبي توصيل
- `MANAGER`: مديرين
- `AREA_MANAGER`: مديري مناطق

---

### 3. فلتر حسب الحد الأدنى للمبلغ

```bash
# الديون أكبر من 10000
GET /finance/accounts-payable/?min_amount=10000

# الديون أكبر من 50000
GET /finance/accounts-payable/?min_amount=50000
```

---

### 4. دمج الفلاتر

```bash
# المتاجر فقط مع بحث
GET /finance/accounts-payable/?role=STORE&search=الأدوية

# المبالغ الكبيرة فقط
GET /finance/accounts-payable/?min_amount=20000&role=STORE

# كل الفلاتر معاً
GET /finance/accounts-payable/?search=شركة&role=STORE&min_amount=5000
```

---

## 📊 Response Structure

```json
{
  "count": 15,
  "total_payable_amount": "250000.00",
  "results": [
    {
      "user_id": 45,
      "supplier_name": "شركة الأدوية المتحدة",
      "username": "+201234567890",
      "role": "STORE",
      "role_label": "متجر",
      "amount_owed": "85000.00",
      "last_payment_date": "2024-10-01T10:30:00Z",
      "last_purchase_date": "2024-10-10T14:20:00Z",
      "days_since_last_payment": 10
    },
    {
      "user_id": 78,
      "supplier_name": "شركة النور للتوزيع",
      "username": "+209876543210",
      "role": "STORE",
      "role_label": "متجر",
      "amount_owed": "65000.00",
      "last_payment_date": "2024-09-25T09:15:00Z",
      "last_purchase_date": "2024-10-08T16:45:00Z",
      "days_since_last_payment": 16
    }
  ]
}
```

---

## 🎯 حالات الاستخدام

### 1. عرض جميع الديون
```bash
GET /finance/accounts-payable/
```

### 2. الديون الكبيرة فقط (أكثر من 50000)
```bash
GET /finance/accounts-payable/?min_amount=50000
```

### 3. البحث عن مورد معين
```bash
GET /finance/accounts-payable/?search=شركة الأدوية
```

### 4. المتاجر التي علينا فلوس لها
```bash
GET /finance/accounts-payable/?role=STORE
```

### 5. الديون الكبيرة للمتاجر
```bash
GET /finance/accounts-payable/?role=STORE&min_amount=30000
```

---

## 📱 أمثلة JavaScript/TypeScript

### React/Next.js

```typescript
interface AccountsPayableParams {
  search?: string;
  role?: string;
  min_amount?: number;
}

async function getAccountsPayable(params: AccountsPayableParams) {
  const url = new URL('/finance/accounts-payable/', 'http://129.212.140.152');
  
  if (params.search) {
    url.searchParams.append('search', params.search);
  }
  
  if (params.role) {
    url.searchParams.append('role', params.role);
  }
  
  if (params.min_amount) {
    url.searchParams.append('min_amount', params.min_amount.toString());
  }
  
  const response = await fetch(url.toString(), {
    headers: {
      'Authorization': `Token ${token}`,
    },
  });
  
  return response.json();
}

// الاستخدام
// جميع الديون
const all = await getAccountsPayable({});

// الديون الكبيرة
const large = await getAccountsPayable({ min_amount: 50000 });

// المتاجر فقط
const stores = await getAccountsPayable({ role: 'STORE' });

// بحث مع فلتر
const filtered = await getAccountsPayable({
  search: 'الأدوية',
  role: 'STORE',
  min_amount: 10000
});
```

---

## 📋 حقول الاستجابة

| الحقل | النوع | الوصف |
|------|------|-------|
| `user_id` | Integer | معرف المورد/المتجر |
| `supplier_name` | String | اسم المورد |
| `username` | String | رقم الهاتف |
| `role` | String | نوع المستخدم (CODE) |
| `role_label` | String | نوع المستخدم (بالعربي) |
| `amount_owed` | Decimal | المبلغ المستحق له |
| `last_payment_date` | DateTime | تاريخ آخر دفعة |
| `last_purchase_date` | DateTime | تاريخ آخر عملية شراء |
| `days_since_last_payment` | Integer | عدد الأيام منذ آخر دفعة |

---

## 🎨 UI Suggestions

### 1. عرض حالة التأخير
```javascript
function getPaymentStatusBadge(item) {
  if (!item.last_payment_date) {
    return <Badge color="red">لم يتم الدفع</Badge>;
  } else if (item.days_since_last_payment > 30) {
    return <Badge color="orange">متأخر {item.days_since_last_payment} يوم</Badge>;
  } else {
    return <Badge color="green">آخر دفعة منذ {item.days_since_last_payment} يوم</Badge>;
  }
}
```

### 2. ترتيب حسب الأولوية
```javascript
function sortByPriority(payables) {
  return payables.sort((a, b) => {
    // الأولوية للمبالغ الكبيرة
    return b.amount_owed - a.amount_owed;
  });
}
```

### 3. عرض إحصائيات سريعة
```javascript
function getPayableStats(data) {
  return {
    totalAmount: data.total_payable_amount,
    count: data.count,
    averageAmount: data.total_payable_amount / data.count,
    largestDebt: Math.max(...data.results.map(r => r.amount_owed)),
  };
}
```

---

## 📊 مقارنة مع Collection Schedule

| الميزة | Accounts Payable | Collection Schedule |
|--------|------------------|---------------------|
| **الهدف** | الفلوس اللي علينا | الفلوس اللي لينا |
| **Balance** | موجب (> 0) | سالب (< 0) |
| **المستخدمين** | متاجر/موردين | صيدليات |
| **الصلاحية** | Manager فقط | Staff (Sales/Manager/AreaManager) |
| **الترتيب** | حسب المبلغ (تنازلي) | حسب التأخير ثم التاريخ |

---

## ⚠️ ملاحظات مهمة

1. **الترتيب التلقائي**: النتائج مرتبة حسب المبلغ المستحق (الأكبر أولاً)

2. **الصلاحيات**: متاح للـ Manager فقط

3. **الرصيد الموجب**: يعني الشركة مديونة للمورد (علينا فلوس له)

4. **آخر دفعة**: من جدول `PurchasePayment`

5. **آخر شراء**: من جدول `PurchaseInvoice`

---

## 🔄 سير العمل المقترح

### 1. عرض الديون
```
GET /finance/accounts-payable/
```

### 2. اختيار مورد للدفع
```
المستخدم يختار مورد من القائمة
```

### 3. إنشاء دفعة
```
POST /finance/purchase-payments/create/
{
  "user": 45,
  "amount": 10000,
  "method": "BANK_TRANSFER",
  "at": "2024-10-11"
}
```

### 4. تحديث القائمة
```
GET /finance/accounts-payable/
// الرصيد تم تحديثه تلقائياً
```

---

## 💡 نصائح

1. **راقب الديون الكبيرة**: استخدم `min_amount` لمراقبة الديون الكبيرة
2. **تابع المتاجر**: استخدم `role=STORE` للتركيز على المتاجر
3. **جدول الدفع**: راجع `days_since_last_payment` لتحديد أولويات الدفع
4. **البحث السريع**: استخدم البحث للوصول السريع لمورد معين

---

## 📞 للدعم

للاستفسارات أو الإبلاغ عن مشاكل، يرجى التواصل مع فريق التطوير.

**آخر تحديث**: 11 أكتوبر 2025

