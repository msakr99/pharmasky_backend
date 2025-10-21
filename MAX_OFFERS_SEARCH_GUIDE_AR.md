# 🎯 دليل البحث المتقدم في Max Offers

## 📍 الـ Endpoint

```
GET /offers/max-offers/
```

---

## 🚀 البدء السريع

### مثال بسيط - Hybrid (الافتراضي):

```bash
curl "http://your-server/offers/max-offers/?q=باراسيتامول"
```

### مع تحديد الوضع:

```bash
# Hybrid Mode
curl "http://your-server/offers/max-offers/?q=باراسيتامول&search_mode=hybrid"

# FTS Mode (أسرع)
curl "http://your-server/offers/max-offers/?q=أسبرين&search_mode=fts"

# Trigram Mode (للأخطاء)
curl "http://your-server/offers/max-offers/?q=parasetmol&search_mode=trigram"
```

---

## 🎨 الأوضاع الثلاثة

### 1. Hybrid Mode - الوضع الذكي (موصى به)

```bash
?q=باراسيتامول&search_mode=hybrid
```

**متى تستخدمه:**
- ✅ الاستخدام العام اليومي
- ✅ عايز أفضل نتائج
- ✅ بتبحث بالعربي أو الإنجليزي
- ✅ ممكن في أخطاء بسيطة

**المميزات:**
- دقة 85-90%
- يجمع FTS + Trigram
- تحمل أخطاء بسيطة
- ترتيب ذكي

**الأداء:**
- أول بحث: 30-150ms
- من الكاش: 5-10ms

---

### 2. FTS Mode - الوضع السريع

```bash
?q=أسبرين&search_mode=fts
```

**متى تستخدمه:**
- ✅ عايز سرعة قصوى
- ✅ متأكد من الكتابة الصحيحة
- ✅ بتبحث بكلمات دقيقة

**المميزات:**
- أسرع وضع (10-50ms)
- دقة عالية للكلمات الصحيحة
- دعم ممتاز للعربية

**ملاحظة:**
- لا يتعامل مع الأخطاء الإملائية

---

### 3. Trigram Mode - وضع الأخطاء

```bash
?q=parasetmol&search_mode=trigram&min_similarity=0.2
```

**متى تستخدمه:**
- ✅ مش متأكد من الكتابة
- ✅ ممكن في خطأ إملائي
- ✅ عايز نتائج مشابهة

**المميزات:**
- يلاقي الكلمات المشابهة
- تحمل أخطاء 80-90%
- Fuzzy matching ذكي

**Parameters:**
- `min_similarity`: 0.0 - 1.0 (الافتراضي: 0.2)
  - `0.15` = نتائج كتير (أقل دقة)
  - `0.2` = متوازن (موصى به)
  - `0.5` = نتائج دقيقة (أقل عدد)

---

## 📊 الحقول المبحوثة

يبحث في 4 حقول بأوزان مختلفة:

| الحقل | وزن FTS | وزن Trigram | مثال |
|-------|---------|-------------|------|
| 🥇 اسم المنتج | A (أعلى) | 100% | "باراسيتامول 500 مجم" |
| 🥈 المادة الفعالة | B | 80% | "باراسيتامول" |
| 🥉 اسم الشركة | C | 60% | "نوفارتس" |
| 🏅 الاسم الإنجليزي | D (أقل) | 40% | "Paracetamol" |

---

## 💰 معلومات العرض المرجعة

```json
{
  "count": 15,
  "results": [
    {
      "id": 123,
      "product": {
        "name": "باراسيتامول 500 مجم",
        "e_name": "Paracetamol 500mg",
        "company": "نوفارتس",
        "effective_material": "باراسيتامول",
        "public_price": "15.50"
      },
      "selling_price": 12.50,
      "selling_discount_percentage": 15.5,
      "actual_discount_precentage": 15.5,  // حسب نوع المستخدم
      "actual_offer_price": 10.56,         // السعر الفعلي
      "remaining_amount": 500,
      "min_purchase": 10,
      "rank": 0.95,      // FTS score
      "sim": 1.0,        // Trigram similarity
      "score": 0.92,     // Combined score (hybrid)
      "starts": 1        // Prefix match boost
    }
  ]
}
```

---

## 🔧 Parameters الكاملة

### Parameters البحث الأساسية:

| Parameter | النوع | الافتراضي | الوصف |
|-----------|-------|-----------|-------|
| `q` | string | - | نص البحث (إجباري) |
| `search_mode` | string | `hybrid` | الوضع: `fts`, `trigram`, `hybrid` |
| `min_similarity` | float | `0.2` | الحد الأدنى للتشابه (0.0-1.0) |

### Parameters إضافية:

| Parameter | الوصف | مثال |
|-----------|-------|------|
| `page` | رقم الصفحة | `?q=test&page=2` |
| `page_size` | حجم الصفحة | `?q=test&page_size=50` |
| `ordering` | الترتيب | `?ordering=-selling_discount_percentage` |

**Ordering المتاح:**
- `product__name` - حسب اسم المنتج
- `product__public_price` - حسب السعر
- `selling_discount_percentage` - حسب نسبة الخصم
- `selling_price` - حسب سعر البيع
- `min_purchase` - حسب الحد الأدنى للشراء

---

## 📝 أمثلة متقدمة

### 1. بحث عن دواء معين

```bash
# بالعربي
GET /offers/max-offers/?q=باراسيتامول&search_mode=hybrid

# بالإنجليزي
GET /offers/max-offers/?q=paracetamol&search_mode=hybrid
```

### 2. بحث عن شركة

```bash
GET /offers/max-offers/?q=نوفارتس&search_mode=fts
```

### 3. بحث مع ترتيب حسب الخصم

```bash
GET /offers/max-offers/?q=أسبرين&ordering=-selling_discount_percentage
```

### 4. بحث مع Pagination

```bash
# أول 50 عرض
GET /offers/max-offers/?q=مسكن&page_size=50

# الصفحة الثانية
GET /offers/max-offers/?q=مسكن&page=2&page_size=50
```

### 5. بحث مع خطأ إملائي

```bash
# يبحث عن: Paracetamol
GET /offers/max-offers/?q=parasetmol&search_mode=trigram&min_similarity=0.2
```

### 6. بحث دقيق جداً

```bash
GET /offers/max-offers/?q=aspirin&search_mode=trigram&min_similarity=0.7
```

---

## ⚡ Redis Caching

البحث يستخدم Redis تلقائياً:

```
┌─────────────────────────────────────┐
│   📊 أداء الكاش                     │
├─────────────────────────────────────┤
│                                     │
│  🔍 أول بحث:      30-150ms         │
│  ⚡ بحث مكرر:     5-10ms           │
│  ⏱️ مدة الكاش:    5 دقائق          │
│  💾 عدد النتائج:   أول 100         │
│                                     │
└─────────────────────────────────────┘
```

**فوائد الكاش:**
- ✅ 10-50 مرة أسرع للبحث المكرر
- ✅ تقليل الحمل على قاعدة البيانات
- ✅ استجابة فورية للمستخدم

---

## 🎯 حالات استخدام شائعة

### حالة 1: صيدلية تبحث عن دواء

```bash
# البحث
GET /offers/max-offers/?q=باراسيتامول&search_mode=hybrid

# النتيجة: 
# - كل عروض الباراسيتامول
# - مرتبة حسب الصلة والسعر
# - actual_offer_price محسوب حسب فترة السداد
```

### حالة 2: موظف مبيعات يبحث بسرعة

```bash
# بحث سريع FTS
GET /offers/max-offers/?q=أسبرين&search_mode=fts

# النتيجة في 10-20ms
```

### حالة 3: مستخدم غير متأكد من الكتابة

```bash
# بحث Trigram مع تحمل أخطاء
GET /offers/max-offers/?q=ibuproffen&search_mode=trigram&min_similarity=0.2

# يلاقي: Ibuprofen (رغم الخطأ المزدوج)
```

---

## 🧪 الاختبار

### على السيرفر مباشرة:

```bash
# اختبار بسيط
curl "http://localhost:8000/offers/max-offers/?q=test"

# اختبار مع Token
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/offers/max-offers/?q=باراسيتامول"
```

### باستخدام السكريبت الجاهز:

```bash
# Python script
python test_max_offers_search.py

# Bash script
bash test_max_offers_search.sh
```

---

## 🔐 Authentication

البحث يحتاج Authentication:

```bash
# مع Token
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/offers/max-offers/?q=test"

# في JavaScript/Axios
axios.get('/offers/max-offers/', {
  params: { q: 'باراسيتامول', search_mode: 'hybrid' },
  headers: { 'Authorization': 'Token YOUR_TOKEN' }
})
```

**الصلاحيات المطلوبة:**
- PHARMACY
- SALES
- DATA_ENTRY
- MANAGER

---

## 💡 نصائح للأداء الأفضل

### 1. استخدم الوضع المناسب

```
✅ استخدام عام → hybrid
✅ سرعة قصوى → fts
✅ أخطاء إملائية → trigram
```

### 2. ضبط min_similarity

```
📊 نتائج كثيرة → 0.15
📊 متوازن → 0.2 (الافتراضي)
📊 دقة عالية → 0.5+
```

### 3. Pagination للنتائج الكثيرة

```bash
# بدل ما تجيب 1000 نتيجة
GET /offers/max-offers/?q=test&page_size=50
```

### 4. استفد من الكاش

```
🔄 البحوث المتكررة تكون أسرع بكثير
⏱️ الكاش يستمر 5 دقائق
```

---

## 🎊 الخلاصة

```
╔═══════════════════════════════════════╗
║   ✅ Max Offers Hybrid Search         ║
╠═══════════════════════════════════════╣
║                                       ║
║  🎯 3 أوضاع ذكية                     ║
║  ⚡ كاش Redis سريع                    ║
║  🔍 4 حقول بحث بأوزان                 ║
║  🇸🇦 دعم كامل للعربية                 ║
║  🔤 دعم الإنجليزية                    ║
║  ✏️ تحمل الأخطاء                      ║
║  💰 حسابات فورية للأسعار              ║
║  📊 نتائج مرتبة ذكياً                 ║
║                                       ║
║  🚀 جاهز للاستخدام الفوري!           ║
║                                       ║
╚═══════════════════════════════════════╝
```

---

**محتاج مساعدة إضافية؟** اتصل بفريق التطوير! 🤝

