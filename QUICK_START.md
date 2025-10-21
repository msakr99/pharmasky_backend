# ⚡ البدء السريع - AI Voice Sales Agent

دليل سريع للبدء في 5 دقائق!

## 🎯 الخطوات الأساسية

### 1. تشغيل الخدمات (دقيقة واحدة)

```bash
docker-compose up -d
```

### 2. تهيئة Ollama (3-5 دقائق)

```bash
./init_ollama.sh
```

### 3. إعداد قاعدة البيانات (30 ثانية)

```bash
docker-compose exec web python manage.py migrate
```

### 4. تصدير بيانات الأدوية (10 ثواني)

```bash
docker-compose exec web python manage.py export_rag_data
```

### 5. اختبار النظام (دقيقة واحدة)

```bash
# اختبار FastAPI
curl http://localhost:8001/health/

# اختبار Django
curl http://localhost:8000/

# اختبار Ollama
docker-compose exec ollama ollama list
```

## ✅ تأكد من التشغيل

افتح المتصفح وزُر:

- **Django Admin**: http://localhost:8000/admin/
- **FastAPI Docs**: http://localhost:8001/docs
- **Test Page**: افتح ملف `test_webrtc.html`

## 🧪 اختبار سريع

```bash
# اختبار شامل
python test_ai_agent.py

# أو اختبار يدوي
curl -X POST http://localhost:8001/agent/process \
  -H "Content-Type: application/json" \
  -d '{"query": "عايز معلومات عن باراسيتامول"}'
```

## 🚨 مشاكل شائعة

**Ollama لا يعمل؟**
```bash
docker-compose restart ollama
./init_ollama.sh
```

**FastAPI لا يتصل بـ Django؟**
```bash
# تأكد من أن API Key متطابق
grep AI_AGENT_API_KEY .env
grep AI_AGENT_API_KEY project/settings.py
```

**RAG لا يجد بيانات؟**
```bash
# أعد تصدير البيانات
docker-compose exec web python manage.py export_rag_data
docker-compose restart fastapi_agent
```

## 📚 للمزيد

اقرأ [README_AI_AGENT.md](README_AI_AGENT.md) للدليل الكامل.

---

**الآن أنت جاهز! 🎉**

