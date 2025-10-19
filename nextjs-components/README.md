# 🔔 ملفات Next.js جاهزة - Push Notifications

جميع الملفات جاهزة للنسخ المباشر في مشروع Next.js!

---

## 📁 الملفات المتوفرة:

```
nextjs-components/
├── lib/
│   └── firebase.ts                    ← إعداد Firebase + دوال مساعدة
├── hooks/
│   └── useNotifications.ts            ← Hook للإشعارات
├── components/
│   ├── NotificationProvider.tsx       ← Provider للـ Layout
│   ├── NotificationsList.tsx          ← UI كامل للإشعارات
│   └── NotificationBadge.tsx          ← (سيتم إنشاؤه)
├── public/
│   └── firebase-messaging-sw.js       ← Service Worker
├── ENV_EXAMPLE.txt                    ← مثال للـ environment variables
└── README.md                          ← هذا الملف
```

---

## ⚡ البدء السريع (10 دقائق)

### 1. تثبيت Dependencies

```bash
cd your-nextjs-project
npm install firebase sonner date-fns lucide-react
```

### 2. نسخ الملفات

```bash
# انسخ جميع الملفات من nextjs-components/ إلى مشروعك
cp -r nextjs-components/lib your-project/
cp -r nextjs-components/hooks your-project/
cp -r nextjs-components/components your-project/
cp nextjs-components/public/firebase-messaging-sw.js your-project/public/
```

### 3. إنشاء .env.local

```bash
# انسخ من ENV_EXAMPLE.txt وعدّل القيم
cp nextjs-components/ENV_EXAMPLE.txt your-project/.env.local
```

ثم عدّل القيم بالقيم الحقيقية من Firebase Console.

### 4. تحديث firebase.ts وfirebase-messaging-sw.js

عدّل الـ config في الملفين ليطابق مشروعك.

### 5. إضافة في Layout

```typescript
// app/layout.tsx
import NotificationProvider from '@/components/NotificationProvider';
import { Toaster } from 'sonner';

export default function RootLayout({ children }) {
  return (
    <html lang="ar" dir="rtl">
      <body>
        <NotificationProvider authToken="your-auth-token">
          {children}
        </NotificationProvider>
        <Toaster position="top-center" richColors />
      </body>
    </html>
  );
}
```

---

## 🎯 الاستخدام

### عرض قائمة الإشعارات:

```typescript
import NotificationsList from '@/components/NotificationsList';

export default function NotificationsPage() {
  return <NotificationsList authToken="user-token" />;
}
```

### استخدام Hook مباشرة:

```typescript
'use client';
import { useNotifications } from '@/hooks/useNotifications';

export default function MyComponent() {
  const { permission, fcmToken, requestPermission } = useNotifications({
    authToken: 'user-token',
    autoRequest: true,
  });

  return (
    <div>
      <p>الإذن: {permission}</p>
      {permission === 'default' && (
        <button onClick={requestPermission}>
          تفعيل الإشعارات
        </button>
      )}
    </div>
  );
}
```

---

## 🔥 الحصول على Firebase Credentials

### من Firebase Console:

1. **apiKey, authDomain, etc.:**
   - Project Settings → Your apps → Web app
   - انسخ جميع القيم

2. **VAPID Key:**
   - Project Settings → Cloud Messaging
   - Web Push certificates → Generate key pair
   - انسخ الـ Key

---

## 📊 APIs المستخدمة

جميع الملفات تستخدم APIs التالية من السيرفر:

| Endpoint | Method | الاستخدام |
|----------|--------|-----------|
| `/notifications/notifications/` | GET | جلب الإشعارات |
| `/notifications/notifications/unread/` | GET | غير المقروءة |
| `/notifications/notifications/stats/` | GET | الإحصائيات |
| `/notifications/notifications/{id}/update/` | PATCH | تحديد كمقروء |
| `/notifications/notifications/mark-all-read/` | POST | تحديد الكل |
| `/notifications/notifications/{id}/delete/` | DELETE | حذف |
| `/notifications/fcm-token/save/` | POST | تسجيل FCM Token ⭐ |

**السيرفر جاهز ✅ - كل الـ APIs تعمل!**

---

## 🎨 تخصيص

### تغيير الألوان:

في `NotificationsList.tsx`:
```typescript
// غيّر الألوان حسب theme تطبيقك
const getPriorityColor = (type: string) => {
  // customize colors here
};
```

### تغيير الأيقونات:

في `firebase-messaging-sw.js`:
```javascript
icon: '/your-custom-icon.png',
badge: '/your-custom-badge.png',
```

---

## ✅ Checklist

- [ ] تثبيت Dependencies
- [ ] نسخ جميع الملفات
- [ ] إنشاء .env.local بالقيم الصحيحة
- [ ] تحديث Firebase config
- [ ] إضافة NotificationProvider في Layout
- [ ] إضافة Toaster من sonner
- [ ] اختبار في localhost
- [ ] اختبار الإشعارات من السيرفر
- [ ] Deploy وتجربة على HTTPS

---

## 🚀 الخطوة التالية

**بعد نسخ الملفات:**

1. شغل `npm run dev`
2. افتح `http://localhost:3000`
3. اسمح بالإشعارات
4. من السيرفر، أنشئ إشعار
5. شاهد الإشعار يظهر! 🎉

---

**كل شيء جاهز! نسخ والصق فقط! 🎊**

