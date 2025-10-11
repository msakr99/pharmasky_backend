# 📄 دليل طباعة كشف الحساب PDF

## 🔗 Endpoint

```
GET /finance/account-statement/pdf/
```

**الصلاحيات**: Staff (Sales, Manager, AreaManager, DataEntry, Delivery)

**الوصف**: طباعة كشف حساب تفصيلي بصيغة PDF مع الرصيد التراكمي عند كل عملية

---

## 📋 المعاملات المطلوبة

### 1. user (مطلوب)

```bash
GET /finance/account-statement/pdf/?user=5
```

### 2. type (اختياري)

```bash
# كل المعاملات
GET /finance/account-statement/pdf/?user=5

# المبيعات فقط
GET /finance/account-statement/pdf/?user=5&type=s

# التحصيلات فقط
GET /finance/account-statement/pdf/?user=5&type=sp

# المشتريات فقط
GET /finance/account-statement/pdf/?user=5&type=p

# الدفعات فقط
GET /finance/account-statement/pdf/?user=5&type=pp
```

---

## 📊 محتويات الـ PDF

### 1. معلومات العميل
- اسم العميل
- رقم الهاتف
- تاريخ الطباعة
- الرصيد الحالي

### 2. جدول المعاملات
- رقم تسلسلي
- تاريخ العملية
- نوع العملية (مبيعات، تحصيل، مشتريات، إلخ)
- المبلغ
- **الرصيد بعد العملية** ← (مميز)
- ملاحظات

### 3. الملخص
- إجمالي المعاملات
- الرصيد الحالي
- الحالة (مديون/دائن/متعادل)

---

## 🎨 التنسيق

- **الحجم**: A4 Portrait
- **اللغة**: العربية
- **الترتيب**: من الأحدث للأقدم
- **الألوان**:
  - ✅ أخضر: رصيد موجب (الشركة مديونة له)
  - ❌ أحمر: رصيد سالب (مديون للشركة)

---

## 📱 أمثلة الاستخدام

### مثال 1: كشف حساب كامل

```bash
GET http://129.212.140.152/finance/account-statement/pdf/?user=5
```

**النتيجة**: يتم تحميل ملف PDF باسم:
```
Account Statement - اسم العميل - 11-10-2024.pdf
```

---

### مثال 2: كشف حساب للمبيعات فقط

```bash
GET http://129.212.140.152/finance/account-statement/pdf/?user=5&type=s
```

**الاستخدام**: لعرض فواتير البيع فقط للعميل

---

### مثال 3: كشف حساب للتحصيلات فقط

```bash
GET http://129.212.140.152/finance/account-statement/pdf/?user=5&type=sp
```

**الاستخدام**: لعرض المبالغ المحصلة من العميل

---

## 💻 أمثلة JavaScript

### React/Next.js

```typescript
// تحميل كشف الحساب PDF
async function downloadAccountStatementPDF(userId: number, type?: string) {
  const url = new URL('/finance/account-statement/pdf/', 'http://129.212.140.152');
  url.searchParams.append('user', userId.toString());
  
  if (type) {
    url.searchParams.append('type', type);
  }
  
  const response = await fetch(url.toString(), {
    headers: {
      'Authorization': `Token ${token}`,
    },
  });
  
  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.download = `account-statement-${userId}.pdf`;
  link.click();
  window.URL.revokeObjectURL(downloadUrl);
}

// الاستخدام
// كشف حساب كامل
await downloadAccountStatementPDF(5);

// المبيعات فقط
await downloadAccountStatementPDF(5, 's');

// التحصيلات فقط
await downloadAccountStatementPDF(5, 'sp');
```

---

### مثال Component

```typescript
import React from 'react';

interface AccountStatementDownloadProps {
  userId: number;
  customerName: string;
}

function AccountStatementDownload({ userId, customerName }: AccountStatementDownloadProps) {
  const [loading, setLoading] = useState(false);
  
  const handleDownload = async (type?: string) => {
    setLoading(true);
    try {
      const url = new URL('/finance/account-statement/pdf/', API_BASE_URL);
      url.searchParams.append('user', userId.toString());
      if (type) {
        url.searchParams.append('type', type);
      }
      
      const response = await fetch(url.toString(), {
        headers: { 'Authorization': `Token ${token}` }
      });
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `كشف-حساب-${customerName}.pdf`;
      link.click();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error('Error downloading PDF:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="download-buttons">
      <h3>تحميل كشف الحساب</h3>
      
      <button onClick={() => handleDownload()} disabled={loading}>
        {loading ? 'جاري التحميل...' : 'كشف حساب كامل'}
      </button>
      
      <button onClick={() => handleDownload('s')} disabled={loading}>
        المبيعات فقط
      </button>
      
      <button onClick={() => handleDownload('sp')} disabled={loading}>
        التحصيلات فقط
      </button>
      
      <button onClick={() => handleDownload('p')} disabled={loading}>
        المشتريات فقط
      </button>
    </div>
  );
}

export default AccountStatementDownload;
```

---

## 🎯 حالات الاستخدام

### 1. طباعة لصيدلية
```bash
GET /finance/account-statement/pdf/?user=89
```
**يعرض**: جميع فواتير البيع والتحصيلات والمرتجعات

---

### 2. طباعة لمتجر/مورد
```bash
GET /finance/account-statement/pdf/?user=45
```
**يعرض**: جميع فواتير الشراء والدفعات والمرتجعات

---

### 3. كشف مبيعات فقط
```bash
GET /finance/account-statement/pdf/?user=89&type=s
```
**الاستخدام**: لمراجعة الفواتير فقط

---

### 4. كشف التحصيلات فقط
```bash
GET /finance/account-statement/pdf/?user=89&type=sp
```
**الاستخدام**: لمراجعة المدفوعات المحصلة

---

## 📋 أنواع المعاملات

| الكود | النوع | يظهر في |
|------|------|---------|
| `s` | Sale | كشف حساب صيدلية (مبيعات) |
| `sp` | Sale Payment | كشف حساب صيدلية (تحصيلات) |
| `p` | Purchase | كشف حساب متجر (مشتريات) |
| `pp` | Purchase Payment | كشف حساب متجر (دفعات) |
| `sr` | Sale Return | مرتجع مبيعات |
| `pr` | Purchase Return | مرتجع مشتريات |

---

## ⚠️ ملاحظات مهمة

1. **user parameter مطلوب**: لا بد من تحديد user_id

2. **الصلاحيات**:
   - Sales: يرى عملاءه فقط
   - Manager: يرى عملاء المندوبين تحته
   - AreaManager: يرى عملاء المنطقة
   - Admin: يرى الكل

3. **الرصيد السالب**: يعني العميل مديون للشركة

4. **الرصيد الموجب**: يعني الشركة مديونة للعميل

5. **الترتيب**: من الأحدث للأقدم (للقراءة السهلة)

6. **الحساب**: الرصيد التراكمي يُحسب من الأقدم للأحدث (للدقة)

---

## 🖨️ نصائح الطباعة

1. **استخدم Chrome/Edge**: للحصول على أفضل نتائج PDF
2. **حدد النوع**: إذا كنت تريد فقط نوع معين من المعاملات
3. **احفظ النسخة**: للرجوع إليها لاحقاً
4. **شارك مع العميل**: يمكن إرسال الـ PDF للعميل عبر البريد/واتساب

---

## 🔗 Endpoints ذات صلة

| Endpoint | الوصف |
|----------|-------|
| `/finance/account-transactions/?user=X` | كشف حساب JSON |
| `/finance/account-statement/pdf/?user=X` | كشف حساب PDF |
| `/finance/collection-schedule/` | قائمة التحصيلات |
| `/finance/accounts-payable/` | قائمة الديون |

---

## 🚀 سير العمل المقترح

```bash
# 1. البحث عن العميل
GET /accounts/simple-users/?search=محمد

# 2. عرض كشف الحساب على الشاشة
GET /finance/account-transactions/?user=5

# 3. طباعة كشف الحساب
GET /finance/account-statement/pdf/?user=5

# 4. مشاركة الـ PDF مع العميل
```

---

## 📞 للدعم

للاستفسارات أو الإبلاغ عن مشاكل، يرجى التواصل مع فريق التطوير.

**آخر تحديث**: 11 أكتوبر 2025

