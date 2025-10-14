# ملخص حسابي المالي - My Account Summary

## ✅ الحل الجديد للصيدليات!

### URL الجديد:
```
GET /finance/my-account-summary/
```

**الصلاحية:** ✅ جميع المستخدمين المسجلين (`IsAuthenticated`)
- ✅ **PHARMACY** - الصيدليات ✓
- ✅ **STORE** - المخازن ✓
- ✅ **SALES** - المبيعات ✓
- ✅ **MANAGER** - المديرين ✓
- ✅ **أي مستخدم مسجل** ✓

---

## 🎯 الفرق بين الـ Endpoints

| Feature | `/finance/user-financial-summary/` | `/finance/my-account-summary/` ✓ |
|---------|-----------------------------------|----------------------------------|
| الصلاحية | ❌ Staff فقط | ✅ الكل |
| للصيدليات | ❌ ممنوع | ✅ متاح |
| يعرض | جميع المستخدمين | المستخدم الحالي فقط |
| معلومات الحساب | ❌ | ✅ |
| آخر المعاملات | ❌ | ✅ (آخر 10) |
| المدفوعات | ✅ | ✅ |
| فترة مخصصة | ✅ | ✅ (افتراضي 30 يوم) |

---

## 📋 الاستخدام

### Request Example

```bash
GET /finance/my-account-summary/
Authorization: Token {your_token}

# اختياري: حدد عدد الأيام
GET /finance/my-account-summary/?days=7     # آخر 7 أيام
GET /finance/my-account-summary/?days=90    # آخر 90 يوم
```

### Query Parameters (اختياري)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | Integer | 30 | عدد الأيام للإحصائيات |

---

## 📊 Response Example

```json
{
  "user": {
    "id": 123,
    "name": "صيدلية النور",
    "username": "+201234567890",
    "role": "PHARMACY"
  },
  "account": {
    "id": 456,
    "balance": 5000.00,
    "credit_limit": 10000.00,
    "remaining_credit": 5000.00
  },
  "period_summary": {
    "days": 30,
    "from_date": "2024-09-14",
    "to_date": "2025-10-14",
    "total_payments_made": 15000.00,
    "payments_count": 10,
    "total_payments_received": 12000.00,
    "receipts_count": 8
  },
  "recent_transactions": [
    {
      "id": 789,
      "transaction_type": "payment",
      "amount": 1000.00,
      "balance_after": 5000.00,
      "description": "دفعة نقدية",
      "at": "2025-10-13T14:30:00Z"
    },
    {
      "id": 788,
      "transaction_type": "invoice",
      "amount": 2000.00,
      "balance_after": 6000.00,
      "description": "فاتورة #INV-2025-123",
      "at": "2025-10-12T10:00:00Z"
    }
  ]
}
```

---

## 🔍 شرح الحقول

### User (معلومات المستخدم)
- `id`: معرف المستخدم
- `name`: الاسم
- `username`: رقم الهاتف
- `role`: الدور (PHARMACY, STORE, etc.)

### Account (معلومات الحساب)
- `balance`: الرصيد الحالي (موجب = لك، سالب = عليك)
- `credit_limit`: حد الائتمان المسموح
- `remaining_credit`: الائتمان المتبقي المتاح

### Period Summary (ملخص الفترة)
- `days`: عدد الأيام المحسوبة
- `from_date`: من تاريخ
- `to_date`: إلى تاريخ
- `total_payments_made`: إجمالي المدفوعات اللي دفعتها في الفترة
- `payments_count`: عدد المدفوعات
- `total_payments_received`: إجمالي المقبوضات اللي استلمتها
- `receipts_count`: عدد المقبوضات

### Recent Transactions (آخر المعاملات)
- آخر 10 معاملات على الحساب
- `transaction_type`: نوع المعاملة (invoice, payment, return, etc.)
- `amount`: المبلغ
- `balance_after`: الرصيد بعد المعاملة
- `description`: الوصف
- `at`: تاريخ ووقت المعاملة

---

## 🔥 أمثلة عملية

### مثال 1: صيدلية تشوف ملخص حسابها

```bash
# 1. تسجيل دخول
curl -X POST http://129.212.140.152/accounts/pharmacy-login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "+201234567890",
    "password": "YourPassword123"
  }'

# Response: {"token": "abc123xyz...", "role": "PHARMACY"}

# 2. جيب ملخص الحساب
curl -X GET http://129.212.140.152/finance/my-account-summary/ \
  -H "Authorization: Token abc123xyz..."

# ✅ Response: ملخص كامل للحساب
```

### مثال 2: صيدلية تشوف آخر 7 أيام فقط

```bash
curl -X GET "http://129.212.140.152/finance/my-account-summary/?days=7" \
  -H "Authorization: Token abc123xyz..."

# Response: ملخص آخر 7 أيام
```

### مثال 3: صيدلية تشوف آخر 90 يوم

```bash
curl -X GET "http://129.212.140.152/finance/my-account-summary/?days=90" \
  -H "Authorization: Token abc123xyz..."

# Response: ملخص آخر 3 أشهر
```

---

## 💻 أمثلة بالكود

### Python Example

```python
import requests

# 1. تسجيل دخول
login_response = requests.post(
    'http://129.212.140.152/accounts/pharmacy-login/',
    json={
        'username': '+201234567890',
        'password': 'YourPassword123'
    }
)

token = login_response.json()['token']
headers = {'Authorization': f'Token {token}'}

# 2. جيب ملخص الحساب
summary_response = requests.get(
    'http://129.212.140.152/finance/my-account-summary/',
    headers=headers
)

summary = summary_response.json()

# 3. اعرض المعلومات
print(f"الرصيد الحالي: {summary['account']['balance']} جنيه")
print(f"حد الائتمان: {summary['account']['credit_limit']} جنيه")
print(f"الائتمان المتبقي: {summary['account']['remaining_credit']} جنيه")
print(f"المدفوعات آخر 30 يوم: {summary['period_summary']['total_payments_made']} جنيه")
print(f"عدد المدفوعات: {summary['period_summary']['payments_count']}")

print("\nآخر المعاملات:")
for transaction in summary['recent_transactions'][:5]:
    print(f"  - {transaction['description']}: {transaction['amount']} جنيه")
```

### JavaScript Example

```javascript
// 1. تسجيل دخول
const loginRes = await fetch('http://129.212.140.152/accounts/pharmacy-login/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    username: '+201234567890',
    password: 'YourPassword123'
  })
});

const {token} = await loginRes.json();

// 2. جيب ملخص الحساب
const summaryRes = await fetch('http://129.212.140.152/finance/my-account-summary/', {
  headers: {'Authorization': `Token ${token}`}
});

const summary = await summaryRes.json();

// 3. اعرض المعلومات
console.log('الرصيد:', summary.account.balance);
console.log('حد الائتمان:', summary.account.credit_limit);
console.log('المدفوعات آخر 30 يوم:', summary.period_summary.total_payments_made);

// 4. اعرض آخر المعاملات
summary.recent_transactions.forEach(t => {
  console.log(`${t.description}: ${t.amount}`);
});
```

### React Example

```javascript
import React, { useEffect, useState } from 'react';

function AccountSummary() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      const token = localStorage.getItem('authToken');
      
      const response = await fetch('http://129.212.140.152/finance/my-account-summary/', {
        headers: { 'Authorization': `Token ${token}` }
      });
      
      const data = await response.json();
      setSummary(data);
      setLoading(false);
    };

    fetchSummary();
  }, []);

  if (loading) return <div>جاري التحميل...</div>;

  return (
    <div className="account-summary">
      <h2>{summary.user.name}</h2>
      
      <div className="account-info">
        <div className="balance">
          <h3>الرصيد الحالي</h3>
          <p>{summary.account.balance} جنيه</p>
        </div>
        
        <div className="credit">
          <h3>حد الائتمان المتبقي</h3>
          <p>{summary.account.remaining_credit} جنيه</p>
        </div>
      </div>

      <div className="period-summary">
        <h3>آخر {summary.period_summary.days} يوم</h3>
        <p>المدفوعات: {summary.period_summary.total_payments_made} جنيه</p>
        <p>عدد المدفوعات: {summary.period_summary.payments_count}</p>
      </div>

      <div className="transactions">
        <h3>آخر المعاملات</h3>
        <ul>
          {summary.recent_transactions.map(t => (
            <li key={t.id}>
              {t.description}: {t.amount} جنيه
              <small>{new Date(t.at).toLocaleDateString('ar-EG')}</small>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

---

## 🎨 UI Example (HTML + CSS)

```html
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>ملخص حسابي</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            border-bottom: 2px solid #24A9E0;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
        }
        .stat-card h3 { margin: 0 0 10px 0; font-size: 14px; }
        .stat-card .value { font-size: 28px; font-weight: bold; }
        .transactions {
            margin-top: 30px;
        }
        .transaction-item {
            background: #f9f9f9;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-right: 4px solid #24A9E0;
        }
        .transaction-item .type { font-weight: bold; color: #333; }
        .transaction-item .amount { color: #27ae60; font-size: 18px; }
        .transaction-item .date { color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 id="userName">ملخص حسابي المالي</h1>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3>الرصيد الحالي</h3>
                <div class="value" id="balance">0.00</div>
                <small>جنيه</small>
            </div>
            
            <div class="stat-card">
                <h3>حد الائتمان المتبقي</h3>
                <div class="value" id="creditLimit">0.00</div>
                <small>جنيه</small>
            </div>
            
            <div class="stat-card">
                <h3>المدفوعات (30 يوم)</h3>
                <div class="value" id="totalPayments">0.00</div>
                <small>جنيه</small>
            </div>
            
            <div class="stat-card">
                <h3>عدد المدفوعات</h3>
                <div class="value" id="paymentsCount">0</div>
                <small>معاملة</small>
            </div>
        </div>

        <div class="transactions">
            <h2>آخر المعاملات</h2>
            <div id="transactionsList"></div>
        </div>
    </div>

    <script>
        async function loadAccountSummary() {
            const token = localStorage.getItem('authToken');
            
            const response = await fetch('http://129.212.140.152/finance/my-account-summary/', {
                headers: { 'Authorization': `Token ${token}` }
            });
            
            const data = await response.json();
            
            // Update UI
            document.getElementById('userName').textContent = data.user.name;
            document.getElementById('balance').textContent = data.account.balance.toFixed(2);
            document.getElementById('creditLimit').textContent = data.account.remaining_credit.toFixed(2);
            document.getElementById('totalPayments').textContent = data.period_summary.total_payments_made.toFixed(2);
            document.getElementById('paymentsCount').textContent = data.period_summary.payments_count;
            
            // Display transactions
            const transactionsList = document.getElementById('transactionsList');
            transactionsList.innerHTML = data.recent_transactions.map(t => `
                <div class="transaction-item">
                    <div class="type">${t.description}</div>
                    <div class="amount">${t.amount.toFixed(2)} جنيه</div>
                    <div class="date">${new Date(t.at).toLocaleString('ar-EG')}</div>
                </div>
            `).join('');
        }

        // Load on page load
        loadAccountSummary();
    </script>
</body>
</html>
```

---

## 🚨 رسائل الخطأ

### 1. لا يوجد حساب مالي

```json
{
  "error": "لا يوجد حساب مالي لهذا المستخدم / No financial account found for this user"
}
```

**Status:** 404

**الحل:** تواصل مع الإدارة لإنشاء حساب مالي

---

### 2. غير مسجل

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**الحل:** أضف header: `Authorization: Token {your_token}`

---

## 📊 ملخص المقارنة

| ما تريده | الطريقة القديمة (ممنوعة) | الطريقة الجديدة ✅ |
|----------|-------------------------|-------------------|
| الرصيد | `/finance/user-financial-summary/` ❌ | `/finance/my-account-summary/` ✅ |
| حد الائتمان | `/profiles/user-profile/` | `/finance/my-account-summary/` ✅ |
| المدفوعات | `/finance/purchase-payments/` | `/finance/my-account-summary/` ✅ |
| آخر المعاملات | ❌ غير متاح | `/finance/my-account-summary/` ✅ |
| الصلاحية | Staff فقط ❌ | الكل ✅ |

---

## ✅ الخلاصة

### قبل:
- ❌ `/finance/user-financial-summary/` ممنوع للصيدليات
- 😞 الصيدليات ما تقدر تشوف ملخص حسابها بسهولة

### بعد (الآن):
- ✅ `/finance/my-account-summary/` متاح للجميع
- 😊 الصيدليات تقدر تشوف ملخص كامل لحسابها
- 🎉 يشمل: الرصيد، حد الائتمان، المدفوعات، آخر المعاملات

---

**استخدم الآن:** `GET /finance/my-account-summary/` 🚀

