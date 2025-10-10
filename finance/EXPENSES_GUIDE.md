# دليل نظام المصاريف
# Expenses System Guide

## 💸 نظام المصاريف الشهرية والنثرية

تم إضافة نظام كامل لتسجيل وتتبع المصاريف!

---

## 🎯 أنواع المصاريف

### 1️⃣ مصاريف شهرية (Monthly)

مصاريف ثابتة تتكرر كل شهر:

| الفئة | الكود | الوصف |
|-------|-------|-------|
| **مرتبات** | `salary` | رواتب الموظفين |
| **إيجار** | `rent` | إيجار المكان |
| **أرباح شركاء** | `profit_share` | أرباح للشركاء/المستثمرين |
| **مرافق** | `utilities` | كهرباء، مياه، غاز، إلخ |

---

### 2️⃣ مصاريف نثرية (Miscellaneous)

مصاريف متغيرة حسب الحاجة:

| الفئة | الكود | الوصف |
|-------|-------|-------|
| **قرطاسية** | `stationery` | ورق، دفاتر، أقلام |
| **صيانة** | `maintenance` | إصلاحات، صيانة |
| **مواصلات** | `transportation` | بنزين، مواصلات |
| **اتصالات** | `communication` | تليفون، إنترنت |
| **أخرى** | `other` | أي مصاريف أخرى |

---

## ➕ إضافة مصروف

### مصروف شهري (مرتب)

```http
POST http://129.212.140.152/finance/expenses/create/
{
  "type": "monthly",           // مصروف شهري
  "category": "salary",        // مرتب
  "amount": 5000,
  "description": "مرتب شهر أكتوبر",
  "recipient": "أحمد محمد - محاسب",
  "payment_method": "cash",
  "expense_date": "2025-10-01"
}
```

---

### مصروف شهري (إيجار)

```http
POST http://129.212.140.152/finance/expenses/create/
{
  "type": "monthly",
  "category": "rent",
  "amount": 10000,
  "description": "إيجار شهر أكتوبر",
  "recipient": "صاحب العقار",
  "payment_method": "cash",
  "expense_date": "2025-10-01"
}
```

---

### مصروف شهري (أرباح شركاء)

```http
POST http://129.212.140.152/finance/expenses/create/
{
  "type": "monthly",
  "category": "profit_share",
  "amount": 15000,
  "description": "أرباح شهر سبتمبر",
  "recipient": "محمد علي - شريك",
  "payment_method": "instapay",
  "expense_date": "2025-10-05"
}
```

---

### مصروف نثري (قرطاسية)

```http
POST http://129.212.140.152/finance/expenses/create/
{
  "type": "misc",
  "category": "stationery",
  "amount": 500,
  "description": "دفاتر وأقلام",
  "recipient": "مكتبة النور",
  "payment_method": "cash",
  "expense_date": "2025-10-08"
}
```

---

### مصروف نثري (صيانة)

```http
POST http://129.212.140.152/finance/expenses/create/
{
  "type": "misc",
  "category": "maintenance",
  "amount": 2000,
  "description": "إصلاح التكييف",
  "recipient": "ورشة الصيانة",
  "payment_method": "cash",
  "expense_date": "2025-10-10"
}
```

---

## 📋 عرض المصاريف

### جميع المصاريف

```http
GET http://129.212.140.152/finance/expenses/
```

**الاستجابة:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "type": "monthly",
      "type_label": "Monthly",
      "category": "salary",
      "category_label": "Salary",
      "amount": "5000.00",
      "description": "مرتب شهر أكتوبر",
      "recipient": "أحمد محمد - محاسب",
      "payment_method": "cash",
      "payment_method_label": "Cash",
      "expense_date": "2025-10-01",
      "created_at": "2025-10-01T08:00:00Z"
    }
  ]
}
```

---

## 🔍 الفلترة والبحث

### حسب النوع (شهرية/نثرية)

```http
# مصاريف شهرية فقط
GET /finance/expenses/?type=monthly

# مصاريف نثرية فقط
GET /finance/expenses/?type=misc
```

---

### حسب الفئة

```http
# المرتبات فقط
GET /finance/expenses/?category=salary

# الإيجارات فقط
GET /finance/expenses/?category=rent

# القرطاسية فقط
GET /finance/expenses/?category=stationery
```

---

### حسب الشهر

```http
# مصاريف شهر أكتوبر 2025
GET /finance/expenses/?month=10&year=2025

# مصاريف شهر سبتمبر 2025
GET /finance/expenses/?month=9&year=2025
```

---

### بحث في الوصف أو المستلم

```http
# بحث عن "أحمد"
GET /finance/expenses/?search=أحمد

# بحث عن "إصلاح"
GET /finance/expenses/?search=إصلاح
```

---

### الترتيب

```http
# حسب التاريخ (الأحدث أولاً)
GET /finance/expenses/?o=-expense_date

# حسب المبلغ (الأكبر أولاً)
GET /finance/expenses/?o=-amount

# حسب الفئة
GET /finance/expenses/?o=category
```

---

## 💰 التأثير على رأس المال

### قبل إضافة المصاريف

```http
GET /finance/safe/
```

```json
{
  "safe_total_amount": "125000.00",
  "credit_total_amount": "45000.00",
  "debt_total_amount": "20000.00",
  "inventory_total_amount": "85000.00",
  "total_amount": "235000.00"
}
```

**الحساب:**
```
235,000 = 125,000 + 45,000 + 85,000 - 20,000
```

---

### بعد إضافة مصاريف

```
سجلت مصاريف:
- مرتبات: 5,000
- إيجار: 10,000
- قرطاسية: 500
= 15,500 جنيه
```

```http
GET /finance/safe/
```

```json
{
  "safe_total_amount": "125000.00",
  "credit_total_amount": "45000.00",
  "debt_total_amount": "20000.00",
  "inventory_total_amount": "85000.00",
  "expenses_total_amount": "15500.00",      // ⬅️ جديد
  "total_amount": "219500.00"               // ⬅️ قل بمقدار المصاريف
}
```

**الحساب الجديد:**
```
رأس المال = كاش + ديون ليك + مخزون - ديون عليك - مصاريف

219,500 = 125,000 + 45,000 + 85,000 - 20,000 - 15,500  ✅
```

---

## 📊 تقارير المصاريف

### تقرير شهري

```http
GET /finance/expenses/?month=10&year=2025
```

**يعرض:**
- جميع مصاريف شهر أكتوبر 2025
- مجموعها التلقائي في `count`

---

### تقرير حسب النوع

```http
# المصاريف الشهرية
GET /finance/expenses/?type=monthly

# المصاريف النثرية
GET /finance/expenses/?type=misc
```

---

### تقرير المرتبات

```http
GET /finance/expenses/?category=salary&month=10&year=2025
```

مرتبات شهر أكتوبر

---

## 🔄 التحديث والحذف

### تعديل مصروف

```http
PUT /finance/expenses/{id}/change/
{
  "amount": 5500,
  "description": "مرتب أكتوبر (محدث)"
}
```

---

### حذف مصروف

```http
DELETE /finance/expenses/{id}/destroy/
```

---

## 📝 أمثلة جاهزة للاستخدام

### 1. تسجيل مرتبات شهر أكتوبر

```http
# الموظف الأول
POST /finance/expenses/create/
{
  "type": "monthly",
  "category": "salary",
  "amount": 5000,
  "recipient": "أحمد محمد",
  "payment_method": "cash",
  "expense_date": "2025-10-01"
}

# الموظف الثاني
POST /finance/expenses/create/
{
  "type": "monthly",
  "category": "salary",
  "amount": 4000,
  "recipient": "فاطمة علي",
  "payment_method": "instapay",
  "expense_date": "2025-10-01"
}
```

---

### 2. تسجيل إيجار الشهر

```http
POST /finance/expenses/create/
{
  "type": "monthly",
  "category": "rent",
  "amount": 10000,
  "recipient": "صاحب العقار",
  "payment_method": "cash",
  "expense_date": "2025-10-01"
}
```

---

### 3. تسجيل أرباح الشركاء

```http
POST /finance/expenses/create/
{
  "type": "monthly",
  "category": "profit_share",
  "amount": 20000,
  "description": "أرباح شهر سبتمبر",
  "recipient": "الشريك: محمد علي",
  "payment_method": "instapay",
  "expense_date": "2025-10-05"
}
```

---

### 4. تسجيل قرطاسية

```http
POST /finance/expenses/create/
{
  "type": "misc",
  "category": "stationery",
  "amount": 300,
  "description": "دفاتر وأقلام",
  "recipient": "مكتبة النور",
  "payment_method": "cash",
  "expense_date": "2025-10-08"
}
```

---

### 5. تقرير مصاريف الشهر

```http
GET /finance/expenses/?month=10&year=2025&o=-amount
```

كل مصاريف أكتوبر، مرتبة من الأكبر للأصغر

---

## 🎯 APIs المتاحة

| الطريقة | المسار | الوصف |
|---------|--------|-------|
| GET | `/finance/expenses/` | قائمة المصاريف |
| POST | `/finance/expenses/create/` | تسجيل مصروف |
| PUT | `/finance/expenses/{id}/change/` | تعديل مصروف |
| DELETE | `/finance/expenses/{id}/destroy/` | حذف مصروف |

---

## 📊 رأس المال مع المصاريف

```http
GET /finance/safe/
```

```json
{
  "safe_total_amount": "125000.00",        // الكاش
  "credit_total_amount": "45000.00",       // ليك
  "debt_total_amount": "20000.00",         // عليك
  "inventory_total_amount": "85000.00",    // المخزون
  "expenses_total_amount": "35500.00",     // ⬅️ المصاريف
  "total_amount": "199500.00"              // ⬅️ رأس المال النهائي
}
```

**المعادلة:**
```
199,500 = 125,000 + 45,000 + 85,000 - 20,000 - 35,500

رأس المال = كاش + ديون ليك + مخزون - ديون عليك - مصاريف
```

---

## 💡 حالات استخدام

### السيناريو 1: بداية الشهر

```http
# 1. تسجيل مرتبات
POST /finance/expenses/create/
{"type": "monthly", "category": "salary", "amount": 15000, ...}

# 2. تسجيل إيجار
POST /finance/expenses/create/
{"type": "monthly", "category": "rent", "amount": 10000, ...}

# 3. تسجيل أرباح شركاء
POST /finance/expenses/create/
{"type": "monthly", "category": "profit_share", "amount": 20000, ...}
```

**إجمالي المصاريف الشهرية:** 45,000 جنيه

---

### السيناريو 2: خلال الشهر

```http
# مصاريف نثرية متفرقة
POST /finance/expenses/create/
{"type": "misc", "category": "stationery", "amount": 300, ...}

POST /finance/expenses/create/
{"type": "misc", "category": "maintenance", "amount": 1500, ...}

POST /finance/expenses/create/
{"type": "misc", "category": "other", "amount": 500, ...}
```

**إجمالي المصاريف النثرية:** 2,300 جنيه

---

### السيناريو 3: تقرير نهاية الشهر

```http
GET /finance/expenses/?month=10&year=2025
```

**النتيجة:**
- إجمالي المصاريف: 47,300 جنيه
  - شهرية: 45,000 جنيه
  - نثرية: 2,300 جنيه

---

## 🎨 طرق الدفع

| الطريقة | متى تستخدم |
|---------|-----------|
| `cash` | دفع كاش → يخصم من الخزنة |
| `instapay` | تحويل بنكي |
| `wallet` | محفظة إلكترونية |
| `product` | مقايضة بمنتجات |

---

## ✅ الميزات

1. **تسجيل تلقائي للمصاريف**
2. **يحسب في رأس المال**
3. **تقارير شهرية**
4. **فلترة حسب النوع والفئة**
5. **بحث في الوصف والمستلم**
6. **تتبع طريقة الدفع**

---

## 📱 مثال JavaScript

```javascript
// تسجيل مرتب
const addSalary = async () => {
  await fetch('http://129.212.140.152/finance/expenses/create/', {
    method: 'POST',
    headers: {
      'Authorization': 'Token your-token',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      type: 'monthly',
      category: 'salary',
      amount: 5000,
      description: 'مرتب أكتوبر',
      recipient: 'أحمد محمد',
      payment_method: 'cash',
      expense_date: '2025-10-01'
    })
  });
};

// عرض مصاريف الشهر
const getMonthExpenses = async (month, year) => {
  const response = await fetch(
    `http://129.212.140.152/finance/expenses/?month=${month}&year=${year}`,
    {
      headers: {'Authorization': 'Token your-token'}
    }
  );
  const data = await response.json();
  
  // حساب الإجمالي
  const total = data.results.reduce((sum, exp) => sum + parseFloat(exp.amount), 0);
  console.log(`إجمالي مصاريف ${month}/${year}: ${total} جنيه`);
};
```

---

## 🎯 خلاصة سريعة

### إضافة مصروف:
```http
POST /finance/expenses/create/
{
  "type": "monthly" أو "misc",
  "category": "salary/rent/stationery/other",
  "amount": 5000,
  "recipient": "الاسم",
  "payment_method": "cash",
  "expense_date": "2025-10-10"
}
```

### عرض رأس المال:
```http
GET /finance/safe/
```

سترى المصاريف مخصومة من `total_amount` ✅

---

**آخر تحديث**: 2025-10-10  
**الإصدار**: 2.0.0  
**الحالة**: ✅ جاهز ويعمل

