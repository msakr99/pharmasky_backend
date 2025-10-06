# خطوات نشر إصلاح البحث على السيرفر 🚀

## المشكلة الحالية

من الـ log:
```
pharmasky_web | ... "GET /offers/max-offers/?search=..." HTTP/1.0" 200 14018
```

الـ response حجمه **14KB**، مما يعني أنه يرجع الكثير من النتائج (ربما كل العروض).

**السبب:** السيرفر لم يتم تحديثه بالكود الجديد!

---

## ✅ الحل: تحديث السيرفر

### الخطوة 1: Push الكود المحدث

على جهازك المحلي (Windows):

```bash
# في مجلد المشروع
cd E:\sky0\sky

# Add files
git add offers/views.py project/settings.py project/settings/base.py

# Commit
git commit -m "Fix: Implement manual search filter in MaxOfferListAPIView"

# Push
git push origin main
```

### الخطوة 2: تحديث السيرفر

#### SSH إلى السيرفر:
```bash
ssh your_user@129.212.140.152
```

#### اذهب إلى مجلد المشروع:
```bash
cd /path/to/pharmasky
# مثال:
# cd /home/pharmasky/app
# أو
# cd /opt/pharmasky
```

#### اسحب آخر التعديلات:
```bash
git pull origin main
# أو
git pull origin master
```

### الخطوة 3: إعادة تشغيل الخدمة

#### إذا كنت تستخدم Docker (الأكثر احتمالاً):

```bash
# الطريقة 1: إعادة بناء وتشغيل
docker-compose down
docker-compose up -d --build

# الطريقة 2: إعادة تشغيل فقط (بدون rebuild)
docker-compose restart pharmasky_web

# الطريقة 3: إعادة تحميل الكود (إذا كان mounted)
docker-compose restart pharmasky_web
```

#### إذا كنت تستخدم systemd:

```bash
sudo systemctl restart pharmasky
```

#### إذا كنت تستخدم supervisor:

```bash
sudo supervisorctl restart pharmasky
```

### الخطوة 4: التحقق من التحديث

#### تحقق من أن الملف محدث على السيرفر:

```bash
# تحقق من وجود البحث اليدوي في الكود
grep -A 5 "if search_term:" offers/views.py

# يجب أن ترى:
# if search_term:
#     queryset = queryset.filter(
#         models.Q(product__name__icontains=search_term) |
#         models.Q(product__e_name__icontains=search_term)
#     )
```

#### راقب الـ logs:

```bash
# إذا كنت تستخدم Docker
docker-compose logs -f pharmasky_web | grep MaxOfferListAPIView

# إذا كنت تستخدم systemd
journalctl -u pharmasky -f | grep MaxOfferListAPIView

# أو
tail -f /var/log/pharmasky/application.log | grep MaxOfferListAPIView
```

### الخطوة 5: اختبار البحث

#### من السيرفر نفسه:

```bash
# احصل على token أولاً (إذا لم يكن لديك)
TOKEN="your_auth_token_here"

# اختبر بدون بحث
curl -H "Authorization: Token $TOKEN" \
     "http://localhost:8000/offers/max-offers/" \
     | jq '.count'

# اختبر مع بحث
curl -H "Authorization: Token $TOKEN" \
     "http://localhost:8000/offers/max-offers/?search=استبرين" \
     | jq '.count'

# يجب أن يكون الرقم الثاني أقل من الأول!
```

#### من Postman أو أي HTTP Client:

```
GET http://129.212.140.152/offers/max-offers/?search=استبرين
Headers:
  Authorization: Token YOUR_TOKEN
```

---

## 📊 النتيجة المتوقعة

### في الـ Logs:

يجب أن ترى:

```
[MaxOfferListAPIView] User: +20..., Search term: 'استبرين'
[MaxOfferListAPIView] Initial queryset count: 15
[MaxOfferListAPIView] After search filter count: 0
```

أو

```
[MaxOfferListAPIView] User: +20..., Search term: 'ا'
[MaxOfferListAPIView] Initial queryset count: 15
[MaxOfferListAPIView] After search filter count: 10
```

### في الـ Response:

#### قبل الإصلاح ❌:
```json
{
  "count": 15,  // نفس العدد دائماً
  "results": [...]
}
```

#### بعد الإصلاح ✅:
```json
{
  "count": 0,   // أو رقم أقل بكثير
  "results": []
}
```

---

## 🔍 Troubleshooting

### المشكلة 1: `git pull` يفشل

```bash
# تحقق من الـ branch
git branch

# تحقق من الـ remote
git remote -v

# إذا كان هناك conflicts
git stash
git pull
git stash pop
```

### المشكلة 2: Docker لا يعيد بناء الـ image

```bash
# Force rebuild
docker-compose build --no-cache pharmasky_web
docker-compose up -d
```

### المشكلة 3: لا توجد logs

```bash
# تحقق من أن الـ logging مفعل في settings
grep -A 10 "LOGGING" project/settings.py

# تحقق من الـ container يعمل
docker-compose ps
```

### المشكلة 4: البحث لا يزال يرجع كل النتائج

```bash
# تحقق من أن الملف محدث
cat offers/views.py | grep -A 10 "def get_queryset"

# تحقق من آخر commit
git log -1 --oneline

# تحقق من الـ logs
docker-compose logs pharmasky_web | tail -100
```

---

## 📋 Checklist

قبل أن تقول "البحث لا يعمل"، تأكد من:

- [ ] ✅ تم عمل `git push` من جهازك المحلي
- [ ] ✅ تم عمل `git pull` على السيرفر
- [ ] ✅ تم إعادة تشغيل الخدمة (Docker/systemd/supervisor)
- [ ] ✅ الـ logs تُظهر الرسائل الجديدة (`[MaxOfferListAPIView]`)
- [ ] ✅ تم اختبار البحث مع token صحيح
- [ ] ✅ استخدام `?search=TEXT` وليس `?s=TEXT`

---

## 🎯 الخلاصة

1. **Push الكود** من جهازك المحلي
2. **Pull الكود** على السيرفر
3. **أعد تشغيل** Docker/systemd/supervisor
4. **راقب الـ logs** للتأكد من تطبيق التعديلات
5. **اختبر البحث** ولاحظ الفرق في count

**بعد تنفيذ كل الخطوات، البحث سيعمل بنجاح!** ✨

---

**آخر تحديث:** 2025-10-06  
**الحالة:** في انتظار النشر على السيرفر

