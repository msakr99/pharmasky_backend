'use client';

import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { ar } from 'date-fns/locale';
import { Phone, Clock, User, CheckCircle, XCircle, Loader } from 'lucide-react';
import { Call } from '@/lib/types';

interface CallsListProps {
  calls: Call[];
  loading?: boolean;
}

export default function CallsList({ calls, loading }: CallsListProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!calls || calls.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg">
        <Phone className="w-12 h-12 mx-auto text-gray-400 mb-3" />
        <p className="text-gray-600">لا توجد مكالمات بعد</p>
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'active':
        return <Loader className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      active: 'نشط',
      completed: 'مكتمل',
      failed: 'فشل',
      cancelled: 'ملغي',
    };
    return statusMap[status] || status;
  };

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              الصيدلية
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              الحالة
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              المدة
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              الأوامر
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              التاريخ
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              الإجراءات
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {calls.map((call) => (
            <tr key={call.id} className="hover:bg-gray-50 transition-colors">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <User className="w-5 h-5 text-gray-400 ml-2" />
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {call.pharmacy?.name || 'غير محدد'}
                    </div>
                    {call.user && (
                      <div className="text-sm text-gray-500">
                        {call.user.username}
                      </div>
                    )}
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  {getStatusIcon(call.status)}
                  <span className="mr-2 text-sm">{getStatusText(call.status)}</span>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div className="flex items-center">
                  <Clock className="w-4 h-4 ml-1" />
                  {call.duration}s
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                  {call.actions_count} أمر
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatDistanceToNow(new Date(call.created_at), {
                  addSuffix: true,
                  locale: ar,
                })}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <Link
                  href={`/calls/${call.id}`}
                  className="text-blue-600 hover:text-blue-900"
                >
                  عرض التفاصيل
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

