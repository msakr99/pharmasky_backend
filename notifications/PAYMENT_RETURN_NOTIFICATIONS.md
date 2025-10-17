# 💰↩️ إشعارات الدفع والمرتجعات

دليل شامل لاستخدام الإشعارات مع عمليات الدفع والمرتجعات.

---

## 📋 جدول المحتويات

1. [إشعارات الدفع](#إشعارات-الدفع)
2. [إشعارات المرتجعات](#إشعارات-المرتجعات)
3. [أمثلة عملية](#أمثلة-عملية)
4. [سيناريوهات حقيقية](#سيناريوهات-حقيقية)

---

## 💰 إشعارات الدفع

### الإشعارات التلقائية (Signals)

#### 1. دفعة شراء (Purchase Payment)

عند تسجيل دفعة من المخزن للمورد:

```python
from finance.models import PurchasePayment

# إنشاء دفعة شراء
payment = PurchasePayment.objects.create(
    user=store_user,  # المخزن
    method='CASH',  # or 'BANK', 'CHEQUE', 'PRODUCT'
    amount=5000.00,
    at=timezone.now(),
    remarks="دفعة للمورد أحمد"
)

# ✨ إشعار تلقائي يُرسل للمخزن:
# "💰 دفعة شراء جديدة"
# "تم تسجيل دفعة شراء بقيمة 5000 جنيه. طريقة الدفع: Cash"
```

#### 2. دفعة بيع (Sale Payment)

عند تسجيل دفعة من الصيدلية للمخزن:

```python
from finance.models import SalePayment

# إنشاء دفعة بيع
payment = SalePayment.objects.create(
    user=pharmacy_user,  # الصيدلية
    method='BANK',
    amount=3000.00,
    at=timezone.now(),
    remarks="تحويل بنكي"
)

# ✨ إشعار تلقائي يُرسل للصيدلية:
# "✅ تم تسجيل دفعتك"
# "تم تسجيل دفعة بقيمة 3000 جنيه بنجاح. طريقة الدفع: Bank Transfer"
```

---

### استخدام Utility Functions

```python
from finance.notifications import (
    notify_purchase_payment,
    notify_sale_payment,
    notify_payment_received,
    notify_payment_reminder,
)

# 1. إشعار دفعة شراء
notify_purchase_payment(payment)

# 2. إشعار دفعة بيع
notify_sale_payment(payment)

# 3. إشعار عام باستلام دفعة
notify_payment_received(
    user=pharmacy_user,
    amount=2000,
    method="نقداً",
    payment_type="sale"
)

# 4. تذكير بالدفع
notify_payment_reminder(
    user=pharmacy_user,
    outstanding_balance=10000
)
# "⏰ تذكير بالدفع"
# "لديك رصيد مستحق بقيمة 10000 جنيه. يرجى السداد في أقرب وقت."
```

---

## ↩️ إشعارات المرتجعات

### الإشعارات التلقائية (Signals)

#### 1. مرتجع شراء (Purchase Return)

عند إرجاع المخزن منتجات للمورد:

```python
from invoices.models import PurchaseReturnInvoice

# إنشاء مرتجع شراء
return_invoice = PurchaseReturnInvoice.objects.create(
    user=store_user,  # المخزن
    items_count=3,
    total_quantity=15,
    total_price=750.00,
    status='PLACED'
)

# ✨ إشعار تلقائي للمخزن:
# "↩️ مرتجع شراء جديد"
# "تم إنشاء مرتجع شراء رقم #789 بقيمة 750 جنيه"
```

#### 2. مرتجع بيع (Sale Return)

عند إرجاع الصيدلية منتجات للمخزن:

```python
from invoices.models import SaleReturnInvoice

# إنشاء مرتجع بيع
return_invoice = SaleReturnInvoice.objects.create(
    user=pharmacy_user,  # الصيدلية
    items_count=2,
    total_quantity=8,
    total_price=400.00,
    status='PLACED'
)

# ✨ إشعار تلقائي للصيدلية:
# "↩️ طلب إرجاع تم إنشاؤه"
# "تم إنشاء طلب إرجاع رقم #456 بقيمة 400 جنيه. سيتم مراجعته قريباً."
```

---

### تحديثات حالة المرتجع

#### تغيير الحالة → تحديث تلقائي

```python
# الموافقة على الإرجاع
return_invoice.status = 'APPROVED'
return_invoice.save()
# ✨ "✅ تمت الموافقة على طلب إرجاعك"

# رفض الإرجاع
return_invoice.status = 'REJECTED'
return_invoice.save()
# ✨ "❌ تم رفض طلب الإرجاع"

# إكمال الإرجاع
return_invoice.status = 'COMPLETED'
return_invoice.save()
# ✨ "✅ تم إكمال عملية الإرجاع واسترداد المبلغ 💰"
```

---

### استخدام Utility Functions

```python
from finance.notifications import (
    notify_return_created,
    notify_return_approved,
    notify_return_rejected,
    notify_return_completed,
    notify_refund_processed,
)

# 1. إشعار بإنشاء طلب إرجاع
notify_return_created(return_invoice, return_type="sale")

# 2. إشعار بالموافقة
notify_return_approved(return_invoice, return_type="sale")

# 3. إشعار بالرفض (مع السبب)
notify_return_rejected(
    return_invoice,
    reason="المنتج تالف بسبب سوء الاستخدام",
    return_type="sale"
)

# 4. إشعار بإكمال الإرجاع
notify_return_completed(
    return_invoice,
    refund_amount=400.00,
    return_type="sale"
)

# 5. إشعار باسترداد المبلغ
notify_refund_processed(
    user=pharmacy_user,
    amount=400.00,
    original_invoice_id=123
)
```

---

## 🎯 أمثلة عملية

### مثال 1: سيناريو دفعة كاملة

```python
from finance.models import SalePayment
from finance.notifications import notify_payment_received

# صيدلية تدفع للمخزن
payment = SalePayment.objects.create(
    user=pharmacy_user,
    method='BANK',
    amount=15000.00,
    at=timezone.now(),
    remarks="دفعة شهر أكتوبر"
)

# إشعار إضافي للمخزن (البائع)
notify_payment_received(
    user=store_owner,  # صاحب المخزن
    amount=15000,
    method="تحويل بنكي",
    payment_type="sale"
)
```

### مثال 2: سيناريو مرتجع كامل

```python
from invoices.models import SaleReturnInvoice
from finance.notifications import (
    notify_return_approved,
    notify_return_completed,
    notify_refund_processed
)

# 1. الصيدلية تنشئ طلب إرجاع
return_invoice = SaleReturnInvoice.objects.create(
    user=pharmacy_user,
    items_count=5,
    total_quantity=20,
    total_price=1200.00,
    status='PLACED'
)
# ✨ إشعار تلقائي: "↩️ طلب إرجاع تم إنشاؤه"

# 2. المخزن يوافق على الإرجاع
return_invoice.status = 'APPROVED'
return_invoice.save()
# ✨ إشعار تلقائي: "✅ تمت الموافقة على طلب إرجاعك"

# 3. يتم إكمال الإرجاع واسترداد المبلغ
return_invoice.status = 'COMPLETED'
return_invoice.save()
# ✨ إشعار تلقائي: "✅ تم إكمال عملية الإرجاع واسترداد المبلغ 💰"

# 4. إشعار إضافي باسترداد المبلغ
notify_refund_processed(
    user=pharmacy_user,
    amount=1200.00,
    original_invoice_id=return_invoice.pk
)
```

### مثال 3: تذكير بالدفع المستحق

```python
from finance.notifications import notify_payment_reminder
from finance.models import Account

# جلب الصيدليات التي عليها رصيد مستحق
pharmacies = User.objects.filter(role='PHARMACY')

for pharmacy in pharmacies:
    account = Account.objects.get(user=pharmacy)
    
    # إذا كان الرصيد سالب (مديون)
    if account.balance < 0:
        outstanding = abs(account.balance)
        
        # إرسال تذكير
        notify_payment_reminder(
            user=pharmacy,
            outstanding_balance=outstanding
        )
```

---

## 🔄 سيناريوهات حقيقية

### سيناريو 1: دفعة جزئية

```python
from finance.models import SalePayment, Account

# الصيدلية عليها 20,000 جنيه
account = Account.objects.get(user=pharmacy_user)
print(f"الرصيد الحالي: {account.balance}")  # -20000

# تدفع 10,000 جنيه
payment = SalePayment.objects.create(
    user=pharmacy_user,
    method='CASH',
    amount=10000.00,
    at=timezone.now(),
    remarks="دفعة جزئية"
)

# ✨ إشعار: "✅ تم تسجيل دفعتك - تم تسجيل دفعة بقيمة 10000 جنيه"

# الرصيد المتبقي
account.refresh_from_db()
remaining = abs(account.balance)  # 10000

# تذكير بالرصيد المتبقي
notify_payment_reminder(pharmacy_user, remaining)
```

### سيناريو 2: مرتجع مرفوض

```python
from invoices.models import SaleReturnInvoice
from finance.notifications import notify_return_rejected

# صيدلية تطلب إرجاع منتجات
return_invoice = SaleReturnInvoice.objects.create(
    user=pharmacy_user,
    items_count=3,
    total_quantity=10,
    total_price=800.00,
    status='PLACED'
)

# المخزن يرفض الإرجاع
return_invoice.status = 'REJECTED'
return_invoice.save()

# إشعار إضافي مع السبب المفصل
notify_return_rejected(
    return_invoice,
    reason="المنتجات تجاوزت تاريخ الصلاحية المسموح للإرجاع (30 يوم)",
    return_type="sale"
)
```

### سيناريو 3: دفعة بالمنتجات

```python
from finance.models import SalePayment

# صيدلية تدفع بمنتجات بدلاً من نقد
payment = SalePayment.objects.create(
    user=pharmacy_user,
    method='PRODUCT',  # دفع بالمنتجات
    amount=5000.00,
    at=timezone.now(),
    remarks="دفع بمنتجات: 100 علبة باراسيتامول"
)

# ✨ إشعار: "✅ تم تسجيل دفعتك - تم تسجيل دفعة بقيمة 5000 جنيه. طريقة الدفع: Products"
```

---

## 📊 ملخص الإشعارات

### إشعارات الدفع

| الحدث | الإشعار | المستقبل |
|------|---------|----------|
| إنشاء دفعة شراء | "💰 دفعة شراء جديدة" | المخزن |
| إنشاء دفعة بيع | "✅ تم تسجيل دفعتك" | الصيدلية |
| تذكير بالدفع | "⏰ تذكير بالدفع" | الصيدلية |
| استلام دفعة | "💰 تم استلام الدفع" | المخزن |

### إشعارات المرتجعات

| الحدث | الإشعار | المستقبل |
|------|---------|----------|
| إنشاء مرتجع شراء | "↩️ مرتجع شراء جديد" | المخزن |
| إنشاء مرتجع بيع | "↩️ طلب إرجاع تم إنشاؤه" | الصيدلية |
| الموافقة على الإرجاع | "✅ تمت الموافقة على طلب إرجاعك" | الصيدلية/المخزن |
| رفض الإرجاع | "❌ تم رفض طلب الإرجاع" | الصيدلية/المخزن |
| إكمال الإرجاع | "✅ تم إكمال عملية الإرجاع" | الصيدلية/المخزن |
| استرداد المبلغ | "💰 تم استرداد المبلغ" | الصيدلية |

---

## 🔧 Integration في Views

### مثال: API Endpoint للدفع

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from finance.models import SalePayment
from finance.notifications import notify_payment_received

class CreatePaymentView(APIView):
    def post(self, request):
        # إنشاء الدفعة
        payment = SalePayment.objects.create(
            user=request.user,
            method=request.data.get('method'),
            amount=request.data.get('amount'),
            at=timezone.now(),
            remarks=request.data.get('remarks', '')
        )
        
        # الإشعار يُرسل تلقائياً بواسطة Signal
        
        return Response({
            "success": True,
            "payment_id": payment.pk,
            "message": "تم تسجيل الدفعة وإرسال الإشعار"
        })
```

### مثال: API Endpoint للمرتجع

```python
from rest_framework.views import APIView
from invoices.models import SaleReturnInvoice

class UpdateReturnStatusView(APIView):
    def patch(self, request, pk):
        return_invoice = SaleReturnInvoice.objects.get(pk=pk)
        
        # تحديث الحالة
        return_invoice.status = request.data.get('status')
        return_invoice.save()
        
        # الإشعار يُرسل تلقائياً بواسطة Signal
        
        return Response({
            "success": True,
            "message": "تم تحديث حالة المرتجع وإرسال الإشعار"
        })
```

---

## ✅ الخلاصة

### التلقائي (Signals) ✨
- ✅ إشعار عند إنشاء دفعة شراء/بيع
- ✅ إشعار عند إنشاء مرتجع
- ✅ إشعار عند تغيير حالة المرتجع

### Manual (Utility Functions) 🔧
- إشعارات مخصصة بسبب محدد
- تذكيرات بالدفع
- إشعارات استرداد المبلغ

**النظام جاهز 100% - فقط استخدمه! 🎉**

