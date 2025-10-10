# حل خطأ 500 عند إغلاق فاتورة الشراء
# Troubleshooting 500 Error When Closing Purchase Invoice

## 🔴 الخطأ | Error

```
PUT /invoices/purchase-invoices/1/change-state/
{
  "supplier_invoice_number": "4601",
  "status": "closed"
}

Response: 500 Internal Server Error
```

---

## 🔍 الأسباب المحتملة | Possible Causes

### السبب 1: الخادم لم يتم تحديثه ⭐ الأكثر احتمالاً

**المشكلة**: التغييرات في الكود موجودة محلياً فقط، ولم يتم تطبيقها على الخادم البعيد.

**التحقق**:
```bash
# اختبر إذا كانت الحقول الجديدة موجودة
GET http://129.212.140.152/invoices/purchase-invoices/1/

# إذا لم ترى هذه الحقول، فالخادم غير محدث:
# - total_public_price
# - average_purchase_discount_percentage
```

**الحل**:
1. ارفع الملفات المعدلة إلى الخادم
2. أعد تشغيل Django
3. راجع [DEPLOYMENT_STEPS.md](./DEPLOYMENT_STEPS.md)

---

### السبب 2: عناصر الفاتورة غير مستلمة

**المشكلة**: يجب أن تكون جميع عناصر الفاتورة في حالة `received` قبل الإغلاق.

**التحقق**:
```bash
GET http://129.212.140.152/invoices/purchase-invoices/1/

# تحقق من items:
{
  "items": [
    {
      "id": 1,
      "status": "placed",  // ❌ ليست received
      ...
    }
  ]
}
```

**الحل**:
```bash
# حدث حالة كل عنصر
PUT http://129.212.140.152/invoices/purchase-invoice-items/1/change-state/
{
  "status": "received"
}

# ثم حاول إغلاق الفاتورة مرة أخرى
```

---

### السبب 3: الفاتورة فارغة (بدون عناصر)

**المشكلة**: الفاتورة لا تحتوي على أي عناصر.

**التحقق**:
```bash
GET http://129.212.140.152/invoices/purchase-invoices/1/

{
  "items_count": 0,
  "items": []  // ❌ فارغة
}
```

**الحل**:
```bash
# أضف عناصر للفاتورة أولاً
POST http://129.212.140.152/invoices/purchase-invoice-items/create/
{
  "invoice": 1,
  "product": 10,
  "quantity": 100,
  "purchase_discount_percentage": 10.00,
  "selling_discount_percentage": 5.00
}
```

---

### السبب 4: المستخدم ليس لديه حساب مالي (قبل الإصلاح)

**المشكلة**: قبل الإصلاح الأخير، كان النظام يتطلب وجود حساب مالي للمستخدم.

**التحقق**:
```bash
# تحقق إذا كان الإصلاح مطبق
# إذا كان الخادم محدث، هذه المشكلة محلولة ✅
```

**الحل**:
- ✅ **تم الإصلاح!** الآن يتم إنشاء الحساب تلقائياً
- لكن يجب تحديث الخادم أولاً

---

### السبب 5: الفاتورة مغلقة بالفعل

**المشكلة**: محاولة تغيير حالة فاتورة مغلقة.

**التحقق**:
```bash
GET http://129.212.140.152/invoices/purchase-invoices/1/

{
  "status": "closed"  // ❌ مغلقة بالفعل
}
```

**الحل**:
- لا يمكن تعديل فاتورة مغلقة
- إذا كنت بحاجة للتعديل، استخدم فاتورة مرتجع

---

## 📋 خطوات الحل خطوة بخطوة | Step-by-Step Solution

### الخطوة 1: تحقق من حالة الفاتورة

```bash
GET http://129.212.140.152/invoices/purchase-invoices/1/
```

**تحقق من**:
- ✅ `items_count > 0` (الفاتورة تحتوي على عناصر)
- ✅ `status != "closed"` (ليست مغلقة بالفعل)
- ✅ جميع `items[].status == "received"` (جميع العناصر مستلمة)

### الخطوة 2: حدث حالة العناصر إذا لزم الأمر

```bash
# لكل عنصر في حالة "placed" أو "accepted"
PUT http://129.212.140.152/invoices/purchase-invoice-items/{item_id}/change-state/
{
  "status": "received"
}
```

### الخطوة 3: تأكد من تحديث الخادم

```bash
# تحقق من وجود الحقول الجديدة
GET http://129.212.140.152/invoices/purchase-invoices/1/

# إذا لم ترى هذه الحقول، حدث الخادم:
# - total_public_price
# - average_purchase_discount_percentage
```

### الخطوة 4: أغلق الفاتورة

```bash
PUT http://129.212.140.152/invoices/purchase-invoices/1/change-state/
{
  "supplier_invoice_number": "4601",
  "status": "closed"
}
```

**الاستجابة المتوقعة**:
```json
{
  "supplier_invoice_number": "4601",
  "status": "closed",
  "status_label": "Closed"
}
```

---

## 🛠️ أدوات تشخيص | Diagnostic Tools

### سكريبت Python للتحقق

```python
import requests

BASE_URL = "http://129.212.140.152"
TOKEN = "your-token-here"
INVOICE_ID = 1

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# 1. احصل على تفاصيل الفاتورة
response = requests.get(
    f"{BASE_URL}/invoices/purchase-invoices/{INVOICE_ID}/",
    headers=headers
)
invoice = response.json()

print("=== تفاصيل الفاتورة ===")
print(f"الحالة: {invoice.get('status')}")
print(f"عدد العناصر: {invoice.get('items_count')}")
print(f"رقم المورد: {invoice.get('supplier_invoice_number', 'فارغ')}")

# 2. تحقق من حالة العناصر
items = invoice.get('items', [])
pending_items = [item for item in items if item['status'] != 'received']

if pending_items:
    print(f"\n⚠️ هناك {len(pending_items)} عنصر غير مستلم:")
    for item in pending_items:
        print(f"  - العنصر {item['id']}: {item['status']}")
    print("\nيجب تحديثها إلى 'received' أولاً!")
else:
    print("\n✅ جميع العناصر مستلمة")

# 3. تحقق من الحقول الجديدة (للتأكد من تحديث الخادم)
if 'total_public_price' in invoice:
    print("\n✅ الخادم محدث (الحقول الجديدة موجودة)")
else:
    print("\n❌ الخادم غير محدث! يجب رفع التحديثات")

# 4. حاول الإغلاق
if invoice['status'] != 'closed' and not pending_items:
    print("\n🔄 محاولة إغلاق الفاتورة...")
    response = requests.put(
        f"{BASE_URL}/invoices/purchase-invoices/{INVOICE_ID}/change-state/",
        headers=headers,
        json={
            "supplier_invoice_number": "4601",
            "status": "closed"
        }
    )
    
    if response.status_code == 200:
        print("✅ تم إغلاق الفاتورة بنجاح!")
        print(response.json())
    else:
        print(f"❌ خطأ {response.status_code}")
        print(response.text)
```

---

## 📞 إذا استمرت المشكلة | If Problem Persists

### افحص سجلات الخادم

```bash
# على الخادم
tail -f /var/log/gunicorn/error.log

# أو
journalctl -u gunicorn -f

# أو
docker logs -f container_name
```

**ابحث عن**:
- `RelatedObjectDoesNotExist` → المستخدم ليس لديه حساب (يجب تحديث الكود)
- `ValidationError: Cannot close invoice` → عناصر غير مستلمة
- `DoesNotExist` → الفاتورة أو العناصر غير موجودة

### اختبر محلياً أولاً

```bash
cd E:\sky0\sky

# شغل الخادم المحلي
python manage.py runserver

# اختبر نفس الطلب محلياً
# إذا نجح محلياً لكن فشل على الخادم → مشكلة في النشر
# إذا فشل محلياً → مشكلة في البيانات أو المنطق
```

---

## ✅ قائمة التحقق النهائية | Final Checklist

قبل محاولة إغلاق الفاتورة، تأكد من:

- [ ] الخادم محدث بآخر التغييرات
- [ ] تم إعادة تشغيل Django
- [ ] الفاتورة تحتوي على عناصر (`items_count > 0`)
- [ ] جميع العناصر في حالة `received`
- [ ] الفاتورة ليست مغلقة بالفعل (`status != "closed"`)
- [ ] رقم فاتورة المورد موجود (`supplier_invoice_number`)

إذا تحققت من كل ذلك وما زال الخطأ موجوداً، شارك سجل الأخطاء من الخادم.

---

**آخر تحديث**: 2025-10-10

