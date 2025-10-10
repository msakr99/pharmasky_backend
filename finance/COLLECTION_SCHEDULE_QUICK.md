# جدول مواعيد التحصيلات - مرجع سريع
# Collection Schedule API - Quick Reference

---

## ⚡ الاستخدام السريع

```http
GET http://129.212.140.152/finance/collection-schedule/
Authorization: Token your-token-here
```

---

## 📊 الاستجابة

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
    }
  ]
}
```

---

## 🔑 الحقول المهمة

| الحقل | الوصف |
|------|-------|
| `customer_name` | اسم الصيدلية |
| `expected_collection_date` | تاريخ التحصيل المتوقع |
| `days_until_collection` | الأيام المتبقية (سالب = متأخر) |
| `outstanding_balance` | المبلغ المستحق |
| `is_overdue` | هل متأخر؟ |
| `payment_period_name` | اسم الشريحة |
| **`penalty_amount`** | **مبلغ الغرامة (للمتأخرين)** |
| **`total_with_penalty`** | **الإجمالي مع الغرامة** |
| **`cashback_amount`** | **مبلغ الكاش باك (للمبكرين)** |
| **`total_with_cashback`** | **الإجمالي بعد الكاش باك** |

---

## 💰 الغرامة والكاش باك

### 🔴 متأخر؟
```
غرامة = المبلغ × 0.20% × عدد أيام التأخير
```
**مثال:** 8,000 ج × 0.20% × 2 يوم = 32 ج غرامة

---

### 🟢 مبكر؟
```
كاش باك = المبلغ × 0.10% × عدد الأيام قبل الموعد
```
**مثال:** 15,000 ج × 0.10% × 5 أيام = 75 ج كاش باك

---

## 📋 الترتيب

القائمة مرتبة تلقائياً:
1. **المتأخرون أولاً** ⬅️
2. **الأقرب موعداً** ⬅️

---

## 🎯 الفلترة السريعة

### المتأخرون

```javascript
const overdue = results.filter(item => item.is_overdue);
```

---

### موعدهم اليوم

```javascript
const today = results.filter(item => item.days_until_collection === 0);
```

---

### الأولوية العالية (اليوم أو غداً)

```javascript
const urgent = results.filter(item => 
  item.days_until_collection >= -999 && item.days_until_collection <= 1
);
```

---

### هذا الأسبوع

```javascript
const thisWeek = results.filter(item => 
  item.days_until_collection >= 0 && item.days_until_collection <= 7
);
```

---

## 💡 أمثلة سريعة

### Python

```python
import requests

url = "http://129.212.140.152/finance/collection-schedule/"
headers = {"Authorization": "Token xxx"}
data = requests.get(url, headers=headers).json()

# المتأخرون
overdue = [i for i in data['results'] if i['is_overdue']]
print(f"المتأخرون: {len(overdue)}")
```

---

### JavaScript

```javascript
fetch('http://129.212.140.152/finance/collection-schedule/', {
  headers: {'Authorization': 'Token xxx'}
})
.then(r => r.json())
.then(data => {
  const overdue = data.results.filter(i => i.is_overdue);
  console.log(`Overdue: ${overdue.length}`);
});
```

---

## 📊 تحليل سريع

```javascript
const stats = {
  total: data.count,
  amount: data.total_outstanding_amount,
  overdue: data.results.filter(i => i.is_overdue).length,
  today: data.results.filter(i => i.days_until_collection === 0).length,
  thisWeek: data.results.filter(i => i.days_until_collection <= 7).length,
};
```

---

## 🎨 عرض بسيط

```
═══════════════════════════════════════════
      جدول مواعيد التحصيلات
═══════════════════════════════════════════

الإجمالي: 45,000 ج | العدد: 3

🔴 متأخر:
   - صيدلية الشفاء: 8,000 ج (متأخر 2 يوم)

🟡 اليوم:
   - صيدلية الأمل: 22,000 ج
   - صيدلية النور: 15,000 ج
```

---

## ✅ سير العمل السريع

```
1. GET /finance/collection-schedule/
   ↓
2. رتّب حسب is_overdue و days_until_collection
   ↓
3. ابدأ بالمتأخرين (is_overdue = true)
   ↓
4. اتصل بالصيدليات
   ↓
5. POST /finance/sale-payments/create/
```

---

## 📞 للتفاصيل الكاملة

**الدليل الشامل:** [COLLECTION_SCHEDULE_API.md](./COLLECTION_SCHEDULE_API.md)

---

**آخر تحديث**: 2025-10-10  
**الحالة**: ✅ جاهز

