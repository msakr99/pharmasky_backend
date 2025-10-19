# 🚀 ابدأ الآن مع Next.js

**نظام الإشعارات جاهز على السيرفر! ✅**  
**الآن فقط اربطه بـ Next.js في 3 خطوات!**

---

## ⚡ الخطوات (10 دقائق):

### 1️⃣ ثبّت Firebase

```bash
cd your-nextjs-project
npm install firebase sonner date-fns lucide-react
```

---

### 2️⃣ انسخ الملفات الجاهزة

من المجلد: **`nextjs-components/`** في هذا المشروع

انسخ إلى مشروع Next.js:

```
✅ lib/firebase.ts                    → your-project/lib/
✅ hooks/useNotifications.ts          → your-project/hooks/
✅ components/NotificationProvider.tsx → your-project/components/
✅ components/NotificationsList.tsx    → your-project/components/
✅ components/NotificationBadge.tsx    → your-project/components/
✅ public/firebase-messaging-sw.js    → your-project/public/
```

---

### 3️⃣ أضف في Layout

```typescript
// app/layout.tsx
import NotificationProvider from '@/components/NotificationProvider';
import { Toaster } from 'sonner';

export default function RootLayout({ children }) {
  const authToken = 'your-auth-token'; // من session/cookies
  
  return (
    <html lang="ar" dir="rtl">
      <body>
        <NotificationProvider authToken={authToken}>
          {children}
        </NotificationProvider>
        <Toaster position="top-center" />
      </body>
    </html>
  );
}
```

---

## 🔥 الحصول على Firebase Keys

### سريع جداً (3 دقائق):

1. **اذهب:** https://console.firebase.google.com/
2. **افتح المشروع:** pharmasky46
3. **اذهب:** Project Settings ⚙️
4. **انسخ Config** من Your apps → Web
5. **احصل على VAPID:** Cloud Messaging → Web Push certificates

---

## ⚙️ Environment Variables

أنشئ `.env.local` في مشروع Next.js:

```bash
NEXT_PUBLIC_FIREBASE_API_KEY=من_Firebase_Console
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=pharmasky46.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=pharmasky46
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=pharmasky46.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=من_Firebase_Console
NEXT_PUBLIC_FIREBASE_APP_ID=من_Firebase_Console
NEXT_PUBLIC_FIREBASE_VAPID_KEY=من_Firebase_Console

NEXT_PUBLIC_API_URL=http://167.71.40.9/api/v1
```

**انظر:** `nextjs-components/ENV_EXAMPLE.txt` للمثال الكامل

---

## ✅ هل نجح؟

### في المتصفح Console يجب أن ترى:

```
✅ Firebase Admin initialized successfully
✅ تم منح إذن الإشعارات
🔑 FCM Token: eLxBu5Z8QoWx...
✅ تم حفظ FCM Token في السيرفر
```

### اختبر من السيرفر:

```bash
# أنشئ إشعار
docker exec -i pharmasky_web python manage.py shell << 'EOF'
from notifications.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.filter(username='+201090572414').first()

Notification.objects.create(
    user=user,
    title='🎉 مرحباً!',
    message='هذا أول إشعار من Next.js!',
    extra={'type': 'test'}
)
print('✅ تم! تحقق من Next.js')
EOF
```

**يجب أن يظهر الإشعار في Next.js فوراً! 🎊**

---

## 📚 للمزيد من التفاصيل:

- **`NEXTJS_SETUP_QUICK_START.md`** - دليل كامل خطوة بخطوة
- **`nextjs-components/README.md`** - شرح كل ملف
- **`COMPLETE_NOTIFICATIONS_SUMMARY.md`** - ملخص شامل لكل شيء

---

## 🎯 المسار السريع:

```
1. npm install firebase sonner date-fns lucide-react
2. انسخ الملفات من nextjs-components/
3. أضف NotificationProvider في Layout
4. احصل على Firebase keys
5. أنشئ .env.local
6. npm run dev
7. اختبر!
```

**كل شيء موثق وجاهز! 🚀**

---

**السيرفر جاهز ✅ | الملفات جاهزة ✅ | ابدأ الآن! 🎊**

