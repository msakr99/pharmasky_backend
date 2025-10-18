# 📱 Pharmacy Frontend API Guide

دليل شامل لاستخدام API الإشعارات من Frontend للصيدليات.

---

## 🔐 Authentication

جميع الطلبات تحتاج Authentication Header:

```javascript
headers: {
  'Authorization': 'Token YOUR_AUTH_TOKEN',
  'Content-Type': 'application/json'
}
```

---

## 📋 جدول المحتويات

1. [جلب الإشعارات](#1-جلب-الإشعارات)
2. [الإشعارات غير المقروءة](#2-الإشعارات-غير-المقروءة)
3. [إحصائيات الإشعارات](#3-إحصائيات-الإشعارات)
4. [تحديد كمقروء](#4-تحديد-كمقروء)
5. [حذف إشعار](#5-حذف-إشعار)
6. [المواضيع والاشتراكات](#6-المواضيع-والاشتراكات)
7. [حالة الوردية](#7-حالة-الوردية)

---

## 1. جلب الإشعارات

### GET `/notifications/notifications/`

جلب قائمة إشعارات الصيدلية مع pagination وfilters.

#### Request:

```javascript
const fetchNotifications = async (page = 1, filters = {}) => {
  const params = new URLSearchParams({
    page: page,
    page_size: 20,
    ...filters
  });
  
  const response = await fetch(
    `http://167.71.40.9/notifications/notifications/?${params}`,
    {
      headers: {
        'Authorization': `Token ${authToken}`,
      }
    }
  );
  
  return await response.json();
};
```

#### Response:

```json
{
  "count": 150,
  "next": "http://167.71.40.9/notifications/notifications/?page=2",
  "previous": null,
  "results": [
    {
      "id": 123,
      "user": {
        "id": 45,
        "username": "+201234567890",
        "name": "صيدلية النور"
      },
      "topic": null,
      "title": "🛒 طلب جديد تم إنشاؤه",
      "message": "تم إنشاء طلبك رقم #456 بنجاح. إجمالي المبلغ: 5000 جنيه",
      "is_read": false,
      "extra": {
        "type": "sale_invoice",
        "invoice_id": 456,
        "total_price": "5000.00",
        "items_count": 10
      },
      "image_url": "",
      "created_at": "2025-10-17T18:30:00Z"
    }
  ]
}
```

#### Filters المتاحة:

```javascript
// فلترة حسب حالة القراءة
const unreadOnly = { is_read: 'false' };
const readOnly = { is_read: 'true' };

// البحث في العنوان والمحتوى
const searchFilters = { search: 'طلب' };

// الترتيب
const orderFilters = { ordering: '-created_at' }; // الأحدث أولاً

// مثال استخدام
const notifications = await fetchNotifications(1, { 
  is_read: 'false',
  ordering: '-created_at'
});
```

---

## 2. الإشعارات غير المقروءة

### GET `/notifications/notifications/unread/`

جلب الإشعارات غير المقروءة فقط (للـ badge والتنبيهات).

#### React/Vue Example:

```javascript
const fetchUnreadNotifications = async () => {
  const response = await fetch(
    'http://167.71.40.9/notifications/notifications/unread/',
    {
      headers: {
        'Authorization': `Token ${authToken}`,
      }
    }
  );
  
  const data = await response.json();
  return data.results;
};

// استخدام في Component
const [unreadNotifs, setUnreadNotifs] = useState([]);
const [unreadCount, setUnreadCount] = useState(0);

useEffect(() => {
  const loadUnread = async () => {
    const notifs = await fetchUnreadNotifications();
    setUnreadNotifs(notifs);
    setUnreadCount(notifs.length);
  };
  
  loadUnread();
  
  // Refresh كل 30 ثانية
  const interval = setInterval(loadUnread, 30000);
  return () => clearInterval(interval);
}, []);
```

#### UI Example:

```jsx
// Notification Badge
<div className="notification-icon">
  <BellIcon />
  {unreadCount > 0 && (
    <span className="badge">{unreadCount}</span>
  )}
</div>
```

---

## 3. إحصائيات الإشعارات

### GET `/notifications/notifications/stats/`

جلب إحصائيات سريعة (لـ Dashboard).

#### Request:

```javascript
const fetchNotificationStats = async () => {
  const response = await fetch(
    'http://167.71.40.9/notifications/notifications/stats/',
    {
      headers: {
        'Authorization': `Token ${authToken}`,
      }
    }
  );
  
  return await response.json();
};
```

#### Response:

```json
{
  "success": true,
  "message": "Notification statistics retrieved successfully",
  "data": {
    "total": 150,
    "unread": 25,
    "read": 125
  }
}
```

#### UI Example:

```jsx
const [stats, setStats] = useState({ total: 0, unread: 0, read: 0 });

useEffect(() => {
  fetchNotificationStats().then(res => setStats(res.data));
}, []);

return (
  <div className="notification-stats">
    <div>إجمالي: {stats.total}</div>
    <div>غير مقروء: {stats.unread}</div>
    <div>مقروء: {stats.read}</div>
  </div>
);
```

---

## 4. تحديد كمقروء

### PATCH `/notifications/notifications/{id}/update/`

تحديث إشعار محدد (تحديد كمقروء/غير مقروء).

#### Single Notification:

```javascript
const markAsRead = async (notificationId) => {
  const response = await fetch(
    `http://167.71.40.9/notifications/notifications/${notificationId}/update/`,
    {
      method: 'PATCH',
      headers: {
        'Authorization': `Token ${authToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        is_read: true
      })
    }
  );
  
  return await response.json();
};

// استخدام
await markAsRead(123);
```

### POST `/notifications/notifications/mark-all-read/`

تحديد **جميع** الإشعارات كمقروءة (زر واحد).

#### Mark All as Read:

```javascript
const markAllAsRead = async () => {
  const response = await fetch(
    'http://167.71.40.9/notifications/notifications/mark-all-read/',
    {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authToken}`,
      }
    }
  );
  
  return await response.json();
};

// UI Example
<button onClick={markAllAsRead}>
  تحديد الكل كمقروء
</button>
```

#### Response:

```json
{
  "success": true,
  "message": "25 notifications marked as read",
  "data": {
    "updated_count": 25
  }
}
```

---

## 5. حذف إشعار

### DELETE `/notifications/notifications/{id}/delete/`

حذف إشعار محدد.

```javascript
const deleteNotification = async (notificationId) => {
  const response = await fetch(
    `http://167.71.40.9/notifications/notifications/${notificationId}/delete/`,
    {
      method: 'DELETE',
      headers: {
        'Authorization': `Token ${authToken}`,
      }
    }
  );
  
  return await response.json();
};

// UI Example
<button onClick={() => deleteNotification(notif.id)}>
  🗑️ حذف
</button>
```

---

## 6. المواضيع والاشتراكات

### GET `/notifications/topics/my-topics/`

جلب جميع المواضيع مع حالة الاشتراك.

#### Request:

```javascript
const fetchMyTopics = async () => {
  const response = await fetch(
    'http://167.71.40.9/notifications/topics/my-topics/',
    {
      headers: {
        'Authorization': `Token ${authToken}`,
      }
    }
  );
  
  return await response.json();
};
```

#### Response:

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "عروض وخصومات",
      "description": "جميع العروض والخصومات الحصرية",
      "subscribers_count": 150,
      "is_subscribed": true,
      "subscription_active": true
    },
    {
      "id": 2,
      "name": "أخبار النظام",
      "description": "آخر الأخبار والتحديثات",
      "subscribers_count": 200,
      "is_subscribed": false,
      "subscription_active": false
    }
  ]
}
```

#### UI Example:

```jsx
const TopicsManager = () => {
  const [topics, setTopics] = useState([]);
  
  useEffect(() => {
    fetchMyTopics().then(res => setTopics(res.data));
  }, []);
  
  const toggleSubscription = async (topicId, isSubscribed) => {
    if (isSubscribed) {
      // إلغاء الاشتراك
      await unsubscribeFromTopic(topicId);
    } else {
      // الاشتراك
      await subscribeToTopic(topicId);
    }
    // Reload
    fetchMyTopics().then(res => setTopics(res.data));
  };
  
  return (
    <div className="topics-list">
      {topics.map(topic => (
        <div key={topic.id} className="topic-item">
          <h3>{topic.name}</h3>
          <p>{topic.description}</p>
          <p>المشتركون: {topic.subscribers_count}</p>
          <button onClick={() => toggleSubscription(topic.id, topic.is_subscribed)}>
            {topic.is_subscribed ? '✅ مشترك' : '➕ اشترك'}
          </button>
        </div>
      ))}
    </div>
  );
};
```

### POST `/notifications/subscriptions/create/`

الاشتراك في موضوع.

```javascript
const subscribeToTopic = async (topicId) => {
  const response = await fetch(
    'http://167.71.40.9/notifications/subscriptions/create/',
    {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        topic: topicId,
        is_active: true
      })
    }
  );
  
  return await response.json();
};
```

### DELETE `/notifications/subscriptions/{id}/delete/`

إلغاء الاشتراك.

```javascript
const unsubscribeFromTopic = async (subscriptionId) => {
  const response = await fetch(
    `http://167.71.40.9/notifications/subscriptions/${subscriptionId}/delete/`,
    {
      method: 'DELETE',
      headers: {
        'Authorization': `Token ${authToken}`,
      }
    }
  );
  
  return await response.json();
};
```

---

## 7. حالة الوردية

### GET `/core/shifts/current/`

التحقق من حالة النظام (هل متاح أم مغلق).

#### Request:

```javascript
const checkSystemStatus = async () => {
  const response = await fetch(
    'http://167.71.40.9/core/shifts/current/',
    {
      headers: {
        'Authorization': `Token ${authToken}`,
      }
    }
  );
  
  return await response.json();
};
```

#### Response (نشط):

```json
{
  "success": true,
  "message": "الوردية النشطة الحالية",
  "data": {
    "id": 123,
    "status": "ACTIVE",
    "started_by": {
      "id": 1,
      "username": "admin",
      "name": "Admin"
    },
    "start_time": "2025-10-17T18:00:00Z",
    "duration": "3.5 ساعة (مستمرة)",
    "total_sale_invoices": 45
  }
}
```

#### Response (مغلق):

```json
{
  "success": true,
  "message": "لا توجد وردية نشطة حالياً",
  "data": null
}
```

#### UI Example:

```jsx
const SystemStatusBanner = () => {
  const [isSystemOpen, setIsSystemOpen] = useState(false);
  const [shiftData, setShiftData] = useState(null);
  
  useEffect(() => {
    const checkStatus = async () => {
      const res = await checkSystemStatus();
      setIsSystemOpen(res.data !== null);
      setShiftData(res.data);
    };
    
    checkStatus();
    
    // التحقق كل دقيقة
    const interval = setInterval(checkStatus, 60000);
    return () => clearInterval(interval);
  }, []);
  
  if (!isSystemOpen) {
    return (
      <div className="system-status-banner closed">
        🔴 النظام مغلق حالياً. سنكون متاحين قريباً.
      </div>
    );
  }
  
  return (
    <div className="system-status-banner open">
      🟢 النظام متاح - بدأ الساعة {formatTime(shiftData.start_time)}
    </div>
  );
};
```

---

## 📱 مكونات React كاملة

### 1. Notifications List Component

```jsx
import React, { useState, useEffect } from 'react';
import { Bell, Check, Trash2 } from 'lucide-react';

const NotificationsList = ({ authToken }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  
  const API_BASE = 'http://167.71.40.9';
  
  const fetchNotifications = async (pageNum = 1) => {
    try {
      setLoading(true);
      const response = await fetch(
        `${API_BASE}/notifications/notifications/?page=${pageNum}&page_size=20`,
        {
          headers: {
            'Authorization': `Token ${authToken}`,
          }
        }
      );
      
      const data = await response.json();
      setNotifications(data.results);
      setHasMore(data.next !== null);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching notifications:', error);
      setLoading(false);
    }
  };
  
  const markAsRead = async (notifId) => {
    try {
      await fetch(
        `${API_BASE}/notifications/notifications/${notifId}/update/`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Token ${authToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ is_read: true })
        }
      );
      
      // Refresh list
      fetchNotifications(page);
    } catch (error) {
      console.error('Error marking as read:', error);
    }
  };
  
  const deleteNotification = async (notifId) => {
    try {
      await fetch(
        `${API_BASE}/notifications/notifications/${notifId}/delete/`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Token ${authToken}`,
          }
        }
      );
      
      // Refresh list
      fetchNotifications(page);
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };
  
  const markAllAsRead = async () => {
    try {
      await fetch(
        `${API_BASE}/notifications/notifications/mark-all-read/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Token ${authToken}`,
          }
        }
      );
      
      fetchNotifications(page);
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };
  
  useEffect(() => {
    fetchNotifications(page);
  }, [page]);
  
  if (loading) {
    return <div className="loading">جاري التحميل...</div>;
  }
  
  return (
    <div className="notifications-container">
      <div className="notifications-header">
        <h2>الإشعارات</h2>
        <button onClick={markAllAsRead} className="btn-mark-all">
          تحديد الكل كمقروء
        </button>
      </div>
      
      <div className="notifications-list">
        {notifications.map(notif => (
          <div 
            key={notif.id} 
            className={`notification-item ${notif.is_read ? 'read' : 'unread'}`}
          >
            <div className="notification-content">
              <h3>{notif.title}</h3>
              <p>{notif.message}</p>
              <span className="notification-time">
                {formatDate(notif.created_at)}
              </span>
            </div>
            
            <div className="notification-actions">
              {!notif.is_read && (
                <button 
                  onClick={() => markAsRead(notif.id)}
                  className="btn-icon"
                  title="تحديد كمقروء"
                >
                  <Check size={16} />
                </button>
              )}
              
              <button 
                onClick={() => deleteNotification(notif.id)}
                className="btn-icon"
                title="حذف"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>
      
      {/* Pagination */}
      <div className="pagination">
        <button 
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
        >
          السابق
        </button>
        <span>صفحة {page}</span>
        <button 
          onClick={() => setPage(p => p + 1)}
          disabled={!hasMore}
        >
          التالي
        </button>
      </div>
    </div>
  );
};

export default NotificationsList;
```

---

### 2. Notification Badge Component

```jsx
import React, { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';

const NotificationBadge = ({ authToken }) => {
  const [unreadCount, setUnreadCount] = useState(0);
  const API_BASE = 'http://167.71.40.9';
  
  const fetchUnreadCount = async () => {
    try {
      const response = await fetch(
        `${API_BASE}/notifications/notifications/stats/`,
        {
          headers: {
            'Authorization': `Token ${authToken}`,
          }
        }
      );
      
      const data = await response.json();
      setUnreadCount(data.data.unread);
    } catch (error) {
      console.error('Error fetching unread count:', error);
    }
  };
  
  useEffect(() => {
    fetchUnreadCount();
    
    // Refresh كل 30 ثانية
    const interval = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="notification-badge-container">
      <Bell size={24} />
      {unreadCount > 0 && (
        <span className="badge">{unreadCount}</span>
      )}
    </div>
  );
};

export default NotificationBadge;
```

#### CSS:

```css
.notification-badge-container {
  position: relative;
  cursor: pointer;
}

.notification-badge-container .badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ef4444;
  color: white;
  border-radius: 50%;
  padding: 2px 6px;
  font-size: 12px;
  font-weight: bold;
  min-width: 20px;
  text-align: center;
}
```

---

### 3. Real-time Notifications (Polling)

```jsx
const useNotifications = (authToken) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const API_BASE = 'http://167.71.40.9';
  
  const fetchUnread = async () => {
    try {
      const response = await fetch(
        `${API_BASE}/notifications/notifications/unread/`,
        {
          headers: {
            'Authorization': `Token ${authToken}`,
          }
        }
      );
      
      const data = await response.json();
      setNotifications(data.results);
      setUnreadCount(data.results.length);
      
      // عرض toast للإشعارات الجديدة
      if (data.results.length > unreadCount) {
        const newNotifs = data.results.slice(0, data.results.length - unreadCount);
        newNotifs.forEach(notif => {
          showToast(notif.title, notif.message);
        });
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };
  
  useEffect(() => {
    fetchUnread();
    
    // Poll كل 30 ثانية
    const interval = setInterval(fetchUnread, 30000);
    return () => clearInterval(interval);
  }, []);
  
  return { notifications, unreadCount };
};

// استخدام
const App = () => {
  const { notifications, unreadCount } = useNotifications(authToken);
  
  return (
    <div>
      <NotificationBadge count={unreadCount} />
      {/* ... */}
    </div>
  );
};
```

---

### 4. System Status Banner

```jsx
const SystemStatusBanner = ({ authToken }) => {
  const [systemOpen, setSystemOpen] = useState(true);
  const [shiftData, setShiftData] = useState(null);
  const API_BASE = 'http://167.71.40.9';
  
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch(
          `${API_BASE}/core/shifts/current/`,
          {
            headers: {
              'Authorization': `Token ${authToken}`,
            }
          }
        );
        
        const data = await response.json();
        setSystemOpen(data.data !== null);
        setShiftData(data.data);
      } catch (error) {
        console.error('Error checking system status:', error);
      }
    };
    
    checkStatus();
    const interval = setInterval(checkStatus, 60000); // كل دقيقة
    return () => clearInterval(interval);
  }, []);
  
  if (!systemOpen) {
    return (
      <div className="banner banner-closed">
        <span className="status-icon">🔴</span>
        <div>
          <strong>النظام مغلق حالياً</strong>
          <p>سنكون متاحين قريباً. شكراً لصبركم.</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="banner banner-open">
      <span className="status-icon">🟢</span>
      <div>
        <strong>النظام متاح</strong>
        <p>يمكنكم تقديم طلباتكم الآن</p>
      </div>
    </div>
  );
};
```

---

## 📊 أنواع الإشعارات للصيدليات

### الإشعارات التي تستقبلها الصيدلية:

| النوع | `extra.type` | الوصف |
|------|--------------|-------|
| 🛒 طلب جديد | `sale_invoice` | عند إنشاء طلب |
| 🔔 تحديث الطلب | `invoice_status_update` | تغيير حالة الطلب |
| ✅ دفعة مسجلة | `sale_payment` | عند تسجيل دفعة |
| ↩️ مرتجع | `sale_return` | عند إنشاء مرتجع |
| ✅ موافقة مرتجع | `return_approved` | الموافقة على المرتجع |
| ❌ رفض مرتجع | `return_rejected` | رفض المرتجع |
| 💰 استرداد | `refund_processed` | استرداد مبلغ |
| ✅ حل شكوى | `complaint_resolved` | حل الشكوى |
| ✨ **Wishlist** | `wishlist_product_available` | توفر منتج ⭐ |
| ⏰ **تذكير دفع** | `payment_due_reminder` | قبل الموعد ⭐ |
| ⚠️ **تأخير دفع** | `payment_overdue` | بعد الموعد ⭐ |
| 🟢 **نظام متاح** | `shift_started` | بدء الوردية ⭐ |
| 🔴 **نظام مغلق** | `shift_closed` | إغلاق الوردية ⭐ |

### معالجة حسب النوع:

```javascript
const handleNotificationClick = (notification) => {
  const { type } = notification.extra;
  
  switch(type) {
    case 'sale_invoice':
    case 'invoice_status_update':
      // فتح صفحة الطلب
      navigateTo(`/orders/${notification.extra.invoice_id}`);
      break;
      
    case 'sale_payment':
      // فتح صفحة الدفعات
      navigateTo(`/payments/${notification.extra.payment_id}`);
      break;
      
    case 'wishlist_product_available':
      // فتح صفحة المنتج
      navigateTo(`/products/${notification.extra.product_id}`);
      break;
      
    case 'payment_due_reminder':
    case 'payment_overdue':
      // فتح صفحة الدفع
      navigateTo('/payments');
      break;
      
    case 'shift_started':
      // عرض رسالة ترحيب
      showWelcomeMessage();
      break;
      
    case 'shift_closed':
      // عرض رسالة إغلاق
      showClosedMessage();
      break;
      
    default:
      // افتراضي
      console.log('Notification:', notification);
  }
  
  // تحديد كمقروء
  markAsRead(notification.id);
};
```

---

## 🎨 UI/UX Best Practices

### 1. Toast Notifications للإشعارات الجديدة

```jsx
import { toast } from 'react-toastify';

const showNotificationToast = (notification) => {
  const { title, message, extra } = notification;
  
  // أيقونات حسب النوع
  const icons = {
    'sale_invoice': '🛒',
    'payment_due_reminder': '⏰',
    'wishlist_product_available': '✨',
    'shift_started': '🟢',
    'shift_closed': '🔴',
  };
  
  const icon = icons[extra.type] || '🔔';
  
  toast.info(
    <div>
      <strong>{icon} {title}</strong>
      <p>{message}</p>
    </div>,
    {
      position: 'top-right',
      autoClose: 5000,
      onClick: () => handleNotificationClick(notification)
    }
  );
};
```

---

### 2. Notification Card Design

```jsx
const NotificationCard = ({ notification, onRead, onDelete }) => {
  const getIcon = (type) => {
    const icons = {
      'sale_invoice': '🛒',
      'invoice_status_update': '🔔',
      'payment_due_reminder': '⏰',
      'wishlist_product_available': '✨',
      'shift_started': '🟢',
      'shift_closed': '🔴',
    };
    return icons[type] || '📢';
  };
  
  const getPriority = (type) => {
    if (['payment_overdue', 'payment_due_reminder'].includes(type)) {
      return 'high';
    }
    if (type === 'wishlist_product_available') {
      return 'medium';
    }
    return 'normal';
  };
  
  const icon = getIcon(notification.extra.type);
  const priority = getPriority(notification.extra.type);
  
  return (
    <div className={`notification-card ${priority} ${notification.is_read ? 'read' : 'unread'}`}>
      <div className="notification-icon">{icon}</div>
      
      <div className="notification-body">
        <h4>{notification.title}</h4>
        <p>{notification.message}</p>
        <small>{formatTimeAgo(notification.created_at)}</small>
      </div>
      
      <div className="notification-actions">
        {!notification.is_read && (
          <button onClick={() => onRead(notification.id)}>✓</button>
        )}
        <button onClick={() => onDelete(notification.id)}>🗑️</button>
      </div>
    </div>
  );
};
```

#### CSS:

```css
.notification-card {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 12px;
  background: white;
  border-left: 4px solid #e5e7eb;
  transition: all 0.3s;
}

.notification-card.unread {
  background: #f0f9ff;
  border-left-color: #3b82f6;
}

.notification-card.high {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.notification-card.medium {
  border-left-color: #f59e0b;
}

.notification-icon {
  font-size: 24px;
}

.notification-body h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #1f2937;
}

.notification-body p {
  margin: 0 0 8px 0;
  color: #6b7280;
  font-size: 14px;
}

.notification-body small {
  color: #9ca3af;
  font-size: 12px;
}

.notification-actions {
  display: flex;
  gap: 8px;
}

.notification-actions button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.notification-actions button:hover {
  background: #f3f4f6;
}
```

---

### 3. Notification Dropdown

```jsx
const NotificationDropdown = ({ authToken }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const API_BASE = 'http://167.71.40.9';
  
  const fetchUnread = async () => {
    const response = await fetch(
      `${API_BASE}/notifications/notifications/unread/?page_size=5`,
      {
        headers: { 'Authorization': `Token ${authToken}` }
      }
    );
    const data = await response.json();
    setNotifications(data.results);
    setUnreadCount(data.count);
  };
  
  useEffect(() => {
    fetchUnread();
    const interval = setInterval(fetchUnread, 30000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="notification-dropdown">
      <button onClick={() => setIsOpen(!isOpen)}>
        <Bell />
        {unreadCount > 0 && (
          <span className="badge">{unreadCount}</span>
        )}
      </button>
      
      {isOpen && (
        <div className="dropdown-menu">
          <div className="dropdown-header">
            <h3>الإشعارات</h3>
            <span className="count">{unreadCount} جديد</span>
          </div>
          
          <div className="dropdown-body">
            {notifications.map(notif => (
              <div key={notif.id} className="dropdown-item">
                <p className="title">{notif.title}</p>
                <p className="message">{notif.message.substring(0, 60)}...</p>
                <small>{formatTimeAgo(notif.created_at)}</small>
              </div>
            ))}
          </div>
          
          <div className="dropdown-footer">
            <a href="/notifications">عرض الكل</a>
          </div>
        </div>
      )}
    </div>
  );
};
```

---

## 🔔 Push Notifications (المستقبل)

عند تفعيل FCM لاحقاً:

```javascript
// Service Worker للـ Push Notifications
self.addEventListener('push', function(event) {
  const data = event.data.json();
  
  const options = {
    body: data.message,
    icon: '/icon.png',
    badge: '/badge.png',
    data: {
      url: data.url,
      notificationId: data.id
    }
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});
```

---

## 📚 Helper Functions

```javascript
// تنسيق التاريخ
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ar-EG', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// منذ متى
const formatTimeAgo = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now - date) / 1000);
  
  if (seconds < 60) return 'الآن';
  if (seconds < 3600) return `منذ ${Math.floor(seconds / 60)} دقيقة`;
  if (seconds < 86400) return `منذ ${Math.floor(seconds / 3600)} ساعة`;
  return `منذ ${Math.floor(seconds / 86400)} يوم`;
};

// ألوان حسب النوع
const getNotificationColor = (type) => {
  const colors = {
    'sale_invoice': '#3b82f6',
    'payment_due_reminder': '#f59e0b',
    'payment_overdue': '#ef4444',
    'wishlist_product_available': '#10b981',
    'shift_started': '#22c55e',
    'shift_closed': '#6b7280',
  };
  return colors[type] || '#6b7280';
};
```

---

## 🎯 ملخص Endpoints للصيدليات

| Endpoint | Method | الاستخدام |
|----------|--------|-----------|
| `/notifications/notifications/` | GET | قائمة الإشعارات |
| `/notifications/notifications/unread/` | GET | غير المقروءة فقط |
| `/notifications/notifications/stats/` | GET | الإحصائيات |
| `/notifications/notifications/{id}/update/` | PATCH | تحديد كمقروء |
| `/notifications/notifications/{id}/delete/` | DELETE | حذف |
| `/notifications/notifications/mark-all-read/` | POST | تحديد الكل |
| `/notifications/topics/my-topics/` | GET | المواضيع + الاشتراكات |
| `/notifications/subscriptions/create/` | POST | الاشتراك |
| `/notifications/subscriptions/{id}/delete/` | DELETE | إلغاء الاشتراك |
| `/core/shifts/current/` | GET | حالة النظام |

---

## ✅ Complete Example - Notifications Page

```jsx
import React, { useState, useEffect } from 'react';

const PharmacyNotificationsPage = ({ authToken }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, unread, read
  const [stats, setStats] = useState({ total: 0, unread: 0, read: 0 });
  
  const API_BASE = 'http://167.71.40.9';
  
  const fetchNotifications = async () => {
    setLoading(true);
    
    let url = `${API_BASE}/notifications/notifications/`;
    if (filter === 'unread') {
      url = `${API_BASE}/notifications/notifications/unread/`;
    } else if (filter === 'read') {
      url = `${API_BASE}/notifications/notifications/?is_read=true`;
    }
    
    const response = await fetch(url, {
      headers: { 'Authorization': `Token ${authToken}` }
    });
    
    const data = await response.json();
    setNotifications(data.results);
    setLoading(false);
  };
  
  const fetchStats = async () => {
    const response = await fetch(
      `${API_BASE}/notifications/notifications/stats/`,
      {
        headers: { 'Authorization': `Token ${authToken}` }
      }
    );
    const data = await response.json();
    setStats(data.data);
  };
  
  useEffect(() => {
    fetchNotifications();
    fetchStats();
  }, [filter]);
  
  const markAsRead = async (id) => {
    await fetch(
      `${API_BASE}/notifications/notifications/${id}/update/`,
      {
        method: 'PATCH',
        headers: {
          'Authorization': `Token ${authToken}`,
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
        headers: { 'Authorization': `Token ${authToken}` }
      }
    );
    
    fetchNotifications();
    fetchStats();
  };
  
  return (
    <div className="notifications-page">
      {/* Header */}
      <div className="page-header">
        <h1>📬 الإشعارات</h1>
        <button onClick={markAllAsRead} className="btn-primary">
          تحديد الكل كمقروء
        </button>
      </div>
      
      {/* Stats */}
      <div className="stats-row">
        <div className="stat-card">
          <span className="stat-number">{stats.total}</span>
          <span className="stat-label">الإجمالي</span>
        </div>
        <div className="stat-card highlight">
          <span className="stat-number">{stats.unread}</span>
          <span className="stat-label">غير مقروء</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">{stats.read}</span>
          <span className="stat-label">مقروء</span>
        </div>
      </div>
      
      {/* Filters */}
      <div className="filters">
        <button 
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          الكل ({stats.total})
        </button>
        <button 
          className={filter === 'unread' ? 'active' : ''}
          onClick={() => setFilter('unread')}
        >
          غير مقروء ({stats.unread})
        </button>
        <button 
          className={filter === 'read' ? 'active' : ''}
          onClick={() => setFilter('read')}
        >
          مقروء ({stats.read})
        </button>
      </div>
      
      {/* Notifications List */}
      {loading ? (
        <div className="loading">جاري التحميل...</div>
      ) : (
        <div className="notifications-list">
          {notifications.map(notif => (
            <NotificationCard
              key={notif.id}
              notification={notif}
              onRead={markAsRead}
              onDelete={() => {/* delete logic */}}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default PharmacyNotificationsPage;
```

---

## 🎊 الخلاصة

### للـ Frontend Developer:

✅ **10 Endpoints** جاهزة للاستخدام  
✅ **13 نوع إشعار** مختلف  
✅ **Real-time polling** كل 30 ثانية  
✅ **Filters متقدمة**  
✅ **Pagination** جاهزة  
✅ **React Components** جاهزة للاستخدام  
✅ **UI/UX Examples** كاملة  

**كل شيء موثق وجاهز للتطبيق! 🚀**

---

## 📝 ملاحظات مهمة

1. **استبدل IP** `167.71.40.9` بالـ domain الفعلي في Production
2. **استخدم HTTPS** في Production
3. **أضف Error Handling** لجميع الطلبات
4. **Cache الـ token** بشكل آمن
5. **استخدم Polling** (30 ثانية) أو **WebSockets** للـ real-time

---

**الملف جاهز في `notifications/PHARMACY_FRONTEND_API.md`! 📚**

