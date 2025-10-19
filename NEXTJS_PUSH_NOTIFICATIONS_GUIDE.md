# 🔔 دليل Push Notifications لـ Next.js - PharmaSky

دليل كامل لإعداد Firebase Cloud Messaging في Next.js للحصول على إشعارات خارج التطبيق (مثل الواتساب).

---

## 📋 المتطلبات

- ✅ Next.js 13+ (App Router أو Pages Router)
- ✅ Firebase Project جاهز
- ✅ السيرفر جاهز (تم ✅)

---

## 🚀 الخطوة 1: تثبيت Firebase في Next.js

```bash
# في مشروع Next.js
npm install firebase
# أو
yarn add firebase
```

---

## 🔥 الخطوة 2: إعداد Firebase Config

### إنشاء ملف `lib/firebase.ts` أو `lib/firebase.js`

```typescript
// lib/firebase.ts
import { initializeApp, getApps } from 'firebase/app';
import { getMessaging, getToken, onMessage, isSupported } from 'firebase/messaging';

// Firebase configuration من Firebase Console
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "pharmasky46.firebaseapp.com",
  projectId: "pharmasky46",
  storageBucket: "pharmasky46.appspot.com",
  messagingSenderId: "XXXXXXXXXXXX",
  appId: "1:XXXXXXXXXXXX:web:XXXXXXXXXXXXXXXXXXXXXXXX"
};

// تهيئة Firebase
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];

// تهيئة Messaging (فقط في المتصفح)
const messaging = typeof window !== 'undefined' ? getMessaging(app) : null;

export { app, messaging };
```

**ملاحظة:** احصل على `firebaseConfig` من:
1. Firebase Console → Project Settings ⚙️
2. Your apps → Web app
3. انسخ الـ Config

---

## 🔔 الخطوة 3: إنشاء Firebase Messaging Service Worker

### إنشاء ملف `public/firebase-messaging-sw.js`

```javascript
// public/firebase-messaging-sw.js
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

// نفس الـ config
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "pharmasky46.firebaseapp.com",
  projectId: "pharmasky46",
  storageBucket: "pharmasky46.appspot.com",
  messagingSenderId: "XXXXXXXXXXXX",
  appId: "1:XXXXXXXXXXXX:web:XXXXXXXXXXXXXXXXXXXXXXXX"
};

firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

// Background notifications
messaging.onBackgroundMessage((payload) => {
  console.log('📩 Background notification received:', payload);
  
  const notificationTitle = payload.notification?.title || 'إشعار جديد';
  const notificationOptions = {
    body: payload.notification?.body || '',
    icon: '/icon-192x192.png',
    badge: '/icon-72x72.png',
    tag: payload.data?.notification_id || 'default',
    data: payload.data,
    requireInteraction: true,
    actions: [
      {
        action: 'open',
        title: 'فتح',
      },
      {
        action: 'close',
        title: 'إغلاق',
      }
    ]
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// معالجة النقر على الإشعار
self.addEventListener('notificationclick', (event) => {
  console.log('📱 Notification clicked:', event);
  
  event.notification.close();
  
  if (event.action === 'open' || !event.action) {
    // فتح التطبيق
    event.waitUntil(
      clients.openWindow(event.notification.data?.url || '/')
    );
  }
});
```

---

## 🎯 الخطوة 4: إنشاء Hook للإشعارات

### إنشاء `hooks/useNotifications.ts`

```typescript
// hooks/useNotifications.ts
import { useEffect, useState } from 'react';
import { messaging } from '@/lib/firebase';
import { getToken, onMessage } from 'firebase/messaging';

interface NotificationPayload {
  title: string;
  body: string;
  data?: any;
}

export const useNotifications = (authToken: string | null) => {
  const [fcmToken, setFcmToken] = useState<string | null>(null);
  const [notification, setNotification] = useState<NotificationPayload | null>(null);
  const [permission, setPermission] = useState<NotificationPermission>('default');

  // طلب الإذن وتسجيل Token
  const requestPermissionAndGetToken = async () => {
    if (!messaging) return;

    try {
      // طلب الإذن
      const perm = await Notification.requestPermission();
      setPermission(perm);

      if (perm === 'granted') {
        console.log('✅ تم منح إذن الإشعارات');

        // الحصول على FCM Token
        const token = await getToken(messaging, {
          vapidKey: 'YOUR_VAPID_KEY_FROM_FIREBASE_CONSOLE' // من Cloud Messaging → Web Push certificates
        });

        console.log('🔑 FCM Token:', token);
        setFcmToken(token);

        // إرسال Token للسيرفر
        if (authToken) {
          await saveFCMTokenToServer(token, authToken);
        }

        return token;
      } else {
        console.log('❌ تم رفض إذن الإشعارات');
      }
    } catch (error) {
      console.error('❌ خطأ في طلب الإذن:', error);
    }
  };

  // حفظ Token في السيرفر
  const saveFCMTokenToServer = async (token: string, authToken: string) => {
    try {
      const response = await fetch('http://167.71.40.9/api/v1/notifications/fcm-token/save/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${authToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fcm_token: token,
          device_type: 'web',
          device_name: `Browser - ${navigator.userAgent.split(' ')[0]}`,
        }),
      });

      if (response.ok) {
        console.log('✅ تم حفظ FCM Token في السيرفر');
      } else {
        console.error('❌ فشل حفظ Token:', await response.text());
      }
    } catch (error) {
      console.error('❌ خطأ في حفظ Token:', error);
    }
  };

  // الاستماع للإشعارات
  useEffect(() => {
    if (!messaging) return;

    const unsubscribe = onMessage(messaging, (payload) => {
      console.log('📩 إشعار جديد:', payload);
      
      const notificationData = {
        title: payload.notification?.title || 'إشعار جديد',
        body: payload.notification?.body || '',
        data: payload.data,
      };

      setNotification(notificationData);

      // عرض إشعار في المتصفح
      if (Notification.permission === 'granted') {
        new Notification(notificationData.title, {
          body: notificationData.body,
          icon: '/icon-192x192.png',
          badge: '/icon-72x72.png',
          data: notificationData.data,
        });
      }
    });

    return () => unsubscribe();
  }, []);

  return {
    fcmToken,
    notification,
    permission,
    requestPermissionAndGetToken,
  };
};
```

---

## 🎨 الخطوة 5: استخدام Hook في Component

### مثال: `components/NotificationSetup.tsx`

```typescript
// components/NotificationSetup.tsx
'use client';

import { useEffect } from 'react';
import { useNotifications } from '@/hooks/useNotifications';
import { Bell, BellOff } from 'lucide-react';
import { toast } from 'sonner'; // أو أي toast library

export default function NotificationSetup({ authToken }: { authToken: string }) {
  const { permission, notification, requestPermissionAndGetToken } = useNotifications(authToken);

  // طلب الإذن عند التحميل
  useEffect(() => {
    if (permission === 'default' && authToken) {
      requestPermissionAndGetToken();
    }
  }, [authToken]);

  // عرض Toast عند وصول إشعار جديد
  useEffect(() => {
    if (notification) {
      toast.success(notification.title, {
        description: notification.body,
        duration: 5000,
      });
    }
  }, [notification]);

  // عرض زر طلب الإذن إذا كان مرفوضاً
  if (permission === 'denied') {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center gap-2">
          <BellOff className="h-5 w-5 text-red-500" />
          <p className="text-red-700 text-sm">
            الإشعارات معطلة. فعّلها من إعدادات المتصفح.
          </p>
        </div>
      </div>
    );
  }

  if (permission === 'default') {
    return (
      <button
        onClick={requestPermissionAndGetToken}
        className="flex items-center gap-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
      >
        <Bell className="h-5 w-5" />
        <span>تفعيل الإشعارات</span>
      </button>
    );
  }

  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-3">
      <div className="flex items-center gap-2">
        <Bell className="h-4 w-4 text-green-500" />
        <p className="text-green-700 text-sm">الإشعارات مفعّلة ✅</p>
      </div>
    </div>
  );
}
```

---

## 📱 الخطوة 6: استخدام في Layout أو Page

### App Router (`app/layout.tsx`):

```typescript
// app/layout.tsx
import NotificationSetup from '@/components/NotificationSetup';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  // احصل على auth token من session/cookies
  const authToken = getAuthToken(); // implement this
  
  return (
    <html lang="ar" dir="rtl">
      <body>
        {authToken && <NotificationSetup authToken={authToken} />}
        {children}
      </body>
    </html>
  );
}
```

### Pages Router (`pages/_app.tsx`):

```typescript
// pages/_app.tsx
import NotificationSetup from '@/components/NotificationSetup';
import { useAuth } from '@/hooks/useAuth'; // your auth hook

export default function App({ Component, pageProps }) {
  const { token } = useAuth();
  
  return (
    <>
      {token && <NotificationSetup authToken={token} />}
      <Component {...pageProps} />
    </>
  );
}
```

---

## 🎯 الخطوة 7: عرض الإشعارات في الـ UI

### Component كامل للإشعارات:

```typescript
// components/NotificationsList.tsx
'use client';

import { useState, useEffect } from 'react';
import { Bell, Check, Trash2 } from 'lucide-react';

interface Notification {
  id: number;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
  extra: any;
}

export default function NotificationsList({ authToken }: { authToken: string }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);

  const API_BASE = 'http://167.71.40.9/api/v1';

  // جلب الإشعارات
  const fetchNotifications = async () => {
    try {
      const response = await fetch(`${API_BASE}/notifications/notifications/`, {
        headers: {
          'Authorization': `Token ${authToken}`,
        },
      });
      
      const data = await response.json();
      setNotifications(data.results || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching notifications:', error);
      setLoading(false);
    }
  };

  // جلب الإحصائيات
  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/notifications/notifications/stats/`, {
        headers: {
          'Authorization': `Token ${authToken}`,
        },
      });
      
      const data = await response.json();
      setUnreadCount(data.data?.unread || 0);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  // تحديد كمقروء
  const markAsRead = async (id: number) => {
    try {
      await fetch(`${API_BASE}/notifications/notifications/${id}/update/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Token ${authToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_read: true }),
      });
      
      fetchNotifications();
      fetchStats();
    } catch (error) {
      console.error('Error marking as read:', error);
    }
  };

  // تحديد الكل كمقروء
  const markAllAsRead = async () => {
    try {
      await fetch(`${API_BASE}/notifications/notifications/mark-all-read/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${authToken}`,
        },
      });
      
      fetchNotifications();
      fetchStats();
    } catch (error) {
      console.error('Error:', error);
    }
  };

  // حذف إشعار
  const deleteNotification = async (id: number) => {
    try {
      await fetch(`${API_BASE}/notifications/notifications/${id}/delete/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Token ${authToken}`,
        },
      });
      
      fetchNotifications();
      fetchStats();
    } catch (error) {
      console.error('Error deleting:', error);
    }
  };

  useEffect(() => {
    fetchNotifications();
    fetchStats();

    // تحديث كل 30 ثانية
    const interval = setInterval(() => {
      fetchStats();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="p-4">جاري التحميل...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Bell className="h-6 w-6" />
          <h1 className="text-2xl font-bold">الإشعارات</h1>
          {unreadCount > 0 && (
            <span className="bg-red-500 text-white px-2 py-1 rounded-full text-sm">
              {unreadCount}
            </span>
          )}
        </div>
        
        {unreadCount > 0 && (
          <button
            onClick={markAllAsRead}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            تحديد الكل كمقروء
          </button>
        )}
      </div>

      {/* Notifications List */}
      <div className="space-y-3">
        {notifications.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            لا توجد إشعارات
          </div>
        ) : (
          notifications.map((notif) => (
            <div
              key={notif.id}
              className={`p-4 rounded-lg border ${
                notif.is_read
                  ? 'bg-white border-gray-200'
                  : 'bg-blue-50 border-blue-200'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg mb-1">
                    {notif.title}
                  </h3>
                  <p className="text-gray-600 text-sm mb-2">
                    {notif.message}
                  </p>
                  <span className="text-xs text-gray-400">
                    {formatDate(notif.created_at)}
                  </span>
                </div>
                
                <div className="flex items-center gap-2">
                  {!notif.is_read && (
                    <button
                      onClick={() => markAsRead(notif.id)}
                      className="p-2 hover:bg-gray-100 rounded"
                      title="تحديد كمقروء"
                    >
                      <Check className="h-4 w-4 text-green-600" />
                    </button>
                  )}
                  
                  <button
                    onClick={() => deleteNotification(notif.id)}
                    className="p-2 hover:bg-gray-100 rounded"
                    title="حذف"
                  >
                    <Trash2 className="h-4 w-4 text-red-600" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// Helper function
function formatDate(dateString: string) {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return 'الآن';
  if (minutes < 60) return `منذ ${minutes} دقيقة`;
  if (hours < 24) return `منذ ${hours} ساعة`;
  return `منذ ${days} يوم`;
}
```

---

## 🔔 الخطوة 8: Notification Badge في Navbar

```typescript
// components/NotificationBadge.tsx
'use client';

import { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';
import Link from 'next/link';

export default function NotificationBadge({ authToken }: { authToken: string }) {
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const fetchUnreadCount = async () => {
      try {
        const response = await fetch(
          'http://167.71.40.9/api/v1/notifications/notifications/stats/',
          {
            headers: { 'Authorization': `Token ${authToken}` }
          }
        );
        
        const data = await response.json();
        setUnreadCount(data.data?.unread || 0);
      } catch (error) {
        console.error('Error:', error);
      }
    };

    fetchUnreadCount();
    
    // تحديث كل 30 ثانية
    const interval = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(interval);
  }, [authToken]);

  return (
    <Link href="/notifications" className="relative">
      <Bell className="h-6 w-6 text-gray-700 hover:text-gray-900" />
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
          {unreadCount > 9 ? '9+' : unreadCount}
        </span>
      )}
    </Link>
  );
}
```

---

## ⚙️ الخطوة 9: Environment Variables في Next.js

### إنشاء `.env.local`:

```bash
# .env.local
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=pharmasky46.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=pharmasky46
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=pharmasky46.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=XXXXXXXXXXXX
NEXT_PUBLIC_FIREBASE_APP_ID=1:XXXXXXXXXXXX:web:XXXXXXXXXXXXXXXXXXXXXXXX
NEXT_PUBLIC_FIREBASE_VAPID_KEY=YOUR_VAPID_KEY_HERE

NEXT_PUBLIC_API_URL=http://167.71.40.9/api/v1
```

### استخدام في firebase.ts:

```typescript
// lib/firebase.ts
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};
```

---

## 🧪 الخطوة 10: اختبار كامل

### صفحة اختبار: `app/test-notifications/page.tsx`

```typescript
// app/test-notifications/page.tsx
'use client';

import { useState } from 'react';
import { useNotifications } from '@/hooks/useNotifications';

export default function TestNotificationsPage() {
  const { fcmToken, permission, requestPermissionAndGetToken } = useNotifications('your_auth_token');
  const [message, setMessage] = useState('');

  const testPushNotification = () => {
    // هذا للاختبار فقط - في الحقيقة الإشعارات تأتي من السيرفر
    if (Notification.permission === 'granted') {
      new Notification('🧪 اختبار', {
        body: 'إشعار تجريبي من Next.js',
        icon: '/icon-192x192.png',
      });
      setMessage('✅ تم إرسال إشعار تجريبي');
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">اختبار Push Notifications</h1>
      
      <div className="space-y-4">
        {/* الحالة */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h2 className="font-semibold mb-2">الحالة:</h2>
          <p>إذن الإشعارات: <strong>{permission}</strong></p>
          {fcmToken && (
            <p className="text-xs text-gray-600 mt-2">
              Token: {fcmToken.substring(0, 30)}...
            </p>
          )}
        </div>

        {/* أزرار */}
        <div className="space-y-2">
          {permission !== 'granted' && (
            <button
              onClick={requestPermissionAndGetToken}
              className="w-full bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600"
            >
              طلب إذن الإشعارات
            </button>
          )}
          
          {permission === 'granted' && (
            <button
              onClick={testPushNotification}
              className="w-full bg-green-500 text-white py-3 rounded-lg hover:bg-green-600"
            >
              اختبار إشعار محلي
            </button>
          )}
        </div>

        {/* رسالة */}
        {message && (
          <div className="bg-green-50 border border-green-200 p-3 rounded-lg">
            {message}
          </div>
        )}

        {/* التعليمات */}
        <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">📋 التعليمات:</h3>
          <ol className="list-decimal list-inside space-y-1 text-sm">
            <li>اضغط "طلب إذن الإشعارات"</li>
            <li>اسمح للمتصفح بإرسال الإشعارات</li>
            <li>سيتم تسجيل FCM Token تلقائياً</li>
            <li>الإشعارات ستصل من السيرفر تلقائياً</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
```

---

## 📊 الخطوة 11: الحصول على VAPID Key من Firebase

1. اذهب إلى: https://console.firebase.google.com/
2. اختر المشروع **pharmasky46**
3. Project Settings ⚙️ → Cloud Messaging
4. Web Push certificates → Generate key pair
5. انسخ الـ **Key pair** (VAPID key)

---

## 🎯 ملخص الملفات المطلوبة:

```
next-app/
├── public/
│   └── firebase-messaging-sw.js  ← Service Worker
├── lib/
│   └── firebase.ts               ← Firebase config
├── hooks/
│   └── useNotifications.ts       ← Hook للإشعارات
├── components/
│   ├── NotificationSetup.tsx     ← Setup component
│   ├── NotificationsList.tsx     ← عرض الإشعارات
│   └── NotificationBadge.tsx     ← Badge في Navbar
├── app/
│   ├── layout.tsx                ← Root layout
│   └── notifications/
│       └── page.tsx              ← صفحة الإشعارات
└── .env.local                    ← Environment variables
```

---

## ✅ Checklist للتطبيق:

- [ ] تثبيت Firebase (`npm install firebase`)
- [ ] إنشاء `firebase.ts` config
- [ ] إنشاء `firebase-messaging-sw.js` في public
- [ ] الحصول على VAPID Key من Firebase Console
- [ ] إنشاء `useNotifications` hook
- [ ] إنشاء `NotificationSetup` component
- [ ] إضافة في Layout
- [ ] طلب الإذن من المستخدم
- [ ] تسجيل FCM Token في السيرفر
- [ ] اختبار استقبال الإشعارات

---

## 🧪 كيف تختبر؟

### من السيرفر (مؤقتاً حتى تعمل التطبيق):

```bash
# على السيرفر
docker exec -i pharmasky_web python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()
user = User.objects.filter(username='+201090572414').first()

if user:
    # إنشاء إشعار - سيظهر في Next.js تلقائياً
    notif = Notification.objects.create(
        user=user,
        title='🎉 مرحباً من Next.js!',
        message='هذا إشعار تجريبي يجب أن تراه في التطبيق',
        extra={'type': 'test_nextjs'}
    )
    print(f'✅ تم إنشاء إشعار #{notif.id}')
    print('📱 افتح Next.js وسترى الإشعار!')
EOF
```

---

## 📖 مصادر إضافية:

- [Firebase Web Setup](https://firebase.google.com/docs/web/setup)
- [FCM for Web](https://firebase.google.com/docs/cloud-messaging/js/client)
- [Next.js with Firebase](https://firebase.google.com/codelabs/firebase-nextjs)

---

## 💡 نصائح مهمة:

1. **HTTPS مطلوب** في Production للـ Service Workers
2. **Icons** يجب أن تكون في `/public`
3. **VAPID Key** ضروري للـ web push
4. **Test في localhost** أولاً قبل Deploy

---

**كل شيء جاهز من ناحية السيرفر! ✅**
**الآن فقط طبق الخطوات في Next.js! 🚀**

