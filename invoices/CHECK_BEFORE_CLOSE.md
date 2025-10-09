# فحص الفاتورة قبل الإغلاق
# Check Invoice Before Closing

## 🎯 Endpoint جديد للفحص | New Check Endpoint

### قبل محاولة إغلاق الفاتورة، افحصها أولاً!

```bash
GET /api/v1/invoices/sale-invoices/{id}/check-closeability/
```

---

## 📊 مثال على الاستخدام | Usage Example

### 1️⃣ فحص الفاتورة

```bash
GET http://129.212.140.152/invoices/sale-invoices/1/check-closeability/
```

### 2️⃣ Response - يمكن الإغلاق ✅

```json
{
  "invoice_id": 1,
  "current_status": "placed",
  "can_close": true,
  "issues": []
}
```

**معنى:** الفاتورة جاهزة للإغلاق! يمكنك المتابعة بأمان.

---

### 3️⃣ Response - لا يمكن الإغلاق (عناصر ليست Received) ❌

```json
{
  "invoice_id": 1,
  "current_status": "placed",
  "can_close": false,
  "issues": [
    {
      "type": "pending_items",
      "message": "Not all items are in Received status",
      "details": [
        {
          "item_id": 2,
          "product_name": "ايه اي جي ايزوميبرازول 40مجم 21 كبسولة",
          "current_status": "accepted",
          "required_status": "received"
        },
        {
          "item_id": 6,
          "product_name": "هاينوتون 10 اكياس",
          "current_status": "accepted",
          "required_status": "received"
        },
        {
          "item_id": 7,
          "product_name": "كيناكورت - ايه 40مجم/مل فيال",
          "current_status": "accepted",
          "required_status": "received"
        },
        {
          "item_id": 8,
          "product_name": "بيوتين 10000مكجم 50 كبسولة مستورد",
          "current_status": "accepted",
          "required_status": "received"
        }
      ]
    }
  ]
}
```

**الحل:** غير حالة جميع العناصر إلى `received`:
```bash
PATCH /api/v1/invoices/sale-invoice-items/2/change-state/
{"status": "received"}
# كرر لـ 6, 7, 8
```

---

### 4️⃣ Response - نقص في المخزون ❌

```json
{
  "invoice_id": 1,
  "current_status": "placed",
  "can_close": false,
  "issues": [
    {
      "type": "insufficient_inventory",
      "message": "Not enough inventory available",
      "details": [
        {
          "product_id": 25,
          "product_name": "هاينوتون 10 اكياس",
          "required": 25,
          "available": 10,
          "shortage": 15
        },
        {
          "product_id": 31,
          "product_name": "كيناكورت - ايه 40مجم/مل فيال",
          "required": 10,
          "available": 5,
          "shortage": 5
        }
      ]
    }
  ]
}
```

**الحلول:**
1. تقليل الكميات في الفاتورة
2. إضافة كميات للمخزون
3. حذف بعض الأصناف

---

### 5️⃣ Response - مشاكل متعددة ❌

```json
{
  "invoice_id": 1,
  "current_status": "placed",
  "can_close": false,
  "issues": [
    {
      "type": "pending_items",
      "message": "Not all items are in Received status",
      "details": [...]
    },
    {
      "type": "insufficient_inventory",
      "message": "Not enough inventory available",
      "details": [...]
    }
  ]
}
```

**معنى:** هناك مشكلتين:
1. العناصر ليست Received
2. نقص في المخزون

---

## 🔄 طريقة العمل الصحيحة | Correct Workflow

```bash
# 1. فحص أولاً
GET /api/v1/invoices/sale-invoices/1/check-closeability/

# 2. إذا can_close = false
#    - اقرأ issues
#    - اصلح المشاكل

# 3. فحص مرة أخرى
GET /api/v1/invoices/sale-invoices/1/check-closeability/

# 4. إذا can_close = true
#    - أغلق الفاتورة
POST /api/v1/invoices/sale-invoices/1/change-state/
{"status": "closed"}
```

---

## 💡 الفوائد | Benefits

### 1. **لا مفاجآت** | No Surprises
- تعرف المشاكل قبل محاولة الإغلاق
- لا أخطاء 500 غامضة

### 2. **معلومات واضحة** | Clear Information
- تعرف بالضبط ماذا تحتاج لإصلاح
- قائمة بكل المشاكل

### 3. **توفير الوقت** | Time Saving
- فحص سريع قبل الإغلاق
- معرفة جميع المشاكل دفعة واحدة

---

## 🔍 هيكل Response | Response Structure

```typescript
{
  invoice_id: number,
  current_status: string,
  can_close: boolean,
  issues: Array<{
    type: "pending_items" | "insufficient_inventory",
    message: string,
    details: Array<any>
  }>
}
```

---

## 📋 أنواع المشاكل | Issue Types

### 1. `pending_items`
**المعنى:** عناصر ليست في حالة Received  
**الحل:** غير حالتها إلى received

### 2. `insufficient_inventory`
**المعنى:** نقص في المخزون  
**الحل:** أضف للمخزون أو قلل الكمية

---

## 🎯 مثال كامل | Complete Example

```javascript
// في Frontend
async function closeInvoice(invoiceId) {
  // 1. فحص أولاً
  const checkResponse = await fetch(
    `/api/v1/invoices/sale-invoices/${invoiceId}/check-closeability/`
  );
  const checkData = await checkResponse.json();
  
  if (!checkData.can_close) {
    // عرض المشاكل للمستخدم
    console.log("Cannot close. Issues:", checkData.issues);
    
    for (const issue of checkData.issues) {
      if (issue.type === 'pending_items') {
        alert(`يجب تحديث ${issue.details.length} عناصر إلى حالة Received`);
      }
      if (issue.type === 'insufficient_inventory') {
        alert(`نقص في المخزون لـ ${issue.details.length} منتجات`);
      }
    }
    
    return false;
  }
  
  // 2. إذا كان يمكن الإغلاق، اغلق
  const closeResponse = await fetch(
    `/api/v1/invoices/sale-invoices/${invoiceId}/change-state/`,
    {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({status: 'closed'})
    }
  );
  
  if (closeResponse.ok) {
    const data = await closeResponse.json();
    console.log("Success!", data.success_details);
    return true;
  }
  
  return false;
}
```

---

## ✅ جاهز للاستخدام | Ready to Use

**الآن جرب:**

```bash
# فحص الفاتورة أولاً
GET http://129.212.140.152/invoices/sale-invoices/1/check-closeability/
```

سيخبرك بالضبط ما هي المشاكل **بدون خطأ 500**! 🎯

---

**التاريخ**: 2025-10-09  
**الحالة**: ✅ جاهز

