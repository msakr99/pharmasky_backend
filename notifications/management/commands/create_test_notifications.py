"""
Django Management Command لإنشاء إشعارات تجريبية

الاستخدام:
python manage.py create_test_notifications
python manage.py create_test_notifications --users pharmacy1 pharmacy2
python manage.py create_test_notifications --count 50
python manage.py create_test_notifications --with-topics
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.models import Notification, Topic, TopicSubscription
from notifications.utils import send_notification_to_users
import random
from datetime import datetime, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'إنشاء إشعارات تجريبية للاختبار'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            nargs='+',
            type=str,
            help='قائمة بأسماء المستخدمين (username) لإرسال الإشعارات لهم'
        )
        
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='عدد الإشعارات التي سيتم إنشاؤها لكل مستخدم (افتراضي: 10)'
        )
        
        parser.add_argument(
            '--with-topics',
            action='store_true',
            help='إنشاء مواضيع تجريبية والاشتراك فيها'
        )
        
        parser.add_argument(
            '--mark-some-read',
            action='store_true',
            help='تحديد بعض الإشعارات كمقروءة (50٪)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 بدء إنشاء الإشعارات التجريبية...\n'))
        
        # جلب المستخدمين
        users = self._get_users(options['users'])
        if not users:
            self.stdout.write(self.style.ERROR('❌ لم يتم العثور على مستخدمين!'))
            return
        
        # إنشاء المواضيع إذا طُلب ذلك
        topics = []
        if options['with_topics']:
            topics = self._create_topics()
            self._subscribe_users_to_topics(users, topics)
        
        # إنشاء الإشعارات
        count = options['count']
        mark_read = options['mark_some_read']
        
        total_created = 0
        for user in users:
            created = self._create_notifications_for_user(user, count, topics, mark_read)
            total_created += created
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ تم إنشاء {total_created} إشعار بنجاح لـ {len(users)} مستخدم!'
            )
        )
    
    def _get_users(self, usernames=None):
        """جلب المستخدمين المحددين أو جميع المستخدمين"""
        if usernames:
            users = User.objects.filter(username__in=usernames)
            self.stdout.write(f'📋 تم العثور على {users.count()} مستخدم محدد')
        else:
            # جلب أول 5 مستخدمين
            users = User.objects.filter(is_active=True)[:5]
            self.stdout.write(f'📋 سيتم استخدام {users.count()} مستخدم')
        
        return list(users)
    
    def _create_topics(self):
        """إنشاء مواضيع تجريبية"""
        self.stdout.write('📂 إنشاء المواضيع التجريبية...')
        
        topics_data = [
            {
                'name': 'عروض وخصومات',
                'description': 'جميع العروض والخصومات الحصرية للصيدليات'
            },
            {
                'name': 'أخبار النظام',
                'description': 'آخر الأخبار والتحديثات على النظام'
            },
            {
                'name': 'تذكيرات الدفع',
                'description': 'تذكيرات بمواعيد الدفع والفواتير المستحقة'
            },
            {
                'name': 'منتجات جديدة',
                'description': 'إشعارات بالمنتجات الجديدة المتوفرة'
            },
        ]
        
        topics = []
        for topic_data in topics_data:
            topic, created = Topic.objects.get_or_create(
                name=topic_data['name'],
                defaults={'description': topic_data['description']}
            )
            topics.append(topic)
            
            if created:
                self.stdout.write(f'  ✅ تم إنشاء موضوع: {topic.name}')
            else:
                self.stdout.write(f'  ℹ️  موضوع موجود مسبقاً: {topic.name}')
        
        return topics
    
    def _subscribe_users_to_topics(self, users, topics):
        """الاشتراك التلقائي للمستخدمين في المواضيع"""
        self.stdout.write('📌 الاشتراك في المواضيع...')
        
        for user in users:
            # اشترك في عدد عشوائي من المواضيع
            num_subscriptions = random.randint(1, len(topics))
            selected_topics = random.sample(topics, num_subscriptions)
            
            for topic in selected_topics:
                TopicSubscription.objects.get_or_create(
                    user=user,
                    topic=topic,
                    defaults={'is_active': True}
                )
            
            self.stdout.write(f'  ✅ {user.name or user.username}: اشترك في {num_subscriptions} موضوع')
    
    def _create_notifications_for_user(self, user, count, topics, mark_read):
        """إنشاء إشعارات لمستخدم محدد"""
        self.stdout.write(f'\n📬 إنشاء {count} إشعار لـ {user.name or user.username}...')
        
        # قوالب الإشعارات المختلفة
        notification_templates = self._get_notification_templates()
        
        created_count = 0
        for i in range(count):
            template = random.choice(notification_templates)
            
            # اختيار موضوع عشوائي (أو None)
            topic = random.choice(topics + [None]) if topics else None
            
            # إنشاء الإشعار
            notification = Notification.objects.create(
                user=user,
                topic=topic,
                title=template['title'],
                message=template['message'],
                extra=template.get('extra', {}),
                image_url=template.get('image_url', ''),
            )
            
            # تحديد بعض الإشعارات كمقروءة
            if mark_read and random.random() < 0.5:
                notification.is_read = True
                notification.save()
            
            created_count += 1
        
        self.stdout.write(f'  ✅ تم إنشاء {created_count} إشعار')
        return created_count
    
    def _get_notification_templates(self):
        """قوالب الإشعارات المختلفة"""
        templates = [
            # إشعارات الطلبات
            {
                'title': '🛒 طلب جديد تم إنشاؤه',
                'message': f'تم إنشاء طلبك رقم #{random.randint(1000, 9999)} بنجاح. إجمالي المبلغ: {random.randint(500, 5000)} جنيه',
                'extra': {
                    'type': 'sale_invoice',
                    'invoice_id': random.randint(1000, 9999),
                    'total_price': f'{random.randint(500, 5000)}.00',
                }
            },
            {
                'title': '✅ تم قبول طلبك',
                'message': f'تم قبول طلبك رقم #{random.randint(1000, 9999)} وجاري التجهيز',
                'extra': {
                    'type': 'invoice_status_update',
                    'invoice_id': random.randint(1000, 9999),
                    'status': 'ACCEPTED',
                }
            },
            {
                'title': '🚚 طلبك في الطريق',
                'message': f'طلبك رقم #{random.randint(1000, 9999)} خرج للتوصيل وسيصل خلال ساعة',
                'extra': {
                    'type': 'invoice_status_update',
                    'invoice_id': random.randint(1000, 9999),
                    'status': 'DELIVERING',
                }
            },
            {
                'title': '✅ تم توصيل الطلب',
                'message': f'تم توصيل طلبك رقم #{random.randint(1000, 9999)} بنجاح. شكراً لتعاملكم معنا!',
                'extra': {
                    'type': 'invoice_status_update',
                    'invoice_id': random.randint(1000, 9999),
                    'status': 'DELIVERED',
                }
            },
            
            # إشعارات الدفع
            {
                'title': '💰 دفعة مسجلة بنجاح',
                'message': f'تم تسجيل دفعة بمبلغ {random.randint(1000, 10000)} جنيه على حسابك',
                'extra': {
                    'type': 'sale_payment',
                    'payment_id': random.randint(100, 999),
                    'amount': f'{random.randint(1000, 10000)}.00',
                }
            },
            {
                'title': '⏰ تذكير بموعد الدفع',
                'message': f'لديك فاتورة مستحقة بمبلغ {random.randint(1000, 10000)} جنيه. الموعد: بعد 3 أيام',
                'extra': {
                    'type': 'payment_due_reminder',
                    'invoice_id': random.randint(1000, 9999),
                    'due_amount': f'{random.randint(1000, 10000)}.00',
                    'days_left': 3,
                }
            },
            {
                'title': '⚠️ تأخير في الدفع',
                'message': f'فاتورة متأخرة بمبلغ {random.randint(1000, 10000)} جنيه. يرجى السداد في أقرب وقت',
                'extra': {
                    'type': 'payment_overdue',
                    'invoice_id': random.randint(1000, 9999),
                    'overdue_amount': f'{random.randint(1000, 10000)}.00',
                    'days_overdue': random.randint(1, 30),
                }
            },
            
            # إشعارات المنتجات
            {
                'title': '✨ منتج متوفر الآن!',
                'message': f'المنتج "باراسيتامول 500 مجم" المطلوب متوفر الآن في المخزون',
                'extra': {
                    'type': 'wishlist_product_available',
                    'product_id': random.randint(1, 100),
                    'product_name': 'باراسيتامول 500 مجم',
                }
            },
            {
                'title': '🎁 عرض خاص',
                'message': 'خصم 20٪ على جميع المضادات الحيوية لفترة محدودة!',
                'extra': {
                    'type': 'special_offer',
                    'discount': 20,
                    'category': 'antibiotics',
                }
            },
            
            # إشعارات النظام
            {
                'title': '🟢 النظام متاح الآن',
                'message': 'تم فتح النظام. يمكنكم تقديم طلباتكم',
                'extra': {
                    'type': 'shift_started',
                }
            },
            {
                'title': '🔴 إغلاق النظام',
                'message': 'تم إغلاق النظام. نعتذر عن الإزعاج',
                'extra': {
                    'type': 'shift_closed',
                }
            },
            
            # إشعارات المرتجعات
            {
                'title': '↩️ طلب مرتجع',
                'message': f'تم تسجيل طلب مرتجع رقم #{random.randint(100, 999)} وسيتم مراجعته قريباً',
                'extra': {
                    'type': 'sale_return',
                    'return_id': random.randint(100, 999),
                }
            },
            {
                'title': '✅ تمت الموافقة على المرتجع',
                'message': f'تمت الموافقة على مرتجعك رقم #{random.randint(100, 999)}. سيتم استرداد المبلغ خلال 3 أيام',
                'extra': {
                    'type': 'return_approved',
                    'return_id': random.randint(100, 999),
                }
            },
        ]
        
        return templates


# يمكن استخدام الكلاس مباشرة
def create_test_notifications_for_user(user, count=10):
    """دالة مساعدة لإنشاء إشعارات تجريبية لمستخدم محدد"""
    cmd = Command()
    return cmd._create_notifications_for_user(user, count, [], False)

