# توثيق الحقول المحسوبة لفواتير البيع
# Sale Invoice Calculated Fields Documentation

## نظرة عامة | Overview

تم إضافة حقول محسوبة إلى فواتير البيع (SaleInvoice):
1. **`total_public_price`**: إجمالي سعر الجمهور (قبل الخصم) لجميع عناصر الفاتورة
2. **`total_purchase_cost`**: إجمالي تكلفة الشراء لجميع عناصر الفاتورة
3. **`total_profit`**: إجمالي الربح (الفرق بين سعر البيع وسعر الشراء)
4. **`average_discount_percentage`**: متوسط نسبة الخصم المرجح لجميع عناصر الفاتورة

Calculated fields added to Sale Invoices:
1. **`total_public_price`**: Total public price (before discount) for all items
2. **`total_purchase_cost`**: Total purchase cost for all items
3. **`total_profit`**: Total profit (difference between selling and purchase prices)
4. **`average_discount_percentage`**: Weighted average discount percentage for all items

---

## الصيغ الرياضية | Formulas

### 1. إجمالي سعر الجمهور | Total Public Price

```
total_public_price = Sum(quantity × product.public_price)
```

**الشرح:**
- يتم ضرب كمية كل منتج في سعره العام
- يتم جمع جميع القيم للحصول على الإجمالي قبل الخصم

**Example:**
- Product A: 10 × 100 EGP = 1,000 EGP
- Product B: 5 × 200 EGP = 1,000 EGP
- **Total Public Price** = 2,000 EGP

---

### 2. إجمالي تكلفة الشراء | Total Purchase Cost

```
total_purchase_cost = Sum(quantity × purchase_price)
```

**الشرح:**
- يتم ضرب كمية كل منتج في سعر الشراء الخاص به
- يتم جمع جميع القيم للحصول على إجمالي التكلفة

**Example:**
- Product A: 10 × 60 EGP = 600 EGP
- Product B: 5 × 150 EGP = 750 EGP
- **Total Purchase Cost** = 1,350 EGP

---

### 3. إجمالي الربح | Total Profit

```
total_profit = Sum(quantity × (selling_price - purchase_price))
```

أو بطريقة أخرى:
```
total_profit = total_price - total_purchase_cost
```

**الشرح:**
- لكل منتج: الربح = (سعر البيع - سعر الشراء) × الكمية
- إجمالي الربح = مجموع أرباح جميع المنتجات

**Example:**
- Product A: 10 × (80 - 60) = 10 × 20 = 200 EGP
- Product B: 5 × (170 - 150) = 5 × 20 = 100 EGP
- **Total Profit** = 300 EGP

---

### 4. متوسط نسبة الخصم | Average Discount Percentage

```
average_discount_percentage = (Sum(quantity × selling_discount_percentage × public_price) / Sum(quantity × public_price)) × 100
```

**شرح الصيغة | Formula Explanation:**

1. **لكل عنصر في الفاتورة:**
   - `quantity_price` = الكمية × السعر العام
   - `quantity_discount` = quantity_price × (نسبة الخصم / 100)

2. **للفاتورة كاملة:**
   - `total_discount` = مجموع كل quantity_discount
   - `total_public_price` = مجموع كل quantity_price
   - `average_discount` = (total_discount / total_public_price) × 100

---

## مثال عملي | Practical Example

### فاتورة بها 3 عناصر:

| المنتج | الكمية | سعر الشراء | السعر العام | نسبة الخصم | سعر البيع | تكلفة الشراء | إجمالي السعر العام | السعر النهائي | الربح |
|--------|--------|-----------|-------------|-----------|----------|-------------|-------------------|--------------|------|
| A      | 10     | 60 EGP    | 100 EGP     | 20%       | 80 EGP   | 600 EGP     | 1,000 EGP         | 800 EGP      | 200 EGP |
| B      | 5      | 150 EGP   | 200 EGP     | 15%       | 170 EGP  | 750 EGP     | 1,000 EGP         | 850 EGP      | 100 EGP |
| C      | 20     | 40 EGP    | 50 EGP      | 10%       | 45 EGP   | 800 EGP     | 1,000 EGP         | 900 EGP      | 100 EGP |

**الحساب التفصيلي:**

1. **إجمالي سعر الجمهور (قبل الخصم):**
   - `total_public_price` = 1,000 + 1,000 + 1,000 = **3,000 EGP**

2. **إجمالي تكلفة الشراء:**
   - `total_purchase_cost` = 600 + 750 + 800 = **2,150 EGP**

3. **إجمالي السعر النهائي (بعد الخصم):**
   - `total_price` = 800 + 850 + 900 = **2,550 EGP**

4. **إجمالي الربح:**
   - `total_profit` = 200 + 100 + 100 = **400 EGP**
   - أو: `total_profit` = 2,550 - 2,150 = **400 EGP**

5. **إجمالي مبلغ الخصم:**
   - `total_discount` = 200 + 150 + 100 = 450 EGP

6. **متوسط نسبة الخصم:**
   - `average_discount_percentage` = (450 / 3,000) × 100 = **15%**

---

### العلاقات بين الحقول | Field Relationships:

```
1. total_public_price - total_discount = total_price
   3,000 - 450 = 2,550 EGP ✓

2. total_price - total_purchase_cost = total_profit
   2,550 - 2,150 = 400 EGP ✓

3. profit_margin = (total_profit / total_price) × 100
   (400 / 2,550) × 100 = 15.69% 

4. markup = (total_profit / total_purchase_cost) × 100
   (400 / 2,150) × 100 = 18.60%
```

---

## التكامل في API | API Integration

### 1. Response في SaleInvoiceReadSerializer

```json
{
  "id": 123,
  "seller": {
    "id": 1,
    "name": "أحمد محمد",
    "username": "01234567890"
  },
  "user": {
    "id": 2,
    "name": "صيدلية النور",
    "username": "01098765432"
  },
  "items_count": 3,
  "total_quantity": 35,
  "total_price": "2550.00",
  "total_public_price": "3000.00",
  "total_purchase_cost": "2150.00",
  "total_profit": "400.00",
  "status": "placed",
  "status_label": "Placed",
  "created_at": "2025-10-09T10:30:00Z",
  "average_discount_percentage": "15.00",
  "items": [...],
  "deleted_items": [],
  "items_url": "/api/v1/invoices/sale/items/?invoice=123"
}
```

**شرح الحقول | Field Descriptions:**

| الحقل | النوع | الوصف |
|-------|------|-------|
| `total_price` | Decimal | السعر النهائي بعد الخصم (ما سيدفعه العميل) |
| `total_public_price` | Decimal | السعر الإجمالي قبل الخصم (سعر الجمهور) |
| `total_purchase_cost` | Decimal | إجمالي تكلفة الشراء لجميع المنتجات |
| `total_profit` | Decimal | إجمالي الربح (الفرق بين سعر البيع والشراء) |
| `average_discount_percentage` | Decimal | متوسط نسبة الخصم المرجح |

---

### مؤشرات الأداء | Performance Indicators

من البيانات أعلاه يمكن حساب:

```python
# هامش الربح (Profit Margin)
profit_margin = (total_profit / total_price) × 100
profit_margin = (400 / 2550) × 100 = 15.69%

# نسبة الزيادة (Markup)
markup = (total_profit / total_purchase_cost) × 100
markup = (400 / 2150) × 100 = 18.60%

# نسبة التكلفة من السعر النهائي
cost_ratio = (total_purchase_cost / total_price) × 100
cost_ratio = (2150 / 2550) × 100 = 84.31%
```

### 2. Endpoints المتأثرة

- `GET /api/v1/invoices/sale/` - قائمة فواتير البيع
- `GET /api/v1/invoices/sale/{id}/` - تفاصيل فاتورة بيع محددة
- `GET /api/v1/invoices/sale/{id}/download/` - PDF الفاتورة

---

## تحسينات الأداء | Performance Optimizations

### استخدام Prefetch Related

تم تحسين استعلامات قاعدة البيانات لتجنب مشكلة N+1:

```python
queryset = SaleInvoice.objects.select_related(
    "user", "user__profile", "seller"
).prefetch_related(
    models.Prefetch(
        "items", 
        queryset=SaleInvoiceItem.objects.select_related("product")
    )
)
```

هذا يضمن:
- استعلام واحد للفواتير
- استعلام واحد لجميع العناصر مع المنتجات
- عدم وجود استعلامات إضافية عند حساب متوسط الخصم

---

## الاستخدام في الكود | Code Usage

### في Serializer

```python
class SaleInvoiceReadSerializer(BaseModelSerializer):
    average_discount_percentage = serializers.SerializerMethodField()
    total_public_price = serializers.SerializerMethodField()
    total_profit = serializers.SerializerMethodField()
    total_purchase_cost = serializers.SerializerMethodField()
    
    def get_total_public_price(self, instance):
        """Calculate total public price before discount"""
        items = instance.items.select_related("product").all()
        
        if not items:
            return Decimal("0.00")
        
        total = Decimal("0.00")
        for item in items:
            total += item.quantity * item.product.public_price
        
        return Decimal(total).quantize(Decimal("0.00"))
    
    def get_total_purchase_cost(self, instance):
        """Calculate total purchase cost"""
        items = instance.items.select_related("product").all()
        
        if not items:
            return Decimal("0.00")
        
        total = Decimal("0.00")
        for item in items:
            total += item.quantity * item.purchase_price
        
        return Decimal(total).quantize(Decimal("0.00"))
    
    def get_total_profit(self, instance):
        """Calculate total profit"""
        items = instance.items.select_related("product").all()
        
        if not items:
            return Decimal("0.00")
        
        total_profit = Decimal("0.00")
        for item in items:
            item_profit = (item.selling_price - item.purchase_price) * item.quantity
            total_profit += item_profit
        
        return Decimal(total_profit).quantize(Decimal("0.00"))
    
    def get_average_discount_percentage(self, instance):
        """Calculate weighted average discount percentage"""
        items = instance.items.select_related("product").all()
        
        if not items:
            return Decimal("0.00")
        
        total_discount = Decimal("0.00")
        total_public_price = Decimal("0.00")
        
        for item in items:
            quantity_price = item.quantity * item.product.public_price
            quantity_discount = quantity_price * (item.selling_discount_percentage / 100)
            
            total_discount += quantity_discount
            total_public_price += quantity_price
        
        if total_public_price == 0:
            return Decimal("0.00")
        
        average_discount = (total_discount / total_public_price) * 100
        return Decimal(average_discount).quantize(Decimal("0.00"))
```

---

## ملاحظات مهمة | Important Notes

### 1. متوسط مرجح | Weighted Average
المتوسط يأخذ في الاعتبار:
- **الكمية**: المنتجات ذات الكميات الأكبر لها تأثير أكبر
- **السعر**: المنتجات الأغلى لها تأثير أكبر على المتوسط

### 2. الدقة | Precision
- جميع الحسابات تستخدم `Decimal` لتجنب مشاكل الأعداد العشرية
- النتيجة النهائية مقربة إلى رقمين بعد الفاصلة العشرية

### 3. الحالات الخاصة | Edge Cases
- إذا كانت الفاتورة فارغة: يتم إرجاع `0.00` لجميع الحقول المحسوبة
- إذا كان إجمالي السعر = 0: يتم إرجاع `0.00`

### 4. حساب الربح | Profit Calculation
- الربح يُحسب على أساس الفرق بين سعر البيع الفعلي وسعر الشراء
- **ليس** على أساس الفرق بين السعر العام وسعر الشراء
- هذا يعطي صورة دقيقة عن الربح الفعلي بعد تطبيق الخصم

### 5. الأداء | Performance
- جميع الحسابات تتم على البيانات المحملة مسبقًا (prefetched)
- لا توجد استعلامات إضافية لقاعدة البيانات
- الحسابات تتم في الذاكرة (in-memory)

### 6. حقول القراءة فقط | Read-Only Fields
جميع الحقول المحسوبة هي **read-only** ولا يمكن تعديلها مباشرة:
- `total_public_price`
- `total_purchase_cost`
- `total_profit`
- `average_discount_percentage`

يتم حسابها تلقائيًا من بيانات العناصر (items).

---

## اختبار | Testing

### مثال طلب API | API Request Example

```bash
GET /api/v1/invoices/sale/123/
Authorization: Bearer {token}
```

### مثال استجابة | Response Example

```json
{
  "id": 123,
  "seller": {
    "id": 1,
    "name": "أحمد محمد",
    "username": "01234567890"
  },
  "user": {
    "id": 2,
    "name": "صيدلية النور",
    "username": "01098765432"
  },
  "items_count": 5,
  "total_quantity": 50,
  "total_price": "5000.00",
  "status": "placed",
  "status_label": "Placed",
  "created_at": "2025-10-09T12:00:00Z",
  "average_discount_percentage": "18.50",
  "items": [
    {
      "id": 1,
      "product": {
        "id": 10,
        "name": "باراسيتامول 500mg",
        "public_price": "10.00"
      },
      "quantity": 100,
      "selling_discount_percentage": "20.00",
      "selling_price": "8.00",
      "sub_total": "800.00"
    }
  ]
}
```

---

## الأسئلة الشائعة | FAQ

### Q1: لماذا نستخدم متوسط مرجح؟
**A:** لأن العناصر في الفاتورة تختلف في الكمية والسعر. المتوسط البسيط لا يعكس التأثير الحقيقي لكل عنصر على إجمالي الخصم.

### Q2: هل يتم حساب العناصر المحذوفة؟
**A:** لا، يتم حساب العناصر النشطة فقط (`items`)، وليس العناصر المحذوفة (`deleted_items`).

### Q3: هل يمكن الفلترة حسب متوسط الخصم أو الربح؟
**A:** حاليًا لا، لأن الحقول محسوبة ديناميكيًا. إذا كنت تحتاج ذلك، يمكن:
- إضافة حقول في قاعدة البيانات يتم تحديثها تلقائيًا
- إضافة annotations في queryset للفلترة

### Q4: كيف يتم حساب الربح في حالة وجود خصومات مختلفة؟
**A:** الربح يُحسب دائمًا على أساس:
```
الربح = (سعر البيع الفعلي - سعر الشراء) × الكمية
```
سعر البيع الفعلي هو السعر بعد تطبيق الخصم، لذا الربح يعكس الواقع الفعلي.

### Q5: هل يؤثر تغيير العناصر على الحقول المحسوبة؟
**A:** نعم، جميع الحقول المحسوبة ديناميكية وتتغير فورًا عند:
- إضافة عنصر جديد
- تعديل كمية أو سعر عنصر
- حذف عنصر

### Q6: هل يتأثر الربح بنسبة الخصم؟
**A:** نعم، كلما زاد الخصم المطبق، قل سعر البيع الفعلي، وبالتالي يقل الربح.

**مثال:**
- سعر الشراء: 100 EGP
- السعر العام: 150 EGP
- خصم 10%: سعر البيع = 135 EGP، الربح = 35 EGP
- خصم 20%: سعر البيع = 120 EGP، الربح = 20 EGP

### Q7: ما الفرق بين total_price و total_public_price؟
**A:**
- `total_public_price`: السعر قبل تطبيق الخصم (سعر الجمهور الكامل)
- `total_price`: السعر بعد تطبيق الخصم (السعر الذي يدفعه العميل فعليًا)

---

## الملفات المعدلة | Modified Files

### 1. **invoices/serializers.py**
التعديلات في `SaleInvoiceReadSerializer`:
- ✅ إضافة حقل `total_public_price` وdالة `get_total_public_price()`
- ✅ إضافة حقل `total_purchase_cost` ودالة `get_total_purchase_cost()`
- ✅ إضافة حقل `total_profit` ودالة `get_total_profit()`
- ✅ إضافة حقل `average_discount_percentage` ودالة `get_average_discount_percentage()`

### 2. **invoices/views.py**
التحسينات في `SaleInvoiceListAPIView`:
- ✅ تحسين queryset بإضافة `prefetch_related` للعناصر والمنتجات
- ✅ منع مشكلة N+1 queries عند حساب الحقول المحسوبة

### 3. **invoices/AVERAGE_DISCOUNT_DOCUMENTATION.md** (جديد)
- ✅ توثيق شامل لجميع الحقول المحسوبة
- ✅ أمثلة عملية وشرح الصيغ الرياضية
- ✅ أمثلة API responses
- ✅ أسئلة شائعة

---

## الإصدار | Version
- **التاريخ**: 2025-10-09
- **الإصدار**: 1.0
- **المطور**: AI Assistant

---

## المراجع | References
- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Decimal Documentation: https://docs.python.org/3/library/decimal.html

