# أوامر تطبيق Migration على السيرفر
# Server Migration Commands

---

## 🚀 الخطوات المطلوبة

### 1. اتصل بالسيرفر

```bash
ssh -i ~/.ssh/pharmasky-github-deploy root@129.212.140.152
```

أو إذا كنت على Windows PowerShell:
```powershell
ssh -i $HOME\.ssh\pharmasky-github-deploy root@129.212.140.152
```

---

### 2. انتقل للمشروع وسحب التحديثات

```bash
cd /opt/pharmasky
git stash
git pull origin main
```

---

### 3. طبق الـ Migrations

```bash
# دخول الـ Docker container
docker compose exec web python manage.py migrate profiles

# تطبيق كل الـ migrations
docker compose exec web python manage.py migrate
```

---

### 4. إعادة تشغيل الخدمة

```bash
docker compose restart web
```

---

### 5. التحقق من الحالة

```bash
# التحقق من حالة الخدمات
docker compose ps

# التحقق من الـ API
curl http://localhost:8000/finance/collection-schedule/
```

---

## ✅ تم!

الآن الـ API جاهز:
```
GET http://129.212.140.152/finance/collection-schedule/
```

---

## 📝 أو نفذ كل الأوامر دفعة واحدة

```bash
ssh -i ~/.ssh/pharmasky-github-deploy root@129.212.140.152 << 'EOF'
cd /opt/pharmasky
git stash
git pull origin main
docker compose exec -T web python manage.py migrate profiles
docker compose exec -T web python manage.py migrate
docker compose restart web
sleep 5
docker compose ps
echo "✅ Migration completed!"
EOF
```

---

## 🔗 للاختبار

```bash
curl -H "Authorization: Token YOUR_TOKEN" http://129.212.140.152/finance/collection-schedule/
```

---

**آخر تحديث**: 2025-10-10  
**الحالة**: جاهز للتطبيق

