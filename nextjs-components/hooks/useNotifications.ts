// hooks/useNotifications.ts
'use client';

import { useEffect, useState, useCallback } from 'react';
import { messaging, requestNotificationPermission, saveFCMTokenToServer, onMessageListener } from '@/lib/firebase';
import { toast } from 'sonner'; // أو أي toast library تستخدمها

interface UseNotificationsProps {
  authToken: string | null;
  autoRequest?: boolean; // طلب الإذن تلقائياً
}

interface NotificationData {
  title: string;
  body: string;
  data?: any;
}

export function useNotifications({ authToken, autoRequest = false }: UseNotificationsProps) {
  const [fcmToken, setFcmToken] = useState<string | null>(null);
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [latestNotification, setLatestNotification] = useState<NotificationData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // طلب الإذن والحصول على Token
  const requestPermission = useCallback(async () => {
    if (!authToken) {
      console.warn('⚠️ Auth token مطلوب لحفظ FCM token');
      return null;
    }

    setIsLoading(true);

    try {
      // طلب الإذن والحصول على Token
      const token = await requestNotificationPermission();
      
      if (token) {
        setFcmToken(token);
        setPermission('granted');
        
        // حفظ في السيرفر
        const saved = await saveFCMTokenToServer(token, authToken);
        
        if (saved) {
          toast.success('✅ تم تفعيل الإشعارات بنجاح');
        } else {
          toast.error('❌ فشل حفظ Token في السيرفر');
        }
        
        return token;
      } else {
        setPermission(Notification.permission);
        if (Notification.permission === 'denied') {
          toast.error('❌ تم رفض إذن الإشعارات');
        }
        return null;
      }
    } catch (error) {
      console.error('❌ خطأ في requestPermission:', error);
      toast.error('❌ حدث خطأ في تفعيل الإشعارات');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [authToken]);

  // الاستماع للإشعارات في Foreground
  useEffect(() => {
    if (!messaging || !authToken) return;

    // استماع مستمر للإشعارات
    const unsubscribe = onMessageListener().then((payload: any) => {
      console.log('📩 إشعار جديد في Foreground:', payload);
      
      const notificationData: NotificationData = {
        title: payload.notification?.title || 'إشعار جديد',
        body: payload.notification?.body || '',
        data: payload.data,
      };

      setLatestNotification(notificationData);

      // عرض Toast
      toast(notificationData.title, {
        description: notificationData.body,
        duration: 5000,
        action: {
          label: 'عرض',
          onClick: () => {
            // التنقل حسب نوع الإشعار
            handleNotificationClick(notificationData.data);
          },
        },
      });
    });

    return () => {
      // cleanup
    };
  }, [authToken]);

  // طلب الإذن تلقائياً عند التحميل
  useEffect(() => {
    if (autoRequest && authToken && permission === 'default') {
      requestPermission();
    }
  }, [autoRequest, authToken, permission, requestPermission]);

  // تحديث حالة الإذن
  useEffect(() => {
    if (typeof window !== 'undefined') {
      setPermission(Notification.permission);
    }
  }, []);

  return {
    fcmToken,
    permission,
    latestNotification,
    isLoading,
    requestPermission,
  };
}

// معالجة النقر على الإشعار
function handleNotificationClick(data: any) {
  const type = data?.type;
  
  switch (type) {
    case 'sale_invoice':
    case 'invoice_status_update':
      window.location.href = `/orders/${data?.invoice_id || ''}`;
      break;
    case 'sale_payment':
      window.location.href = '/payments';
      break;
    case 'wishlist_product_available':
      window.location.href = `/products/${data?.product_id || ''}`;
      break;
    case 'payment_due_reminder':
    case 'payment_overdue':
      window.location.href = '/payments/due';
      break;
    default:
      window.location.href = '/notifications';
  }
}

