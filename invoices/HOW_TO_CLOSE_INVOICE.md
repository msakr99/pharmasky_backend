# دليل إغلاق الفاتورة خطوة بخطوة
# Step-by-Step Invoice Closing Guide

## 🎯 الهدف | Goal

إغلاق فاتورة بيع **بدون أخطاء 500** مع معرفة المشاكل بالضبط.

Close a sale invoice **without 500 errors** and know exactly what's wrong.

---

## ✨ الطريقة الجديدة (الموصى بها) | New Method (Recommended)

### الخطوة 1: افحص الفاتورة أولاً

```bash
GET http://129.212.140.152/invoices/sale-invoices/1/check-closeability/
```

**Response:**
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
          "product_name": "ايه اي جي ايزوميبرازول",
          "current_status": "accepted",
          "required_status": "received"
        },
        {
          "item_id": 6,
          "product_name": "هاينوتون",
          "current_status": "accepted",
          "required_status": "received"
        }
      ]
    }
  ]
}
```

---

### الخطوة 2: اصلح المشاكل

#### إذا كانت المشكلة: `pending_items`

```bash
# غير حالة كل عنصر
PATCH http://129.212.140.152/invoices/sale-invoice-items/2/change-state/
{
  "status": "received"
}

PATCH http://129.212.140.152/invoices/sale-invoice-items/6/change-state/
{
  "status": "received"
}

# كرر لجميع العناصر...
```

#### إذا كانت المشكلة: `insufficient_inventory`

**الخيار 1: تقليل الكمية**
```bash
PATCH http://129.212.140.152/invoices/sale-invoice-items/6/
{
  "quantity": 10  # بدلاً من 25
}
```

**الخيار 2: حذف الصنف**
```bash
DELETE http://129.212.140.152/invoices/sale-invoice-items/6/
```

**الخيار 3: إضافة للمخزون**
- أضف المنتج عبر فاتورة شراء

---

### الخطوة 3: افحص مرة أخرى

```bash
GET http://129.212.140.152/invoices/sale-invoices/1/check-closeability/
```

**Response:**
```json
{
  "invoice_id": 1,
  "current_status": "placed",
  "can_close": true,  // ✅ جاهز!
  "issues": []
}
```

---

### الخطوة 4: أغلق الفاتورة

```bash
POST http://129.212.140.152/invoices/sale-invoices/1/change-state/
{
  "status": "closed"
}
```

**Response:**
```json
{
  "status": "closed",
  "status_label": "Closed",
  "success_details": {
    "message": "تم إغلاق الفاتورة بنجاح",
    "invoice_id": 1,
    "total_price": "11425.09",
    "items_count": 4
  }
}
```

---

## 🔍 معرفة الأخطاء بوضوح | Clear Error Messages

### بدلاً من:
```html
<!doctype html>
<html>
  <title>Server Error (500)</title>
</html>
```
❌ **غير واضح - ما المشكلة؟**

---

### الآن تحصل على:
```json
{
  "can_close": false,
  "issues": [
    {
      "type": "pending_items",
      "details": [
        {
          "item_id": 2,
          "product_name": "ايه اي جي ايزوميبرازول",
          "current_status": "accepted",
          "required_status": "received"
        }
      ]
    }
  ]
}
```
✅ **واضح تماماً - تعرف ماذا تفعل!**

---

## 📋 الحالات الممكنة | Possible Cases

| الحالة | can_close | issues |
|--------|-----------|--------|
| كل شيء جاهز | `true` | `[]` |
| عناصر ليست received | `false` | `[{type: "pending_items", ...}]` |
| نقص في المخزون | `false` | `[{type: "insufficient_inventory", ...}]` |
| مشاكل متعددة | `false` | `[{...}, {...}]` |

---

## 🎯 مثال في Frontend | Frontend Example

```javascript
// دالة مساعدة
async function checkAndCloseInvoice(invoiceId) {
  try {
    // 1. فحص
    const checkResp = await fetch(
      `http://129.212.140.152/invoices/sale-invoices/${invoiceId}/check-closeability/`
    );
    const checkData = await checkResp.json();
    
    // 2. عرض النتائج
    if (!checkData.can_close) {
      console.log("❌ لا يمكن الإغلاق. المشاكل:");
      
      for (const issue of checkData.issues) {
        console.log(`\n📌 ${issue.type}:`);
        console.log(`   ${issue.message}`);
        console.log(`   عدد المشاكل: ${issue.details.length}`);
        
        // عرض التفاصيل
        issue.details.forEach(detail => {
          if (issue.type === 'pending_items') {
            console.log(`   - ${detail.product_name}: ${detail.current_status} → ${detail.required_status}`);
          } else if (issue.type === 'insufficient_inventory') {
            console.log(`   - ${detail.product_name}: needs ${detail.required} but only ${detail.available} available`);
          }
        });
      }
      
      return {success: false, data: checkData};
    }
    
    // 3. إذا يمكن الإغلاق
    console.log("✅ يمكن الإغلاق. جاري الإغلاق...");
    
    const closeResp = await fetch(
      `http://129.212.140.152/invoices/sale-invoices/${invoiceId}/change-state/`,
      {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({status: 'closed'})
      }
    );
    
    const closeData = await closeResp.json();
    
    if (closeResp.ok) {
      console.log("✅ تم الإغلاق بنجاح!");
      console.log(closeData.success_details);
      return {success: true, data: closeData};
    } else {
      console.log("❌ فشل الإغلاق:", closeData);
      return {success: false, data: closeData};
    }
    
  } catch (error) {
    console.error("💥 خطأ غير متوقع:", error);
    return {success: false, error};
  }
}

// استخدام
checkAndCloseInvoice(1);
```

---

## 📊 مقارنة | Comparison

### الطريقة القديمة:
```
1. محاولة الإغلاق
2. ❌ خطأ 500
3. ??? ما المشكلة
4. محاولة يدوية للفحص
5. إصلاح
6. محاولة مرة أخرى
7. ❌ خطأ آخر...
```

### الطريقة الجديدة:
```
1. فحص (check-closeability)
2. ✅ قائمة بجميع المشاكل
3. إصلاح كل المشاكل
4. فحص مرة أخرى
5. ✅ can_close = true
6. إغلاق
7. ✅ نجح!
```

---

## 🚀 ابدأ الآن | Start Now

```bash
# جرب الآن
GET http://129.212.140.152/invoices/sale-invoices/1/check-closeability/
```

**ستحصل على معلومات واضحة بدون 500!** ✅

---

## 📁 الملفات ذات الصلة | Related Files

- `invoices/views.py` - `SaleInvoiceCheckCloseabilityAPIView`
- `invoices/urls.py` - endpoint الجديد
- `invoices/utils.py` - `close_sale_invoice()` مع فحوصات مفصلة

---

**الحالة**: ✅ جاهز للاستخدام  
**التاريخ**: 2025-10-09

