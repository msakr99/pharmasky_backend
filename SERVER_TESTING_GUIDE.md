# 🖥️ دليل اختبار الإشعارات على السيرفر

## 📋 المتطلبات

أنت الآن على السيرفر في المسار: `/opt/pharmasky/`

تأكد من توفر:
- ✅ curl
- ✅ python3
- ✅ الاتصال بالإنترنت
- ✅ معلومات تسجيل الدخول (Username/Password)

---

## 🚀 الطريقة 1: استخدام السكريبت التلقائي (الأسهل)

### 1. ارفع السكريبت للسيرفر

إذا كنت على جهازك المحلي، ارفع الملف:

```bash
scp test_notifications_server.sh root@167.71.40.9:/opt/pharmasky/
```

أو أنشئه مباشرة على السيرفر:

```bash
cd /opt/pharmasky/
nano test_notifications_server.sh
# الصق محتوى السكريبت واحفظ
```

### 2. أعط صلاحيات التنفيذ

```bash
chmod +x test_notifications_server.sh
```

### 3. شغل السكريبت

```bash
bash test_notifications_server.sh
```

سيطلب منك:
- Username (رقم الهاتف مع +2)
- Password

ثم سيختبر تلقائياً:
- ✅ حالة السيرفر
- ✅ تسجيل الدخول
- ✅ الإحصائيات
- ✅ جلب الإشعارات
- ✅ الإشعارات غير المقروءة
- ✅ المواضيع

---

## 🔧 الطريقة 2: اختبار يدوي بـ curl

### الخطوة 1: تسجيل الدخول

```bash
curl -X POST "http://167.71.40.9/api/v1/accounts/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"+201234567890","password":"your_password"}' \
  | python3 -m json.tool
```

**احفظ الـ Token من الاستجابة!**

### الخطوة 2: اختبر الإشعارات

```bash
# ضع الـ Token هنا
TOKEN="your_token_here"

# 1. جلب الإحصائيات
curl -H "Authorization: Token $TOKEN" \
  "http://167.71.40.9/api/v1/notifications/notifications/stats/" \
  | python3 -m json.tool

# 2. جلب جميع الإشعارات
curl -H "Authorization: Token $TOKEN" \
  "http://167.71.40.9/api/v1/notifications/notifications/" \
  | python3 -m json.tool

# 3. جلب الإشعارات غير المقروءة
curl -H "Authorization: Token $TOKEN" \
  "http://167.71.40.9/api/v1/notifications/notifications/unread/" \
  | python3 -m json.tool

# 4. جلب المواضيع
curl -H "Authorization: Token $TOKEN" \
  "http://167.71.40.9/api/v1/notifications/topics/my-topics/" \
  | python3 -m json.tool
```

### الخطوة 3: عمليات متقدمة

```bash
# تحديد إشعار كمقروء (استبدل NOTIF_ID برقم الإشعار)
curl -X PATCH "http://167.71.40.9/api/v1/notifications/notifications/NOTIF_ID/update/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_read": true}' \
  | python3 -m json.tool

# تحديد جميع الإشعارات كمقروءة
curl -X POST "http://167.71.40.9/api/v1/notifications/notifications/mark-all-read/" \
  -H "Authorization: Token $TOKEN" \
  | python3 -m json.tool

# حذف إشعار
curl -X DELETE "http://167.71.40.9/api/v1/notifications/notifications/NOTIF_ID/delete/" \
  -H "Authorization: Token $TOKEN" \
  | python3 -m json.tool
```

---

## 🐍 الطريقة 3: استخدام Django Management Commands

### 1. تفعيل البيئة الافتراضية

```bash
cd /opt/pharmasky/
source venv/bin/activate  # أو المسار الصحيح للـ venv
```

### 2. إنشاء إشعارات تجريبية

```bash
# إنشاء 10 إشعارات تجريبية
python manage.py create_test_notifications --count 10

# إنشاء مع مواضيع
python manage.py create_test_notifications --with-topics --count 20

# لمستخدم محدد
python manage.py create_test_notifications --users +201234567890 --count 15
```

### 3. استخدام Django Shell

```bash
python manage.py shell
```

ثم:

```python
from django.contrib.auth import get_user_model
from notifications.models import Notification, Topic

User = get_user_model()

# جلب مستخدم
user = User.objects.filter(username="+201234567890").first()

# عرض إشعارات المستخدم
notifs = Notification.objects.filter(user=user)[:5]
for n in notifs:
    status = "غير مقروء" if not n.is_read else "مقروء"
    print(f"{n.id}: {n.title} - {status}")

# إحصائيات
total = Notification.objects.filter(user=user).count()
unread = Notification.objects.filter(user=user, is_read=False).count()
print(f"الإجمالي: {total}, غير المقروءة: {unread}")

# إنشاء إشعار تجريبي
Notification.objects.create(
    user=user,
    title="🧪 إشعار تجريبي",
    message="هذا إشعار تجريبي من Django Shell",
    extra={"type": "test"}
)

# تحديد جميع الإشعارات كمقروءة
Notification.objects.filter(user=user, is_read=False).update(is_read=True)
```

---

## 📊 التحقق من حالة السيرفر

### تحقق من Docker Containers (إذا كنت تستخدم Docker)

```bash
# عرض جميع الـ containers
docker ps

# عرض logs للـ web container
docker logs pharmasky-web

# الدخول إلى container
docker exec -it pharmasky-web bash
```

### تحقق من Nginx

```bash
# حالة Nginx
systemctl status nginx

# عرض logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### تحقق من قاعدة البيانات

```bash
# إذا كنت تستخدم PostgreSQL
sudo -u postgres psql -d pharmasky_db -c "SELECT COUNT(*) FROM notifications_notification;"
```

---

## 🔍 استكشاف الأخطاء

### مشكلة: Connection refused

```bash
# تحقق من تشغيل السيرفر
curl -I http://167.71.40.9

# تحقق من الـ port
netstat -tulpn | grep :80
```

### مشكلة: Authentication failed

```bash
# تحقق من المستخدمين الموجودين
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print([u.username for u in User.objects.all()[:5]])"
```

### مشكلة: لا توجد إشعارات

```bash
# عدد الإشعارات في قاعدة البيانات
python manage.py shell -c "from notifications.models import Notification; print(f'Total: {Notification.objects.count()}')"

# إنشاء بيانات تجريبية
python manage.py create_test_notifications --count 10
```

---

## 📝 أمثلة سريعة

### مثال 1: اختبار كامل بأمر واحد

```bash
# احفظ هذا في ملف test_quick.sh
TOKEN=$(curl -s -X POST "http://167.71.40.9/api/v1/accounts/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"+201234567890","password":"yourpass"}' \
  | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

echo "Token: $TOKEN"

curl -H "Authorization: Token $TOKEN" \
  "http://167.71.40.9/api/v1/notifications/notifications/stats/" \
  | python3 -m json.tool
```

### مثال 2: مراقبة الإشعارات الجديدة

```bash
# سكريبت للتحقق من الإشعارات الجديدة كل 30 ثانية
while true; do
  clear
  echo "=== $(date) ==="
  curl -s -H "Authorization: Token $TOKEN" \
    "http://167.71.40.9/api/v1/notifications/notifications/stats/" \
    | python3 -m json.tool
  sleep 30
done
```

---

## ⚠️ تحذيرات مهمة

### على السيرفر الفعلي (Production):

1. ❗ **لا تنشئ الكثير من البيانات التجريبية**
   - استخدم `--count 10` كحد أقصى
   - احذف البيانات التجريبية بعد الانتهاء

2. ❗ **لا تحذف بيانات حقيقية**
   - تأكد من رقم الإشعار قبل الحذف
   - استخدم Django Shell بحذر

3. ❗ **النسخ الاحتياطي**
   - قبل أي اختبار كبير، خذ نسخة احتياطية
   ```bash
   python manage.py dumpdata notifications > backup_notifications.json
   ```

4. ❗ **السجلات (Logs)**
   - راقب الـ logs أثناء الاختبار
   - تحقق من عدم وجود أخطاء

---

## 📱 اختبار من تطبيق الموبايل/Frontend

إذا كان لديك frontend:

```javascript
// في JavaScript/React/Vue
const API_BASE = 'http://167.71.40.9';
const token = 'your_token';

// جلب الإشعارات
fetch(`${API_BASE}/api/v1/notifications/notifications/`, {
  headers: {
    'Authorization': `Token ${token}`
  }
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## ✅ Checklist للاختبار على السيرفر

- [ ] التحقق من تشغيل السيرفر
- [ ] تسجيل الدخول بنجاح
- [ ] جلب الإحصائيات
- [ ] جلب الإشعارات
- [ ] جلب الإشعارات غير المقروءة
- [ ] تحديد إشعار كمقروء
- [ ] جلب المواضيع
- [ ] الاشتراك في موضوع (إن وجد)
- [ ] التحقق من الـ logs
- [ ] اختبار من Frontend (إن وجد)

---

## 🎯 الخلاصة

**الطريقة الأسرع على السيرفر:**

```bash
cd /opt/pharmasky/
bash test_notifications_server.sh
```

أدخل Username وPassword وسيتم الاختبار تلقائياً!

---

**تم التحضير لـ PharmaSky Production Server 🚀**

