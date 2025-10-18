# 🏪 Store Frontend API Guide

دليل شامل لاستخدام API الإشعارات من Frontend للمخازن.

---

## 🔐 Authentication

جميع الطلبات تحتاج Store token:

```javascript
headers: {
  'Authorization': 'Token STORE_AUTH_TOKEN',
  'Content-Type': 'application/json'
}
```

---

## 📋 جدول المحتويات

1. [جلب الإشعارات](#1-جلب-الإشعارات)
2. [الإشعارات غير المقروءة](#2-الإشعارات-غير-المقروءة)
3. [إحصائيات الإشعارات](#3-إحصائيات-الإشعارات)
4. [تحديد كمقروء/حذف](#4-تحديد-كمقروءحذف)
5. [حالة النظام](#5-حالة-النظام)

---

## 1. جلب الإشعارات

### GET `/notifications/notifications/`

جلب قائمة إشعارات المخزن.

```typescript
const fetchNotifications = async (page = 1) => {
  const response = await fetch(
    `http://167.71.40.9/notifications/notifications/?page=${page}`,
    {
      headers: {
        'Authorization': `Token ${storeToken}`,
      }
    }
  );
  
  return await response.json();
};
```

---

## 2. الإشعارات غير المقروءة

### GET `/notifications/notifications/unread/`

```typescript
const fetchUnreadNotifications = async () => {
  const response = await fetch(
    'http://167.71.40.9/notifications/notifications/unread/',
    {
      headers: {
        'Authorization': `Token ${storeToken}`,
      }
    }
  );
  
  const data = await response.json();
  return data.results;
};
```

---

## 3. إحصائيات الإشعارات

### GET `/notifications/notifications/stats/`

```typescript
const fetchStats = async () => {
  const response = await fetch(
    'http://167.71.40.9/notifications/notifications/stats/',
    {
      headers: {
        'Authorization': `Token ${storeToken}`,
      }
    }
  );
  
  return await response.json();
};
```

---

## 4. تحديد كمقروء/حذف

### PATCH - تحديد كمقروء

```typescript
const markAsRead = async (notificationId: number) => {
  await fetch(
    `http://167.71.40.9/notifications/notifications/${notificationId}/update/`,
    {
      method: 'PATCH',
      headers: {
        'Authorization': `Token ${storeToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ is_read: true })
    }
  );
};
```

### POST - تحديد الكل كمقروء

```typescript
const markAllAsRead = async () => {
  await fetch(
    'http://167.71.40.9/notifications/notifications/mark-all-read/',
    {
      method: 'POST',
      headers: {
        'Authorization': `Token ${storeToken}`,
      }
    }
  );
};
```

### DELETE - حذف إشعار

```typescript
const deleteNotification = async (notificationId: number) => {
  await fetch(
    `http://167.71.40.9/notifications/notifications/${notificationId}/delete/`,
    {
      method: 'DELETE',
      headers: {
        'Authorization': `Token ${storeToken}`,
      }
    }
  );
};
```

---

## 5. حالة النظام

### GET `/core/shifts/current/`

```typescript
const checkSystemStatus = async () => {
  const response = await fetch(
    'http://167.71.40.9/core/shifts/current/',
    {
      headers: {
        'Authorization': `Token ${storeToken}`,
      }
    }
  );
  
  return await response.json();
};
```

---

## 📊 أنواع الإشعارات للمخزن

| النوع | `extra.type` | الوصف | الأهمية |
|------|--------------|-------|---------|
| 📦 فاتورة شراء | `purchase_invoice` | فاتورة شراء جديدة | عادي |
| 🔔 تحديث | `invoice_status_update` | تغيير حالة | عادي |
| 💰 دفعة شراء | `purchase_payment` | دفعة جديدة | مهم |
| ↩️ مرتجع شراء | `purchase_return` | مرتجع جديد | مهم |
| ✅/❌ حالة مرتجع | `return_status_update` | تحديث المرتجع | عادي |

---

## 📱 React Components للمخزن

### 1. Store Notifications Component

```tsx
// components/store/StoreNotifications.tsx

'use client';

import React, { useState, useEffect } from 'react';
import type { Notification } from '@/types/notifications';

interface StoreNotificationsProps {
  token: string;
}

export const StoreNotifications: React.FC<StoreNotificationsProps> = ({ token }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [stats, setStats] = useState({ total: 0, unread: 0, read: 0 });
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  
  const API_BASE = 'http://167.71.40.9';
  
  const fetchNotifications = async () => {
    const url = filter === 'unread'
      ? `${API_BASE}/notifications/notifications/unread/`
      : `${API_BASE}/notifications/notifications/`;
    
    const response = await fetch(url, {
      headers: { 'Authorization': `Token ${token}` }
    });
    
    const data = await response.json();
    setNotifications(data.results);
  };
  
  const fetchStats = async () => {
    const response = await fetch(
      `${API_BASE}/notifications/notifications/stats/`,
      {
        headers: { 'Authorization': `Token ${token}` }
      }
    );
    const data = await response.json();
    setStats(data.data);
  };
  
  useEffect(() => {
    fetchNotifications();
    fetchStats();
    
    // Refresh كل 30 ثانية
    const interval = setInterval(() => {
      fetchNotifications();
      fetchStats();
    }, 30000);
    
    return () => clearInterval(interval);
  }, [filter]);
  
  const markAsRead = async (id: number) => {
    await fetch(
      `${API_BASE}/notifications/notifications/${id}/update/`,
      {
        method: 'PATCH',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_read: true })
      }
    );
    
    fetchNotifications();
    fetchStats();
  };
  
  const getNotificationIcon = (type: string) => {
    const icons: Record<string, string> = {
      'purchase_invoice': '📦',
      'invoice_status_update': '🔔',
      'purchase_payment': '💰',
      'purchase_return': '↩️',
      'return_status_update': '🔄',
    };
    return icons[type] || '📋';
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">📬 الإشعارات</h1>
      
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-3xl font-bold">{stats.total}</p>
          <p className="text-sm text-gray-600">الإجمالي</p>
        </div>
        <div className="bg-blue-50 p-4 rounded-lg shadow">
          <p className="text-3xl font-bold text-blue-600">{stats.unread}</p>
          <p className="text-sm text-gray-600">غير مقروء</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-3xl font-bold">{stats.read}</p>
          <p className="text-sm text-gray-600">مقروء</p>
        </div>
      </div>
      
      {/* Filters */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded ${
            filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200'
          }`}
        >
          الكل ({stats.total})
        </button>
        <button
          onClick={() => setFilter('unread')}
          className={`px-4 py-2 rounded ${
            filter === 'unread' ? 'bg-blue-600 text-white' : 'bg-gray-200'
          }`}
        >
          غير مقروء ({stats.unread})
        </button>
      </div>
      
      {/* Notifications List */}
      <div className="space-y-3">
        {notifications.map(notif => (
          <div
            key={notif.id}
            className={`flex gap-3 p-4 rounded-lg ${
              notif.is_read ? 'bg-white' : 'bg-blue-50 border-l-4 border-l-blue-500'
            } shadow hover:shadow-md transition-shadow`}
          >
            <div className="text-2xl">
              {getNotificationIcon(notif.extra.type)}
            </div>
            <div className="flex-1">
              <h3 className="font-semibold">{notif.title}</h3>
              <p className="text-sm text-gray-600 mt-1">{notif.message}</p>
              <span className="text-xs text-gray-400 mt-2 block">
                {formatTimeAgo(notif.created_at)}
              </span>
            </div>
            {!notif.is_read && (
              <button
                onClick={() => markAsRead(notif.id)}
                className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
              >
                ✓
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (seconds < 60) return 'الآن';
  if (seconds < 3600) return `منذ ${Math.floor(seconds / 60)} دقيقة`;
  if (seconds < 86400) return `منذ ${Math.floor(seconds / 3600)} ساعة`;
  return `منذ ${Math.floor(seconds / 86400)} يوم`;
}
```

---

### 2. Notification Badge

```tsx
// components/store/NotificationBadge.tsx

'use client';

import React, { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';

export const StoreNotificationBadge: React.FC<{token: string}> = ({ token }) => {
  const [unreadCount, setUnreadCount] = useState(0);
  
  useEffect(() => {
    const fetchCount = async () => {
      try {
        const response = await fetch(
          'http://167.71.40.9/notifications/notifications/stats/',
          {
            headers: { 'Authorization': `Token ${token}` }
          }
        );
        const data = await response.json();
        setUnreadCount(data.data.unread);
      } catch (error) {
        console.error('Error:', error);
      }
    };
    
    fetchCount();
    const interval = setInterval(fetchCount, 30000);
    return () => clearInterval(interval);
  }, [token]);
  
  return (
    <div className="relative">
      <Bell size={24} className="text-gray-700" />
      {unreadCount > 0 && (
        <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
          {unreadCount}
        </span>
      )}
    </div>
  );
};
```

---

### 3. System Status Banner

```tsx
// components/store/SystemStatusBanner.tsx

'use client';

import React, { useState, useEffect } from 'react';

export const SystemStatusBanner: React.FC<{token: string}> = ({ token }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch(
          'http://167.71.40.9/core/shifts/current/',
          {
            headers: { 'Authorization': `Token ${token}` }
          }
        );
        const data = await response.json();
        setIsOpen(data.data !== null);
      } catch (error) {
        console.error('Error:', error);
      }
    };
    
    checkStatus();
    const interval = setInterval(checkStatus, 60000);
    return () => clearInterval(interval);
  }, [token]);
  
  if (!isOpen) {
    return (
      <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🔴</span>
          <div>
            <p className="font-semibold text-red-800">النظام مغلق</p>
            <p className="text-sm text-red-600">سيكون متاحاً قريباً</p>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-green-50 border-l-4 border-green-500 p-4 mb-6">
      <div className="flex items-center gap-3">
        <span className="text-2xl">🟢</span>
        <div>
          <p className="font-semibold text-green-800">النظام متاح</p>
          <p className="text-sm text-green-600">يمكنك إدارة العمليات الآن</p>
        </div>
      </div>
    </div>
  );
};
```

---

## 📊 أنواع الإشعارات للمخزن

### الإشعارات التي يستقبلها المخزن:

| الإشعار | `extra.type` | متى | البيانات الإضافية |
|---------|--------------|-----|-------------------|
| 📦 فاتورة شراء جديدة | `purchase_invoice` | عند الشراء | `invoice_id`, `total_price` |
| 🔔 تحديث حالة الفاتورة | `invoice_status_update` | تغيير الحالة | `invoice_id`, `new_status` |
| 💰 دفعة شراء جديدة | `purchase_payment` | عند الدفع | `payment_id`, `amount`, `method` |
| ↩️ مرتجع شراء جديد | `purchase_return` | عند الإرجاع | `return_id`, `total_price` |
| 🔔 تحديث المرتجع | `return_status_update` | تغيير حالة | `return_id`, `new_status` |

---

## 🎨 UI Components

### Complete Notifications Page

```tsx
// app/store/notifications/page.tsx

'use client';

import React, { useState, useEffect } from 'react';
import { Bell, Check, Trash2, RefreshCw } from 'lucide-react';
import type { Notification } from '@/types/notifications';

export default function StoreNotificationsPage() {
  const token = getStoreToken();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [stats, setStats] = useState({ total: 0, unread: 0, read: 0 });
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  
  const API_BASE = 'http://167.71.40.9';
  
  const fetchNotifications = async () => {
    const url = filter === 'unread'
      ? `${API_BASE}/notifications/notifications/unread/`
      : `${API_BASE}/notifications/notifications/`;
    
    const response = await fetch(url, {
      headers: { 'Authorization': `Token ${token}` }
    });
    
    const data = await response.json();
    setNotifications(data.results);
    setLoading(false);
  };
  
  const fetchStats = async () => {
    const response = await fetch(
      `${API_BASE}/notifications/notifications/stats/`,
      {
        headers: { 'Authorization': `Token ${token}` }
      }
    );
    const data = await response.json();
    setStats(data.data);
  };
  
  useEffect(() => {
    fetchNotifications();
    fetchStats();
  }, [filter]);
  
  const markAsRead = async (id: number) => {
    await fetch(
      `${API_BASE}/notifications/notifications/${id}/update/`,
      {
        method: 'PATCH',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_read: true })
      }
    );
    
    fetchNotifications();
    fetchStats();
  };
  
  const markAllAsRead = async () => {
    await fetch(
      `${API_BASE}/notifications/notifications/mark-all-read/`,
      {
        method: 'POST',
        headers: { 'Authorization': `Token ${token}` }
      }
    );
    
    fetchNotifications();
    fetchStats();
  };
  
  const deleteNotification = async (id: number) => {
    await fetch(
      `${API_BASE}/notifications/notifications/${id}/delete/`,
      {
        method: 'DELETE',
        headers: { 'Authorization': `Token ${token}` }
      }
    );
    
    fetchNotifications();
    fetchStats();
  };
  
  const getIcon = (type: string) => {
    const icons: Record<string, string> = {
      'purchase_invoice': '📦',
      'invoice_status_update': '🔔',
      'purchase_payment': '💰',
      'purchase_return': '↩️',
      'return_status_update': '🔄',
    };
    return icons[type] || '📋';
  };
  
  if (loading) {
    return <div className="flex justify-center p-8">جاري التحميل...</div>;
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Bell size={32} />
          الإشعارات
        </h1>
        <button
          onClick={markAllAsRead}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
        >
          <Check size={18} />
          تحديد الكل كمقروء
        </button>
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow text-center">
          <p className="text-3xl font-bold text-gray-800">{stats.total}</p>
          <p className="text-sm text-gray-600">الإجمالي</p>
        </div>
        <div className="bg-blue-50 p-4 rounded-lg shadow text-center">
          <p className="text-3xl font-bold text-blue-600">{stats.unread}</p>
          <p className="text-sm text-gray-600">غير مقروء</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow text-center">
          <p className="text-3xl font-bold text-gray-800">{stats.read}</p>
          <p className="text-sm text-gray-600">مقروء</p>
        </div>
      </div>
      
      {/* Filters */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg ${
            filter === 'all' 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-200 hover:bg-gray-300'
          }`}
        >
          الكل
        </button>
        <button
          onClick={() => setFilter('unread')}
          className={`px-4 py-2 rounded-lg ${
            filter === 'unread' 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-200 hover:bg-gray-300'
          }`}
        >
          غير مقروء
        </button>
      </div>
      
      {/* Notifications */}
      <div className="space-y-3">
        {notifications.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            لا توجد إشعارات
          </div>
        ) : (
          notifications.map(notif => (
            <div
              key={notif.id}
              className={`flex gap-3 p-4 rounded-lg ${
                notif.is_read 
                  ? 'bg-white border border-gray-200' 
                  : 'bg-blue-50 border-l-4 border-l-blue-500'
              } hover:shadow-md transition-shadow`}
            >
              <div className="text-2xl">{getIcon(notif.extra.type)}</div>
              
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">{notif.title}</h3>
                <p className="text-sm text-gray-600 mt-1">{notif.message}</p>
                
                {/* Extra Info */}
                {notif.extra.invoice_id && (
                  <p className="text-xs text-gray-500 mt-2">
                    رقم الفاتورة: #{notif.extra.invoice_id}
                  </p>
                )}
                
                <span className="text-xs text-gray-400 mt-2 block">
                  {formatTimeAgo(notif.created_at)}
                </span>
              </div>
              
              <div className="flex gap-2">
                {!notif.is_read && (
                  <button
                    onClick={() => markAsRead(notif.id)}
                    className="p-2 hover:bg-gray-100 rounded-full"
                    title="تحديد كمقروء"
                  >
                    <Check size={18} className="text-green-600" />
                  </button>
                )}
                
                <button
                  onClick={() => deleteNotification(notif.id)}
                  className="p-2 hover:bg-gray-100 rounded-full"
                  title="حذف"
                >
                  <Trash2 size={18} className="text-red-600" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (seconds < 60) return 'الآن';
  if (seconds < 3600) return `منذ ${Math.floor(seconds / 60)} دقيقة`;
  if (seconds < 86400) return `منذ ${Math.floor(seconds / 3600)} ساعة`;
  return `منذ ${Math.floor(seconds / 86400)} يوم`;
}
```

---

## 🔔 Notification Types للمخزن

### معالجة النقر حسب النوع:

```typescript
const handleNotificationClick = (notification: Notification) => {
  const { type } = notification.extra;
  
  switch(type) {
    case 'purchase_invoice':
    case 'invoice_status_update':
      // فتح صفحة الفاتورة
      navigateTo(`/store/purchases/${notification.extra.invoice_id}`);
      break;
      
    case 'purchase_payment':
      // فتح صفحة الدفعات
      navigateTo(`/store/payments/${notification.extra.payment_id}`);
      break;
      
    case 'purchase_return':
    case 'return_status_update':
      // فتح صفحة المرتجع
      navigateTo(`/store/returns/${notification.extra.return_id}`);
      break;
      
    default:
      console.log('Notification:', notification);
  }
  
  // تحديد كمقروء
  markAsRead(notification.id);
};
```

---

## 📱 Store App Layout

```tsx
// app/store/layout.tsx

import { SystemStatusBanner } from '@/components/store/SystemStatusBanner';
import { StoreNotificationBadge } from '@/components/store/NotificationBadge';

export default function StoreLayout({ children }: { children: React.ReactNode }) {
  const token = getStoreToken();
  
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-3 flex justify-between items-center">
          <div className="text-xl font-bold">🏪 Pharmasky Store</div>
          
          <div className="flex items-center gap-4">
            <StoreNotificationBadge token={token} />
            <span className="text-sm text-gray-600">اسم المخزن</span>
          </div>
        </div>
      </nav>
      
      <main className="container mx-auto px-4 py-6">
        <SystemStatusBanner token={token} />
        {children}
      </main>
    </div>
  );
}
```

---

## 🎯 ملخص Endpoints للمخزن

| Endpoint | Method | الاستخدام |
|----------|--------|-----------|
| `/notifications/notifications/` | GET | قائمة الإشعارات |
| `/notifications/notifications/unread/` | GET | غير المقروءة |
| `/notifications/notifications/stats/` | GET | الإحصائيات |
| `/notifications/notifications/{id}/update/` | PATCH | تحديد كمقروء |
| `/notifications/notifications/{id}/delete/` | DELETE | حذف |
| `/notifications/notifications/mark-all-read/` | POST | تحديد الكل |
| `/core/shifts/current/` | GET | حالة النظام |

---

## ✅ الخلاصة

### للمخزن:

✅ **5 أنواع إشعارات** رئيسية  
✅ **7 Endpoints** مفيدة  
✅ **Real-time status** للنظام  
✅ **React Components** جاهزة  
✅ **TypeScript Types** كاملة  
✅ **UI/UX Examples** للمخازن  

**كل شيء جاهز للتطبيق! 🚀**


