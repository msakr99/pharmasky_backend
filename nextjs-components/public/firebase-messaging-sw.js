// public/firebase-messaging-sw.js
// Firebase Cloud Messaging Service Worker

importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

// Firebase configuration - نفس الـ config من firebase.ts
const firebaseConfig = {
  apiKey: "AIzaSyCbmKWUqVmKqZGq4UhEEoZ8RXqnqfnPqkE",
  authDomain: "pharmasky46.firebaseapp.com",
  projectId: "pharmasky46",
  storageBucket: "pharmasky46.appspot.com",
  messagingSenderId: "104845058540",
  appId: "1:104845058540:web:xxxxx"
};

firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

// معالجة الإشعارات في الخلفية (Background)
messaging.onBackgroundMessage((payload) => {
  console.log('📩 [Background] إشعار جديد:', payload);
  
  const notificationTitle = payload.notification?.title || 'PharmaSky';
  const notificationOptions = {
    body: payload.notification?.body || 'إشعار جديد',
    icon: '/icon-192x192.png',
    badge: '/icon-72x72.png',
    tag: payload.data?.notification_id || 'pharmasky-notification',
    data: payload.data,
    requireInteraction: true,
    vibrate: [200, 100, 200], // اهتزاز
    actions: [
      {
        action: 'open',
        title: 'فتح',
        icon: '/icon-check.png'
      },
      {
        action: 'close',
        title: 'إغلاق',
        icon: '/icon-close.png'
      }
    ]
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// معالجة النقر على الإشعار
self.addEventListener('notificationclick', (event) => {
  console.log('📱 تم النقر على الإشعار:', event);
  
  event.notification.close();
  
  if (event.action === 'open' || !event.action) {
    // حدد الصفحة المناسبة حسب نوع الإشعار
    const urlToOpen = getUrlFromNotification(event.notification.data);
    
    event.waitUntil(
      clients.matchAll({ type: 'window', includeUncontrolled: true })
        .then((clientList) => {
          // إذا كان التطبيق مفتوح، استخدمه
          for (const client of clientList) {
            if (client.url === urlToOpen && 'focus' in client) {
              return client.focus();
            }
          }
          // وإلا افتح نافذة جديدة
          if (clients.openWindow) {
            return clients.openWindow(urlToOpen);
          }
        })
    );
  }
});

// دالة مساعدة لتحديد الـ URL حسب نوع الإشعار
function getUrlFromNotification(data) {
  const baseUrl = self.location.origin;
  const type = data?.type;
  
  switch (type) {
    case 'sale_invoice':
    case 'invoice_status_update':
      return `${baseUrl}/orders/${data?.invoice_id || ''}`;
    case 'sale_payment':
      return `${baseUrl}/payments`;
    case 'wishlist_product_available':
      return `${baseUrl}/products/${data?.product_id || ''}`;
    case 'payment_due_reminder':
    case 'payment_overdue':
      return `${baseUrl}/payments/due`;
    default:
      return `${baseUrl}/notifications`;
  }
}

