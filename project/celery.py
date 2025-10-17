import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

app = Celery("project")
app.config_from_object("project.settings", namespace="CELERYD")

app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    # إرسال تذكيرات مواعيد التحصيل يومياً الساعة 9 صباحاً
    'send-payment-due-reminders': {
        'task': 'notifications.tasks.send_payment_due_reminders',
        'schedule': crontab(hour=9, minute=0),  # كل يوم الساعة 9 صباحاً
    },
    
    # حذف الإشعارات المقروءة القديمة (أسبوعياً)
    'delete-old-notifications': {
        'task': 'notifications.tasks.delete_old_read_notifications',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # كل أحد الساعة 2 صباحاً
        'args': (30,)  # حذف الأقدم من 30 يوم
    },
}
