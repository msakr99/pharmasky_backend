# FastAPI AI Agent Service

خدمة الذكاء الاصطناعي المتقدمة لشركة فارماسكاي - بديل كامل لـ `ai_agent` Django app

## 🚀 المميزات

### ✅ جميع وظائف `ai_agent` Django:
- **Chat API** - محادثة نصية مع الذكاء الاصطناعي
- **Voice API** - معالجة الصوت وتحويله لنص
- **Call API** - محاكاة المكالمات الصوتية المباشرة
- **Function Calling** - تنفيذ وظائف محددة (9 وظائف)
- **Session Management** - إدارة جلسات المحادثة
- **RAG Integration** - استرجاع المعلومات الذكي

### 🛠️ الأدوات المتاحة:
1. `check_availability` - فحص توفر الأدوية
2. `suggest_alternative` - اقتراح بدائل
3. `create_order` - إنشاء طلبات
4. `track_order` - تتبع الطلبات
5. `cancel_order` - إلغاء الطلبات
6. `submit_complaint` - تسجيل شكاوى
7. `get_wishlist` - قائمة المفضلة
8. `add_to_wishlist` - إضافة للمفضلة
9. `get_order_total` - حساب إجمالي الطلبات

## 📡 API Endpoints

### Chat Endpoints
```
POST /agent/chat
POST /agent/voice
POST /agent/call
```

### Function Endpoints
```
POST /agent/check-availability
POST /agent/suggest-alternative
POST /agent/create-order
POST /agent/track-order
POST /agent/cancel-order
POST /agent/submit-complaint
GET  /agent/get-wishlist/{user_id}
POST /agent/add-to-wishlist
GET  /agent/get-order-total/{user_id}
```

### Processing Endpoint
```
POST /agent/process
```

## 🔧 الإعداد

### 1. متغيرات البيئة
```env
# Django Backend
DJANGO_API_URL=http://web:8000
DJANGO_API_KEY=your-api-key

# OpenAI (اختياري)
OPENAI_API_KEY=your-openai-key
DIGITALOCEAN_AGENT_URL=your-digitalocean-url

# Ollama
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=phi3:mini

# Database
DATABASE_URL=postgresql://agent:agent@fastapi_db:5432/agent_db
```

### 2. تشغيل الخدمة
```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل الخدمة
python main.py
```

## 🎯 الاستخدام

### مثال على Chat API:
```python
import httpx

# إرسال رسالة نصية مع التوكن
response = await httpx.post("http://localhost:8001/agent/chat", 
    headers={"Authorization": "Bearer your_jwt_token"},
    json={
        "message": "عايز باراسيتامول",
        "session_id": 123
    }
)

# أو مع التوكن في الـ body
response = await httpx.post("http://localhost:8001/agent/chat", json={
    "message": "عايز باراسيتامول",
    "session_id": 123,
    "token": "your_jwt_token"
})

# أو مع user_id (fallback)
response = await httpx.post("http://localhost:8001/agent/chat", json={
    "message": "عايز باراسيتامول",
    "session_id": 123,
    "context": {"user_id": 456}
})
```

### مثال على Voice API:
```python
# إرسال رسالة صوتية مع التوكن
response = await httpx.post("http://localhost:8001/agent/voice", 
    headers={"Authorization": "Bearer your_jwt_token"},
    json={
        "audio_base64": "base64_encoded_audio",
        "session_id": 123
    }
)
```

### مثال على Function Calling:
```python
# فحص توفر دواء مع التوكن
response = await httpx.post("http://localhost:8001/agent/check-availability", 
    headers={"Authorization": "Bearer your_jwt_token"},
    json={
        "medicine_name": "باراسيتامول"
    }
)
```

## 🔄 التكامل مع Django

الخدمة تتواصل مع Django backend عبر MCP (Model Context Protocol) لتنفيذ جميع العمليات:

- **Database Operations** - عمليات قاعدة البيانات
- **User Management** - إدارة المستخدمين
- **Order Processing** - معالجة الطلبات
- **Inventory Management** - إدارة المخزون

## 📊 المميزات المتقدمة

### 1. RAG (Retrieval Augmented Generation)
- استرجاع المعلومات الذكي من قاعدة البيانات
- تحسين دقة الإجابات
- دعم البحث المتقدم

### 2. Intent Detection
- تحليل نوايا المستخدم
- استخراج الكيانات (الأدوية، الكميات)
- توجيه الطلبات للوظائف المناسبة

### 3. Function Calling
- تنفيذ تلقائي للوظائف
- معالجة الأخطاء
- تتبع العمليات

## 🚀 النشر

### Docker
```bash
docker build -t fastapi-agent .
docker run -p 8001:8001 fastapi-agent
```

### Docker Compose
```yaml
services:
  fastapi-agent:
    build: .
    ports:
      - "8001:8001"
    environment:
      - DJANGO_API_URL=http://web:8000
      - OLLAMA_URL=http://ollama:11434
```

## 🔐 المصادقة بالتوكن

### **طرق المصادقة:**
1. **Authorization Header** - `Bearer your_jwt_token`
2. **Token in Body** - `{"token": "your_jwt_token"}`
3. **Fallback** - `{"context": {"user_id": 123}}`

### **مثال على الاستخدام:**
```python
# الطريقة المفضلة - Authorization Header
response = await httpx.post("http://localhost:8001/agent/chat", 
    headers={"Authorization": "Bearer your_jwt_token"},
    json={"message": "صباح الخير"}
)

# أو مع التوكن في الـ body
response = await httpx.post("http://localhost:8001/agent/chat", 
    json={
        "message": "صباح الخير",
        "token": "your_jwt_token"
    }
)
```

### **التحقق من التوكن:**
```python
# التحقق من صحة التوكن
response = await httpx.post("http://localhost:8001/agent/verify-token", 
    json={"token": "your_jwt_token"}
)
```

## 📈 المراقبة

### Health Check
```
GET /health
```

### Logs
```bash
# عرض السجلات
docker logs fastapi-agent

# مراقبة الأداء
curl http://localhost:8001/health
```

## 🔧 التطوير

### إضافة وظيفة جديدة:
1. أضف الوظيفة في `services/mcp_service.py`
2. أضف الـ endpoint في `api/routes/agent.py`
3. حدث الـ schema في `api/schemas.py`
4. اختبر الوظيفة

### إضافة نموذج جديد:
1. أضف النموذج في `api/schemas.py`
2. حدث الـ database models
3. أضف الـ migration
4. اختبر النموذج

## 📝 ملاحظات مهمة

- **التوافق الكامل** مع `ai_agent` Django app
- **دعم جميع الوظائف** الموجودة في Django
- **معمارية microservice** منفصلة
- **تكامل مع RAG** للبحث الذكي
- **دعم Ollama** كبديل أرخص من OpenAI

## 🤝 المساهمة

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة
3. Commit التغييرات
4. إنشاء Pull Request

---

**تم تطوير هذا المشروع ليكون بديلاً كاملاً لـ `ai_agent` Django app مع مميزات إضافية!** 🎉
