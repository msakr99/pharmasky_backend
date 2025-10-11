# 📊 دليل الملخص المالي للمستخدمين
# User Financial Summary API Guide

## 🔗 Endpoint

```
GET /finance/user-financial-summary/
```

**الصلاحيات**: Staff (Sales, Manager, AreaManager, DataEntry)

**الوصف**: يعرض ملخص مالي شامل لكل مستخدم (صيدلية أو متجر) يتضمن جميع المعاملات المالية

---

## 📋 المعاملات الاختيارية (Query Parameters)

### 1. user_id (اختياري)
لعرض إحصائيات مستخدم واحد فقط

```bash
# عرض إحصائيات المستخدم رقم 5
GET /finance/user-financial-summary/?user_id=5
```

### 2. search (اختياري)
البحث باسم المستخدم أو رقم الهاتف

```bash
GET /finance/user-financial-summary/?search=محمد
```

### 3. role (اختياري)
فلترة حسب نوع المستخدم

```bash
# عرض الصيدليات فقط
GET /finance/user-financial-summary/?role=PHARMACY

# عرض المتاجر فقط
GET /finance/user-financial-summary/?role=STORE
```

### 4. min_volume (اختياري)
الحد الأدنى لحجم التعامل

```bash
GET /finance/user-financial-summary/?min_volume=100000
```

### 5. date_from & date_to (اختياري)
فلترة حسب التاريخ

```bash
# من 1 يناير 2025
GET /finance/user-financial-summary/?date_from=2025-01-01

# حتى 31 ديسمبر 2025
GET /finance/user-financial-summary/?date_to=2025-12-31

# فترة محددة
GET /finance/user-financial-summary/?date_from=2025-01-01&date_to=2025-12-31
```

---

## 📊 البيانات المُعادة

### Response Format

```json
{
  "count": 50,
  "grand_totals": {
    "total_purchases": 5000000.00,
    "total_sales": 8000000.00,
    "total_purchase_returns": 200000.00,
    "total_sale_returns": 150000.00,
    "total_cash_paid": 4500000.00,
    "total_cash_received": 7500000.00,
    "total_transaction_volume": 12650000.00
  },
  "results": [
    {
      "user_id": 5,
      "user_name": "صيدلية النور",
      "username": "+201234567890",
      "role": "PHARMACY",
      "role_label": "صيدلية",
      "total_purchases": 0.00,
      "total_sales": 500000.00,
      "total_purchase_returns": 0.00,
      "total_sale_returns": 5000.00,
      "total_cash_paid": 0.00,
      "total_cash_received": 450000.00,
      "transaction_volume": 495000.00,
      "current_balance": -50000.00
    },
    {
      "user_id": 12,
      "user_name": "متجر الأدوية الكبير",
      "username": "+201987654321",
      "role": "STORE",
      "role_label": "متجر",
      "total_purchases": 1000000.00,
      "total_sales": 0.00,
      "total_purchase_returns": 10000.00,
      "total_sale_returns": 0.00,
      "total_cash_paid": 950000.00,
      "total_cash_received": 0.00,
      "transaction_volume": 990000.00,
      "current_balance": 40000.00
    }
  ]
}
```

### شرح الحقول

| الحقل | الوصف | الملاحظات |
|------|------|----------|
| `user_id` | معرف المستخدم | - |
| `user_name` | اسم المستخدم | - |
| `username` | رقم الهاتف | - |
| `role` | نوع المستخدم | PHARMACY, STORE, etc. |
| `role_label` | اسم النوع بالعربية | صيدلية، متجر، إلخ |
| `total_purchases` | إجمالي المشتريات | للمتاجر |
| `total_sales` | إجمالي المبيعات | للصيدليات |
| `total_purchase_returns` | إجمالي مرتجعات المشتريات | للمتاجر |
| `total_sale_returns` | إجمالي مرتجعات المبيعات | للصيدليات |
| `total_cash_paid` | إجمالي النقدية المدفوعة | دفعات الشراء |
| `total_cash_received` | إجمالي النقدية المستلمة | تحصيلات البيع |
| `transaction_volume` | حجم التعامل | (مشتريات + مبيعات - مرتجعات) |
| `current_balance` | الرصيد الحالي | سالب = مديون للشركة |

---

## 📱 أمثلة الاستخدام

### مثال 1: عرض إحصائيات مستخدم واحد

```bash
GET http://129.212.140.152/finance/user-financial-summary/?user_id=5
```

**النتيجة**: ملخص مالي للمستخدم رقم 5 فقط

---

### مثال 2: عرض كل المستخدمين

```bash
GET http://129.212.140.152/finance/user-financial-summary/
```

**النتيجة**: قائمة بجميع المستخدمين مرتبة حسب حجم التعامل (الأعلى أولاً)

---

### مثال 3: البحث عن صيدلية معينة

```bash
GET http://129.212.140.152/finance/user-financial-summary/?search=النور
```

**النتيجة**: جميع المستخدمين الذين يحتوي اسمهم على "النور"

---

### مثال 4: عرض الصيدليات فقط

```bash
GET http://129.212.140.152/finance/user-financial-summary/?role=PHARMACY
```

**النتيجة**: ملخص مالي للصيدليات فقط

---

### مثال 5: عرض المستخدمين بحجم تعامل أكثر من 100,000

```bash
GET http://129.212.140.152/finance/user-financial-summary/?min_volume=100000
```

**النتيجة**: فقط المستخدمين الذين حجم تعاملهم أكبر من 100,000 جنيه

---

### مثال 6: ملخص شهر معين

```bash
GET http://129.212.140.152/finance/user-financial-summary/?date_from=2025-10-01&date_to=2025-10-31
```

**النتيجة**: ملخص مالي لشهر أكتوبر 2025 فقط

---

## 💻 أمثلة JavaScript

### React/Next.js

```typescript
interface FinancialSummary {
  user_id: number;
  user_name: string;
  username: string;
  role: string;
  role_label: string;
  total_purchases: number;
  total_sales: number;
  total_purchase_returns: number;
  total_sale_returns: number;
  total_cash_paid: number;
  total_cash_received: number;
  transaction_volume: number;
  current_balance: number;
}

interface FinancialSummaryResponse {
  count: number;
  grand_totals: {
    total_purchases: number;
    total_sales: number;
    total_purchase_returns: number;
    total_sale_returns: number;
    total_cash_paid: number;
    total_cash_received: number;
    total_transaction_volume: number;
  };
  results: FinancialSummary[];
}

async function getFinancialSummary(
  search?: string,
  role?: string,
  minVolume?: number,
  dateFrom?: string,
  dateTo?: string
): Promise<FinancialSummaryResponse> {
  const url = new URL('/finance/user-financial-summary/', API_BASE_URL);
  
  if (search) url.searchParams.append('search', search);
  if (role) url.searchParams.append('role', role);
  if (minVolume) url.searchParams.append('min_volume', minVolume.toString());
  if (dateFrom) url.searchParams.append('date_from', dateFrom);
  if (dateTo) url.searchParams.append('date_to', dateTo);
  
  const response = await fetch(url.toString(), {
    headers: {
      'Authorization': `Token ${token}`,
    },
  });
  
  return await response.json();
}

// الاستخدام
const data = await getFinancialSummary('محمد', 'PHARMACY', 100000);
console.log(`إجمالي حجم التعامل: ${data.grand_totals.total_transaction_volume}`);
```

---

### مثال Component

```typescript
import React, { useState, useEffect } from 'react';

interface FinancialSummaryProps {
  token: string;
}

function FinancialSummaryList({ token }: FinancialSummaryProps) {
  const [data, setData] = useState<FinancialSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    role: '',
    minVolume: '',
    dateFrom: '',
    dateTo: '',
  });
  
  const fetchData = async () => {
    setLoading(true);
    try {
      const url = new URL('/finance/user-financial-summary/', API_BASE_URL);
      
      if (filters.search) url.searchParams.append('search', filters.search);
      if (filters.role) url.searchParams.append('role', filters.role);
      if (filters.minVolume) url.searchParams.append('min_volume', filters.minVolume);
      if (filters.dateFrom) url.searchParams.append('date_from', filters.dateFrom);
      if (filters.dateTo) url.searchParams.append('date_to', filters.dateTo);
      
      const response = await fetch(url.toString(), {
        headers: { 'Authorization': `Token ${token}` }
      });
      
      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error('Error fetching financial summary:', error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchData();
  }, [filters]);
  
  if (loading) return <div>جاري التحميل...</div>;
  if (!data) return <div>لا توجد بيانات</div>;
  
  return (
    <div>
      <h2>الملخص المالي للمستخدمين</h2>
      
      {/* Filters */}
      <div className="filters">
        <input
          type="text"
          placeholder="البحث..."
          value={filters.search}
          onChange={(e) => setFilters({...filters, search: e.target.value})}
        />
        
        <select
          value={filters.role}
          onChange={(e) => setFilters({...filters, role: e.target.value})}
        >
          <option value="">كل الأنواع</option>
          <option value="PHARMACY">صيدليات</option>
          <option value="STORE">متاجر</option>
        </select>
        
        <input
          type="date"
          value={filters.dateFrom}
          onChange={(e) => setFilters({...filters, dateFrom: e.target.value})}
        />
        
        <input
          type="date"
          value={filters.dateTo}
          onChange={(e) => setFilters({...filters, dateTo: e.target.value})}
        />
      </div>
      
      {/* Grand Totals */}
      <div className="grand-totals">
        <h3>الإجماليات</h3>
        <p>حجم التعامل الكلي: {data.grand_totals.total_transaction_volume.toLocaleString()} جنيه</p>
        <p>إجمالي المبيعات: {data.grand_totals.total_sales.toLocaleString()} جنيه</p>
        <p>إجمالي المشتريات: {data.grand_totals.total_purchases.toLocaleString()} جنيه</p>
      </div>
      
      {/* Results Table */}
      <table>
        <thead>
          <tr>
            <th>الاسم</th>
            <th>النوع</th>
            <th>المبيعات</th>
            <th>المشتريات</th>
            <th>حجم التعامل</th>
            <th>الرصيد</th>
          </tr>
        </thead>
        <tbody>
          {data.results.map((user) => (
            <tr key={user.user_id}>
              <td>{user.user_name}</td>
              <td>{user.role_label}</td>
              <td>{user.total_sales.toLocaleString()}</td>
              <td>{user.total_purchases.toLocaleString()}</td>
              <td>{user.transaction_volume.toLocaleString()}</td>
              <td className={user.current_balance < 0 ? 'negative' : 'positive'}>
                {user.current_balance.toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default FinancialSummaryList;
```

---

## 🎯 حالات الاستخدام

### 1. عرض إحصائيات عميل محدد

```bash
GET /finance/user-financial-summary/?user_id=5
```

**يعرض**: ملخص مالي كامل للمستخدم رقم 5

---

### 2. عرض إحصائيات عميل في فترة محددة

```bash
GET /finance/user-financial-summary/?user_id=5&date_from=2025-10-01&date_to=2025-10-31
```

**يعرض**: ملخص مالي للمستخدم رقم 5 خلال شهر أكتوبر فقط

---

### 3. عرض أفضل 10 عملاء

```bash
GET /finance/user-financial-summary/?min_volume=500000
```

**يعرض**: العملاء الذين لديهم حجم تعامل أكثر من 500,000 جنيه

---

### 4. تقرير شهري للصيدليات

```bash
GET /finance/user-financial-summary/?role=PHARMACY&date_from=2025-10-01&date_to=2025-10-31
```

**يعرض**: ملخص مالي لجميع الصيدليات في شهر أكتوبر

---

### 5. البحث عن عميل معين

```bash
GET /finance/user-financial-summary/?search=النور
```

**يعرض**: جميع العملاء الذين يحتوي اسمهم على "النور"

---

## 📊 حساب حجم التعامل

حجم التعامل يُحسب كالتالي:

```
حجم التعامل = (إجمالي المشتريات + إجمالي المبيعات) - (مرتجعات المشتريات + مرتجعات المبيعات)
```

**مثال:**
- مشتريات: 1,000,000 جنيه
- مبيعات: 1,500,000 جنيه
- مرتجعات مشتريات: 50,000 جنيه
- مرتجعات مبيعات: 30,000 جنيه

**حجم التعامل** = (1,000,000 + 1,500,000) - (50,000 + 30,000) = **2,420,000 جنيه**

---

## ⚠️ ملاحظات مهمة

1. **الصلاحيات**:
   - Sales: يرى عملاءه فقط
   - Manager: يرى عملاء المندوبين تحته
   - AreaManager: يرى عملاء المنطقة
   - Admin: يرى الكل

2. **الترتيب**: النتائج مرتبة حسب حجم التعامل (الأعلى أولاً)

3. **التواريخ**: يجب أن تكون بصيغة `YYYY-MM-DD` (مثل: `2025-10-11`)

4. **الرصيد السالب**: يعني المستخدم مديون للشركة

5. **الرصيد الموجب**: يعني الشركة مديونة للمستخدم

---

## 🔗 Endpoints ذات صلة

| Endpoint | الوصف |
|----------|-------|
| `/finance/user-financial-summary/` | ملخص مالي للمستخدمين |
| `/finance/collection-schedule/` | قائمة التحصيلات المتوقعة |
| `/finance/accounts-payable/` | الحسابات الدائنة |
| `/finance/account-transactions/?user=X` | معاملات مستخدم معين |

---

## 📞 للدعم

للاستفسارات أو الإبلاغ عن مشاكل، يرجى التواصل مع فريق التطوير.

**آخر تحديث**: 11 أكتوبر 2025

