# 🚀 دليل سريع: Push Notifications في Next.js

دليل مختصر لإعداد الإشعارات الفورية في Next.js (5-10 دقائق)

---

## ⚡ البدء السريع (3 خطوات فقط!)

### 1️⃣ تثبيت Firebase

```bash
npm install firebase sonner date-fns
# sonner: للـ toast notifications
# date-fns: لتنسيق التواريخ
```

---

### 2️⃣ نسخ الملفات الجاهزة

انسخ هذه الملفات من `nextjs-components/` إلى مشروعك:

```
✅ lib/firebase.ts                    → نسخ كما هو
✅ hooks/useNotifications.ts          → نسخ كما هو
✅ components/NotificationProvider.tsx → نسخ كما هو
✅ components/NotificationsList.tsx    → نسخ كما هو
✅ public/firebase-messaging-sw.js    → نسخ كما هو
```

---

### 3️⃣ إضافة في Layout

```typescript
// app/layout.tsx
import NotificationProvider from '@/components/NotificationProvider';
import { Toaster } from 'sonner';

export default function RootLayout({ children }) {
  const authToken = getAuthToken(); // احصل على token من session
  
  return (
    <html lang="ar" dir="rtl">
      <body>
        <NotificationProvider authToken={authToken}>
          {children}
        </NotificationProvider>
        <Toaster position="top-center" richColors />
      </body>
    </html>
  );
}
```

---

## 🔥 الحصول على Firebase Config

### الخطوة 1: Firebase Console

1. اذهب إلى: https://console.firebase.google.com/
2. افتح مشروع **pharmasky46** (أو أنشئ مشروع جديد)

### الخطوة 2: Web App Config

1. Project Settings ⚙️ → Your apps
2. اضغط على Web (</>) icon
3. انسخ الـ Config:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "pharmasky46.firebaseapp.com",
  projectId: "pharmasky46",
  // ... الخ
};
```

### الخطوة 3: VAPID Key

1. Project Settings ⚙️ → Cloud Messaging
2. Web Push certificates → Generate key pair
3. انسخ الـ Key

---

## ⚙️ Environment Variables

### إنشاء `.env.local`:

```bash
# .env.local
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyCbmKWUqVmKqZGq4UhEEoZ8RXqnqfnPqkE
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=pharmasky46.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=pharmasky46
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=pharmasky46.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=104845058540
NEXT_PUBLIC_FIREBASE_APP_ID=1:104845058540:web:xxxxx
NEXT_PUBLIC_FIREBASE_VAPID_KEY=YOUR_VAPID_KEY_HERE

NEXT_PUBLIC_API_URL=http://167.71.40.9/api/v1
```

**ملاحظة:** عدّل القيم حسب مشروعك!

---

## 📱 استخدام في الصفحات

### صفحة الإشعارات: `app/notifications/page.tsx`

```typescript
// app/notifications/page.tsx
import NotificationsList from '@/components/NotificationsList';
import { getAuthToken } from '@/lib/auth'; // your auth helper

export default async function NotificationsPage() {
  const authToken = await getAuthToken();
  
  if (!authToken) {
    return <div>يجب تسجيل الدخول</div>;
  }

  return <NotificationsList authToken={authToken} />;
}
```

### Notification Badge في Navbar:

```typescript
// components/Navbar.tsx
'use client';

import { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';
import Link from 'next/link';

export default function Navbar({ authToken }: { authToken: string }) {
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const fetchUnread = async () => {
      const res = await fetch('http://167.71.40.9/api/v1/notifications/notifications/stats/', {
        headers: { 'Authorization': `Token ${authToken}` }
      });
      const data = await res.json();
      setUnreadCount(data.data?.unread || 0);
    };

    fetchUnread();
    const interval = setInterval(fetchUnread, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <h1 className="text-xl font-bold">PharmaSky</h1>
        
        <Link href="/notifications" className="relative">
          <Bell className="h-6 w-6" />
          {unreadCount > 0 && (
            <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
              {unreadCount}
            </span>
          )}
        </Link>
      </div>
    </nav>
  );
}
```

---

## 🧪 اختبار

### 1. في المتصفح:

1. شغل Next.js: `npm run dev`
2. افتح: `http://localhost:3000`
3. اسمح بالإشعارات
4. تحقق من Console: يجب أن ترى FCM Token

### 2. من السيرفر (إرسال إشعار تجريبي):

```bash
# على السيرفر
docker exec -i pharmasky_web python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()
user = User.objects.filter(username='+201090572414').first()

if user:
    notif = Notification.objects.create(
        user=user,
        title='🎉 مرحباً من Next.js!',
        message='هذا إشعار تجريبي من السيرفر',
        extra={'type': 'test_nextjs'}
    )
    print(f'✅ تم إنشاء إشعار #{notif.id}')
    print('📱 يجب أن يظهر في Next.js الآن!')
EOF
```

---

## 🎯 الخلاصة

### ✅ ما تم توفيره:

1. ✅ `firebase.ts` - إعداد Firebase
2. ✅ `useNotifications.ts` - Hook كامل
3. ✅ `NotificationProvider.tsx` - Provider للتطبيق
4. ✅ `NotificationsList.tsx` - UI كامل
5. ✅ `firebase-messaging-sw.js` - Service Worker
6. ✅ التوثيق الكامل

### 📋 ما تحتاجه:

1. ✅ Firebase Config (من Firebase Console)
2. ✅ VAPID Key (من Firebase Console)
3. ✅ Auth Token (من نظام Login)

---

## 💡 نصائح:

1. **اختبر في localhost أولاً** (http://localhost:3000)
2. **Service Worker يحتاج HTTPS** في production
3. **Icons** ضع ملفات PNG في `/public`
4. **استخدم Vercel/Netlify** للـ deployment السهل

---

## 🆘 استكشاف الأخطاء

### خطأ: Service Worker لا يعمل

```bash
# تحقق من:
1. الملف موجود في: public/firebase-messaging-sw.js
2. المتصفح يدعم Service Workers (Chrome/Firefox)
3. في localhost أو HTTPS
```

### خطأ: لا يطلب الإذن

```javascript
// في Console
console.log('Permission:', Notification.permission);
// يجب أن يكون: "default" أو "granted" أو "denied"
```

### خطأ: Token لا يُحفظ في السيرفر

```javascript
// تحقق من:
1. authToken صحيح
2. API URL صحيح
3. CORS معداً في السيرفر (موجود ✅)
```

---

## 📚 ملفات مساعدة:

- `NEXTJS_PUSH_NOTIFICATIONS_GUIDE.md` - دليل مفصل
- `notifications/PHARMACY_FRONTEND_API.md` - توثيق APIs
- `notifications/FCM_SETUP_GUIDE.md` - إعداد Firebase

---

**الملفات جاهزة للنسخ في: `nextjs-components/` 📂**

**ابدأ الآن! 🚀**

