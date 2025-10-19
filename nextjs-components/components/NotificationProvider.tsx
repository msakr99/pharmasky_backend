// components/NotificationProvider.tsx
'use client';

import { useEffect } from 'react';
import { useNotifications } from '@/hooks/useNotifications';
import { Bell, BellOff, BellRing } from 'lucide-react';
import { toast } from 'sonner';

interface NotificationProviderProps {
  authToken: string | null;
  children: React.ReactNode;
}

export default function NotificationProvider({ authToken, children }: NotificationProviderProps) {
  const { permission, requestPermission, isLoading } = useNotifications({
    authToken,
    autoRequest: false, // غيّره لـ true لطلب الإذن تلقائياً
  });

  // عرض Toast للطلب الأول
  useEffect(() => {
    if (permission === 'default' && authToken) {
      const hasAskedBefore = localStorage.getItem('notification-permission-asked');
      
      if (!hasAskedBefore) {
        // اسأل المستخدم بعد 5 ثواني
        const timer = setTimeout(() => {
          toast.info('🔔 تفعيل الإشعارات', {
            description: 'فعّل الإشعارات لتصلك التحديثات فوراً',
            duration: 10000,
            action: {
              label: 'تفعيل',
              onClick: async () => {
                await requestPermission();
                localStorage.setItem('notification-permission-asked', 'true');
              },
            },
          });
        }, 5000);

        return () => clearTimeout(timer);
      }
    }
  }, [permission, authToken, requestPermission]);

  return <>{children}</>;
}

/**
 * Component بسيط لزر تفعيل الإشعارات
 */
export function NotificationButton({ authToken }: { authToken: string }) {
  const { permission, requestPermission, isLoading } = useNotifications({ authToken });

  if (permission === 'granted') {
    return (
      <div className="flex items-center gap-2 text-sm text-green-600">
        <BellRing className="h-4 w-4" />
        <span>الإشعارات مفعّلة</span>
      </div>
    );
  }

  if (permission === 'denied') {
    return (
      <div className="flex items-center gap-2 text-sm text-red-600">
        <BellOff className="h-4 w-4" />
        <span>الإشعارات معطلة</span>
      </div>
    );
  }

  return (
    <button
      onClick={requestPermission}
      disabled={isLoading}
      className="flex items-center gap-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <Bell className="h-4 w-4" />
      <span>{isLoading ? 'جاري التفعيل...' : 'تفعيل الإشعارات'}</span>
    </button>
  );
}

