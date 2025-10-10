# الخزنة ورأس المال - ملخص سريع
# Safe & Capital - Quick Summary

## 🎯 كل اللي تحتاجه في API واحد!

```http
GET http://129.212.140.152/finance/safe/
```

## 📊 الاستجابة

```json
{
  "safe_total_amount": "125000.00",      // 💵 الكاش في الخزنة
  "credit_total_amount": "45000.00",     // 💰 الفلوس اللي ليك
  "debt_total_amount": "20000.00",       // 💸 الفلوس اللي عليك
  "inventory_total_amount": "85000.00",  // 📦 تكلفة المخزون
  "expenses_total_amount": "35500.00",   // 💸 المصاريف (جديد)
  "total_amount": "199500.00"            // 💎 إجمالي رأس المال
}
```

---

## ➕ إضافة كاش للخزنة

```http
POST http://129.212.140.152/finance/safe-transactions/create/
{
  "type": "d",       // d = Deposit (إيداع)
  "amount": 50000
}
```

---

## ➖ سحب كاش من الخزنة

```http
POST http://129.212.140.152/finance/safe-transactions/create/
{
  "type": "w",       // w = Withdrawal (سحب)
  "amount": 10000
}
```

---

## 💰 تسجيل دفعة من صيدلية (كاش)

```http
POST http://129.212.140.152/finance/sale-payments/create/
{
  "user": 5,
  "method": "cash",
  "amount": 5000,
  "at": "2025-10-10"
}
```

**يحدث تلقائياً:**
- ✅ الكاش في الخزنة += 5,000
- ✅ دين الصيدلية -= 5,000

---

## 💸 تسجيل دفعة لمورد (كاش)

```http
POST http://129.212.140.152/finance/purchase-payments/create/
{
  "user": 3,
  "method": "cash",
  "amount": 10000,
  "at": "2025-10-10"
}
```

**يحدث تلقائياً:**
- ✅ الكاش في الخزنة -= 10,000
- ✅ دينك للمورد -= 10,000

---

## 📈 المعادلة

```
رأس المال = الكاش + الديون ليك + المخزون - الديون عليك - المصاريف

199,500 = 125,000 + 45,000 + 85,000 - 20,000 - 35,500  ✅
```

---

## 💸 تسجيل المصاريف (جديد!)

### مصروف شهري (مرتب)

```http
POST http://129.212.140.152/finance/expenses/create/
{
  "type": "monthly",
  "category": "salary",
  "amount": 5000,
  "recipient": "أحمد محمد",
  "payment_method": "cash",
  "expense_date": "2025-10-01"
}
```

### مصروف نثري (قرطاسية)

```http
POST http://129.212.140.152/finance/expenses/create/
{
  "type": "misc",
  "category": "stationery",
  "amount": 500,
  "recipient": "مكتبة النور",
  "payment_method": "cash",
  "expense_date": "2025-10-10"
}
```

### عرض المصاريف

```http
GET http://129.212.140.152/finance/expenses/?month=10&year=2025
```

---

## 🔄 التحديث التلقائي

الخزنة تتحدث تلقائياً عند:
- ✅ إيداع/سحب
- ✅ دفعات البيع (كاش)
- ✅ دفعات الشراء (كاش)

---

## 📚 التفاصيل الكاملة

راجع:
- [finance/SAFE_GUIDE.md](./finance/SAFE_GUIDE.md) - دليل شامل
- [FINANCE_QUICK_SUMMARY.md](./FINANCE_QUICK_SUMMARY.md) - شرح النظام المالي

---

**جاهز ويعمل الآن!** 💰✨

