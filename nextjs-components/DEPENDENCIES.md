# 📦 Dependencies المطلوبة لـ Next.js

## تثبيت سريع:

```bash
npm install firebase sonner date-fns lucide-react
```

أو:

```bash
yarn add firebase sonner date-fns lucide-react
```

---

## 📋 تفاصيل الـ Packages:

### 1. firebase (مطلوب ⭐)
```bash
npm install firebase
```
- **الاستخدام:** Firebase SDK للـ Web
- **الإصدار:** ^10.7.0 أو أحدث
- **الحجم:** ~200 KB
- **الملفات:** `lib/firebase.ts`, `hooks/useNotifications.ts`

---

### 2. sonner (مستحسن)
```bash
npm install sonner
```
- **الاستخدام:** Toast notifications جميلة
- **البديل:** react-hot-toast, react-toastify
- **الملفات:** `hooks/useNotifications.ts`, `components/NotificationProvider.tsx`

**إذا لم تستخدم sonner:**
```typescript
// استبدل
import { toast } from 'sonner';
toast.success('رسالة');

// بـ
console.log('رسالة'); // أو أي toast library تستخدمها
```

---

### 3. date-fns (مستحسن)
```bash
npm install date-fns
```
- **الاستخدام:** تنسيق التواريخ ("منذ 5 دقائق")
- **البديل:** moment, dayjs
- **الملفات:** `components/NotificationsList.tsx`

**إذا لم تستخدم date-fns:**
```typescript
// استبدل
formatDistanceToNow(new Date(notif.created_at), { locale: ar })

// بـ
new Date(notif.created_at).toLocaleDateString('ar-EG')
```

---

### 4. lucide-react (مستحسن)
```bash
npm install lucide-react
```
- **الاستخدام:** Icons جميلة
- **البديل:** react-icons, heroicons
- **الملفات:** جميع الـ Components

**إذا لم تستخدم lucide-react:**
استبدل الـ icons بأي library تستخدمها أو استخدم emojis:
```typescript
// بدلاً من
<Bell className="h-6 w-6" />

// استخدم
🔔 {/* emoji */}
```

---

## 📦 package.json مثال:

```json
{
  "name": "pharmasky-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    
    "firebase": "^10.7.1",
    "sonner": "^1.2.0",
    "date-fns": "^3.0.0",
    "lucide-react": "^0.300.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.4.0"
  }
}
```

---

## ⚙️ tsconfig.json (إذا كنت تستخدم TypeScript)

تأكد من وجود:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

---

## 🎨 Tailwind CSS (اختياري)

إذا كنت تستخدم Tailwind، تأكد من:

```javascript
// tailwind.config.js
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  // ...
}
```

---

## ✅ Dependencies الأساسية فقط:

إذا أردت الحد الأدنى:

```bash
# الضروري فقط
npm install firebase

# باقي الـ components ستحتاج تعديل بسيط
```

---

## 📖 روابط مفيدة:

- [Firebase Documentation](https://firebase.google.com/docs/web/setup)
- [Sonner Documentation](https://sonner.emilkowal.ski/)
- [date-fns Documentation](https://date-fns.org/)
- [Lucide Icons](https://lucide.dev/)

---

**جميع الملفات معدة للعمل مع هذه الـ Dependencies! 🚀**

