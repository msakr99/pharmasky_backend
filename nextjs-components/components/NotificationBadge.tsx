// components/NotificationBadge.tsx
'use client';

import { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';
import Link from 'next/link';

interface NotificationBadgeProps {
  authToken: string;
  showCount?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export default function NotificationBadge({
  authToken,
  showCount = true,
  size = 'md',
  className = '',
}: NotificationBadgeProps) {
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://167.71.40.9/api/v1';

  // جلب عدد الإشعارات غير المقروءة
  const fetchUnreadCount = async () => {
    try {
      const response = await fetch(`${API_BASE}/notifications/notifications/stats/`, {
        headers: {
          'Authorization': `Token ${authToken}`,
        },
        cache: 'no-store',
      });

      const data = await response.json();
      setUnreadCount(data.data?.unread || 0);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching unread count:', error);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!authToken) return;

    fetchUnreadCount();

    // تحديث كل 30 ثانية
    const interval = setInterval(fetchUnreadCount, 30000);

    return () => clearInterval(interval);
  }, [authToken]);

  // أحجام الأيقونة
  const iconSizes = {
    sm: 'h-5 w-5',
    md: 'h-6 w-6',
    lg: 'h-7 w-7',
  };

  // أحجام Badge
  const badgeSizes = {
    sm: 'h-4 w-4 text-[10px]',
    md: 'h-5 w-5 text-xs',
    lg: 'h-6 w-6 text-sm',
  };

  return (
    <Link 
      href="/notifications" 
      className={`relative inline-flex items-center justify-center ${className}`}
      title={`${unreadCount} إشعار غير مقروء`}
    >
      <Bell className={`${iconSizes[size]} text-gray-700 hover:text-gray-900 transition`} />
      
      {showCount && unreadCount > 0 && (
        <span className={`absolute -top-2 -right-2 bg-red-500 text-white rounded-full ${badgeSizes[size]} flex items-center justify-center font-bold shadow-md animate-pulse`}>
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      )}
      
      {!showCount && unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full animate-pulse"></span>
      )}
    </Link>
  );
}

/**
 * Notification Badge مع Dropdown
 */
export function NotificationBadgeWithDropdown({ authToken }: { authToken: string }) {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://167.71.40.9/api/v1';

  const fetchUnread = async () => {
    try {
      const [statsRes, notifsRes] = await Promise.all([
        fetch(`${API_BASE}/notifications/notifications/stats/`, {
          headers: { 'Authorization': `Token ${authToken}` }
        }),
        fetch(`${API_BASE}/notifications/notifications/unread/?page_size=5`, {
          headers: { 'Authorization': `Token ${authToken}` }
        })
      ]);

      const stats = await statsRes.json();
      const notifs = await notifsRes.json();

      setUnreadCount(stats.data?.unread || 0);
      setNotifications(notifs.results || []);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  useEffect(() => {
    if (authToken) {
      fetchUnread();
      const interval = setInterval(fetchUnread, 30000);
      return () => clearInterval(interval);
    }
  }, [authToken]);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 hover:bg-gray-100 rounded-lg transition"
      >
        <Bell className="h-6 w-6 text-gray-700" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute left-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b">
            <h3 className="font-semibold">الإشعارات</h3>
            <span className="text-sm text-gray-500">{unreadCount} جديد</span>
          </div>

          {/* Notifications */}
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                لا توجد إشعارات جديدة
              </div>
            ) : (
              notifications.map((notif) => (
                <Link
                  key={notif.id}
                  href="/notifications"
                  onClick={() => setIsOpen(false)}
                  className="block p-4 hover:bg-gray-50 border-b last:border-b-0"
                >
                  <p className="font-medium text-sm mb-1">{notif.title}</p>
                  <p className="text-xs text-gray-600 line-clamp-2">{notif.message}</p>
                  <span className="text-xs text-gray-400 mt-1 block">
                    {formatDate(notif.created_at)}
                  </span>
                </Link>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="p-3 border-t bg-gray-50">
            <Link
              href="/notifications"
              onClick={() => setIsOpen(false)}
              className="block text-center text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              عرض جميع الإشعارات
            </Link>
          </div>
        </div>
      )}

      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        ></div>
      )}
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

