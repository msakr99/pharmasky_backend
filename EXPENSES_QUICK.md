# المصاريف - ملخص سريع
# Expenses - Quick Summary

## ➕ إضافة مصروف

```http
POST http://129.212.140.152/finance/expenses/create/
{
  "type": "monthly",           // أو "misc"
  "category": "salary",        // الفئة
  "amount": 5000,
  "description": "مرتب أكتوبر",
  "recipient": "أحمد محمد",
  "payment_method": "cash",
  "expense_date": "2025-10-01"
}
```

---

## 📋 الفئات المتاحة

### مصاريف شهرية (`type: "monthly"`)

| الفئة | الكود |
|-------|-------|
| مرتبات | `salary` |
| إيجار | `rent` |
| أرباح شركاء | `profit_share` |
| مرافق | `utilities` |

### مصاريف نثرية (`type: "misc"`)

| الفئة | الكود |
|-------|-------|
| قرطاسية | `stationery` |
| صيانة | `maintenance` |
| مواصلات | `transportation` |
| اتصالات | `communication` |
| أخرى | `other` |

---

## 📊 عرض المصاريف

```http
# كل المصاريف
GET /finance/expenses/

# مصاريف شهر أكتوبر
GET /finance/expenses/?month=10&year=2025

# المصاريف الشهرية فقط
GET /finance/expenses/?type=monthly

# المرتبات فقط
GET /finance/expenses/?category=salary
```

---

## 💰 رأس المال مع المصاريف

```http
GET /finance/safe/
```

```json
{
  "safe_total_amount": "125000.00",
  "credit_total_amount": "45000.00",
  "debt_total_amount": "20000.00",
  "inventory_total_amount": "85000.00",
  "expenses_total_amount": "35500.00",    // ⬅️ المصاريف
  "total_amount": "199500.00"             // ⬅️ رأس المال بعد المصاريف
}
```

**المعادلة:**
```
رأس المال = كاش + ديون ليك + مخزون - ديون عليك - مصاريف
199,500 = 125,000 + 45,000 + 85,000 - 20,000 - 35,500
```

---

## 🎯 أمثلة سريعة

```http
# مرتب
POST /finance/expenses/create/
{"type": "monthly", "category": "salary", "amount": 5000, "recipient": "أحمد", "payment_method": "cash", "expense_date": "2025-10-01"}

# إيجار
POST /finance/expenses/create/
{"type": "monthly", "category": "rent", "amount": 10000, "recipient": "المالك", "payment_method": "cash", "expense_date": "2025-10-01"}

# أرباح
POST /finance/expenses/create/
{"type": "monthly", "category": "profit_share", "amount": 15000, "recipient": "الشريك", "payment_method": "instapay", "expense_date": "2025-10-05"}

# قرطاسية
POST /finance/expenses/create/
{"type": "misc", "category": "stationery", "amount": 500, "payment_method": "cash", "expense_date": "2025-10-10"}
```

---

**للتفاصيل**: راجع [finance/EXPENSES_GUIDE.md](./finance/EXPENSES_GUIDE.md)

---

**آخر تحديث**: 2025-10-10

