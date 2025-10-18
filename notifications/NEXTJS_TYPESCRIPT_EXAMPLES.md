# 🚀 Next.js + TypeScript Examples

أمثلة كاملة لاستخدام Notifications API في Next.js مع TypeScript.

---

## 📦 Types

```typescript
// types/notifications.ts

export interface User {
  id: number;
  username: string;
  name: string;
}

export interface Topic {
  id: number;
  name: string;
  description: string;
  subscribers_count: number;
}

export interface Notification {
  id: number;
  user: User;
  topic: Topic | null;
  title: string;
  message: string;
  is_read: boolean;
  extra: Record<string, any>;
  image_url: string;
  created_at: string;
}

export interface NotificationStats {
  total: number;
  unread: number;
  read: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface APIResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface WorkShift {
  id: number;
  status: 'ACTIVE' | 'CLOSED';
  started_by: User;
  closed_by: User | null;
  start_time: string;
  end_time: string | null;
  duration: string;
  total_sale_invoices: number;
  total_sales_amount: string;
}
```

---

## 🔧 API Service

```typescript
// services/notificationService.ts

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://167.71.40.9';

class NotificationService {
  private getHeaders(token: string): HeadersInit {
    return {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json',
    };
  }
  
  async getNotifications(
    token: string,
    page: number = 1,
    filters?: Record<string, string>
  ): Promise<PaginatedResponse<Notification>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: '20',
      ...filters,
    });
    
    const response = await fetch(
      `${API_BASE}/notifications/notifications/?${params}`,
      {
        headers: this.getHeaders(token),
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch notifications');
    }
    
    return await response.json();
  }
  
  async getUnreadNotifications(token: string): Promise<Notification[]> {
    const response = await fetch(
      `${API_BASE}/notifications/notifications/unread/`,
      {
        headers: this.getHeaders(token),
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch unread notifications');
    }
    
    const data = await response.json();
    return data.results;
  }
  
  async getStats(token: string): Promise<NotificationStats> {
    const response = await fetch(
      `${API_BASE}/notifications/notifications/stats/`,
      {
        headers: this.getHeaders(token),
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch stats');
    }
    
    const data: APIResponse<NotificationStats> = await response.json();
    return data.data;
  }
  
  async markAsRead(token: string, notificationId: number): Promise<void> {
    const response = await fetch(
      `${API_BASE}/notifications/notifications/${notificationId}/update/`,
      {
        method: 'PATCH',
        headers: this.getHeaders(token),
        body: JSON.stringify({ is_read: true }),
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to mark as read');
    }
  }
  
  async markAllAsRead(token: string): Promise<void> {
    const response = await fetch(
      `${API_BASE}/notifications/notifications/mark-all-read/`,
      {
        method: 'POST',
        headers: this.getHeaders(token),
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to mark all as read');
    }
  }
  
  async deleteNotification(token: string, notificationId: number): Promise<void> {
    const response = await fetch(
      `${API_BASE}/notifications/notifications/${notificationId}/delete/`,
      {
        method: 'DELETE',
        headers: this.getHeaders(token),
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to delete notification');
    }
  }
  
  async getCurrentShift(token: string): Promise<WorkShift | null> {
    const response = await fetch(
      `${API_BASE}/core/shifts/current/`,
      {
        headers: this.getHeaders(token),
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch current shift');
    }
    
    const data: APIResponse<WorkShift | null> = await response.json();
    return data.data;
  }
}

export const notificationService = new NotificationService();
```

---

## 🪝 Custom Hooks

```typescript
// hooks/useNotifications.ts

import { useState, useEffect } from 'react';
import { notificationService } from '@/services/notificationService';
import type { Notification, NotificationStats } from '@/types/notifications';

export const useNotifications = (token: string, pollInterval: number = 30000) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [stats, setStats] = useState<NotificationStats>({
    total: 0,
    unread: 0,
    read: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const fetchNotifications = async () => {
    try {
      const data = await notificationService.getNotifications(token);
      setNotifications(data.results);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };
  
  const fetchStats = async () => {
    try {
      const statsData = await notificationService.getStats(token);
      setStats(statsData);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };
  
  const markAsRead = async (id: number) => {
    try {
      await notificationService.markAsRead(token, id);
      await Promise.all([fetchNotifications(), fetchStats()]);
    } catch (err) {
      console.error('Failed to mark as read:', err);
    }
  };
  
  const markAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead(token);
      await Promise.all([fetchNotifications(), fetchStats()]);
    } catch (err) {
      console.error('Failed to mark all as read:', err);
    }
  };
  
  const deleteNotification = async (id: number) => {
    try {
      await notificationService.deleteNotification(token, id);
      await Promise.all([fetchNotifications(), fetchStats()]);
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };
  
  useEffect(() => {
    fetchNotifications();
    fetchStats();
    
    // Polling
    if (pollInterval > 0) {
      const interval = setInterval(() => {
        fetchNotifications();
        fetchStats();
      }, pollInterval);
      
      return () => clearInterval(interval);
    }
  }, [token, pollInterval]);
  
  return {
    notifications,
    stats,
    loading,
    error,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    refresh: fetchNotifications,
  };
};
```

---

## 🎨 UI Components

### 1. Notifications Page (App Router)

```typescript
// app/notifications/page.tsx

'use client';

import { useNotifications } from '@/hooks/useNotifications';
import { NotificationCard } from '@/components/NotificationCard';
import { NotificationFilters } from '@/components/NotificationFilters';

export default function NotificationsPage() {
  const token = getAuthToken(); // من context أو session
  
  const {
    notifications,
    stats,
    loading,
    markAsRead,
    markAllAsRead,
    deleteNotification,
  } = useNotifications(token);
  
  if (loading) {
    return <div className="loading">جاري التحميل...</div>;
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">📬 الإشعارات</h1>
        <button 
          onClick={markAllAsRead}
          className="btn btn-primary"
        >
          تحديد الكل كمقروء
        </button>
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="stat-card">
          <div className="text-3xl font-bold">{stats.total}</div>
          <div className="text-gray-600">الإجمالي</div>
        </div>
        <div className="stat-card bg-blue-50">
          <div className="text-3xl font-bold text-blue-600">{stats.unread}</div>
          <div className="text-gray-600">غير مقروء</div>
        </div>
        <div className="stat-card">
          <div className="text-3xl font-bold">{stats.read}</div>
          <div className="text-gray-600">مقروء</div>
        </div>
      </div>
      
      {/* Notifications List */}
      <div className="space-y-3">
        {notifications.map(notification => (
          <NotificationCard
            key={notification.id}
            notification={notification}
            onRead={markAsRead}
            onDelete={deleteNotification}
          />
        ))}
      </div>
    </div>
  );
}
```

---

### 2. Notification Card Component

```typescript
// components/NotificationCard.tsx

import React from 'react';
import { Check, Trash2 } from 'lucide-react';
import type { Notification } from '@/types/notifications';

interface NotificationCardProps {
  notification: Notification;
  onRead: (id: number) => void;
  onDelete: (id: number) => void;
}

export const NotificationCard: React.FC<NotificationCardProps> = ({
  notification,
  onRead,
  onDelete,
}) => {
  const getIcon = (type: string) => {
    const icons: Record<string, string> = {
      'sale_invoice': '🛒',
      'invoice_status_update': '🔔',
      'payment_due_reminder': '⏰',
      'payment_overdue': '⚠️',
      'wishlist_product_available': '✨',
      'shift_started': '🟢',
      'shift_closed': '🔴',
    };
    return icons[type] || '📢';
  };
  
  const getPriorityClass = (type: string) => {
    if (['payment_overdue', 'payment_due_reminder'].includes(type)) {
      return 'border-l-4 border-l-red-500 bg-red-50';
    }
    if (type === 'wishlist_product_available') {
      return 'border-l-4 border-l-green-500 bg-green-50';
    }
    return notification.is_read 
      ? 'border-l-4 border-l-gray-300' 
      : 'border-l-4 border-l-blue-500 bg-blue-50';
  };
  
  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (seconds < 60) return 'الآن';
    if (seconds < 3600) return `منذ ${Math.floor(seconds / 60)} دقيقة`;
    if (seconds < 86400) return `منذ ${Math.floor(seconds / 3600)} ساعة`;
    return `منذ ${Math.floor(seconds / 86400)} يوم`;
  };
  
  const icon = getIcon(notification.extra.type);
  const priorityClass = getPriorityClass(notification.extra.type);
  
  return (
    <div className={`flex gap-3 p-4 rounded-lg ${priorityClass} hover:shadow-md transition-shadow`}>
      <div className="text-2xl">{icon}</div>
      
      <div className="flex-1">
        <h3 className="font-semibold text-gray-900">{notification.title}</h3>
        <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
        <span className="text-xs text-gray-400 mt-2 block">
          {formatTimeAgo(notification.created_at)}
        </span>
      </div>
      
      <div className="flex gap-2">
        {!notification.is_read && (
          <button
            onClick={() => onRead(notification.id)}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            title="تحديد كمقروء"
          >
            <Check size={18} className="text-green-600" />
          </button>
        )}
        
        <button
          onClick={() => onDelete(notification.id)}
          className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          title="حذف"
        >
          <Trash2 size={18} className="text-red-600" />
        </button>
      </div>
    </div>
  );
};
```

---

### 3. Notification Badge (Server Component)

```typescript
// components/NotificationBadge.tsx

'use client';

import React, { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';
import { notificationService } from '@/services/notificationService';

interface NotificationBadgeProps {
  token: string;
}

export const NotificationBadge: React.FC<NotificationBadgeProps> = ({ token }) => {
  const [unreadCount, setUnreadCount] = useState(0);
  
  useEffect(() => {
    const fetchCount = async () => {
      try {
        const stats = await notificationService.getStats(token);
        setUnreadCount(stats.unread);
      } catch (error) {
        console.error('Failed to fetch unread count:', error);
      }
    };
    
    fetchCount();
    
    const interval = setInterval(fetchCount, 30000);
    return () => clearInterval(interval);
  }, [token]);
  
  return (
    <div className="relative cursor-pointer">
      <Bell size={24} className="text-gray-700" />
      {unreadCount > 0 && (
        <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      )}
    </div>
  );
};
```

---

### 4. System Status Banner

```typescript
// components/SystemStatusBanner.tsx

'use client';

import React, { useState, useEffect } from 'react';
import { notificationService } from '@/services/notificationService';
import type { WorkShift } from '@/types/notifications';

interface SystemStatusBannerProps {
  token: string;
}

export const SystemStatusBanner: React.FC<SystemStatusBannerProps> = ({ token }) => {
  const [shift, setShift] = useState<WorkShift | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const checkShift = async () => {
      try {
        const currentShift = await notificationService.getCurrentShift(token);
        setShift(currentShift);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch shift:', error);
        setLoading(false);
      }
    };
    
    checkShift();
    
    const interval = setInterval(checkShift, 60000); // كل دقيقة
    return () => clearInterval(interval);
  }, [token]);
  
  if (loading) return null;
  
  if (!shift) {
    return (
      <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
        <div className="flex items-center">
          <span className="text-2xl mr-3">🔴</span>
          <div>
            <p className="font-semibold text-red-800">النظام مغلق حالياً</p>
            <p className="text-sm text-red-600">سنكون متاحين قريباً. شكراً لصبركم.</p>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-green-50 border-l-4 border-green-500 p-4 mb-6">
      <div className="flex items-center">
        <span className="text-2xl mr-3">🟢</span>
        <div>
          <p className="font-semibold text-green-800">النظام متاح الآن</p>
          <p className="text-sm text-green-600">
            يمكنكم تقديم طلباتكم. بدأنا منذ {shift.duration}
          </p>
        </div>
      </div>
    </div>
  );
};
```

---

### 5. Notification Dropdown

```typescript
// components/NotificationDropdown.tsx

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Bell } from 'lucide-react';
import { notificationService } from '@/services/notificationService';
import type { Notification } from '@/types/notifications';

interface NotificationDropdownProps {
  token: string;
}

export const NotificationDropdown: React.FC<NotificationDropdownProps> = ({ token }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const fetchUnread = async () => {
      try {
        const unread = await notificationService.getUnreadNotifications(token);
        setNotifications(unread.slice(0, 5)); // آخر 5
        setUnreadCount(unread.length);
      } catch (error) {
        console.error('Error:', error);
      }
    };
    
    fetchUnread();
    const interval = setInterval(fetchUnread, 30000);
    return () => clearInterval(interval);
  }, [token]);
  
  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);
  
  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 hover:bg-gray-100 rounded-full transition-colors"
      >
        <Bell size={24} />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount}
          </span>
        )}
      </button>
      
      {isOpen && (
        <div className="absolute left-0 mt-2 w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
          {/* Header */}
          <div className="flex justify-between items-center p-4 border-b">
            <h3 className="font-semibold">الإشعارات</h3>
            <span className="text-sm text-gray-500">{unreadCount} جديد</span>
          </div>
          
          {/* Body */}
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                لا توجد إشعارات جديدة
              </div>
            ) : (
              notifications.map(notif => (
                <div
                  key={notif.id}
                  className="p-4 border-b hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => {
                    // Handle click
                    setIsOpen(false);
                  }}
                >
                  <p className="font-medium text-sm">{notif.title}</p>
                  <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                    {notif.message}
                  </p>
                  <span className="text-xs text-gray-400 mt-1 block">
                    {formatTimeAgo(notif.created_at)}
                  </span>
                </div>
              ))
            )}
          </div>
          
          {/* Footer */}
          <div className="p-3 border-t text-center">
            <a 
              href="/notifications" 
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              عرض جميع الإشعارات
            </a>
          </div>
        </div>
      )}
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

### 6. Toast Notifications

```typescript
// hooks/useNotificationToasts.ts

import { useEffect, useRef } from 'react';
import { toast } from 'react-hot-toast';
import { notificationService } from '@/services/notificationService';
import type { Notification } from '@/types/notifications';

export const useNotificationToasts = (token: string) => {
  const lastCheckRef = useRef<Date>(new Date());
  
  useEffect(() => {
    const checkForNew = async () => {
      try {
        const unread = await notificationService.getUnreadNotifications(token);
        
        // فقط الإشعارات الجديدة بعد آخر فحص
        const newNotifs = unread.filter(notif => 
          new Date(notif.created_at) > lastCheckRef.current
        );
        
        newNotifs.forEach(notif => {
          const icon = getIcon(notif.extra.type);
          
          toast.custom(
            (t) => (
              <div
                className={`${
                  t.visible ? 'animate-enter' : 'animate-leave'
                } max-w-md w-full bg-white shadow-lg rounded-lg pointer-events-auto flex ring-1 ring-black ring-opacity-5`}
              >
                <div className="flex-1 w-0 p-4">
                  <div className="flex items-start">
                    <div className="text-2xl mr-3">{icon}</div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">
                        {notif.title}
                      </p>
                      <p className="mt-1 text-sm text-gray-500">
                        {notif.message}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex border-l border-gray-200">
                  <button
                    onClick={() => toast.dismiss(t.id)}
                    className="w-full border border-transparent rounded-none rounded-r-lg p-4 flex items-center justify-center text-sm font-medium text-blue-600 hover:text-blue-500"
                  >
                    إغلاق
                  </button>
                </div>
              </div>
            ),
            { duration: 5000 }
          );
        });
        
        lastCheckRef.current = new Date();
      } catch (error) {
        console.error('Error checking for new notifications:', error);
      }
    };
    
    // Check كل 30 ثانية
    const interval = setInterval(checkForNew, 30000);
    return () => clearInterval(interval);
  }, [token]);
};

function getIcon(type: string): string {
  const icons: Record<string, string> = {
    'sale_invoice': '🛒',
    'wishlist_product_available': '✨',
    'payment_due_reminder': '⏰',
    'shift_started': '🟢',
    'shift_closed': '🔴',
  };
  return icons[type] || '🔔';
}
```

---

## 🎯 Complete App Layout

```typescript
// app/layout.tsx

import { Toaster } from 'react-hot-toast';
import { NotificationBadge } from '@/components/NotificationBadge';
import { SystemStatusBanner } from '@/components/SystemStatusBanner';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const token = getAuthToken();
  
  return (
    <html lang="ar" dir="rtl">
      <body>
        <nav className="bg-white shadow-sm">
          <div className="container mx-auto px-4 py-3 flex justify-between items-center">
            <div className="text-xl font-bold">صيدلية Pharmasky</div>
            
            <div className="flex items-center gap-4">
              <NotificationBadge token={token} />
              {/* other nav items */}
            </div>
          </div>
        </nav>
        
        <main className="container mx-auto px-4 py-6">
          <SystemStatusBanner token={token} />
          {children}
        </main>
        
        <Toaster position="top-left" />
      </body>
    </html>
  );
}
```

---

## 🔐 Environment Variables

```bash
# .env.local

NEXT_PUBLIC_API_URL=http://167.71.40.9
NEXT_PUBLIC_WS_URL=ws://167.71.40.9
NEXT_PUBLIC_POLLING_INTERVAL=30000
```

---

## 📱 Mobile Responsive

```css
/* styles/notifications.css */

@media (max-width: 768px) {
  .notification-card {
    flex-direction: column;
    padding: 12px;
  }
  
  .notification-actions {
    flex-direction: row;
    justify-content: flex-end;
    width: 100%;
    margin-top: 8px;
  }
  
  .notifications-list {
    padding: 0;
  }
}
```

---

## ✅ الخلاصة

### ما تم توفيره:

✅ **Types كاملة** - TypeScript definitions  
✅ **API Service** - Reusable service class  
✅ **Custom Hooks** - useNotifications  
✅ **React Components** - جاهزة للاستخدام  
✅ **Next.js Examples** - App Router  
✅ **Tailwind CSS** - Styling examples  
✅ **Real-time Polling** - كل 30 ثانية  
✅ **Toast Notifications** - للإشعارات الجديدة  
✅ **Mobile Responsive** - جاهز للموبايل  

**كل شيء جاهز للـ copy & paste! 🚀**

---

## 📚 الملفات المطلوبة:

```
frontend/
├── types/
│   └── notifications.ts        ✅
├── services/
│   └── notificationService.ts  ✅
├── hooks/
│   ├── useNotifications.ts     ✅
│   └── useNotificationToasts.ts ✅
├── components/
│   ├── NotificationCard.tsx    ✅
│   ├── NotificationBadge.tsx   ✅
│   ├── NotificationDropdown.tsx ✅
│   └── SystemStatusBanner.tsx  ✅
└── app/
    ├── layout.tsx              ✅
    └── notifications/
        └── page.tsx            ✅
```

**جاهز للتطبيق! 📱🚀**


