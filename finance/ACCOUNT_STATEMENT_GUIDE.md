# 📊 دليل استخدام كشف الحساب (Account Statement)

## 🔗 Endpoint

```
GET /finance/account-transactions/
```

**الصلاحيات**: Staff (Sales, Manager, DataEntry, Delivery, AreaManager)

---

## 🔍 الفلاتر

### 1️⃣ **بـ User ID** (الطريقة الجديدة - الأسهل)

```bash
GET /finance/account-transactions/?user=45
```

**مثال**:
```bash
# كشف حساب للصيدلية رقم 89
GET http://129.212.140.152/finance/account-transactions/?user=89

# كشف حساب للمتجر رقم 45
GET http://129.212.140.152/finance/account-transactions/?user=45
```

---

### 2️⃣ **بـ Account ID** (الطريقة القديمة)

```bash
GET /finance/account-transactions/?account=123
```

---

### 3️⃣ **فلتر حسب نوع المعاملة**

```bash
# المبيعات فقط
GET /finance/account-transactions/?user=89&type=s

# التحصيلات فقط
GET /finance/account-transactions/?user=89&type=sp

# المشتريات فقط
GET /finance/account-transactions/?user=45&type=p

# الدفعات فقط
GET /finance/account-transactions/?user=45&type=pp
```

---

## 📋 أنواع المعاملات

| الكود | النوع | الوصف | يظهر في |
|------|------|-------|---------|
| `p` | Purchase | مشتريات | حساب المتاجر/الموردين |
| `s` | Sale | مبيعات | حساب الصيدليات |
| `pp` | Purchase Payment | دفعة شراء | حساب المتاجر (دفعنا لهم) |
| `sp` | Sale Payment | تحصيل | حساب الصيدليات (حصلنا منهم) |
| `pr` | Purchase Return | مرتجع مشتريات | حساب المتاجر |
| `sr` | Sale Return | مرتجع مبيعات | حساب الصيدليات |
| `f` | Refund | استرداد | أي حساب |

---

## 📊 Response Structure

```json
{
  "count": 50,
  "next": "http://...?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "account": {
        "id": 123,
        "balance": "-15000.00",
        "credit_limit": "50000.00",
        "remaining_credit": "35000.00",
        "transactions_url": "/finance/account-transactions/?account=123"
      },
      "type": "s",
      "type_label": "Sale",
      "amount": "5000.00",
      "at": "2024-10-11T10:30:00Z",
      "timestamp": "2024-10-11T10:35:20Z"
    }
  ]
}
```

---

## 🎯 أمثلة عملية

### مثال 1: كشف حساب صيدلية كامل

```bash
GET /finance/account-transactions/?user=89
```

**النتيجة**: جميع المعاملات (مبيعات، تحصيلات، مرتجعات)

---

### مثال 2: فواتير البيع فقط

```bash
GET /finance/account-transactions/?user=89&type=s
```

**النتيجة**: المبيعات فقط (الفواتير)

---

### مثال 3: التحصيلات فقط

```bash
GET /finance/account-transactions/?user=89&type=sp
```

**النتيجة**: المبالغ المحصلة من الصيدلية

---

### مثال 4: كشف حساب متجر

```bash
# كل المعاملات
GET /finance/account-transactions/?user=45

# المشتريات فقط
GET /finance/account-transactions/?user=45&type=p

# الدفعات فقط
GET /finance/account-transactions/?user=45&type=pp
```

---

## 📱 أمثلة JavaScript/TypeScript

```typescript
interface AccountTransactionParams {
  user?: number;
  account?: number;
  type?: string;
}

async function getAccountStatement(params: AccountTransactionParams) {
  const url = new URL('/finance/account-transactions/', 'http://129.212.140.152');
  
  if (params.user) {
    url.searchParams.append('user', params.user.toString());
  }
  
  if (params.account) {
    url.searchParams.append('account', params.account.toString());
  }
  
  if (params.type) {
    url.searchParams.append('type', params.type);
  }
  
  const response = await fetch(url.toString(), {
    headers: {
      'Authorization': `Token ${token}`,
    },
  });
  
  return response.json();
}

// الاستخدام
// كشف حساب كامل بـ user_id
const fullStatement = await getAccountStatement({ user: 89 });

// المبيعات فقط
const sales = await getAccountStatement({ user: 89, type: 's' });

// التحصيلات فقط
const collections = await getAccountStatement({ user: 89, type: 'sp' });

// كشف حساب متجر
const supplierStatement = await getAccountStatement({ user: 45 });
```

---

## 🎨 مثال React Component متقدم

```typescript
import { useState, useEffect } from 'react';

interface Transaction {
  id: number;
  type: string;
  type_label: string;
  amount: string;
  at: string;
  timestamp: string;
}

interface AccountStatementProps {
  userId: number;
  transactionType?: string;
}

function AccountStatementView({ userId, transactionType }: AccountStatementProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState(transactionType || 'all');
  
  useEffect(() => {
    loadStatement();
  }, [userId, filter]);
  
  const loadStatement = async () => {
    setLoading(true);
    const params = new URLSearchParams({ user: userId.toString() });
    
    if (filter !== 'all') {
      params.append('type', filter);
    }
    
    const response = await fetch(
      `http://129.212.140.152/finance/account-transactions/?${params}`,
      {
        headers: { 'Authorization': `Token ${token}` }
      }
    );
    
    const result = await response.json();
    setData(result);
    setLoading(false);
  };
  
  if (loading) return <div>جاري التحميل...</div>;
  
  const account = data.results[0]?.account;
  
  return (
    <div>
      <h2>كشف حساب</h2>
      
      {/* معلومات الحساب */}
      {account && (
        <div className="account-info">
          <p>الرصيد: {account.balance} ج.م</p>
          <p>حد الائتمان: {account.credit_limit} ج.م</p>
          <p>المتبقي: {account.remaining_credit} ج.م</p>
        </div>
      )}
      
      {/* فلتر نوع المعاملة */}
      <select value={filter} onChange={(e) => setFilter(e.target.value)}>
        <option value="all">الكل</option>
        <option value="s">المبيعات</option>
        <option value="sp">التحصيلات</option>
        <option value="p">المشتريات</option>
        <option value="pp">الدفعات</option>
        <option value="sr">مرتجع مبيعات</option>
        <option value="pr">مرتجع مشتريات</option>
      </select>
      
      {/* جدول المعاملات */}
      <table>
        <thead>
          <tr>
            <th>التاريخ</th>
            <th>النوع</th>
            <th>المبلغ</th>
            <th>الرصيد بعدها</th>
          </tr>
        </thead>
        <tbody>
          {data.results.map((tx: Transaction, index: number) => (
            <tr key={tx.id}>
              <td>{new Date(tx.at).toLocaleDateString('ar-EG')}</td>
              <td>{tx.type_label}</td>
              <td className={getAmountClass(tx.type)}>
                {tx.amount} ج.م
              </td>
              <td>{tx.account?.balance || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      
      <p>إجمالي المعاملات: {data.count}</p>
    </div>
  );
}

// دالة مساعدة لتلوين المبالغ
function getAmountClass(type: string) {
  if (['s', 'pr'].includes(type)) return 'text-red'; // زيادة الدين
  if (['sp', 'sr'].includes(type)) return 'text-green'; // تقليل الدين
  return '';
}
```

---

## 🔄 سير العمل المبسط

### الطريقة القديمة (معقدة):
```bash
1. GET /accounts/users/{user_id}/
2. استخرج account.id من الـ response
3. GET /finance/account-transactions/?account={account_id}
```

### الطريقة الجديدة (بسيطة):
```bash
GET /finance/account-transactions/?user={user_id}
```

✅ **أسهل وأسرع!**

---

## 📋 أمثلة الاستخدام:

```bash
# كشف حساب صيدلية بـ user_id
GET /finance/account-transactions/?user=89

# مبيعات صيدلية معينة
GET /finance/account-transactions/?user=89&type=s

# تحصيلات صيدلية معينة
GET /finance/account-transactions/?user=89&type=sp

# كشف حساب متجر
GET /finance/account-transactions/?user=45

# دفعات لمتجر معين
GET /finance/account-transactions/?user=45&type=pp
```

---

## ⚡ الميزات الجديدة:

✅ **استخدام user_id مباشرة** - لا حاجة لـ account_id

✅ **يعمل مع account_id القديم** - للتوافقية

✅ **فلترة حسب النوع** - لعرض معاملات محددة

✅ **مرتب تلقائياً** - من الأحدث للأقدم

---

راجع الملف `finance/ACCOUNT_STATEMENT_GUIDE.md` لمزيد من التفاصيل! 📚

جاهز للاستخدام الآن! 🚀
