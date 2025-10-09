# رسائل الخطأ المفصلة عند إغلاق الفواتير
# Detailed Error Messages for Invoice Closure

## 🎯 الهدف | Purpose

عند محاولة إغلاق فاتورة بيع، يتم الآن عرض رسائل خطأ **مفصلة** توضح المشكلة بالضبط بدلاً من رسائل عامة.

When attempting to close a sale invoice, detailed error messages are now provided instead of generic ones.

---

## ✨ ما الجديد | What's New

### قبل التحديث | Before

```json
{
  "detail": "Cannot close invoice with pending action items."
}
```

❌ **رسالة غير واضحة** - ما هي المشكلة بالضبط؟

---

### بعد التحديث | After

#### 1️⃣ خطأ: عناصر لم تستلم | Not Received Items

```json
{
  "detail": "❌ لا يمكن إغلاق الفاتورة - يجب أن تكون جميع العناصر في حالة Received:\n• ايه اي جي ايزوميبرازول 40مجم: الحالة الحالية (Accepted) - يجب تغييرها إلى (Received)\n• هاينوتون 10 اكياس: الحالة الحالية (Placed) - يجب تغييرها إلى (Received)",
  "pending_items": [
    {
      "item_id": 2,
      "product_name": "ايه اي جي ايزوميبرازول 40مجم",
      "current_status": "accepted",
      "current_status_label": "Accepted",
      "required_status": "received"
    },
    {
      "item_id": 6,
      "product_name": "هاينوتون 10 اكياس",
      "current_status": "placed",
      "current_status_label": "Placed",
      "required_status": "received"
    }
  ]
}
```

✅ **رسالة واضحة** - تعرف بالضبط أي عناصر تحتاج تحديث!

---

#### 2️⃣ خطأ: نقص في المخزون | Inventory Shortage

```json
{
  "detail": "❌ لا يمكن إغلاق الفاتورة - نقص في المخزون:\n• هاينوتون 10 اكياس: يحتاج 25 لكن متوفر 10 (نقص: 15)\n• كيناكورت - ايه 40مجم: يحتاج 10 لكن متوفر 5 (نقص: 5)",
  "inventory_issues": [
    {
      "product_id": 25,
      "product_name": "هاينوتون 10 اكياس",
      "required": 25,
      "available": 10,
      "shortage": 15
    },
    {
      "product_id": 31,
      "product_name": "كيناكورت - ايه 40مجم",
      "required": 10,
      "available": 5,
      "shortage": 5
    }
  ],
  "can_close": false
}
```

✅ **رسالة دقيقة** - تعرف بالضبط كم تحتاج لإضافة المخزون!

---

#### 3️⃣ نجاح: تم الإغلاق | Success

```json
{
  "status": "closed",
  "status_label": "Closed",
  "success_details": {
    "message": "✅ تم إغلاق الفاتورة بنجاح",
    "invoice_id": 1,
    "total_price": "11425.09",
    "items_count": 4,
    "total_quantity": 93,
    "closed_at": "2025-10-09T10:16:12.960632Z"
  }
}
```

✅ **تأكيد واضح** - معلومات كاملة عن الفاتورة المغلقة!

---

## 📊 أمثلة عملية | Practical Examples

### مثال 1: عناصر ليست Received

```bash
POST /api/v1/invoices/sale-invoices/1/change-state/
{
  "status": "closed"
}

# Response (400 Bad Request)
{
  "detail": "❌ لا يمكن إغلاق الفاتورة - يجب أن تكون جميع العناصر في حالة Received:\n• ايه اي جي ايزوميبرازول: الحالة الحالية (Accepted) - يجب تغييرها إلى (Received)\n• هاينوتون: الحالة الحالية (Accepted) - يجب تغييرها إلى (Received)\n• كيناكورت: الحالة الحالية (Accepted) - يجب تغييرها إلى (Received)\n• بيوتين: الحالة الحالية (Accepted) - يجب تغييرها إلى (Received)",
  "pending_items": [
    {
      "item_id": 2,
      "product_name": "ايه اي جي ايزوميبرازول 40مجم 21 كبسولة",
      "current_status": "accepted",
      "current_status_label": "Accepted",
      "required_status": "received"
    },
    {
      "item_id": 6,
      "product_name": "هاينوتون 10 اكياس",
      "current_status": "accepted",
      "current_status_label": "Accepted",
      "required_status": "received"
    },
    {
      "item_id": 7,
      "product_name": "كيناكورت - ايه 40مجم/مل فيال",
      "current_status": "accepted",
      "current_status_label": "Accepted",
      "required_status": "received"
    },
    {
      "item_id": 8,
      "product_name": "بيوتين 10000مكجم 50 كبسولة مستورد",
      "current_status": "accepted",
      "current_status_label": "Accepted",
      "required_status": "received"
    }
  ]
}
```

**الحل:**
```bash
# تحديث كل عنصر
PATCH /api/v1/invoices/sale-invoice-items/2/change-state/
{"status": "received"}

PATCH /api/v1/invoices/sale-invoice-items/6/change-state/
{"status": "received"}

PATCH /api/v1/invoices/sale-invoice-items/7/change-state/
{"status": "received"}

PATCH /api/v1/invoices/sale-invoice-items/8/change-state/
{"status": "received"}
```

---

### مثال 2: نقص في المخزون

```bash
POST /api/v1/invoices/sale-invoices/1/change-state/
{
  "status": "closed"
}

# Response (400 Bad Request)
{
  "detail": "❌ لا يمكن إغلاق الفاتورة - نقص في المخزون:\n• هاينوتون 10 اكياس: يحتاج 25 لكن متوفر 10 (نقص: 15)",
  "inventory_issues": [
    {
      "product_id": 25,
      "product_name": "هاينوتون 10 اكياس",
      "required": 25,
      "available": 10,
      "shortage": 15
    }
  ],
  "can_close": false
}
```

**الحلول:**

#### الحل 1: تقليل الكمية
```bash
PATCH /api/v1/invoices/sale-invoice-items/6/
{
  "quantity": 10  # بدلاً من 25
}
```

#### الحل 2: حذف الصنف
```bash
DELETE /api/v1/invoices/sale-invoice-items/6/
```

#### الحل 3: إضافة للمخزون
```bash
# إضافة المنتج للمخزون عبر فاتورة شراء
POST /api/v1/invoices/purchase-invoices/
{
  "user": 5,
  "items": [
    {
      "offer": 92,
      "quantity": 20  # إضافة 20 وحدة
    }
  ]
}
```

---

### مثال 3: النجاح

```bash
POST /api/v1/invoices/sale-invoices/1/change-state/
{
  "status": "closed"
}

# Response (200 OK)
{
  "status": "closed",
  "status_label": "Closed",
  "success_details": {
    "message": "✅ تم إغلاق الفاتورة بنجاح",
    "invoice_id": 1,
    "total_price": "11425.09",
    "items_count": 4,
    "total_quantity": 93,
    "closed_at": "2025-10-09T10:16:12.960632Z"
  }
}
```

---

## 🔍 التفاصيل الفنية | Technical Details

### التحقق من حالة العناصر

```python
# في utils.py - close_sale_invoice()
pending_action_items = invoice.items.exclude(
    status=SaleInvoiceItemStatusChoice.RECEIVED
)

if pending_action_items.exists():
    # بناء رسالة مفصلة
    pending_details = []
    for item in pending_action_items:
        pending_details.append(
            f"• {item.product.name}: "
            f"الحالة الحالية ({item.get_status_display()}) - "
            f"يجب تغييرها إلى (Received)"
        )
```

### التحقق من المخزون

```python
# في utils.py - close_sale_invoice()
if update_inventory:
    inventory = get_or_create_main_inventory()
    inventory_issues = []
    
    for item in invoice.items.all():
        available_quantity = InventoryItem.objects.filter(
            inventory=inventory,
            product=item.product
        ).aggregate(total=Sum('remaining_quantity'))['total'] or 0
        
        if available_quantity < item.quantity:
            shortage = item.quantity - available_quantity
            inventory_issues.append({
                "product_id": item.product.id,
                "product_name": item.product.name,
                "required": item.quantity,
                "available": available_quantity,
                "shortage": shortage
            })
```

---

## 📋 هيكل رسالة الخطأ | Error Response Structure

### خطأ العناصر | Items Error

```typescript
{
  detail: string,              // رسالة مفصلة متعددة الأسطر
  pending_items: Array<{
    item_id: number,
    product_name: string,
    current_status: string,
    current_status_label: string,
    required_status: string
  }>
}
```

### خطأ المخزون | Inventory Error

```typescript
{
  detail: string,              // رسالة مفصلة متعددة الأسطر
  inventory_issues: Array<{
    product_id: number,
    product_name: string,
    required: number,
    available: number,
    shortage: number
  }>,
  can_close: false
}
```

### رسالة النجاح | Success Response

```typescript
{
  status: "closed",
  status_label: "Closed",
  success_details: {
    message: string,
    invoice_id: number,
    total_price: string,
    items_count: number,
    total_quantity: number,
    closed_at: string
  }
}
```

---

## 🎯 الفوائد | Benefits

### 1. **وضوح أكبر** | Better Clarity
- معرفة المشكلة بالضبط
- معرفة الحل المطلوب

### 2. **توفير الوقت** | Time Saving
- لا حاجة لفحص كل عنصر يدوياً
- معرفة النقص في المخزون مباشرة

### 3. **تجربة مستخدم أفضل** | Better UX
- رسائل بالعربية واضحة
- معلومات قابلة للتنفيذ

### 4. **تكامل سهل** | Easy Integration
- JSON منظم
- سهل الاستخدام في Frontend

---

## 💡 استخدام في Frontend

```javascript
// محاولة إغلاق الفاتورة
try {
  const response = await fetch('/api/v1/invoices/sale-invoices/1/change-state/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({status: 'closed'})
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // نجح الإغلاق
    alert(data.success_details.message);
    console.log('تم إغلاق الفاتورة:', data.success_details);
  } else {
    // فشل الإغلاق
    if (data.pending_items) {
      // مشكلة في حالة العناصر
      console.log('عناصر تحتاج تحديث:', data.pending_items);
      showPendingItemsModal(data.pending_items);
    }
    
    if (data.inventory_issues) {
      // نقص في المخزون
      console.log('نقص في المخزون:', data.inventory_issues);
      showInventoryShortageModal(data.inventory_issues);
    }
    
    // عرض الرسالة
    alert(data.detail);
  }
} catch (error) {
  console.error('خطأ:', error);
}
```

---

## 📁 الملفات المعدلة | Modified Files

1. **`invoices/utils.py`**
   - ✅ تحسين `close_sale_invoice()`
   - ✅ إضافة فحص العناصر المفصل
   - ✅ إضافة فحص المخزون المفصل

2. **`invoices/views.py`**
   - ✅ تحسين `SaleInvoiceStateUpdateAPIView`
   - ✅ إضافة `success_details` عند النجاح
   - ✅ إضافة `prefetch_related` للأداء

---

## 🚀 الحالة | Status

✅ **جاهز للإنتاج** | Production Ready  
📅 **التاريخ**: 2025-10-09  
🔖 **الإصدار**: 1.0

---

**ملاحظة**: هذه التحسينات تعمل تلقائياً عند محاولة إغلاق أي فاتورة بيع!

