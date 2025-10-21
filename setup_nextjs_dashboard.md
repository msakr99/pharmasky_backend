# إعداد Next.js Dashboard للنظام

## إنشاء المشروع

```bash
# في مجلد المشروع الرئيسي
npx create-next-app@latest dashboard --typescript --tailwind --app --no-src-dir
cd dashboard
```

## تثبيت المكتبات المطلوبة

```bash
npm install axios
npm install @tanstack/react-query
npm install date-fns
npm install lucide-react
```

## هيكل المشروع

```
dashboard/
├── app/
│   ├── layout.tsx          # Layout رئيسي
│   ├── page.tsx            # الصفحة الرئيسية (Dashboard)
│   ├── calls/
│   │   ├── page.tsx        # قائمة المكالمات
│   │   └── [id]/
│   │       └── page.tsx    # تفاصيل المكالمة
│   └── test/
│       └── page.tsx        # صفحة اختبار المكالمات
├── components/
│   ├── CallsList.tsx       # جدول المكالمات
│   ├── CallDetail.tsx      # تفاصيل مكالمة واحدة
│   ├── AudioPlayer.tsx     # مشغل الصوت
│   ├── Transcript.tsx      # عرض النص المكتوب
│   ├── Actions.tsx         # الأوامر المنفذة
│   └── WebRTCTest.tsx      # واجهة اختبار المكالمات
├── lib/
│   ├── api.ts              # API Client
│   └── types.ts            # TypeScript Types
└── public/
    └── ...
```

## الملفات الأساسية

سأقوم بإنشاء الملفات الأساسية في مجلد `nextjs-components/` حتى يمكنك نسخها بسهولة.

