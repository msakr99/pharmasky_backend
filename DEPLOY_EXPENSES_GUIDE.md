# دليل نشر نظام المصاريف
# Expenses System Deployment Guide

## 🎯 ما تم إضافته

✅ **نظام كامل للمصاريف**
- مصاريف شهرية (مرتبات، إيجارات، أرباح)
- مصاريف نثرية (قرطاسية، صيانة، إلخ)
- يُحسب تلقائياً في رأس المال

---

## 📦 الملفات الجديدة/المعدلة

### ملفات جديدة (7):
1. `finance/expense_choices.py` - خيارات المصاريف
2. `finance/migrations/0004_expense.py` - Migration
3. `finance/EXPENSES_GUIDE.md` - دليل شامل (21 KB)
4. `finance/EXPENSES_CHANGELOG.md` - سجل التحديثات
5. `EXPENSES_QUICK.md` - ملخص سريع
6. `DEPLOY_EXPENSES_GUIDE.md` - هذا الملف

### ملفات معدلة (6):
1. `finance/models.py` - إضافة Expense model
2. `finance/serializers.py` - إضافة ExpenseSerializer
3. `finance/views.py` - إضافة Expense views
4. `finance/urls.py` - إضافة URLs
5. `finance/admin.py` - إضافة Expense admin
6. `SAFE_QUICK.md` - تحديث

---

## 🚀 خطوات النشر

### 1️⃣ على جهازك (محلياً)

```bash
cd E:\sky0\sky

# رفع التحديثات
git add finance/
git add EXPENSES_QUICK.md
git add SAFE_QUICK.md
git add DEPLOY_EXPENSES_GUIDE.md

git commit -m "feat: Add expenses system (monthly & miscellaneous)"
git push origin main
```

---

### 2️⃣ على السيرفر البعيد (129.212.140.152)

```bash
# الاتصال
ssh user@129.212.140.152

# الانتقال للمشروع
cd /path/to/project

# سحب التحديثات
git pull origin main

# 🔴 مهم جداً: تشغيل Migration
python manage.py migrate

# إعادة تشغيل Django
sudo systemctl restart gunicorn
# أو: sudo systemctl restart uwsgi
```

---

## ⚠️ Migration مطلوب!

**هذه المرة Migration مطلوب!** ⚠️

```bash
python manage.py migrate
```

**السبب**: تم إضافة نموذج جديد (`Expense`) لقاعدة البيانات

---

## ✅ التحقق من النجاح

### 1. اختبر تسجيل مصروف

```http
POST http://129.212.140.152/finance/expenses/create/
{
  "type": "monthly",
  "category": "salary",
  "amount": 5000,
  "recipient": "test",
  "payment_method": "cash",
  "expense_date": "2025-10-10"
}
```

**المتوقع:** نجاح 201 Created

---

### 2. اختبر رأس المال

```http
GET http://129.212.140.152/finance/safe/
```

**المتوقع:** ترى حقل `expenses_total_amount`

```json
{
  "safe_total_amount": "...",
  "credit_total_amount": "...",
  "debt_total_amount": "...",
  "inventory_total_amount": "...",
  "expenses_total_amount": "5000.00",  // ⬅️ المصروف اللي سجلته
  "total_amount": "..."                 // ⬅️ محسوب بعد المصاريف
}
```

---

## 📊 أمثلة الاستخدام بعد النشر

### تسجيل مصاريف الشهر

```http
# مرتبات
POST /finance/expenses/create/
{"type": "monthly", "category": "salary", "amount": 15000, "recipient": "الموظفين", "payment_method": "cash", "expense_date": "2025-10-01"}

# إيجار
POST /finance/expenses/create/
{"type": "monthly", "category": "rent", "amount": 10000, "recipient": "المالك", "payment_method": "cash", "expense_date": "2025-10-01"}

# أرباح شركاء
POST /finance/expenses/create/
{"type": "monthly", "category": "profit_share", "amount": 20000, "recipient": "الشريك", "payment_method": "instapay", "expense_date": "2025-10-05"}
```

---

### عرض تقرير شهري

```http
GET /finance/expenses/?month=10&year=2025
```

**النتيجة:**
- قائمة بجميع مصاريف الشهر
- يمكن حساب الإجمالي من النتائج

---

### عرض رأس المال النهائي

```http
GET /finance/safe/
```

**النتيجة:**
```json
{
  "safe_total_amount": "125000.00",
  "credit_total_amount": "45000.00",
  "debt_total_amount": "20000.00",
  "inventory_total_amount": "85000.00",
  "expenses_total_amount": "45000.00",
  "total_amount": "190000.00"
}
```

---

## 🎯 الميزات

### ✅ ما يعمل الآن

1. **تسجيل المصاريف**
   - شهرية (مرتبات، إيجار، أرباح)
   - نثرية (قرطاسية، صيانة، إلخ)

2. **الفلترة والبحث**
   - حسب النوع (شهري/نثري)
   - حسب الفئة (مرتب، إيجار، إلخ)
   - حسب الشهر والسنة
   - بحث في الوصف والمستلم

3. **حساب رأس المال**
   - يشمل المصاريف تلقائياً
   - المعادلة: `كاش + ديون ليك + مخزون - ديون عليك - مصاريف`

4. **لوحة الإدارة**
   - إضافة/تعديل/حذف المصاريف
   - فلترة وبحث متقدم

---

## 📝 قائمة التحقق

### قبل النشر:
- [x] إنشاء النموذج (`Expense`)
- [x] إنشاء Migration
- [x] إنشاء Serializers
- [x] إنشاء Views
- [x] إنشاء URLs
- [x] إضافة Admin
- [x] تحديث SafeRetrieveAPIView
- [x] كتابة التوثيق

### بعد النشر:
- [ ] git pull
- [ ] python manage.py migrate ⚠️
- [ ] restart Django
- [ ] اختبار الـ APIs

---

## 🐛 استكشاف الأخطاء

### خطأ: Migration لم يُنفذ

```
django.db.utils.OperationalError: no such table: finance_expense
```

**الحل:**
```bash
python manage.py migrate
```

---

### خطأ: Import Error

```
ImportError: cannot import name 'Expense'
```

**الحل:**
```bash
# تأكد من رفع جميع الملفات
git status
git add finance/
git push
```

---

## 📚 التوثيق الكامل

- [EXPENSES_GUIDE.md](./finance/EXPENSES_GUIDE.md) - دليل شامل
- [EXPENSES_QUICK.md](./EXPENSES_QUICK.md) - ملخص سريع
- [SAFE_QUICK.md](./SAFE_QUICK.md) - رأس المال محدث

---

## 🎉 النتيجة النهائية

بعد النشر، ستتمكن من:

✅ تسجيل جميع المصاريف (شهرية ونثرية)  
✅ عرض تقارير شهرية مفصلة  
✅ حساب رأس المال الحقيقي (بعد خصم المصاريف)  
✅ تتبع كل فلس صُرف ولمن وفي أي تاريخ  

---

**آخر تحديث**: 2025-10-10  
**الإصدار**: 2.0.0  
**الحالة**: ✅ جاهز للنشر

**Migration مطلوب**: ⚠️ نعم - لا تنسى `python manage.py migrate`

