// app/page.tsx - Dashboard Home
'use client';

import { useEffect, useState } from 'react';
import { Phone, CheckCircle, ShoppingCart, TrendingUp } from 'lucide-react';
import Link from 'next/link';
import { getCalls, checkHealth } from '@/lib/api';

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalCalls: 0,
    completedCalls: 0,
    totalOrders: 0,
    activeNow: 0,
  });
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Load calls
      const callsData = await getCalls({ page_size: 100 });
      const calls = callsData.results || [];
      
      setStats({
        totalCalls: callsData.count || 0,
        completedCalls: calls.filter((c: any) => c.status === 'completed').length,
        totalOrders: calls.reduce((sum: number, c: any) => sum + c.actions_count, 0),
        activeNow: calls.filter((c: any) => c.status === 'active').length,
      });

      // Load health
      const healthData = await checkHealth();
      setHealth(healthData);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const StatCard = ({ icon: Icon, title, value, color }: any) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className={`p-3 rounded-full ${color} bg-opacity-10`}>
          <Icon className={`w-8 h-8 ${color.replace('bg-', 'text-')}`} />
        </div>
        <div className="mr-4">
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-3xl font-bold">{value}</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-8" dir="rtl">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          🤖 لوحة التحكم - وكيل المبيعات الذكي
        </h1>

        {/* Health Status */}
        {health && (
          <div className="bg-white rounded-lg shadow p-4 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm text-gray-600">حالة النظام: </span>
                <span className="font-semibold text-green-600">{health.status}</span>
              </div>
              <div className="text-sm text-gray-500">
                الإصدار: {health.version}
              </div>
            </div>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={Phone}
            title="إجمالي المكالمات"
            value={stats.totalCalls}
            color="bg-blue-500"
          />
          <StatCard
            icon={CheckCircle}
            title="مكالمات مكتملة"
            value={stats.completedCalls}
            color="bg-green-500"
          />
          <StatCard
            icon={ShoppingCart}
            title="طلبات منفذة"
            value={stats.totalOrders}
            color="bg-purple-500"
          />
          <StatCard
            icon={TrendingUp}
            title="مكالمات نشطة"
            value={stats.activeNow}
            color="bg-orange-500"
          />
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link
            href="/calls"
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
          >
            <Phone className="w-12 h-12 text-blue-500 mb-3" />
            <h3 className="text-xl font-semibold mb-2">عرض المكالمات</h3>
            <p className="text-gray-600">
              استعرض جميع المكالمات السابقة والنصوص المكتوبة
            </p>
          </Link>

          <Link
            href="/test"
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
          >
            <TrendingUp className="w-12 h-12 text-green-500 mb-3" />
            <h3 className="text-xl font-semibold mb-2">اختبار المكالمات</h3>
            <p className="text-gray-600">
              اختبر النظام بمكالمة صوتية تجريبية
            </p>
          </Link>

          <div className="bg-white rounded-lg shadow p-6">
            <ShoppingCart className="w-12 h-12 text-purple-500 mb-3" />
            <h3 className="text-xl font-semibold mb-2">الإحصائيات</h3>
            <p className="text-gray-600">
              تقارير وإحصائيات شاملة عن الأداء
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

