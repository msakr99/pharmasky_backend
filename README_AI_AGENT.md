# 🤖 AI Voice Sales Agent - نظام الوكيل الصوتي الذكي للمبيعات

نظام متكامل لوكيل مبيعات ذكي يعمل بالذكاء الاصطناعي لشركات توزيع الأدوية، يدعم المكالمات الصوتية، معالجة اللغة الطبيعية، والتكامل مع نظام إدارة الصيدليات.

## 🏗️ البنية المعمارية (Architecture)

```
┌─────────────────────────────────────────────────────────────────┐
│                         المستخدم / Browser                       │
│                    (Dashboard / WebRTC Client)                  │
└────────────────┬────────────────────────────┬───────────────────┘
                 │                            │
                 │ HTTP/WS                    │ HTTP/REST
                 ▼                            ▼
┌────────────────────────────┐  ┌────────────────────────────────┐
│   FastAPI AI Service       │  │      Django Backend            │
│   (Port 8001)              │◄─┤      (Port 8000)               │
│                            │  │                                │
│  ┌──────────────────────┐  │  │  ┌──────────────────────┐     │
│  │ STT (Whisper)        │  │  │  │ Drug Catalog API     │     │
│  │ - Arabic Support     │  │  │  │ Order Management     │     │
│  └──────────────────────┘  │  │  │ Stock Check          │     │
│                            │  │  └──────────────────────┘     │
│  ┌──────────────────────┐  │  │                                │
│  │ LLM (Ollama/Phi-3)   │  │  │  ┌──────────────────────┐     │
│  │ - Intent Detection   │  │  │  │ PostgreSQL           │     │
│  │ - Response Gen       │  │  │  │ - Products           │     │
│  └──────────────────────┘  │  │  │ - Orders             │     │
│                            │  │  │ - Pharmacies         │     │
│  ┌──────────────────────┐  │  │  └──────────────────────┘     │
│  │ RAG (ChromaDB)       │  │  │                                │
│  │ - Drug Knowledge     │  │  │  ┌──────────────────────┐     │
│  │ - Policies           │  │  │  │ Voice Calls Models   │     │
│  └──────────────────────┘  │  │  │ - VoiceCall          │     │
│                            │  │  │ - CallTranscript     │     │
│  ┌──────────────────────┐  │  │  │ - CallAction         │     │
│  │ TTS (gTTS)           │  │  │  └──────────────────────┘     │
│  │ - Arabic Voice       │  │  │                                │
│  └──────────────────────┘  │  └────────────────────────────────┘
│                            │
│  ┌──────────────────────┐  │
│  │ MCP Service          │──┤ API Key Auth
│  │ - Django API Client  │  │ REST Calls
│  └──────────────────────┘  │
└────────────────────────────┘
         │
         ▼
┌────────────────────────────┐
│   Ollama Container         │
│   - Phi-3 Mini Model       │
│   (Port 11434)             │
└────────────────────────────┘
```

## 📋 المتطلبات (Prerequisites)

- Docker & Docker Compose
- Python 3.11+ (للتطوير المحلي)
- Node.js 18+ (للـ Dashboard)
- 8GB RAM على الأقل
- 10GB مساحة تخزين حرة

## 🚀 التثبيت والتشغيل (Quick Start)

### 1. استنساخ المشروع

```bash
git clone <repository-url>
cd sky
```

### 2. إعداد ملفات البيئة

```bash
# نسخ ملف البيئة المثالي
cp fastapi_agent/.env.example fastapi_agent/.env

# تعديل المتغيرات المطلوبة
# - DJANGO_API_KEY: مفتاح API مشترك بين الخدمات
# - DATABASE_URL: اتصال قاعدة البيانات
```

### 3. بناء وتشغيل الخدمات

```bash
# بناء وتشغيل جميع الخدمات
docker-compose up -d

# مشاهدة السجلات
docker-compose logs -f
```

### 4. تهيئة Ollama وتحميل النموذج

```bash
# تشغيل سكريبت التهيئة
./init_ollama.sh

# أو يدوياً:
docker-compose exec ollama ollama pull phi3:mini
```

### 5. تشغيل Migrations وتصدير البيانات

```bash
# Django migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# تصدير بيانات الأدوية لـ RAG
docker-compose exec web python manage.py export_rag_data
```

### 6. التحقق من تشغيل الخدمات

```bash
# Django API
curl http://localhost:8000/

# FastAPI Agent
curl http://localhost:8001/health/

# Ollama
curl http://localhost:11434/api/tags
```

## 🧪 الاختبار (Testing)

### اختبار شامل للـ AI Agent

```bash
python test_ai_agent.py
```

هذا السكريبت يختبر:
- ✓ Health Check
- ✓ RAG Query
- ✓ Django Drug Search API
- ✓ Agent Text Processing
- ✓ Call Session Management
- ✓ MCP Integration

### اختبار WebRTC والمكالمات الصوتية

افتح الملف `test_webrtc.html` في المتصفح:

```bash
# على Windows
start test_webrtc.html

# على Mac/Linux
open test_webrtc.html
```

الواجهة توفر:
- 📞 بدء/إنهاء مكالمة
- 🎤 تسجيل صوتي
- 📝 عرض Transcript فوري
- 📊 سجل الأحداث

## 📡 نقاط النهاية الرئيسية (API Endpoints)

### Django Backend (Port 8000)

#### Drug Catalog APIs

```bash
# البحث عن أدوية
GET /market/ai/drugs/search/?q=باراسيتامول&limit=10
Headers: X-API-Key: your-api-key

# فحص المخزون
POST /market/ai/drugs/stock/
Body: {"product_id": 123, "store_id": 1}

# الحصول على بدائل
GET /market/ai/drugs/123/recommendations/

# إنشاء طلب
POST /market/ai/orders/create/
Body: {
  "pharmacy_id": 1,
  "items": [{"product_id": 1, "quantity": 10}],
  "notes": "طلب عاجل"
}

# معلومات صيدلية
GET /market/ai/pharmacies/1/
```

#### Voice Call Management

```bash
# قائمة المكالمات
GET /ai-agent/calls/?status=completed&page=1

# تفاصيل مكالمة
GET /ai-agent/calls/123/

# الملف الصوتي
GET /ai-agent/calls/123/audio/
```

### FastAPI AI Service (Port 8001)

#### Health & Status

```bash
# Health Check
GET /health/

# Readiness Check
GET /health/ready
```

#### Speech-to-Text

```bash
# تحويل صوت إلى نص
POST /stt/transcribe
Body: {
  "audio_base64": "...",
  "language": "ar"
}

# رفع ملف صوتي
POST /stt/transcribe/file
Form Data: audio=@file.wav, language=ar
```

#### Agent Processing

```bash
# معالجة استعلام نصي
POST /agent/process
Body: {
  "query": "عايز معلومات عن باراسيتامول",
  "session_id": "optional-session-id"
}

# اختبار RAG مباشرة
GET /agent/rag/query?q=أدوية البرد&top_k=5
```

#### Voice Calls

```bash
# بدء مكالمة
POST /calls/start
Body: {"pharmacy_id": 1, "user_id": 1}
Response: {
  "session_id": "uuid",
  "status": "active",
  "websocket_url": "ws://localhost:8001/calls/{session_id}/audio"
}

# WebSocket للصوت الفوري
WS /calls/{session_id}/audio

# إنهاء مكالمة
POST /calls/{session_id}/end
Body: {"session_id": "uuid"}

# تفاصيل المكالمة
GET /calls/{session_id}
```

## 🔧 التكوين (Configuration)

### Django Settings

في `project/settings.py`:

```python
# API Key للـ AI Agent Service
AI_AGENT_API_KEY = env('AI_AGENT_API_KEY', default='change-this-in-production')

# CORS للسماح بـ FastAPI
CORS_ALLOW_HEADERS = [
    # ... existing headers
    "X-API-Key",
]
```

### FastAPI Settings

في `fastapi_agent/config.py`:

```python
class Settings(BaseSettings):
    # Django Backend
    DJANGO_API_URL: str = "http://web:8000"
    DJANGO_API_KEY: str = "your-api-key"
    
    # Ollama LLM
    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "phi3:mini"
    
    # Whisper STT
    WHISPER_MODEL: str = "base"  # tiny, base, small, medium, large
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_db"
```

## 📊 قاعدة البيانات (Database Models)

### Django Models (ai_agent/models.py)

```python
# نموذج المكالمة الصوتية
VoiceCall
  - pharmacy (ForeignKey)
  - user (ForeignKey)
  - session_id (CharField, unique)
  - audio_file (FileField)
  - duration (IntegerField)
  - status (CharField: active/completed/failed)
  - summary (TextField)
  - created_at, updated_at, ended_at

# نص المحادثة
CallTranscript
  - call (ForeignKey)
  - speaker (CharField: user/assistant/system)
  - text (TextField)
  - timestamp (FloatField)

# الأوامر المنفذة
CallAction
  - call (ForeignKey)
  - action_type (CharField: create_order/check_stock/etc)
  - parameters (JSONField)
  - result (JSONField)
  - status (CharField: pending/success/failed)
```

## 🔄 سير العمل (Workflow)

### سيناريو: إنشاء طلب عبر المكالمة الصوتية

```
1. صيدلي يتصل عبر WebRTC
   ↓
2. الصوت يُسجل ويُرسل لـ FastAPI
   ↓
3. Whisper يحول الصوت لنص: "عايز 5 علب باراسيتامول 500"
   ↓
4. RAG يبحث في قاعدة المعرفة عن باراسيتامول
   ↓
5. LLM (Phi-3) يفهم النية: "create_order"
   ↓
6. MCP Service يستدعي Django API:
   POST /market/ai/orders/create/
   ↓
7. Django ينشئ الطلب ويرجع order_id
   ↓
8. LLM يصيغ الرد: "تم تسجيل طلبك رقم 453 بنجاح"
   ↓
9. gTTS يحول النص لصوت
   ↓
10. الصوت يُرسل للصيدلي عبر WebSocket
```

## 🛠️ أدوات التطوير (Development Tools)

### إعادة بناء الخدمات

```bash
# إعادة بناء FastAPI Agent
docker-compose build fastapi_agent

# إعادة بناء Django
docker-compose build web

# إعادة تشغيل جميع الخدمات
docker-compose restart
```

### مشاهدة السجلات

```bash
# جميع الخدمات
docker-compose logs -f

# FastAPI فقط
docker-compose logs -f fastapi_agent

# Django فقط
docker-compose logs -f web

# Ollama فقط
docker-compose logs -f ollama
```

### الدخول للـ Containers

```bash
# Django shell
docker-compose exec web python manage.py shell

# FastAPI container
docker-compose exec fastapi_agent bash

# Ollama
docker-compose exec ollama bash
```

## 🐛 استكشاف الأخطاء (Troubleshooting)

### المشكلة: Ollama لا يعمل

```bash
# التحقق من حالة Ollama
docker-compose ps ollama

# التحقق من النماذج المحملة
docker-compose exec ollama ollama list

# إعادة تحميل النموذج
docker-compose exec ollama ollama pull phi3:mini
```

### المشكلة: FastAPI لا يتصل بـ Django

```bash
# التحقق من API Key
# تأكد أن AI_AGENT_API_KEY متطابق في كلا الخدمتين

# اختبار الاتصال يدوياً
docker-compose exec fastapi_agent curl -H "X-API-Key: your-key" http://web:8000/market/ai/drugs/search/?q=test
```

### المشكلة: RAG لا يجد البيانات

```bash
# تصدير البيانات من جديد
docker-compose exec web python manage.py export_rag_data

# التحقق من الملفات
ls -la rag_data/

# إعادة تشغيل FastAPI لإعادة تحميل البيانات
docker-compose restart fastapi_agent
```

### المشكلة: Whisper بطيء جداً

```bash
# استخدم نموذج أصغر
# في fastapi_agent/config.py
WHISPER_MODEL=tiny  # بدلاً من base

# أو استخدم GPU (إذا متوفر)
# في docker-compose.yml، أضف:
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

## 📈 التحسينات المستقبلية (Future Enhancements)

- [ ] دعم نماذج LLM أكبر (Llama 2, GPT-4)
- [ ] تحسين دقة STT للعربية باستخدام نماذج مخصصة
- [ ] إضافة نظام cache للاستجابات المتكررة
- [ ] دعم مكالمات SIP عبر Asterisk
- [ ] لوحة تحكم Next.js متقدمة مع Analytics
- [ ] نظام تقييم جودة المكالمات
- [ ] تكامل مع أنظمة CRM خارجية
- [ ] دعم لغات إضافية (الإنجليزية، الفرنسية)

## 📝 ملاحظات الأمان (Security Notes)

⚠️ **مهم للإنتاج**:

1. **تغيير API Keys**: غيّر `AI_AGENT_API_KEY` في production
2. **HTTPS**: استخدم HTTPS لجميع الخدمات
3. **Database Passwords**: استخدم كلمات مرور قوية
4. **CORS**: حدد Origins المسموحة فقط
5. **Rate Limiting**: أضف rate limiting للـ APIs
6. **Audio Storage**: احذف الملفات الصوتية القديمة دورياً
7. **Logs**: لا تسجل معلومات حساسة في اللوجات

## 🤝 المساهمة (Contributing)

نرحب بالمساهمات! يرجى:

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة
3. Commit التغييرات
4. إنشاء Pull Request

## 📄 الترخيص (License)

هذا المشروع مرخص تحت MIT License.

## 📞 الدعم (Support)

للمساعدة أو الأسئلة:
- افتح Issue على GitHub
- راجع الوثائق في `/docs`
- تحقق من السجلات: `docker-compose logs`

---

**تم بناؤه بـ ❤️ باستخدام Django, FastAPI, Whisper, Ollama, و ChromaDB**

