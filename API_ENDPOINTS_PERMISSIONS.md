# 🔐 دليل صلاحيات نقاط النهاية - PharmasSky API

دليل شامل لجميع نقاط النهاية في نظام PharmasSky مع تحديد المستخدمين المصرح لهم بالوصول لكل endpoint

## 👥 أنواع المستخدمين والأدوار

| الدور | الكود | الوصف |
|-------|------|-------|
| مدير عام | `ADMIN` | مدير النظام (صلاحيات كاملة) |
| صيدلية | `PHARMACY` | مستخدم صيدلية |
| توصيل | `DELIVERY` | مندوب توصيل |
| مخزن | `STORE` | مسؤول مخزن |
| مدير | `MANAGER` | مدير |
| مبيعات | `SALES` | مندوب مبيعات |
| إدخال بيانات | `DATA_ENTRY` | موظف إدخال بيانات |
| مدير منطقة | `AREA_MANAGER` | مدير منطقة |

### 🏷️ مجموعات الصلاحيات

- **Staff**: `MANAGER`, `AREA_MANAGER`, `SALES`, `DATA_ENTRY`, `DELIVERY`
- **Management**: `MANAGER`, `AREA_MANAGER`, `SALES`
- **Superuser**: صلاحيات كاملة لجميع الـ endpoints

---

## 🔑 Authentication Endpoints

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/accounts/login/` | POST | **الجميع** (بدون authentication) | تسجيل الدخول |
| `/accounts/whoami/` | POST | **جميع المستخدمين المسجلين** | بيانات المستخدم الحالي |

---

## 👤 Accounts Endpoints

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/accounts/users/` | GET | **Staff** | قائمة جميع المستخدمين |
| `/accounts/users/{id}/` | GET | **Staff** | تفاصيل مستخدم معين |
| `/accounts/simple-users/` | GET | **Management** | قائمة مبسطة للمستخدمين |
| `/accounts/register/pharmacy/` | POST | **الجميع** (بدون authentication) | تسجيل صيدلية جديدة |

---

## 🏪 Market Endpoints

### المنتجات (Products)

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/market/products/` | GET | **جميع المستخدمين المسجلين** | قائمة جميع المنتجات |
| `/market/products/create/` | POST | **Staff** | إضافة منتج جديد |
| `/market/products/{id}/` | GET | **جميع المستخدمين المسجلين** | تفاصيل منتج معين |
| `/market/products/{id}/change/` | PUT | **Staff** | تحديث منتج |
| `/market/products/object/{id}/product-alternatives/list` | GET | **جميع المستخدمين المسجلين** | قائمة البدائل للمنتج |
| `/market/products/object/{id}/product-instances/list` | GET | **جميع المستخدمين المسجلين** | قائمة نسخ المنتج في المخازن |

### الشركات والفئات

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/market/companies/list` | GET | **PHARMACY** | قائمة جميع الشركات |
| `/market/categories/list` | GET | **PHARMACY** | قائمة جميع فئات المنتجات |

### أكواد المنتجات

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/market/product-codes/` | GET | **SALES**, **DATA_ENTRY**, **PHARMACY**, **MANAGER** | قائمة أكواد المنتجات |

### قائمة الرغبات

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/market/user/product-wishlist/` | GET | **PHARMACY** | قائمة رغبات المستخدم |
| `/market/user/product-wishlist/create/` | POST | **PHARMACY** | إضافة منتج لقائمة الرغبات |

### فلاتر المنتجات

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/market/filters/products/company` | GET | **PHARMACY** | فلتر المنتجات حسب الشركة |
| `/market/filters/products/category` | GET | **PHARMACY** | فلتر المنتجات حسب الفئة |
| `/market/filters/products/letter` | GET | **PHARMACY** | فلتر المنتجات حسب الحرف الأول |
| `/market/filters/products/shape` | GET | **PHARMACY** | فلتر المنتجات حسب الشكل |

---

## 📦 Inventory Endpoints

### المخازن (Inventories)

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/inventory/inventories/` | GET | **جميع المستخدمين المسجلين** | قائمة جميع المخازن |
| `/inventory/inventories/create/` | POST | **جميع المستخدمين المسجلين** | إنشاء مخزن جديد |
| `/inventory/inventories/{id}/` | GET | **جميع المستخدمين المسجلين** | تفاصيل مخزن معين |
| `/inventory/inventories/{id}/change/` | PUT | **جميع المستخدمين المسجلين** | تحديث بيانات المخزن |

### عناصر المخزون (Inventory Items)

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/inventory/inventory-items/` | GET | **جميع المستخدمين المسجلين** | قائمة جميع عناصر المخزون |
| `/inventory/inventory-items/create/` | POST | **جميع المستخدمين المسجلين** | إضافة منتج للمخزن |
| `/inventory/inventory-items/{id}/` | GET | **جميع المستخدمين المسجلين** | تفاصيل عنصر مخزون معين |
| `/inventory/inventory-items/{id}/change/` | PUT | **جميع المستخدمين المسجلين** | تحديث عنصر المخزون |
| `/inventory/inventory-items/{id}/change-inventory/` | PUT | **جميع المستخدمين المسجلين** | نقل منتج من مخزن لآخر |
| `/inventory/inventory-items/{id}/destroy/` | DELETE | **جميع المستخدمين المسجلين** | حذف عنصر من المخزون |

---

## 📄 Invoices Endpoints

### فواتير الشراء (Purchase Invoices)

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/invoices/purchase-invoices/` | GET | **جميع المستخدمين المسجلين** | قائمة فواتير الشراء |
| `/invoices/purchase-invoices/create/` | POST | **جميع المستخدمين المسجلين** | إنشاء فاتورة شراء جديدة |
| `/invoices/purchase-invoices/{id}/` | GET | **جميع المستخدمين المسجلين** | تفاصيل فاتورة شراء |
| `/invoices/purchase-invoices/{id}/change-state/` | PUT | **جميع المستخدمين المسجلين** | تغيير حالة فاتورة الشراء |

### عناصر فاتورة الشراء

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/invoices/purchase-invoice-items/` | GET | **جميع المستخدمين المسجلين** | قائمة عناصر فواتير الشراء |
| `/invoices/purchase-invoice-items/create/` | POST | **جميع المستخدمين المسجلين** | إضافة عنصر لفاتورة شراء |
| `/invoices/purchase-invoice-items/{id}/change-state/` | PUT | **جميع المستخدمين المسجلين** | تغيير حالة عنصر فاتورة |
| `/invoices/purchase-invoice-items/change-state/` | PUT | **جميع المستخدمين المسجلين** | تغيير حالة عدة عناصر مرة واحدة |
| `/invoices/purchase-invoice-items/{id}/destroy/` | DELETE | **جميع المستخدمين المسجلين** | حذف عنصر من الفاتورة |

### فواتير مرتجع الشراء

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/invoices/purchase-return-invoices/` | GET | **جميع المستخدمين المسجلين** | قائمة فواتير مرتجع الشراء |
| `/invoices/purchase-return-invoices/create/` | POST | **جميع المستخدمين المسجلين** | إنشاء فاتورة مرتجع شراء |
| `/invoices/purchase-return-invoices/{id}/` | GET | **جميع المستخدمين المسجلين** | تفاصيل فاتورة مرتجع |
| `/invoices/purchase-return-invoices/{id}/change-state/` | PUT | **جميع المستخدمين المسجلين** | تغيير حالة فاتورة المرتجع |

### فواتير البيع (Sale Invoices)

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/invoices/sale-invoices/` | GET | **جميع المستخدمين المسجلين** | قائمة فواتير البيع |
| `/invoices/sale-invoices/create/` | POST | **جميع المستخدمين المسجلين** | إنشاء فاتورة بيع جديدة |
| `/invoices/sale-invoices/{id}/` | GET | **جميع المستخدمين المسجلين** | تفاصيل فاتورة بيع |
| `/invoices/sale-invoices/{id}/download/` | GET | **جميع المستخدمين المسجلين** | تحميل فاتورة البيع كـ PDF |
| `/invoices/sale-invoices/{id}/change-state/` | PUT | **جميع المستخدمين المسجلين** | تغيير حالة فاتورة البيع |

### عناصر فاتورة البيع

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/invoices/sale-invoice-items/` | GET | **جميع المستخدمين المسجلين** | قائمة عناصر فواتير البيع |
| `/invoices/sale-invoice-items/create/` | POST | **جميع المستخدمين المسجلين** | إضافة عنصر لفاتورة بيع |
| `/invoices/sale-invoice-items/{id}/change/` | PUT | **جميع المستخدمين المسجلين** | تحديث عنصر فاتورة |
| `/invoices/sale-invoice-items/{id}/change-state/` | PUT | **جميع المستخدمين المسجلين** | تغيير حالة عنصر |
| `/invoices/sale-invoice-items/change-state/` | PUT | **جميع المستخدمين المسجلين** | تغيير حالة عدة عناصر |
| `/invoices/sale-invoice-items/{id}/destroy/` | DELETE | **جميع المستخدمين المسجلين** | حذف عنصر من الفاتورة |

### فواتير مرتجع البيع

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/invoices/sale-return-invoices/` | GET | **جميع المستخدمين المسجلين** | قائمة فواتير مرتجع البيع |
| `/invoices/sale-return-invoices/create/` | POST | **جميع المستخدمين المسجلين** | إنشاء فاتورة مرتجع بيع |
| `/invoices/sale-return-invoices/{id}/` | GET | **جميع المستخدمين المسجلين** | تفاصيل فاتورة مرتجع البيع |
| `/invoices/sale-return-invoices/{id}/change-state/` | PUT | **جميع المستخدمين المسجلين** | تغيير حالة فاتورة المرتجع |

---

## 💰 Finance Endpoints

### الحسابات المالية

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/finance/accounts/{id}/change/` | PUT | **MANAGER**, **AREA_MANAGER** | تحديث بيانات حساب مالي |
| `/finance/account-transactions/` | GET | **Staff** | قائمة حركات الحسابات المالية |

### مدفوعات الشراء

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/finance/purchase-payments/` | GET | **جميع المستخدمين المسجلين** | قائمة مدفوعات الشراء |
| `/finance/purchase-payments/create/` | POST | **Management** | إنشاء دفع شراء جديد |
| `/finance/purchase-payments/{id}/change/` | PUT | **Management** | تحديث دفع شراء |
| `/finance/purchase-payments/{id}/destroy/` | DELETE | **Management** | حذف دفع شراء |

### مدفوعات البيع

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/finance/sale-payments/` | GET | **جميع المستخدمين المسجلين** | قائمة مدفوعات البيع |
| `/finance/sale-payments/create/` | POST | **جميع المستخدمين المسجلين** | إنشاء دفع بيع جديد |
| `/finance/sale-payments/{id}/change/` | PUT | **جميع المستخدمين المسجلين** | تحديث دفع بيع |
| `/finance/sale-payments/{id}/destroy/` | DELETE | **جميع المستخدمين المسجلين** | حذف دفع بيع |

### معاملات الخزينة

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/finance/safe-transactions/` | GET | **جميع المستخدمين المسجلين** | قائمة معاملات الخزينة |
| `/finance/safe-transactions/create/` | POST | **جميع المستخدمين المسجلين** | إنشاء معاملة خزينة جديدة |
| `/finance/safe/` | GET | **جميع المستخدمين المسجلين** | بيانات الخزينة الحالية |

---

## 🎯 Offers Endpoints

### العروض

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/offers/offers/` | GET | **جميع المستخدمين المسجلين** | قائمة جميع العروض |
| `/offers/offers/create/` | POST | **SALES**, **DATA_ENTRY**, **MANAGER** | إنشاء عرض جديد |
| `/offers/offers/{id}/change/` | PUT | **SALES**, **DATA_ENTRY**, **MANAGER** | تحديث عرض |
| `/offers/offers/{id}/destroy/` | DELETE | **SALES**, **DATA_ENTRY**, **MANAGER** | حذف عرض |

### أفضل العروض

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/offers/max-offers/` | GET | **SALES**, **DATA_ENTRY**, **MANAGER** | قائمة أفضل العروض الحالية |
| `/offers/max-offers/excel/` | GET | **SALES**, **DATA_ENTRY**, **MANAGER** | تحميل أفضل العروض كملف Excel |

### رفع العروض

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/offers/offers/upload/` | POST | **SALES**, **DATA_ENTRY**, **MANAGER** | رفع العروض من ملف Excel |

### عروض المستخدم

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/offers/user/offers/` | GET | **PHARMACY** | قائمة عروض المستخدم الحالي |
| `/offers/user/offers/create/` | POST | **PHARMACY** | إنشاء عرض من المستخدم |

---

## 👥 Profiles Endpoints

### الملفات الشخصية

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/profiles/user-profiles/create/` | POST | **Management** | إنشاء ملف شخصي للمستخدم |
| `/profiles/user-profiles/{id}/change/` | PUT | **Management** | تحديث الملف الشخصي |
| `/profiles/user-profile/` | GET | **جميع المستخدمين المسجلين** | الحصول على الملف الشخصي للمستخدم الحالي |

### البيانات المرجعية

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/profiles/areas/` | GET | **جميع المستخدمين المسجلين** | قائمة المناطق |
| `/profiles/countries/` | GET | **جميع المستخدمين المسجلين** | قائمة الدول |
| `/profiles/cities/` | GET | **جميع المستخدمين المسجلين** | قائمة المدن |
| `/profiles/payment-periods/` | GET | **PHARMACY**, **STORE**, **MANAGER** | قائمة فترات السداد |

### الشكاوى

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/profiles/complaints/` | GET | **جميع المستخدمين المسجلين** | قائمة الشكاوى |
| `/profiles/complaints/create/` | POST | **PHARMACY**, **STORE** | إنشاء شكوى جديدة |

---

## 🛒 Shop Endpoints

### عربة التسوق

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/shop/carts/{id}/` | GET | **جميع المستخدمين المسجلين** | تفاصيل عربة تسوق معينة |
| `/shop/user/cart/` | GET | **جميع المستخدمين المسجلين** | عربة التسوق للمستخدم الحالي |
| `/shop/user/cart/checkout/` | POST | **جميع المستخدمين المسجلين** | إتمام عملية الشراء من العربة |

### عناصر عربة التسوق

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/shop/user/cart-items/create/` | POST | **جميع المستخدمين المسجلين** | إضافة منتج لعربة التسوق |
| `/shop/user/cart-items/{id}/change/` | PUT | **جميع المستخدمين المسجلين** | تحديث كمية منتج في العربة |
| `/shop/user/cart-items/{id}/destroy/` | DELETE | **جميع المستخدمين المسجلين** | إزالة منتج من العربة |

---

## 📢 Ads Endpoints

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/ads/` | GET | **جميع المستخدمين المسجلين** | قائمة جميع الإعلانات النشطة |

---

## 🔔 Push Notifications

### تسجيل الجهاز

| Endpoint | Method | المصرح لهم | الوصف |
|----------|--------|------------|-------|
| `/push-notifications/devices/fcm/register/` | POST | **جميع المستخدمين المسجلين** | تسجيل جهاز لاستقبال الإشعارات |
| `/push-notifications/devices/fcm/unregister/` | DELETE | **جميع المستخدمين المسجلين** | إلغاء تسجيل الجهاز |

---

## 📊 ملخص الصلاحيات حسب الدور

### 🔹 ADMIN (مدير عام)
- **صلاحيات كاملة** لجميع الـ endpoints

### 🔹 PHARMACY (صيدلية)
- جميع endpoints المتعلقة بالمنتجات والفلاتر
- قائمة الرغبات والعروض الشخصية
- عربة التسوق والشراء
- إنشاء الشكاوى
- جميع العمليات الأساسية (عرض، إضافة، تعديل)

### 🔹 MANAGER (مدير)
- جميع عمليات العروض والمنتجات
- إدارة الحسابات المالية
- إنشاء وتحديث الملفات الشخصية
- مدفوعات الشراء
- جميع العمليات الأساسية

### 🔹 SALES (مبيعات)
- إدارة العروض والمنتجات
- عرض قوائم المستخدمين
- مدفوعات الشراء
- جميع العمليات الأساسية

### 🔹 DATA_ENTRY (إدخال بيانات)
- إدارة العروض والمنتجات
- أكواد المنتجات
- جميع العمليات الأساسية

### 🔹 AREA_MANAGER (مدير منطقة)
- عرض قوائم المستخدمين
- إدارة الحسابات المالية
- إنشاء وتحديث الملفات الشخصية
- مدفوعات الشراء
- جميع العمليات الأساسية

### 🔹 STORE (مخزن)
- فترات السداد
- إنشاء الشكاوى
- جميع العمليات الأساسية

### 🔹 DELIVERY (توصيل)
- جميع العمليات الأساسية فقط

---

## 🔒 ملاحظات أمنية مهمة

1. **Token Authentication مطلوب** لجميع الـ endpoints عدا تسجيل الدخول وتسجيل الصيدليات الجديدة
2. **Superuser** له صلاحيات كاملة لجميع الـ endpoints
3. **ADMIN** له صلاحيات كاملة مماثلة للـ Superuser
4. **Staff** يشمل: `MANAGER`, `AREA_MANAGER`, `SALES`, `DATA_ENTRY`, `DELIVERY`
5. **Management** يشمل: `MANAGER`, `AREA_MANAGER`, `SALES`
6. بعض الـ endpoints تستخدم **Object-level permissions** للتحكم في الوصول للبيانات الشخصية

## 🚨 مشاكل محلولة حديثاً

### المشكلة: دور ADMIN لا يمكنه الوصول للمنتجات
- **السبب**: عدم تضمين دور ADMIN في صلاحيات ProductListAPIView
- **الحل**: تحديث نظام الصلاحيات ليتعامل مع ADMIN تلقائياً
- **التاريخ**: 2025-09-27

### المشكلة: is_superuser = False للمدراء
- **السبب**: إعدادات قاعدة البيانات
- **الحل المؤقت**: إضافة فحص خاص لدور ADMIN في نظام الصلاحيات
- **الحل الدائم**: تحديث قاعدة البيانات لجعل ADMIN = is_superuser

### تحسينات نظام الصلاحيات
- ✅ إضافة `SmartRolePermission` للتعامل الذكي مع الأدوار
- ✅ إضافة `AllAuthenticatedUsers` للـ endpoints العامة  
- ✅ إضافة `StaffOnly` و `ManagementOnly` للتصنيف الواضح
- ✅ توحيد نظام الصلاحيات في `core/permissions.py`

---

**تم إنشاء هذا الملف في:** `2024-12-20`  
**إصدار API:** `v1.0`  
**المطور:** Mohamed Sakr
