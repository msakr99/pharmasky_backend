// components/NotificationsList.tsx
'use client';

import { useState, useEffect } from 'react';
import { Bell, Check, Trash2, RefreshCw } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { ar } from 'date-fns/locale';

interface Notification {
  id: number;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
  extra: {
    type: string;
    [key: string]: any;
  };
}

interface NotificationsListProps {
  authToken: string;
}

export default function NotificationsList({ authToken }: NotificationsListProps) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [stats, setStats] = useState({ total: 0, unread: 0, read: 0 });
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'unread' | 'read'>('all');

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://167.71.40.9/api/v1';

  // جلب الإشعارات
  const fetchNotifications = async () => {
    setLoading(true);
    try {
      let url = `${API_BASE}/notifications/notifications/`;
      
      if (filter === 'unread') {
        url = `${API_BASE}/notifications/notifications/unread/`;
      } else if (filter === 'read') {
        url = `${API_BASE}/notifications/notifications/?is_read=true`;
      }

      const response = await fetch(url, {
        headers: {
          'Authorization': `Token ${authToken}`,
        },
      });

      const data = await response.json();
      setNotifications(data.results || []);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
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
      setStats(data.data || { total: 0, unread: 0, read: 0 });
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
      console.error('Error marking all as read:', error);
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
      console.error('Error deleting notification:', error);
    }
  };

  // تحديث تلقائي
  useEffect(() => {
    fetchNotifications();
    fetchStats();

    // Polling كل 30 ثانية
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, [filter]);

  // الحصول على أيقونة حسب النوع
  const getNotificationIcon = (type: string) => {
    const icons: Record<string, string> = {
      'sale_invoice': '🛒',
      'invoice_status_update': '🔔',
      'sale_payment': '💰',
      'payment_due_reminder': '⏰',
      'payment_overdue': '⚠️',
      'wishlist_product_available': '✨',
      'shift_started': '🟢',
      'shift_closed': '🔴',
      'special_offer': '🎁',
    };
    return icons[type] || '📢';
  };

  // الحصول على لون حسب الأولوية
  const getPriorityColor = (type: string) => {
    if (['payment_overdue', 'payment_due_reminder'].includes(type)) {
      return 'border-red-200 bg-red-50';
    }
    if (type === 'wishlist_product_available') {
      return 'border-orange-200 bg-orange-50';
    }
    return 'border-gray-200 bg-white';
  };

  return (
    <div className="max-w-4xl mx-auto p-4 md:p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Bell className="h-7 w-7 text-gray-700" />
          <h1 className="text-2xl md:text-3xl font-bold">الإشعارات</h1>
        </div>
        
        <button
          onClick={() => {
            fetchNotifications();
            fetchStats();
          }}
          className="p-2 hover:bg-gray-100 rounded-lg"
          title="تحديث"
        >
          <RefreshCw className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
          <div className="text-sm text-gray-500">الإجمالي</div>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">{stats.unread}</div>
          <div className="text-sm text-blue-600">غير مقروءة</div>
        </div>
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-gray-600">{stats.read}</div>
          <div className="text-sm text-gray-500">مقروءة</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 mb-6">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
            filter === 'all'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          الكل ({stats.total})
        </button>
        <button
          onClick={() => setFilter('unread')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
            filter === 'unread'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          غير مقروءة ({stats.unread})
        </button>
        <button
          onClick={() => setFilter('read')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
            filter === 'read'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          مقروءة ({stats.read})
        </button>
        
        {stats.unread > 0 && (
          <button
            onClick={markAllAsRead}
            className="mr-auto text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            تحديد الكل كمقروء
          </button>
        )}
      </div>

      {/* Notifications List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-500">جاري التحميل...</p>
        </div>
      ) : notifications.length === 0 ? (
        <div className="text-center py-12">
          <Bell className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">لا توجد إشعارات</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((notif) => (
            <div
              key={notif.id}
              className={`border rounded-lg p-4 transition hover:shadow-md ${
                notif.is_read ? 'bg-white border-gray-200' : 'bg-blue-50 border-blue-300'
              } ${getPriorityColor(notif.extra?.type || '')}`}
            >
              <div className="flex items-start gap-3">
                {/* Icon */}
                <div className="text-3xl">
                  {getNotificationIcon(notif.extra?.type || '')}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-lg mb-1">
                    {notif.title}
                  </h3>
                  <p className="text-gray-600 text-sm mb-2">
                    {notif.message}
                  </p>
                  <span className="text-xs text-gray-400">
                    {formatDistanceToNow(new Date(notif.created_at), {
                      addSuffix: true,
                      locale: ar,
                    })}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1">
                  {!notif.is_read && (
                    <button
                      onClick={() => markAsRead(notif.id)}
                      className="p-2 hover:bg-gray-100 rounded-lg transition"
                      title="تحديد كمقروء"
                    >
                      <Check className="h-4 w-4 text-green-600" />
                    </button>
                  )}
                  
                  <button
                    onClick={() => {
                      if (confirm('هل تريد حذف هذا الإشعار؟')) {
                        deleteNotification(notif.id);
                      }
                    }}
                    className="p-2 hover:bg-gray-100 rounded-lg transition"
                    title="حذف"
                  >
                    <Trash2 className="h-4 w-4 text-red-600" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

