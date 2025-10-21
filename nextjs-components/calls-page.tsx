// app/calls/page.tsx - Calls List Page
'use client';

import { useEffect, useState } from 'react';
import { getCalls } from '@/lib/api';
import CallsList from '@/components/CallsList';
import { Search, Filter } from 'lucide-react';

export default function CallsPage() {
  const [calls, setCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: '',
    search: '',
    page: 1,
  });

  useEffect(() => {
    loadCalls();
  }, [filters]);

  const loadCalls = async () => {
    try {
      setLoading(true);
      const data = await getCalls({
        status: filters.status || undefined,
        page: filters.page,
        page_size: 20,
      });
      setCalls(data.results || []);
    } catch (error) {
      console.error('Error loading calls:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8" dir="rtl">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          📞 المكالمات الصوتية
        </h1>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                البحث
              </label>
              <div className="relative">
                <Search className="absolute right-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="ابحث عن صيدلية..."
                  className="w-full pr-10 pl-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={filters.search}
                  onChange={(e) =>
                    setFilters({ ...filters, search: e.target.value })
                  }
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                الحالة
              </label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={filters.status}
                onChange={(e) =>
                  setFilters({ ...filters, status: e.target.value })
                }
              >
                <option value="">الكل</option>
                <option value="active">نشط</option>
                <option value="completed">مكتمل</option>
                <option value="failed">فشل</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={loadCalls}
                className="w-full bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                تحديث
              </button>
            </div>
          </div>
        </div>

        {/* Calls List */}
        <CallsList calls={calls} loading={loading} />
      </div>
    </div>
  );
}

