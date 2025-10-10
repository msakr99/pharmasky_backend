# دليل حل خطأ 500 السريع
# Quick Guide to Fix 500 Error

## ❓ المشكلة

تحصل على خطأ 500 عند محاولة إغلاق فاتورة الشراء:

```http
PUT http://129.212.140.152/invoices/purchase-invoices/1/change-state/
{
  "supplier_invoice_number": "4601",
  "status": "closed"
}

❌ Response: 500 Internal Server Error
```

---

## ✅ الحل السريع (3 خطوات)

### الخطوة 1: شغل السكريبت التشخيصي

```bash
cd E:\sky0\sky

# عدل السكريبت أولاً
# افتح diagnose_invoice.py وغير:
#   - TOKEN = "your-token-here"  → ضع توكن المصادقة
#   - INVOICE_ID = 1             → رقم الفاتورة

# شغل السكريبت
python diagnose_invoice.py
```

**السكريبت سيفحص**:
- ✓ هل الخادم محدث؟
- ✓ هل الفاتورة في حالة صحيحة؟
- ✓ هل توجد عناصر في الفاتورة؟
- ✓ هل العناصر مستلمة؟

---

### الخطوة 2: حسب نتيجة السكريبت

#### إذا قال: "❌ الخادم غير محدث"

**المشكلة**: التعديلات موجودة محلياً فقط!

**الحل**:
```bash
# على جهاز التطوير (عندك)
git add invoices/models.py finance/models.py invoices/serializers.py
git commit -m "Fix 500 error on invoice close"
git push origin main

# على الخادم البعيد
ssh user@129.212.140.152
cd /path/to/project
git pull origin main

# أعد تشغيل Django
sudo systemctl restart gunicorn
# أو
sudo systemctl restart uwsgi
# أو
docker-compose restart
```

#### إذا قال: "❌ عناصر غير مستلمة"

**الحل**:
```bash
# حدث حالة كل عنصر
PUT http://129.212.140.152/invoices/purchase-invoice-items/1/change-state/
{
  "status": "received"
}

PUT http://129.212.140.152/invoices/purchase-invoice-items/2/change-state/
{
  "status": "received"
}

# ثم حاول الإغلاق مرة أخرى
```

#### إذا قال: "❌ الفاتورة فارغة"

**الحل**:
```bash
# أضف عناصر أولاً
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

### الخطوة 3: حاول الإغلاق مرة أخرى

```bash
PUT http://129.212.140.152/invoices/purchase-invoices/1/change-state/
{
  "supplier_invoice_number": "4601",
  "status": "closed"
}

✅ Response: 200 OK
{
  "supplier_invoice_number": "4601",
  "status": "closed",
  "status_label": "Closed"
}
```

---

## 🎯 الحل الأكثر احتمالاً

**في 90% من الحالات**، المشكلة هي:
> **الخادم البعيد لم يتم تحديثه بعد**

**الخطوات**:

1. **ارفع الملفات** إلى الخادم:
   ```bash
   git push origin main
   ```

2. **على الخادم**، اسحب التحديثات:
   ```bash
   ssh user@129.212.140.152
   cd /path/to/project
   git pull origin main
   ```

3. **أعد تشغيل** Django:
   ```bash
   sudo systemctl restart gunicorn
   ```

4. **جرب مرة أخرى**!

---

## 🔍 كيف تتحقق؟

### تحقق إذا كان الخادم محدث:

```bash
# اطلب تفاصيل الفاتورة
GET http://129.212.140.152/invoices/purchase-invoices/1/

# تحقق من وجود هذه الحقول:
{
  "total_public_price": "...",              // ⬅️ جديد
  "average_purchase_discount_percentage": "...",  // ⬅️ جديد
  ...
}
```

**إذا رأيت الحقول الجديدة** ✅ → الخادم محدث  
**إذا لم ترها** ❌ → الخادم غير محدث (ارفع التحديثات!)

---

## 📚 ملفات مساعدة

حسب المشكلة، راجع:

| المشكلة | الملف |
|---------|-------|
| كيفية النشر على الخادم | [DEPLOYMENT_STEPS.md](./DEPLOYMENT_STEPS.md) |
| تشخيص تفصيلي للأخطاء | [TROUBLESHOOTING_500_ERROR.md](./TROUBLESHOOTING_500_ERROR.md) |
| فهم الحقول الجديدة | [PURCHASE_DISCOUNT_DOCUMENTATION.md](./invoices/PURCHASE_DISCOUNT_DOCUMENTATION.md) |
| أمثلة عملية | [EXAMPLES.md](./invoices/EXAMPLES.md) |
| مرجع سريع | [QUICK_REFERENCE.md](./invoices/QUICK_REFERENCE.md) |

---

## 💡 نصائح سريعة

### 1. اختبر محلياً أولاً

قبل النشر، جرب محلياً:

```bash
cd E:\sky0\sky
python manage.py runserver

# في نافذة أخرى
curl -X PUT http://localhost:8000/invoices/purchase-invoices/1/change-state/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{"supplier_invoice_number": "4601", "status": "closed"}'
```

إذا نجح محلياً ← المشكلة في النشر  
إذا فشل محلياً ← المشكلة في البيانات

### 2. استخدم السكريبت التشخيصي

```bash
python diagnose_invoice.py
```

يعطيك تقرير كامل عن حالة الفاتورة!

### 3. افحص سجلات الخادم

```bash
# على الخادم
tail -f /var/log/gunicorn/error.log
```

ستجد الخطأ الدقيق هناك.

---

## 🆘 إذا استمرت المشكلة

إذا جربت كل شيء وما زال الخطأ موجوداً:

1. ✅ شغل السكريبت: `python diagnose_invoice.py`
2. ✅ افحص سجلات الخادم
3. ✅ راجع [TROUBLESHOOTING_500_ERROR.md](./TROUBLESHOOTING_500_ERROR.md)
4. ✅ شارك رسالة الخطأ من السجلات

---

## ✨ بعد حل المشكلة

بعد نجاح الإغلاق، ستحصل على:

```json
GET /invoices/purchase-invoices/1/

{
  "status": "closed",
  "status_label": "Closed",
  "supplier_invoice_number": "4601",
  "total_price": "1750.00",
  "total_public_price": "2000.00",           // ⬅️ جديد
  "average_purchase_discount_percentage": "12.50",  // ⬅️ جديد
  ...
}
```

**الميزات الجديدة**:
- 📊 متابعة متوسط الخصم من الموردين
- 💰 مقارنة الأسعار قبل وبعد الخصم
- 📈 تقارير شهرية للتوفير

---

**آخر تحديث**: 2025-10-10  
**حظاً موفقاً!** 🚀

