# صلاحيات Finance - Finance Permissions Guide

## ❌ المشكلة: `/finance/user-financial-summary/`

```json
{
  "detail": "You do not have permission to perform this action."
}
```

### السبب:
هذا الـ endpoint **مخصص للموظفين فقط** (Staff)، مش للصيدليات!

```python
class UserFinancialSummaryAPIView(GenericAPIView):
    permission_classes = [StaffRoleAuthentication]  # ← مش للصيدليات!
```

---

## 📋 صلاحيات Finance كاملة

### 1️⃣ للصيدليات (PHARMACY) 🏪

#### ✅ يقدر يعمل:
```
GET  /finance/purchase-payments/      ← شوف مدفوعاته
GET  /finance/sale-payments/          ← شوف المقبوضات
```

#### ❌ مش يقدر يعمل:
```
GET  /finance/user-financial-summary/ ← ممنوع! (للموظفين فقط)
POST /finance/purchase-payments/create/ ← ممنوع! (للمبيعات فقط)
POST /finance/sale-payments/create/ ← ممنوع! (للمبيعات فقط)
GET  /finance/account-transactions/ ← ممنوع! (للموظفين فقط)
GET  /finance/expenses/ ← ممنوع! (للمديرين فقط)
GET  /finance/collection-schedule/ ← ممنوع! (للموظفين فقط)
GET  /finance/accounts-payable/ ← ممنوع! (للموظفين فقط)
```

---

### 2️⃣ لمندوب المبيعات (SALES) 💼

#### ✅ يقدر يعمل:
```
GET  /finance/account-transactions/          ← شوف معاملات الحسابات
GET  /finance/purchase-payments/             ← شوف المدفوعات
POST /finance/purchase-payments/create/      ← إنشاء مدفوعات شراء
PUT  /finance/purchase-payments/<id>/change/ ← تعديل مدفوعات
DELETE /finance/purchase-payments/<id>/      ← حذف مدفوعات
GET  /finance/sale-payments/                 ← شوف مقبوضات البيع
POST /finance/sale-payments/create/          ← إنشاء مقبوضات بيع
PUT  /finance/sale-payments/<id>/change/     ← تعديل مقبوضات
DELETE /finance/sale-payments/<id>/          ← حذف مقبوضات
GET  /finance/user-financial-summary/        ← ملخص مالي للمستخدمين
GET  /finance/collection-schedule/           ← جدول التحصيل
GET  /finance/accounts-payable/              ← الحسابات الدائنة
GET  /finance/account-statement-pdf/         ← كشف حساب PDF
```

---

### 3️⃣ للمدير (MANAGER) 👔

#### ✅ يقدر يعمل كل حاجة:
```
✅ كل صلاحيات SALES
✅ بالإضافة إلى:
   - PUT  /finance/accounts/<id>/change/     ← تعديل الحسابات
   - GET  /finance/safe-transactions/        ← معاملات الخزنة
   - POST /finance/safe-transactions/create/ ← إضافة معاملة خزنة
   - GET  /finance/safe/                     ← رصيد الخزنة
   - GET  /finance/expenses/                 ← المصروفات
   - POST /finance/expenses/create/          ← إضافة مصروف
   - PUT  /finance/expenses/<id>/change/     ← تعديل مصروف
   - DELETE /finance/expenses/<id>/          ← حذف مصروف
```

---

### 4️⃣ لمدير المنطقة (AREA_MANAGER) 🗺️

#### ✅ يقدر يعمل:
- كل صلاحيات SALES
- تعديل الحسابات في منطقته

---

## 📊 جدول الصلاحيات الكامل

| Endpoint | PHARMACY | SALES | MANAGER | ADMIN |
|----------|----------|-------|---------|-------|
| `/finance/account-transactions/` | ❌ | ✅ | ✅ | ✅ |
| `/finance/accounts/<id>/change/` | ❌ | ❌ | ✅ | ✅ |
| `/finance/purchase-payments/` | ✅ (بتاعته) | ✅ | ✅ | ✅ |
| `/finance/purchase-payments/create/` | ❌ | ✅ | ✅ | ✅ |
| `/finance/purchase-payments/<id>/change/` | ❌ | ✅ | ✅ | ✅ |
| `/finance/purchase-payments/<id>/` (DELETE) | ❌ | ✅ | ✅ | ✅ |
| `/finance/sale-payments/` | ✅ (بتاعته) | ✅ | ✅ | ✅ |
| `/finance/sale-payments/create/` | ❌ | ✅ | ✅ | ✅ |
| `/finance/sale-payments/<id>/change/` | ❌ | ✅ | ✅ | ✅ |
| `/finance/sale-payments/<id>/` (DELETE) | ❌ | ✅ | ✅ | ✅ |
| `/finance/safe-transactions/` | ❌ | ❌ | ✅ | ✅ |
| `/finance/safe/` | ❌ | ❌ | ✅ | ✅ |
| `/finance/expenses/` | ❌ | ❌ | ✅ | ✅ |
| `/finance/user-financial-summary/` | ❌ | ✅ | ✅ | ✅ |
| `/finance/collection-schedule/` | ❌ | ✅ | ✅ | ✅ |
| `/finance/accounts-payable/` | ❌ | ✅ | ✅ | ✅ |
| `/finance/account-statement-pdf/` | ❌ | ✅ | ✅ | ✅ |

---

## 🎯 تفصيل الـ Endpoints

### 1. Account Transactions (معاملات الحسابات)

```
GET /finance/account-transactions/
```

**الصلاحية:** Staff فقط (SALES, MANAGER, AREA_MANAGER, DATA_ENTRY, DELIVERY)

**Parameters:**
- `account__user`: فلترة حسب المستخدم
- `transaction_type`: نوع المعاملة (initial_balance, invoice, return, payment, refund)
- `at_after`, `at_before`: فلترة حسب التاريخ

**Response:**
```json
[
  {
    "id": 1,
    "account": {...},
    "transaction_type": "invoice",
    "amount": 1000.00,
    "balance_after": 5000.00,
    "description": "فاتورة رقم #123",
    "at": "2025-10-14T10:30:00Z"
  }
]
```

---

### 2. Purchase Payments (مدفوعات الشراء)

```
GET /finance/purchase-payments/
```

**الصلاحية:** IsAuthenticated (الكل)

**الفلترة:**
- **PHARMACY/STORE:** يشوف مدفوعاته بس
- **SALES:** يشوف مدفوعات المستخدمين المعينين له
- **MANAGER/AREA_MANAGER:** يشوف مدفوعات المستخدمين في فريقه

**Response:**
```json
[
  {
    "id": 1,
    "user": {
      "id": 123,
      "name": "صيدلية النور",
      "username": "+201234567890"
    },
    "amount": 500.00,
    "payment_method": "cash",
    "remarks": "دفعة نقدية",
    "at": "2025-10-14T10:30:00Z"
  }
]
```

---

### 3. Sale Payments (مقبوضات البيع)

```
GET /finance/sale-payments/
```

**الصلاحية:** IsAuthenticated (الكل)

نفس الفلترة زي Purchase Payments

---

### 4. User Financial Summary (الملخص المالي) ⚠️

```
GET /finance/user-financial-summary/
```

**الصلاحية:** ❌ Staff فقط (SALES, MANAGER, AREA_MANAGER, DATA_ENTRY, DELIVERY)

**⚠️ الصيدليات مش مسموح لهم!**

**Parameters:**
- `user_id`: معرف المستخدم المحدد
- `search`: البحث باسم أو رقم هاتف
- `role`: فلترة حسب الدور (PHARMACY, STORE)
- `min_volume`: الحد الأدنى لحجم التعامل
- `date_from`, `date_to`: نطاق التاريخ

**Response:**
```json
[
  {
    "user_id": 123,
    "username": "+201234567890",
    "name": "صيدلية النور",
    "role": "PHARMACY",
    "total_purchases": 50000.00,
    "total_sales": 45000.00,
    "total_purchase_returns": 2000.00,
    "total_sale_returns": 1000.00,
    "total_cash_paid": 30000.00,
    "total_cash_received": 28000.00,
    "transaction_volume": 95000.00,
    "current_balance": 5000.00
  }
]
```

---

### 5. Collection Schedule (جدول التحصيل)

```
GET /finance/collection-schedule/
```

**الصلاحية:** Staff فقط

**Parameters:**
- `days_ahead`: عدد الأيام القادمة (افتراضي: 7)
- `user_id`: فلترة حسب مستخدم معين
- `sort_by`: الترتيب (due_date, amount, user_name)

**Response:**
```json
[
  {
    "user": {
      "id": 123,
      "name": "صيدلية النور",
      "username": "+201234567890"
    },
    "invoice_id": 456,
    "invoice_number": "INV-2025-001",
    "total_amount": 5000.00,
    "paid_amount": 2000.00,
    "remaining_amount": 3000.00,
    "payment_due_date": "2025-10-20",
    "days_remaining": 6,
    "is_overdue": false
  }
]
```

---

### 6. Accounts Payable (الحسابات الدائنة)

```
GET /finance/accounts-payable/
```

**الصلاحية:** Staff فقط

**Parameters:**
- `days_ahead`: عدد الأيام القادمة (افتراضي: 30)
- `user_id`: فلترة حسب مستخدم معين

**Response:**
```json
[
  {
    "supplier_id": 789,
    "supplier_name": "شركة الأدوية",
    "purchase_order_id": 100,
    "total_amount": 10000.00,
    "paid_amount": 5000.00,
    "remaining_amount": 5000.00,
    "payment_due_date": "2025-10-25",
    "days_remaining": 11,
    "is_overdue": false
  }
]
```

---

### 7. Account Statement PDF (كشف الحساب)

```
GET /finance/account-statement-pdf/
```

**الصلاحية:** Staff فقط

**Parameters:**
- `user_id`: (مطلوب) معرف المستخدم
- `date_from`: من تاريخ
- `date_to`: إلى تاريخ
- `language`: اللغة (ar/en)

**Response:** PDF File

---

### 8. Safe Transactions (معاملات الخزنة)

```
GET /finance/safe-transactions/
POST /finance/safe-transactions/create/
```

**الصلاحية:** MANAGER فقط

---

### 9. Expenses (المصروفات)

```
GET /finance/expenses/
POST /finance/expenses/create/
PUT /finance/expenses/<id>/change/
DELETE /finance/expenses/<id>/
```

**الصلاحية:** MANAGER فقط

---

## 💡 الحل للصيدليات

### ✅ بدل `/finance/user-financial-summary/`

الصيدليات يمكنها استخدام:

#### 1. شوف البروفايل (فيه معلومات الحساب)
```bash
GET /profiles/user-profile/
```

**Response:**
```json
{
  "id": 1,
  "user": {...},
  "account": {
    "id": 456,
    "balance": 5000.00,          ← الرصيد
    "credit_limit": 10000.00,    ← حد الائتمان
    "remaining_credit": 5000.00  ← الائتمان المتبقي
  },
  ...
}
```

#### 2. شوف الحساب من `whoami`
```bash
POST /accounts/whoami/
```

**Response:**
```json
{
  "id": 123,
  "username": "+201234567890",
  "name": "صيدلية النور",
  "account": {
    "id": 456,
    "balance": 5000.00,
    "credit_limit": 10000.00
  }
}
```

#### 3. شوف المدفوعات والمقبوضات
```bash
GET /finance/purchase-payments/     ← المدفوعات
GET /finance/sale-payments/         ← المقبوضات
```

---

## 🔥 أمثلة عملية

### مثال 1: صيدلية تشوف مدفوعاتها

```bash
# 1. تسجيل دخول
curl -X POST http://129.212.140.152/accounts/pharmacy-login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "+201234567890", "password": "pass123"}'

# Response: {"token": "abc123..."}

# 2. جيب المدفوعات
curl -X GET http://129.212.140.152/finance/purchase-payments/ \
  -H "Authorization: Token abc123..."

# ✅ يشتغل - يجيب المدفوعات بتاعتها بس
```

### مثال 2: صيدلية تحاول تشوف الملخص المالي

```bash
curl -X GET http://129.212.140.152/finance/user-financial-summary/ \
  -H "Authorization: Token pharmacy_token..."

# ❌ Response: 403 Forbidden
# {
#   "detail": "You do not have permission to perform this action."
# }
```

### مثال 3: مندوب مبيعات يشوف الملخص المالي

```bash
# 1. تسجيل دخول كمندوب مبيعات
curl -X POST http://129.212.140.152/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "+201111111111", "password": "pass123"}'

# Response: {"token": "xyz789...", "role": "SALES"}

# 2. جيب الملخص المالي
curl -X GET "http://129.212.140.152/finance/user-financial-summary/?role=PHARMACY" \
  -H "Authorization: Token xyz789..."

# ✅ يشتغل - يجيب ملخص مالي لجميع الصيدليات المعينة له
```

---

## 🚨 رسائل الخطأ الشائعة

### 1. "You do not have permission"
```json
{"detail": "You do not have permission to perform this action."}
```

**السبب:** الدور بتاعك مش مسموح له

**الحل للصيدليات:**
- استخدم `/profiles/user-profile/` لرؤية الرصيد
- استخدم `/finance/purchase-payments/` لرؤية المدفوعات
- استخدم `/finance/sale-payments/` لرؤية المقبوضات

---

## 📊 ملخص سريع

| ما تريد معرفته | الصيدلية يستخدم | المبيعات يستخدم |
|----------------|-----------------|------------------|
| الرصيد | `/profiles/user-profile/` | `/profiles/user-profile/` |
| المدفوعات | `/finance/purchase-payments/` | `/finance/purchase-payments/` |
| المقبوضات | `/finance/sale-payments/` | `/finance/sale-payments/` |
| ملخص مالي شامل | ❌ غير متاح | `/finance/user-financial-summary/` |
| جدول التحصيل | ❌ غير متاح | `/finance/collection-schedule/` |
| كشف الحساب PDF | ❌ غير متاح | `/finance/account-statement-pdf/` |

---

## 💡 نصائح

### للصيدليات 🏪
1. ✅ استخدم `/profiles/user-profile/` لمعرفة رصيدك
2. ✅ استخدم `/finance/purchase-payments/` لرؤية مدفوعاتك
3. ❌ لا تحاول الوصول لـ `/finance/user-financial-summary/` (مش هيشتغل)

### لمندوبين المبيعات 💼
1. ✅ يمكنك رؤية الملخص المالي لجميع عملائك
2. ✅ يمكنك إنشاء مدفوعات ومقبوضات
3. ✅ يمكنك طباعة كشف حساب PDF

### للمديرين 👔
1. ✅ لديك صلاحية كاملة على Finance
2. ✅ يمكنك إدارة الخزنة والمصروفات
3. ✅ يمكنك رؤية جميع التقارير المالية

---

**ملخص:** 
- `/finance/user-financial-summary/` **للموظفين فقط** (Staff)
- الصيدليات تستخدم `/profiles/user-profile/` لرؤية الرصيد
- الصيدليات تستخدم `/finance/purchase-payments/` و `/finance/sale-payments/` لرؤية المدفوعات

