"""
Django Management Command لاختبار نظام Push Notifications
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.utils import (
    send_push_to_user,
    send_push_notification,
    test_push_notification,
)
from notifications.models import FCMToken

User = get_user_model()


class Command(BaseCommand):
    help = "اختبار نظام Push Notifications مع FCM"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id",
            type=int,
            help="معرف المستخدم لإرسال إشعار تجريبي له",
        )
        parser.add_argument(
            "--list-tokens",
            action="store_true",
            help="عرض جميع الـ FCM Tokens المسجلة",
        )
        parser.add_argument(
            "--test",
            action="store_true",
            help="إرسال إشعار تجريبي",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(
            self.style.SUCCESS("اختبار نظام Push Notifications - Firebase Cloud Messaging")
        )
        self.stdout.write(self.style.SUCCESS("=" * 70))

        # عرض الـ FCM Tokens
        if options["list_tokens"]:
            self.list_tokens()
            return

        # إرسال إشعار تجريبي
        user_id = options.get("user_id")
        
        if options["test"] or user_id:
            if not user_id:
                # الحصول على أول مستخدم لديه FCM token
                first_token = FCMToken.objects.filter(is_active=True).first()
                if first_token:
                    user_id = first_token.user.id
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            "❌ لا يوجد مستخدمين مسجلين لديهم FCM Tokens"
                        )
                    )
                    self.stdout.write(
                        self.style.WARNING(
                            "يرجى تسجيل الدخول من المتصفح وتفعيل الإشعارات أولاً"
                        )
                    )
                    return
            
            self.send_test_notification(user_id)
            return

        # عرض معلومات عامة
        self.show_stats()

    def list_tokens(self):
        """عرض جميع الـ FCM Tokens المسجلة"""
        tokens = FCMToken.objects.select_related("user").all()

        if not tokens.exists():
            self.stdout.write(
                self.style.WARNING("⚠️ لا يوجد FCM Tokens مسجلة في النظام")
            )
            return

        self.stdout.write(self.style.SUCCESS(f"\n📱 FCM Tokens المسجلة ({tokens.count()}):"))
        self.stdout.write("-" * 70)

        for token in tokens:
            status = "✅ نشط" if token.is_active else "❌ غير نشط"
            self.stdout.write(
                f"\n{status} | المستخدم: {token.user.username} ({token.user.name})"
            )
            self.stdout.write(f"   النوع: {token.device_type}")
            self.stdout.write(f"   الجهاز: {token.device_name or 'غير محدد'}")
            self.stdout.write(f"   آخر استخدام: {token.last_used or 'لم يستخدم بعد'}")
            self.stdout.write(f"   تاريخ الإنشاء: {token.created_at}")

    def send_test_notification(self, user_id):
        """إرسال إشعار تجريبي"""
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ المستخدم رقم {user_id} غير موجود")
            )
            return

        # التحقق من وجود FCM tokens للمستخدم
        tokens_count = FCMToken.objects.filter(
            user_id=user_id, is_active=True
        ).count()

        if tokens_count == 0:
            self.stdout.write(
                self.style.ERROR(
                    f"❌ المستخدم {user.username} ليس لديه FCM tokens نشطة"
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    "يرجى تسجيل الدخول من المتصفح وتفعيل الإشعارات أولاً"
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🚀 إرسال إشعار تجريبي إلى: {user.username} ({user.name})"
            )
        )
        self.stdout.write(f"   عدد الأجهزة: {tokens_count}")

        # إرسال الإشعار
        result = send_push_to_user(
            user_id=user_id,
            title="🎉 اختبار الإشعارات",
            message="هذا إشعار تجريبي للتأكد من عمل النظام بشكل صحيح!",
            data={
                "type": "test",
                "test_id": 1,
                "url": "/notifications",
            },
        )

        # عرض النتيجة
        if result.get("success", 0) > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ تم إرسال الإشعار بنجاح إلى {result['success']} جهاز"
                )
            )
            self.stdout.write(
                self.style.SUCCESS("تحقق من المتصفح لرؤية الإشعار!")
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"\n❌ فشل إرسال الإشعار: {result.get('error', 'Unknown error')}"
                )
            )

        if result.get("failure", 0) > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️ فشل الإرسال إلى {result['failure']} جهاز"
                )
            )

    def show_stats(self):
        """عرض إحصائيات عامة"""
        total_tokens = FCMToken.objects.count()
        active_tokens = FCMToken.objects.filter(is_active=True).count()
        inactive_tokens = total_tokens - active_tokens

        users_with_tokens = (
            FCMToken.objects.filter(is_active=True)
            .values("user")
            .distinct()
            .count()
        )

        self.stdout.write(self.style.SUCCESS("\n📊 إحصائيات النظام:"))
        self.stdout.write("-" * 70)
        self.stdout.write(f"إجمالي FCM Tokens: {total_tokens}")
        self.stdout.write(f"Tokens نشطة: {active_tokens}")
        self.stdout.write(f"Tokens غير نشطة: {inactive_tokens}")
        self.stdout.write(f"مستخدمين لديهم tokens: {users_with_tokens}")

        self.stdout.write(self.style.SUCCESS("\n💡 كيفية الاستخدام:"))
        self.stdout.write("-" * 70)
        self.stdout.write("1. عرض جميع الـ tokens:")
        self.stdout.write("   python manage.py test_fcm --list-tokens")
        self.stdout.write("\n2. إرسال إشعار تجريبي:")
        self.stdout.write("   python manage.py test_fcm --test")
        self.stdout.write("\n3. إرسال إشعار لمستخدم محدد:")
        self.stdout.write("   python manage.py test_fcm --user-id 1")

        if active_tokens == 0:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️ لا يوجد FCM tokens نشطة في النظام"
                )
            )
            self.stdout.write("للبدء:")
            self.stdout.write("1. افتح التطبيق في المتصفح")
            self.stdout.write("2. سجل الدخول")
            self.stdout.write("3. اضغط على زر 'تفعيل الإشعارات'")
            self.stdout.write("4. وافق على طلب الإذن")
            self.stdout.write("5. أعد تشغيل الأمر")

