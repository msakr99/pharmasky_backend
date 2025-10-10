# نظام الغرامة والكاش باك - ملخص سريع
# Penalty & Cashback System - Quick Summary

---

## 🎯 الفكرة

تشجيع الدفع المبكر ومعاقبة التأخير:

```
🔴 متأخر → غرامة 0.20% يومياً
⚪ في الموعد → لا شيء
🟢 مبكر → كاش باك 0.10% يومياً
```

---

## 🔴 الغرامة (Penalty)

### الحساب

```
غرامة = المبلغ × 0.20% × عدد أيام التأخير
```

### مثال

```
8,000 ج × 0.20% × 2 يوم = 32 ج غرامة
الإجمالي = 8,032 ج
```

---

## 🟢 الكاش باك (Cashback)

### الحساب

```
كاش باك = المبلغ × 0.10% × عدد الأيام قبل الموعد
```

### مثال

```
15,000 ج × 0.10% × 5 أيام = 75 ج كاش باك
الإجمالي = 14,925 ج
```

---

## 📊 في الـ API

```http
GET http://129.212.140.152/finance/collection-schedule/
```

**الاستجابة:**
```json
{
  "outstanding_balance": "8000.00",
  "days_until_collection": -2,
  "is_overdue": true,
  
  "penalty_amount": "32.00",
  "total_with_penalty": "8032.00",
  
  "cashback_amount": "0.00",
  "total_with_cashback": "8000.00"
}
```

---

## ⚙️ التخصيص

في البروفايل:
- `late_payment_penalty_percentage` = 0.20
- `early_payment_cashback_percentage` = 0.10

---

## 📖 للتفاصيل

**الدليل الشامل:** [PENALTY_CASHBACK_GUIDE.md](./PENALTY_CASHBACK_GUIDE.md)

---

**آخر تحديث**: 2025-10-10  
**الحالة**: ✅ جاهز

