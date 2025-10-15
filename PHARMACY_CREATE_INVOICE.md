# دليل إنشاء الفاتورة للصيدليات 🏪

## ✅ الآن الصيدلي يقدر يعمل فاتورة لنفسه!

تم تحديث النظام ليسمح للصيدليات بإنشاء فواتير لأنفسهم فقط.

---

## 🎯 ما الجديد؟

### قبل ❌:
- الصيدليات **فقط** تشوف الفواتير
- لا يمكنها إنشاء أو تعديل

### الآن ✅:
- ✅ الصيدليات تقدر **تنشئ فواتير لنفسها**
- ✅ تقدر **تضيف بنود** للفاتورة
- ✅ تقدر **تعدل البنود**
- ✅ تقدر **تحذف البنود**
- ⚠️ **لكن فقط لفواتيرها الخاصة**

---

## 🔐 القيود الأمنية

### ✅ مسموح:
- إنشاء فاتورة لنفسك
- إضافة بنود لفاتورتك
- تعديل بنود فاتورتك
- حذف بنود من فاتورتك

### ❌ ممنوع:
- إنشاء فاتورة لصيدلية أخرى
- إضافة/تعديل بنود في فواتير الآخرين

---

## 📋 خطوات إنشاء فاتورة

### الخطوة 1: تسجيل الدخول

```bash
curl -X POST http://129.212.140.152/accounts/pharmacy-login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "+201234567890",
    "password": "YourPassword"
  }'
```

**Response:**
```json
{
  "token": "abc123xyz...",
  "role": "PHARMACY",
  "user_id": 123,
  "name": "صيدلية النور"
}
```

---

### الخطوة 2: إنشاء الفاتورة

```bash
curl -X POST http://129.212.140.152/invoices/sale-invoices/create/ \
  -H "Authorization: Token abc123xyz..." \
  -H "Content-Type: application/json" \
  -d '{
    "user": 123,
    "payment_method": "cash",
    "remarks": "فاتورة شراء أدوية",
    "items": [
      {
        "product": 456,
        "quantity": 10,
        "unit_price": 50.00,
        "discount_percentage": 0.00
      },
      {
        "product": 789,
        "quantity": 5,
        "unit_price": 100.00,
        "discount_percentage": 5.00
      }
    ]
  }'
```

**ملاحظة:** `user` يجب أن يكون **معرفك أنت** (123 في هذا المثال)

**Response:**
```json
{
  "id": 1001,
  "invoice_number": "INV-2025-1001",
  "user": {
    "id": 123,
    "name": "صيدلية النور",
    "username": "+201234567890"
  },
  "items": [
    {
      "id": 5001,
      "product": {
        "id": 456,
        "name": "باراسيتامول 500 مجم",
        "barcode": "123456"
      },
      "quantity": 10,
      "unit_price": 50.00,
      "discount_percentage": 0.00,
      "final_price": 500.00
    },
    {
      "id": 5002,
      "product": {
        "id": 789,
        "name": "أسبرين 100 مجم",
        "barcode": "789012"
      },
      "quantity": 5,
      "unit_price": 100.00,
      "discount_percentage": 5.00,
      "final_price": 475.00
    }
  ],
  "total_price": 975.00,
  "status": "pending",
  "payment_method": "cash",
  "created_at": "2025-10-14T21:00:00Z"
}
```

---

### الخطوة 3: إضافة بند جديد للفاتورة (اختياري)

إذا عايز تضيف منتج بعد إنشاء الفاتورة:

```bash
curl -X POST http://129.212.140.152/invoices/sale-invoice-items/create/ \
  -H "Authorization: Token abc123xyz..." \
  -H "Content-Type: application/json" \
  -d '{
    "sale_invoice": 1001,
    "product": 999,
    "quantity": 20,
    "unit_price": 25.00,
    "discount_percentage": 0.00
  }'
```

**Response:**
```json
{
  "id": 5003,
  "sale_invoice": 1001,
  "product": {
    "id": 999,
    "name": "فيتامين سي",
    "barcode": "999888"
  },
  "quantity": 20,
  "unit_price": 25.00,
  "discount_percentage": 0.00,
  "final_price": 500.00
}
```

---

### الخطوة 4: تعديل بند موجود (اختياري)

```bash
curl -X PUT http://129.212.140.152/invoices/sale-invoice-items/5001/change/ \
  -H "Authorization: Token abc123xyz..." \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 15,
    "discount_percentage": 10.00
  }'
```

---

### الخطوة 5: حذف بند (اختياري)

```bash
curl -X DELETE http://129.212.140.152/invoices/sale-invoice-items/5002/destroy/ \
  -H "Authorization: Token abc123xyz..."
```

**Response:** `204 No Content`

---

## 💻 كود Python كامل

```python
import requests

BASE_URL = "http://129.212.140.152"

# 1. تسجيل دخول
login_res = requests.post(
    f'{BASE_URL}/accounts/pharmacy-login/',
    json={
        'username': '+201234567890',
        'password': 'YourPassword'
    }
)
token = login_res.json()['token']
user_id = login_res.json()['user_id']
headers = {'Authorization': f'Token {token}'}

print(f"✅ تم تسجيل الدخول - User ID: {user_id}")

# 2. إنشاء فاتورة
invoice_data = {
    'user': user_id,  # استخدم معرفك
    'payment_method': 'cash',
    'remarks': 'فاتورة شراء أدوية',
    'items': [
        {
            'product': 456,
            'quantity': 10,
            'unit_price': 50.00,
            'discount_percentage': 0.00
        },
        {
            'product': 789,
            'quantity': 5,
            'unit_price': 100.00,
            'discount_percentage': 5.00
        }
    ]
}

invoice_res = requests.post(
    f'{BASE_URL}/invoices/sale-invoices/create/',
    headers=headers,
    json=invoice_data
)

if invoice_res.status_code == 201:
    invoice = invoice_res.json()
    print(f"✅ تم إنشاء الفاتورة #{invoice['invoice_number']}")
    print(f"   الإجمالي: {invoice['total_price']} جنيه")
    print(f"   عدد البنود: {len(invoice['items'])}")
    
    invoice_id = invoice['id']
    
    # 3. إضافة بند جديد
    new_item = {
        'sale_invoice': invoice_id,
        'product': 999,
        'quantity': 20,
        'unit_price': 25.00
    }
    
    item_res = requests.post(
        f'{BASE_URL}/invoices/sale-invoice-items/create/',
        headers=headers,
        json=new_item
    )
    
    if item_res.status_code == 201:
        print(f"✅ تم إضافة بند جديد")
else:
    print(f"❌ خطأ: {invoice_res.json()}")
```

---

## 💻 كود JavaScript كامل

```javascript
const BASE_URL = 'http://129.212.140.152';

async function createInvoice() {
  try {
    // 1. تسجيل دخول
    const loginRes = await fetch(`${BASE_URL}/accounts/pharmacy-login/`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        username: '+201234567890',
        password: 'YourPassword'
      })
    });
    
    const {token, user_id} = await loginRes.json();
    const headers = {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    };
    
    console.log('✅ تم تسجيل الدخول');
    
    // 2. إنشاء فاتورة
    const invoiceData = {
      user: user_id,  // استخدم معرفك
      payment_method: 'cash',
      remarks: 'فاتورة شراء أدوية',
      items: [
        {
          product: 456,
          quantity: 10,
          unit_price: 50.00,
          discount_percentage: 0.00
        },
        {
          product: 789,
          quantity: 5,
          unit_price: 100.00,
          discount_percentage: 5.00
        }
      ]
    };
    
    const invoiceRes = await fetch(`${BASE_URL}/invoices/sale-invoices/create/`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(invoiceData)
    });
    
    if (invoiceRes.ok) {
      const invoice = await invoiceRes.json();
      console.log(`✅ تم إنشاء الفاتورة #${invoice.invoice_number}`);
      console.log(`الإجمالي: ${invoice.total_price} جنيه`);
      
      // 3. إضافة بند جديد
      const newItem = {
        sale_invoice: invoice.id,
        product: 999,
        quantity: 20,
        unit_price: 25.00
      };
      
      const itemRes = await fetch(`${BASE_URL}/invoices/sale-invoice-items/create/`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(newItem)
      });
      
      if (itemRes.ok) {
        console.log('✅ تم إضافة بند جديد');
      }
    } else {
      const error = await invoiceRes.json();
      console.error('❌ خطأ:', error);
    }
    
  } catch (error) {
    console.error('❌ خطأ:', error);
  }
}

createInvoice();
```

---

## 🚨 رسائل الخطأ المحتملة

### 1. محاولة إنشاء فاتورة لمستخدم آخر

```json
{
  "error": "الصيدليات والمخازن يمكنها فقط إنشاء فواتير لأنفسها / Pharmacies and stores can only create invoices for themselves",
  "detail": "يجب أن يكون user = 123"
}
```

**الحل:** استخدم معرفك أنت في حقل `user`

---

### 2. محاولة إضافة بند لفاتورة مستخدم آخر

```json
{
  "error": "لا يمكنك إضافة بنود لفواتير مستخدمين آخرين / You cannot add items to other users' invoices"
}
```

**الحل:** أضف بنود فقط لفواتيرك أنت

---

### 3. الفاتورة غير موجودة

```json
{
  "error": "الفاتورة غير موجودة / Invoice not found"
}
```

**الحل:** تأكد من ID الفاتورة صحيح

---

## 📊 حقول الفاتورة

### الحقول المطلوبة:

| الحقل | النوع | المثال | الوصف |
|-------|------|---------|-------|
| `user` | Integer | 123 | معرف المستخدم (يجب أن يكون معرفك) |
| `payment_method` | String | "cash" | طريقة الدفع |
| `items` | Array | [...] | البنود (اختياري عند الإنشاء) |

### طرق الدفع المتاحة:

| القيمة | الوصف |
|-------|------|
| `"cash"` | نقدي |
| `"credit"` | آجل |
| `"instapay"` | إنستاباي |

---

## 📊 حقول البند (Item)

### الحقول المطلوبة:

| الحقل | النوع | المثال | الوصف |
|-------|------|---------|-------|
| `sale_invoice` | Integer | 1001 | معرف الفاتورة |
| `product` | Integer | 456 | معرف المنتج |
| `quantity` | Decimal | 10 | الكمية |
| `unit_price` | Decimal | 50.00 | سعر الوحدة |
| `discount_percentage` | Decimal | 5.00 | نسبة الخصم (اختياري) |

---

## 💡 نصائح مهمة

### 1. استخدم معرفك دائماً ✅
```python
# ✅ صح
invoice_data = {
    'user': user_id,  # معرفك من الـ login response
    'items': [...]
}

# ❌ خطأ
invoice_data = {
    'user': 999,  # معرف مستخدم آخر
    'items': [...]
}
```

### 2. تأكد من الفاتورة لك قبل التعديل ✅
```python
# قبل إضافة بند، تأكد أن الفاتورة لك
invoice = requests.get(
    f'{BASE_URL}/invoices/sale-invoices/{invoice_id}/',
    headers=headers
).json()

if invoice['user']['id'] == user_id:
    # يمكنك إضافة بند
    pass
```

### 3. استخدم الفلترة ✅
```python
# جيب فواتيرك أنت فقط
my_invoices = requests.get(
    f'{BASE_URL}/invoices/sale-invoices/?user={user_id}',
    headers=headers
).json()
```

---

## 🎯 ملخص سريع

| العملية | الصيدلية (قبل) | الصيدلية (الآن) ✅ |
|---------|----------------|-------------------|
| عرض فواتيره | ✅ | ✅ |
| إنشاء فاتورة لنفسه | ❌ | ✅ |
| إضافة بند لفاتورته | ❌ | ✅ |
| تعديل بند في فاتورته | ❌ | ✅ |
| حذف بند من فاتورته | ❌ | ✅ |
| إنشاء فاتورة لآخر | ❌ | ❌ |
| تعديل فاتورة آخر | ❌ | ❌ |

---

## 🎨 مثال React Component

```javascript
import React, { useState } from 'react';

function CreateInvoice() {
  const [items, setItems] = useState([
    { product: '', quantity: 1, unit_price: 0 }
  ]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const token = localStorage.getItem('authToken');
    const userId = localStorage.getItem('userId');

    const invoiceData = {
      user: parseInt(userId),
      payment_method: 'cash',
      items: items.filter(item => item.product) // فقط البنود المكتملة
    };

    try {
      const response = await fetch('http://129.212.140.152/invoices/sale-invoices/create/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(invoiceData)
      });

      if (response.ok) {
        const invoice = await response.json();
        alert(`✅ تم إنشاء الفاتورة #${invoice.invoice_number}`);
        // إعادة تعيين النموذج
        setItems([{ product: '', quantity: 1, unit_price: 0 }]);
      } else {
        const error = await response.json();
        alert(`❌ خطأ: ${error.error || 'فشل الإنشاء'}`);
      }
    } catch (error) {
      alert(`❌ خطأ: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const addItem = () => {
    setItems([...items, { product: '', quantity: 1, unit_price: 0 }]);
  };

  const removeItem = (index) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const updateItem = (index, field, value) => {
    const newItems = [...items];
    newItems[index][field] = value;
    setItems(newItems);
  };

  return (
    <div className="create-invoice">
      <h2>إنشاء فاتورة جديدة</h2>
      
      <form onSubmit={handleSubmit}>
        <h3>البنود</h3>
        
        {items.map((item, index) => (
          <div key={index} className="item-row">
            <input
              type="number"
              placeholder="معرف المنتج"
              value={item.product}
              onChange={(e) => updateItem(index, 'product', e.target.value)}
              required
            />
            
            <input
              type="number"
              placeholder="الكمية"
              value={item.quantity}
              onChange={(e) => updateItem(index, 'quantity', e.target.value)}
              min="1"
              required
            />
            
            <input
              type="number"
              placeholder="السعر"
              value={item.unit_price}
              onChange={(e) => updateItem(index, 'unit_price', e.target.value)}
              min="0"
              step="0.01"
              required
            />
            
            {items.length > 1 && (
              <button type="button" onClick={() => removeItem(index)}>
                حذف
              </button>
            )}
          </div>
        ))}
        
        <button type="button" onClick={addItem}>
          إضافة بند
        </button>
        
        <button type="submit" disabled={loading}>
          {loading ? 'جاري الإنشاء...' : 'إنشاء الفاتورة'}
        </button>
      </form>
    </div>
  );
}

export default CreateInvoice;
```

---

## ✅ الخلاصة

### الآن الصيدلي يقدر:
1. ✅ **إنشاء فاتورة** لنفسه
2. ✅ **إضافة بنود** للفاتورة
3. ✅ **تعديل البنود**
4. ✅ **حذف البنود**

### لكن **فقط** لفواتيره الخاصة!

---

**تم! 🎉** الآن الصيدلي عنده صلاحية كاملة لإدارة فواتيره!

