# 🚦 دليل حل مشكلة Rate Limiting - AI Agent

## 🔍 **المشكلة المكتشفة:**

**الخطأ:** `429 Too Many Requests` من OpenAI API  
**السبب:** تجاوز حد الاستخدام المسموح من OpenAI

---

## ✅ **الحلول المطبقة:**

### 1. **Rate Limiting على مستوى Django:**

تم إضافة حماية من الطلبات الكثيرة:

```python
# ai_agent/throttling.py
- 10 طلبات في الدقيقة للمستخدمين المصرح لهم
- 5 طلبات في الدقيقة للمستخدمين غير المصرح لهم
- حماية من Burst requests
```

### 2. **معالجة أخطاء محسنة:**

```python
# ai_agent/error_handler.py
✅ رسائل خطأ عربية واضحة
✅ معالجة خاصة لـ Rate Limit (429)
✅ معالجة خاصة لـ Auth errors (401)
✅ معالجة خاصة لـ Service errors (502/503)
```

### 3. **رسائل مستخدم واضحة:**

**بدلاً من:**
```json
{
  "error": "Internal Server Error 500"
}
```

**الآن:**
```json
{
  "error": "تم تجاوز حد الاستخدام المؤقت للخدمة",
  "message": "يرجى الانتظار قليلاً والمحاولة مرة أخرى",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

---

## 🛠️ **حلول إضافية موصى بها:**

### 1. **Caching للردود الشائعة:**

```python
# استخدام Redis لتخزين الردود المتكررة
from django.core.cache import cache

def get_cached_response(message):
    cache_key = f"ai_response:{hash(message)}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    # ... call OpenAI
    cache.set(cache_key, response, timeout=3600)  # 1 hour
```

### 2. **Queue System للطلبات:**

```python
# استخدام Celery لمعالجة الطلبات بشكل تسلسلي
@celery_app.task(rate_limit='10/m')
def process_ai_request(user_id, message):
    # معالجة الطلب
    pass
```

### 3. **زيادة حدود OpenAI:**

- ترقية الـ API tier في OpenAI
- زيادة الـ RPM (Requests Per Minute)
- زيادة الـ TPM (Tokens Per Minute)

### 4. **Load Balancing:**

```python
# استخدام أكثر من API key وتوزيع الطلبات
OPENAI_API_KEYS = [
    'key1',
    'key2',
    'key3'
]

# Round-robin between keys
```

---

## 📊 **حدود OpenAI الحالية:**

| Plan | RPM | TPM | TPD |
|------|-----|-----|-----|
| Free | 3 | 40,000 | 200 |
| Tier 1 | 500 | 60,000 | 10,000 |
| Tier 2 | 5,000 | 160,000 | 50,000 |
| Tier 3 | 10,000 | 1,000,000 | 200,000 |

---

## 🔧 **كيفية التطبيق:**

### على السيرفر:

```bash
# 1. Pull التحديثات
cd /opt/pharmasky
git pull origin main

# 2. إعادة build
docker-compose down
docker-compose build --no-cache

# 3. إعادة التشغيل
docker-compose up -d

# 4. التحقق
docker-compose logs web --tail=50
```

---

## 📝 **تعديل الحدود:**

لتعديل Rate Limiting:

```python
# في project/settings/base.py
"DEFAULT_THROTTLE_RATES": {
    "ai_agent_user": "20/minute",  # زيادة إلى 20
    "ai_agent_anon": "10/minute",  # زيادة إلى 10
}
```

---

## 🎯 **النتيجة المتوقعة:**

بعد التطبيق:
- ✅ رسائل خطأ واضحة بالعربية
- ✅ حماية من تجاوز حدود OpenAI
- ✅ تجربة مستخدم أفضل
- ✅ تقليل أخطاء 429

---

## 📞 **للمزيد من التحسينات:**

1. **Implement Caching** - لتقليل الطلبات المتكررة
2. **Queue System** - لمعالجة تسلسلية
3. **Multiple API Keys** - لتوزيع الحمل
4. **Upgrade OpenAI Plan** - لحدود أعلى

---

**آخر تحديث:** 16 أكتوبر 2025  
**الحالة:** ✅ تم تطبيق الحلول الأساسية

