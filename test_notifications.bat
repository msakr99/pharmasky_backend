@echo off
chcp 65001 >nul
title 🔔 اختبار نظام الإشعارات - PharmaSky

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                🔔 اختبار نظام الإشعارات                          ║
echo ║                      PharmaSky System                              ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

REM تفعيل البيئة الافتراضية
if exist "venv\Scripts\activate.bat" (
    echo 📦 تفعيل البيئة الافتراضية...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  تحذير: لم يتم العثور على البيئة الافتراضية
    echo    سيتم استخدام Python الافتراضي
)

echo.
echo ══════════════════════════════════════════════════════════════════════
echo.
echo اختر العملية التي تريد تنفيذها:
echo.
echo   1. تشغيل السيرفر
echo   2. إنشاء بيانات تجريبية (10 إشعارات)
echo   3. إنشاء بيانات تجريبية متقدمة (مع مواضيع)
echo   4. تشغيل السكريبت التفاعلي للاختبار
echo   5. فتح Django Shell
echo   0. خروج
echo.
echo ══════════════════════════════════════════════════════════════════════
echo.

set /p choice="اختيارك (0-5): "

if "%choice%"=="1" goto run_server
if "%choice%"=="2" goto create_basic_data
if "%choice%"=="3" goto create_advanced_data
if "%choice%"=="4" goto run_test_script
if "%choice%"=="5" goto open_shell
if "%choice%"=="0" goto end

echo ❌ اختيار غير صحيح
pause
goto end

:run_server
echo.
echo 🚀 تشغيل السيرفر...
echo ════════════════════════════════════════════════════════════════════
echo السيرفر سيعمل على: http://127.0.0.1:8000
echo اضغط Ctrl+C لإيقاف السيرفر
echo ════════════════════════════════════════════════════════════════════
echo.
python manage.py runserver
pause
goto end

:create_basic_data
echo.
echo 📦 إنشاء بيانات تجريبية أساسية...
echo ════════════════════════════════════════════════════════════════════
python manage.py create_test_notifications --count 10 --mark-some-read
echo.
echo ✅ تم إنشاء البيانات التجريبية بنجاح!
echo.
pause
goto end

:create_advanced_data
echo.
echo 📦 إنشاء بيانات تجريبية متقدمة...
echo ════════════════════════════════════════════════════════════════════
python manage.py create_test_notifications --with-topics --count 20 --mark-some-read
echo.
echo ✅ تم إنشاء البيانات التجريبية بنجاح!
echo.
pause
goto end

:run_test_script
echo.
echo 🧪 تشغيل السكريبت التفاعلي...
echo ════════════════════════════════════════════════════════════════════
echo تأكد من تشغيل السيرفر في نافذة أخرى!
echo.
python test_notifications.py
pause
goto end

:open_shell
echo.
echo 🐚 فتح Django Shell...
echo ════════════════════════════════════════════════════════════════════
echo.
python manage.py shell
pause
goto end

:end
echo.
echo 👋 شكراً لاستخدامك نظام الإشعارات!
echo.

