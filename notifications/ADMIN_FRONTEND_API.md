# 👨‍💼 Admin Frontend API Guide

دليل شامل لاستخدام API الإشعارات والوردية من Frontend للـ Admin/Manager.

---

## 🔐 Authentication

جميع الطلبات تحتاج Admin/Manager token:

```javascript
headers: {
  'Authorization': 'Token ADMIN_AUTH_TOKEN',
  'Content-Type': 'application/json'
}
```

---

## 📋 جدول المحتويات

1. [إدارة الوردية](#1-إدارة-الوردية)
2. [إرسال الإشعارات](#2-إرسال-الإشعارات)
3. [إدارة المواضيع](#3-إدارة-المواضيع)
4. [إحصائيات الورديات](#4-إحصائيات-الورديات)
5. [مراقبة النشاطات](#5-مراقبة-النشاطات)

---

## 1. إدارة الوردية

### 🟢 POST `/core/shifts/start/` - بدء الوردية

بدء وردية عمل جديدة وإرسال إشعارات لجميع الصيدليات.

#### Request:

```typescript
const startShift = async (customMessage?: string) => {
  const response = await fetch('http://167.71.40.9/core/shifts/start/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${adminToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      send_notifications: true,
      notification_message: customMessage || ''
    })
  });
  
  return await response.json();
};

// استخدام
await startShift('مساء الخير! النظام متاح الآن. يمكنكم تقديم طلباتكم 🌙');
```

#### Response:

```json
{
  "success": true,
  "message": "تم بدء الوردية بنجاح وإرسال الإشعارات للصيدليات",
  "data": {
    "id": 123,
    "status": "ACTIVE",
    "started_by": {
      "id": 1,
      "username": "admin",
      "name": "Admin"
    },
    "start_time": "2025-10-17T18:00:00Z",
    "total_sale_invoices": 0,
    "total_sales_amount": "0.00"
  }
}
```

**ما يحدث:**
- ✅ إنشاء WorkShift (status=ACTIVE)
- ✅ إرسال إشعار "🟢 النظام متاح الآن" لـ **جميع الصيدليات**
- ✅ بدء تسجيل الإحصائيات

---

### 🔴 POST `/core/shifts/close/` - إغلاق الوردية

إغلاق الوردية الحالية مع الإحصائيات النهائية.

#### Request:

```typescript
const closeShift = async (notes: string, customMessage?: string) => {
  const response = await fetch('http://167.71.40.9/core/shifts/close/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${adminToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      notes: notes,
      send_notifications: true,
      notification_message: customMessage || ''
    })
  });
  
  return await response.json();
};

// استخدام
await closeShift(
  'وردية ممتازة - 75 طلب تم معالجتها',
  'تصبحون على خير! انتهت الوردية. سنعود غداً 🌙'
);
```

#### Response:

```json
{
  "success": true,
  "message": "تم إغلاق الوردية بنجاح",
  "data": {
    "id": 123,
    "status": "CLOSED",
    "start_time": "2025-10-17T18:00:00Z",
    "end_time": "2025-10-18T02:00:00Z",
    "duration": "8.0 ساعة",
    "total_sale_invoices": 75,
    "total_purchase_invoices": 10,
    "total_payments": 45,
    "total_returns": 5,
    "total_complaints": 3,
    "total_new_registrations": 8,
    "total_sales_amount": "187500.00",
    "total_payments_amount": "125000.00",
    "notes": "وردية ممتازة - 75 طلب تم معالجتها"
  }
}
```

**ما يحدث:**
- ✅ تحديث إحصائيات الوردية تلقائياً
- ✅ إغلاق الوردية (status=CLOSED)
- ✅ إرسال إشعار "🔴 تم إغلاق النظام" لـ **جميع الصيدليات**
- ✅ حفظ الملاحظات

---

### 📊 GET `/core/shifts/current/` - الوردية الحالية

```typescript
const getCurrentShift = async () => {
  const response = await fetch('http://167.71.40.9/core/shifts/current/', {
    headers: {
      'Authorization': `Token ${adminToken}`,
    }
  });
  
  return await response.json();
};
```

---

### 📋 GET `/core/shifts/` - قائمة الورديات

```typescript
const getShifts = async (page: number = 1, status?: 'ACTIVE' | 'CLOSED') => {
  const params = new URLSearchParams({
    page: page.toString(),
    ...(status && { status })
  });
  
  const response = await fetch(
    `http://167.71.40.9/core/shifts/?${params}`,
    {
      headers: {
        'Authorization': `Token ${adminToken}`,
      }
    }
  );
  
  return await response.json();
};
```

---

### 📈 GET `/core/shifts/stats/` - إحصائيات عامة

```typescript
const getShiftsStats = async () => {
  const response = await fetch('http://167.71.40.9/core/shifts/stats/', {
    headers: {
      'Authorization': `Token ${adminToken}`,
    }
  });
  
  return await response.json();
};
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_shifts": 150,
    "active_shifts": 1,
    "closed_shifts": 149,
    "total_sales_all_shifts": "28125000.00",
    "total_payments_all_shifts": "22500000.00",
    "average_invoices_per_shift": 67.5
  }
}
```

---

## 2. إرسال الإشعارات

### 📢 POST `/notifications/notifications/create/` - إشعار فردي

إرسال إشعار لمستخدم محدد أو موضوع.

#### لمستخدم محدد:

```typescript
const sendNotificationToUser = async (userId: number, title: string, message: string) => {
  const response = await fetch('http://167.71.40.9/notifications/notifications/create/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${adminToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user: userId,
      title: title,
      message: message,
      extra: {
        type: 'admin_message',
        sent_by: 'Admin'
      }
    })
  });
  
  return await response.json();
};

// استخدام
await sendNotificationToUser(
  45,  // pharmacy_id
  '🎉 عرض خاص',
  'لديك خصم 20% على طلبك القادم!'
);
```

#### لموضوع (جميع المشتركين):

```typescript
const sendNotificationToTopic = async (topicId: number, title: string, message: string) => {
  const response = await fetch('http://167.71.40.9/notifications/notifications/create/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${adminToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      topic: topicId,
      title: title,
      message: message,
      extra: {
        type: 'topic_announcement'
      }
    })
  });
  
  return await response.json();
};

// استخدام
await sendNotificationToTopic(
  1,  // topic: "عروض وخصومات"
  '🔥 عرض محدود',
  'خصم 50% على جميع المنتجات اليوم فقط!'
);
```

---

### 📨 POST `/notifications/notifications/bulk-create/` - إشعار جماعي

إرسال إشعار لعدة مستخدمين.

```typescript
const sendBulkNotifications = async (
  userIds: number[],
  title: string,
  message: string
) => {
  const response = await fetch('http://167.71.40.9/notifications/notifications/bulk-create/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${adminToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_ids: userIds,
      title: title,
      message: message,
      extra: {
        type: 'bulk_announcement',
        timestamp: new Date().toISOString()
      }
    })
  });
  
  return await response.json();
};

// استخدام - إرسال لـ 50 صيدلية
await sendBulkNotifications(
  [1, 2, 3, 4, 5, /* ... */, 50],
  '📢 إعلان مهم',
  'تحديث النظام سيتم يوم الجمعة'
);
```

**Response:**
```json
{
  "success": true,
  "message": "Bulk notifications sent successfully",
  "data": {
    "count": 50,
    "message": "50 notifications created successfully"
  }
}
```

---

## 3. إدارة المواضيع

### 📝 POST `/notifications/topics/create/` - إنشاء موضوع

```typescript
const createTopic = async (name: string, description: string) => {
  const response = await fetch('http://167.71.40.9/notifications/topics/create/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${adminToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: name,
      description: description
    })
  });
  
  return await response.json();
};

// استخدام
await createTopic('تحديثات المنتجات', 'آخر التحديثات والإضافات الجديدة');
```

---

### 📋 GET `/notifications/topics/` - قائمة المواضيع

```typescript
const getTopics = async () => {
  const response = await fetch('http://167.71.40.9/notifications/topics/', {
    headers: {
      'Authorization': `Token ${adminToken}`,
    }
  });
  
  return await response.json();
};
```

---

### ✏️ PATCH `/notifications/topics/{id}/update/` - تحديث موضوع

```typescript
const updateTopic = async (topicId: number, data: {name?: string, description?: string}) => {
  const response = await fetch(
    `http://167.71.40.9/notifications/topics/${topicId}/update/`,
    {
      method: 'PATCH',
      headers: {
        'Authorization': `Token ${adminToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    }
  );
  
  return await response.json();
};
```

---

### 🗑️ DELETE `/notifications/topics/{id}/delete/` - حذف موضوع

```typescript
const deleteTopic = async (topicId: number) => {
  const response = await fetch(
    `http://167.71.40.9/notifications/topics/${topicId}/delete/`,
    {
      method: 'DELETE',
      headers: {
        'Authorization': `Token ${adminToken}`,
      }
    }
  );
  
  return await response.json();
};
```

---

## 4. إحصائيات الورديات

### 📊 GET `/core/shifts/stats/`

```typescript
interface ShiftStats {
  total_shifts: number;
  active_shifts: number;
  closed_shifts: number;
  total_sales_all_shifts: string;
  total_payments_all_shifts: string;
  average_invoices_per_shift: number;
}

const getShiftStats = async (): Promise<ShiftStats> => {
  const response = await fetch('http://167.71.40.9/core/shifts/stats/', {
    headers: {
      'Authorization': `Token ${adminToken}`,
    }
  });
  
  const data = await response.json();
  return data.data;
};
```

---

## 5. مراقبة النشاطات

### Admin Dashboard - Live Stats

```typescript
const getAdminDashboardData = async () => {
  // 1. الوردية الحالية
  const currentShift = await getCurrentShift();
  
  // 2. إحصائيات الورديات
  const shiftStats = await getShiftStats();
  
  // 3. إشعارات الـ Admin (آخر 10)
  const adminNotifications = await fetch(
    'http://167.71.40.9/notifications/notifications/?page_size=10',
    {
      headers: { 'Authorization': `Token ${adminToken}` }
    }
  ).then(res => res.json());
  
  return {
    currentShift,
    shiftStats,
    notifications: adminNotifications.results
  };
};
```

---

## 📱 React Components للـ Admin

### 1. Shift Control Panel

```tsx
// components/admin/ShiftControlPanel.tsx

'use client';

import React, { useState, useEffect } from 'react';
import { PlayCircle, StopCircle, Clock } from 'lucide-react';
import type { WorkShift } from '@/types/notifications';

interface ShiftControlPanelProps {
  token: string;
}

export const ShiftControlPanel: React.FC<ShiftControlPanelProps> = ({ token }) => {
  const [currentShift, setCurrentShift] = useState<WorkShift | null>(null);
  const [loading, setLoading] = useState(false);
  const [customMessage, setCustomMessage] = useState('');
  const [notes, setNotes] = useState('');
  
  const API_BASE = 'http://167.71.40.9';
  
  const fetchCurrentShift = async () => {
    try {
      const response = await fetch(`${API_BASE}/core/shifts/current/`, {
        headers: { 'Authorization': `Token ${token}` }
      });
      const data = await response.json();
      setCurrentShift(data.data);
    } catch (error) {
      console.error('Error:', error);
    }
  };
  
  useEffect(() => {
    fetchCurrentShift();
    const interval = setInterval(fetchCurrentShift, 60000); // كل دقيقة
    return () => clearInterval(interval);
  }, []);
  
  const handleStartShift = async () => {
    setLoading(true);
    try {
      await fetch(`${API_BASE}/core/shifts/start/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          send_notifications: true,
          notification_message: customMessage
        })
      });
      
      await fetchCurrentShift();
      setCustomMessage('');
      alert('✅ تم بدء الوردية وإرسال الإشعارات');
    } catch (error) {
      alert('❌ فشل في بدء الوردية');
    } finally {
      setLoading(false);
    }
  };
  
  const handleCloseShift = async () => {
    if (!confirm('هل أنت متأكد من إغلاق الوردية؟')) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/core/shifts/close/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          notes: notes,
          send_notifications: true,
          notification_message: customMessage
        })
      });
      
      const data = await response.json();
      
      // عرض الإحصائيات
      alert(
        `✅ تم إغلاق الوردية بنجاح!\n\n` +
        `المدة: ${data.data.duration}\n` +
        `الطلبات: ${data.data.total_sale_invoices}\n` +
        `المبيعات: ${data.data.total_sales_amount} جنيه`
      );
      
      await fetchCurrentShift();
      setNotes('');
      setCustomMessage('');
    } catch (error) {
      alert('❌ فشل في إغلاق الوردية');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Clock size={28} />
        إدارة الوردية
      </h2>
      
      {/* الحالة الحالية */}
      {currentShift ? (
        <div className="bg-green-50 border-l-4 border-green-500 p-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold text-green-800">🟢 الوردية نشطة</p>
              <p className="text-sm text-green-600">
                بدأت: {new Date(currentShift.start_time).toLocaleString('ar-EG')}
              </p>
              <p className="text-sm text-green-600">
                المدة: {currentShift.duration}
              </p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-green-800">
                {currentShift.total_sale_invoices}
              </p>
              <p className="text-xs text-green-600">طلب</p>
            </div>
          </div>
          
          {/* Live Stats */}
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="text-center">
              <p className="text-lg font-bold">{currentShift.total_sale_invoices}</p>
              <p className="text-xs text-gray-600">الطلبات</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold">{currentShift.total_payments}</p>
              <p className="text-xs text-gray-600">الدفعات</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold">{currentShift.total_sales_amount}</p>
              <p className="text-xs text-gray-600">جنيه</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
          <p className="font-semibold text-red-800">🔴 لا توجد وردية نشطة</p>
          <p className="text-sm text-red-600">ابدأ وردية جديدة لبدء العمل</p>
        </div>
      )}
      
      {/* Actions */}
      {!currentShift ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              رسالة مخصصة للصيدليات (اختياري)
            </label>
            <textarea
              value={customMessage}
              onChange={(e) => setCustomMessage(e.target.value)}
              className="w-full p-3 border rounded-lg"
              rows={3}
              placeholder="مساء الخير! النظام متاح الآن..."
            />
          </div>
          
          <button
            onClick={handleStartShift}
            disabled={loading}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-4 px-6 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <PlayCircle size={24} />
            {loading ? 'جاري البدء...' : '🟢 بدء الوردية'}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              ملاحظات عن الوردية
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full p-3 border rounded-lg"
              rows={2}
              placeholder="وردية ممتازة، 75 طلب..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">
              رسالة الإغلاق للصيدليات (اختياري)
            </label>
            <textarea
              value={customMessage}
              onChange={(e) => setCustomMessage(e.target.value)}
              className="w-full p-3 border rounded-lg"
              rows={3}
              placeholder="تصبحون على خير! سنعود غداً..."
            />
          </div>
          
          <button
            onClick={handleCloseShift}
            disabled={loading}
            className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-4 px-6 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <StopCircle size={24} />
            {loading ? 'جاري الإغلاق...' : '🔴 إغلاق الوردية'}
          </button>
        </div>
      )}
    </div>
  );
};
```

---

### 2. Admin Notifications List

```tsx
// components/admin/AdminNotificationsList.tsx

'use client';

import React, { useState, useEffect } from 'react';
import type { Notification } from '@/types/notifications';

export const AdminNotificationsList: React.FC<{token: string}> = ({ token }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [filter, setFilter] = useState<string>('all');
  
  const API_BASE = 'http://167.71.40.9';
  
  const fetchNotifications = async () => {
    let url = `${API_BASE}/notifications/notifications/?page_size=50`;
    
    // فلترة حسب نوع الإشعار
    if (filter !== 'all') {
      url += `&extra__type__contains=${filter}`;
    }
    
    const response = await fetch(url, {
      headers: { 'Authorization': `Token ${token}` }
    });
    
    const data = await response.json();
    setNotifications(data.results);
  };
  
  useEffect(() => {
    fetchNotifications();
  }, [filter]);
  
  // تصنيف الإشعارات حسب النوع
  const adminTypes = [
    { value: 'all', label: 'الكل', icon: '📋' },
    { value: 'admin_sale_invoice', label: 'الطلبات', icon: '🛒' },
    { value: 'new_pharmacy_registration', label: 'تسجيلات', icon: '🏪' },
    { value: 'new_complaint', label: 'الشكاوي', icon: '📢' },
    { value: 'admin_purchase_invoice', label: 'فواتير الشراء', icon: '📦' },
  ];
  
  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {adminTypes.map(type => (
          <button
            key={type.value}
            onClick={() => setFilter(type.value)}
            className={`px-4 py-2 rounded-lg whitespace-nowrap ${
              filter === type.value
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {type.icon} {type.label}
          </button>
        ))}
      </div>
      
      {/* Notifications */}
      <div className="space-y-2">
        {notifications.map(notif => (
          <AdminNotificationCard key={notif.id} notification={notif} />
        ))}
      </div>
    </div>
  );
};

const AdminNotificationCard: React.FC<{notification: Notification}> = ({ notification }) => {
  const getTypeConfig = (type: string) => {
    const configs: Record<string, {icon: string, color: string}> = {
      'admin_sale_invoice': { icon: '🛒', color: 'blue' },
      'new_pharmacy_registration': { icon: '🏪', color: 'green' },
      'new_complaint': { icon: '📢', color: 'red' },
      'admin_purchase_invoice': { icon: '📦', color: 'purple' },
    };
    return configs[type] || { icon: '📋', color: 'gray' };
  };
  
  const config = getTypeConfig(notification.extra.type);
  
  return (
    <div className={`p-4 rounded-lg border-l-4 border-l-${config.color}-500 bg-${config.color}-50 hover:shadow-md transition-shadow`}>
      <div className="flex gap-3">
        <div className="text-2xl">{config.icon}</div>
        <div className="flex-1">
          <h4 className="font-semibold">{notification.title}</h4>
          <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
          <div className="flex gap-4 mt-2 text-xs text-gray-500">
            <span>{formatDate(notification.created_at)}</span>
            {notification.extra.user_name && (
              <span>من: {notification.extra.user_name}</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString('ar-EG', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
```

---

### 3. Send Notification Form

```tsx
// components/admin/SendNotificationForm.tsx

'use client';

import React, { useState, useEffect } from 'react';
import { Send } from 'lucide-react';

interface SendNotificationFormProps {
  token: string;
}

export const SendNotificationForm: React.FC<SendNotificationFormProps> = ({ token }) => {
  const [sendType, setSendType] = useState<'user' | 'topic' | 'bulk'>('user');
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [selectedUser, setSelectedUser] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('');
  const [userIds, setUserIds] = useState('');
  const [topics, setTopics] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  
  const API_BASE = 'http://167.71.40.9';
  
  useEffect(() => {
    // جلب المواضيع
    fetch(`${API_BASE}/notifications/topics/`, {
      headers: { 'Authorization': `Token ${token}` }
    })
      .then(res => res.json())
      .then(data => setTopics(data.results));
  }, []);
  
  const handleSend = async () => {
    setLoading(true);
    
    try {
      let url = '';
      let body = {};
      
      if (sendType === 'user') {
        url = `${API_BASE}/notifications/notifications/create/`;
        body = {
          user: parseInt(selectedUser),
          title,
          message,
          extra: { type: 'admin_message' }
        };
      } else if (sendType === 'topic') {
        url = `${API_BASE}/notifications/notifications/create/`;
        body = {
          topic: parseInt(selectedTopic),
          title,
          message,
          extra: { type: 'topic_announcement' }
        };
      } else if (sendType === 'bulk') {
        url = `${API_BASE}/notifications/notifications/bulk-create/`;
        body = {
          user_ids: userIds.split(',').map(id => parseInt(id.trim())),
          title,
          message,
          extra: { type: 'bulk_message' }
        };
      }
      
      await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      });
      
      alert('✅ تم إرسال الإشعار بنجاح');
      
      // Reset form
      setTitle('');
      setMessage('');
      setSelectedUser('');
      setSelectedTopic('');
      setUserIds('');
    } catch (error) {
      alert('❌ فشل في إرسال الإشعار');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6">📨 إرسال إشعار</h2>
      
      {/* نوع الإرسال */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">نوع الإرسال</label>
        <div className="flex gap-2">
          <button
            onClick={() => setSendType('user')}
            className={`px-4 py-2 rounded ${sendType === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            مستخدم واحد
          </button>
          <button
            onClick={() => setSendType('topic')}
            className={`px-4 py-2 rounded ${sendType === 'topic' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            موضوع
          </button>
          <button
            onClick={() => setSendType('bulk')}
            className={`px-4 py-2 rounded ${sendType === 'bulk' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            إرسال جماعي
          </button>
        </div>
      </div>
      
      {/* المستقبل */}
      {sendType === 'user' && (
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">User ID</label>
          <input
            type="number"
            value={selectedUser}
            onChange={(e) => setSelectedUser(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="45"
          />
        </div>
      )}
      
      {sendType === 'topic' && (
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">الموضوع</label>
          <select
            value={selectedTopic}
            onChange={(e) => setSelectedTopic(e.target.value)}
            className="w-full p-2 border rounded"
          >
            <option value="">اختر موضوع</option>
            {topics.map(topic => (
              <option key={topic.id} value={topic.id}>
                {topic.name} ({topic.subscribers_count} مشترك)
              </option>
            ))}
          </select>
        </div>
      )}
      
      {sendType === 'bulk' && (
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">User IDs (مفصولة بفاصلة)</label>
          <input
            type="text"
            value={userIds}
            onChange={(e) => setUserIds(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="1, 2, 3, 4, 5"
          />
        </div>
      )}
      
      {/* العنوان */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">العنوان</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full p-2 border rounded"
          placeholder="🎉 عرض خاص"
        />
      </div>
      
      {/* الرسالة */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">الرسالة</label>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className="w-full p-2 border rounded"
          rows={4}
          placeholder="خصم 30% على جميع المنتجات..."
        />
      </div>
      
      {/* Send Button */}
      <button
        onClick={handleSend}
        disabled={loading || !title || !message}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"
      >
        <Send size={20} />
        {loading ? 'جاري الإرسال...' : 'إرسال الإشعار'}
      </button>
    </div>
  );
};
```

---

### 4. Dashboard Stats

```tsx
// app/admin/dashboard/page.tsx

'use client';

import { useState, useEffect } from 'react';
import { ShiftControlPanel } from '@/components/admin/ShiftControlPanel';
import { AdminNotificationsList } from '@/components/admin/AdminNotificationsList';

export default function AdminDashboard() {
  const token = getAdminToken();
  const [stats, setStats] = useState<any>(null);
  
  useEffect(() => {
    const fetchStats = async () => {
      const response = await fetch('http://167.71.40.9/core/shifts/stats/', {
        headers: { 'Authorization': `Token ${token}` }
      });
      const data = await response.json();
      setStats(data.data);
    };
    
    fetchStats();
  }, []);
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">👨‍💼 لوحة تحكم الإدارة</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Shift Control */}
        <ShiftControlPanel token={token} />
        
        {/* Stats */}
        {stats && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4">📊 الإحصائيات العامة</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="stat-box">
                <p className="text-3xl font-bold">{stats.total_shifts}</p>
                <p className="text-sm text-gray-600">إجمالي الورديات</p>
              </div>
              <div className="stat-box">
                <p className="text-3xl font-bold">{stats.active_shifts}</p>
                <p className="text-sm text-gray-600">الورديات النشطة</p>
              </div>
              <div className="stat-box">
                <p className="text-3xl font-bold">
                  {parseFloat(stats.total_sales_all_shifts).toLocaleString()}
                </p>
                <p className="text-sm text-gray-600">إجمالي المبيعات</p>
              </div>
              <div className="stat-box">
                <p className="text-3xl font-bold">
                  {stats.average_invoices_per_shift.toFixed(1)}
                </p>
                <p className="text-sm text-gray-600">متوسط الطلبات/وردية</p>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Notifications */}
      <AdminNotificationsList token={token} />
    </div>
  );
}
```

---

## 📊 أنواع الإشعارات للـ Admin

| النوع | `extra.type` | الوصف |
|------|--------------|-------|
| 🏪 صيدلية جديدة | `new_pharmacy_registration` | تسجيل صيدلية |
| 📢 شكوى | `new_complaint` | شكوى جديدة |
| 🛒 طلب | `admin_sale_invoice` | طلب صيدلية |
| 📦 فاتورة شراء | `admin_purchase_invoice` | فاتورة مخزن |
| 💰 دفعة بيع | `sale_payment` | دفعة صيدلية |
| 💰 دفعة شراء | `purchase_payment` | دفعة مخزن |
| ↩️ مرتجع بيع | `sale_return` | مرتجع صيدلية |
| ↩️ مرتجع شراء | `purchase_return` | مرتجع مخزن |

### معالجة النقر:

```typescript
const handleAdminNotificationClick = (notification: Notification) => {
  const { type } = notification.extra;
  
  switch(type) {
    case 'new_pharmacy_registration':
      navigateTo(`/admin/pharmacies/${notification.extra.pharmacy_id}`);
      break;
      
    case 'new_complaint':
      navigateTo(`/admin/complaints/${notification.extra.complaint_id}`);
      break;
      
    case 'admin_sale_invoice':
      navigateTo(`/admin/orders/${notification.extra.invoice_id}`);
      break;
      
    case 'admin_purchase_invoice':
      navigateTo(`/admin/purchases/${notification.extra.invoice_id}`);
      break;
      
    default:
      console.log('Notification:', notification);
  }
};
```

---

## 🎯 Complete Admin Dashboard Example

```tsx
// app/admin/page.tsx

'use client';

import { ShiftControlPanel } from '@/components/admin/ShiftControlPanel';
import { SendNotificationForm } from '@/components/admin/SendNotificationForm';
import { AdminNotificationsList } from '@/components/admin/AdminNotificationsList';
import { ShiftHistory } from '@/components/admin/ShiftHistory';

export default function AdminPage() {
  const token = getAdminToken();
  
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8">👨‍💼 لوحة تحكم الإدارة</h1>
        
        {/* Row 1: Shift Control + Send Notification */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ShiftControlPanel token={token} />
          <SendNotificationForm token={token} />
        </div>
        
        {/* Row 2: Notifications */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">📬 آخر الإشعارات</h2>
          <AdminNotificationsList token={token} />
        </div>
        
        {/* Row 3: Shift History */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold mb-4">📊 سجل الورديات</h2>
          <ShiftHistory token={token} />
        </div>
      </div>
    </div>
  );
}
```

---

## ✅ الخلاصة

### للـ Admin Dashboard:

✅ **إدارة الوردية** - بدء/إغلاق بضغطة زر  
✅ **إرسال إشعارات** - فردي/جماعي/موضوع  
✅ **إدارة المواضيع** - إنشاء/تعديل/حذف  
✅ **مراقبة النشاطات** - real-time stats  
✅ **سجل الورديات** - جميع الورديات السابقة  
✅ **React Components** - جاهزة للاستخدام  
✅ **TypeScript** - مع Types كاملة  

**النظام جاهز للتطبيق! 🚀**


