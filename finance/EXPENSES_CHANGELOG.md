# سجل التحديثات - نظام المصاريف
# Expenses System Changelog

## 📅 التاريخ: 2025-10-10 | الإصدار: 2.0.0

### ✨ ميزة جديدة كاملة: نظام المصاريف

تم إضافة نظام كامل لتسجيل وتتبع المصاريف الشهرية والنثرية!

---

## 🆕 ما تم إضافته

### 1️⃣ نموذج جديد: `Expense`

**الحقول:**
- `type` - نوع المصروف (شهري/نثري)
- `category` - الفئة (مرتب، إيجار، قرطاسية، إلخ)
- `amount` - المبلغ
- `description` - الوصف
- `recipient` - المستلم
- `payment_method` - طريقة الدفع
- `expense_date` - تاريخ المصروف

---

### 2️⃣ أنواع المصاريف

#### مصاريف شهرية:
- ✅ مرتبات (`salary`)
- ✅ إيجارات (`rent`)
- ✅ أرباح شركاء (`profit_share`)
- ✅ مرافق (`utilities`)

#### مصاريف نثرية:
- ✅ قرطاسية (`stationery`)
- ✅ صيانة (`maintenance`)
- ✅ مواصلات (`transportation`)
- ✅ اتصالات (`communication`)
- ✅ أخرى (`other`)

---

### 3️⃣ APIs جديدة

| الطريقة | المسار | الوصف |
|---------|--------|-------|
| GET | `/finance/expenses/` | قائمة المصاريف |
| POST | `/finance/expenses/create/` | تسجيل مصروف |
| PUT | `/finance/expenses/{id}/change/` | تعديل مصروف |
| DELETE | `/finance/expenses/{id}/destroy/` | حذف مصروف |

---

### 4️⃣ فلترة متقدمة

```http
# حسب النوع
?type=monthly

# حسب الفئة
?category=salary

# حسب الشهر
?month=10&year=2025

# بحث
?search=أحمد
```

---

### 5️⃣ تحديث حساب رأس المال

تم تحديث `/finance/safe/` لتشمل المصاريف:

**قبل:**
```json
{
  "total_amount": "235000.00"
}
```

**بعد:**
```json
{
  "expenses_total_amount": "35500.00",  // جديد
  "total_amount": "199500.00"           // محدث
}
```

**المعادلة الجديدة:**
```
total_amount = safe + credit + inventory - debt - expenses
```

---

## 📁 الملفات المضافة/المعدلة

### ملفات جديدة:
- ✅ `finance/expense_choices.py` - خيارات المصاريف
- ✅ `finance/migrations/0004_expense.py` - Migration
- ✅ `finance/EXPENSES_GUIDE.md` - دليل شامل
- ✅ `EXPENSES_QUICK.md` - ملخص سريع

### ملفات معدلة:
- ✅ `finance/models.py` - إضافة Expense model
- ✅ `finance/serializers.py` - إضافة ExpenseSerializer + تحديث SafeSerializer
- ✅ `finance/views.py` - إضافة Expense views + تحديث SafeRetrieveAPIView
- ✅ `finance/urls.py` - إضافة URLs المصاريف
- ✅ `finance/admin.py` - إضافة Expense admin
- ✅ `SAFE_QUICK.md` - تحديث مع المصاريف

---

## 🎯 الفوائد

### 1. تتبع دقيق للمصاريف
```
- مرتبات الموظفين
- الإيجارات
- أرباح الشركاء
- المصاريف النثرية
```

### 2. تقارير شهرية
```
GET /finance/expenses/?month=10&year=2025

→ جميع مصاريف أكتوبر
```

### 3. تأثير على رأس المال
```
رأس المال يُحسب بعد خصم المصاريف تلقائياً
```

### 4. فئات منظمة
```
9 فئات مختلفة للمصاريف
فلترة سهلة وسريعة
```

---

## 📱 مثال استخدام

### تسجيل مصاريف شهر أكتوبر

```http
# 1. مرتبات (15,000)
POST /finance/expenses/create/
{"type": "monthly", "category": "salary", "amount": 15000, ...}

# 2. إيجار (10,000)
POST /finance/expenses/create/
{"type": "monthly", "category": "rent", "amount": 10000, ...}

# 3. أرباح (20,000)
POST /finance/expenses/create/
{"type": "monthly", "category": "profit_share", "amount": 20000, ...}

# 4. قرطاسية (500)
POST /finance/expenses/create/
{"type": "misc", "category": "stationery", "amount": 500, ...}

إجمالي: 45,500 جنيه
```

### عرض رأس المال

```http
GET /finance/safe/

→ {
  "expenses_total_amount": "45500.00",
  "total_amount": "189500.00"  // انخفض بمقدار المصاريف
}
```

---

## 🚀 الخطوات المطلوبة

### على الخادم البعيد:

```bash
# 1. سحب التحديثات
git pull origin main

# 2. تشغيل Migration
python manage.py migrate

# 3. إعادة تشغيل Django
sudo systemctl restart gunicorn
```

---

## 📚 التوثيق

- [EXPENSES_GUIDE.md](./finance/EXPENSES_GUIDE.md) - دليل شامل
- [EXPENSES_QUICK.md](./EXPENSES_QUICK.md) - ملخص سريع
- [SAFE_QUICK.md](./SAFE_QUICK.md) - تحديث مع المصاريف

---

**آخر تحديث**: 2025-10-10  
**الإصدار**: 2.0.0  
**الحالة**: ✅ جاهز - يحتاج migration

