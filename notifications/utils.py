"""
utilities لإرسال Push Notifications باستخدام Firebase Cloud Messaging (FCM)
استخدام Firebase Admin SDK - الطريقة الرسمية الموصى بها من Google
"""

import logging
from typing import List, Dict, Optional
from django.conf import settings
import os

# استيراد Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logging.warning("firebase-admin library not installed. Install it with: pip install firebase-admin")

from notifications.models import FCMToken, Notification

logger = logging.getLogger(__name__)

# متغير global للـ Firebase App
_firebase_app = None


# ═══════════════════════════════════════════════════════════════════
# تهيئة Firebase Admin SDK
# ═══════════════════════════════════════════════════════════════════

def initialize_firebase():
    """
    تهيئة Firebase Admin SDK
    
    يتم استدعاء هذه الدالة تلقائياً عند أول استخدام
    
    ملف Service Account موجود في: sky/credentials/pharmasky46-firebase-adminsdk.json
    """
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    if not FIREBASE_AVAILABLE:
        logger.error("Firebase Admin SDK is not installed")
        return None
    
    try:
        # التحقق من وجود Firebase app مُهيأ بالفعل
        _firebase_app = firebase_admin.get_app()
        logger.info("Firebase Admin SDK already initialized")
        return _firebase_app
    except ValueError:
        # Firebase app غير مُهيأ، نقوم بتهيئته
        pass
    
    try:
        # الحصول على مسار ملف Service Account
        credentials_path = getattr(
            settings, 
            "FIREBASE_CREDENTIALS_PATH",
            os.path.join(settings.BASE_DIR, "credentials", "pharmasky46-firebase-adminsdk.json")
        )
        
        if not os.path.exists(credentials_path):
            logger.error(f"Firebase credentials file not found at: {credentials_path}")
            return None
        
        # تهيئة Firebase Admin SDK
        cred = credentials.Certificate(credentials_path)
        _firebase_app = firebase_admin.initialize_app(cred)
        
        logger.info("Firebase Admin SDK initialized successfully")
        return _firebase_app
        
    except Exception as e:
        logger.error(f"Error initializing Firebase Admin SDK: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════
# دوال إرسال الإشعارات
# ═══════════════════════════════════════════════════════════════════

def send_push_notification(
    title: str,
    message: str,
    user_ids: Optional[List[int]] = None,
    tokens: Optional[List[str]] = None,
    data: Optional[Dict] = None,
    image_url: Optional[str] = None,
    click_action: Optional[str] = None,
) -> Dict[str, any]:
    """
    إرسال Push Notification عبر FCM باستخدام Firebase Admin SDK
    
    Args:
        title (str): عنوان الإشعار
        message (str): نص الإشعار
        user_ids (List[int], optional): قائمة معرفات المستخدمين
        tokens (List[str], optional): قائمة FCM tokens مباشرة
        data (Dict, optional): بيانات إضافية ترسل مع الإشعار
        image_url (str, optional): رابط صورة تظهر في الإشعار
        click_action (str, optional): URL للانتقال إليه عند النقر على الإشعار
    
    Returns:
        Dict: نتيجة الإرسال تحتوي على success, failure, results
    
    Example:
        >>> result = send_push_notification(
        ...     title="طلب جديد",
        ...     message="تم استلام طلبك بنجاح!",
        ...     user_ids=[1, 2, 3],
        ...     data={"order_id": 123, "type": "new_order"}
        ... )
    """
    # تهيئة Firebase
    app = initialize_firebase()
    
    if not app:
        logger.error("Firebase Admin SDK not available")
        return {
            "success": 0,
            "failure": 0,
            "error": "Firebase Admin SDK not available"
        }
    
    # الحصول على tokens
    if tokens is None:
        if user_ids:
            # الحصول على tokens من قاعدة البيانات
            tokens = list(
                FCMToken.objects.filter(
                    user_id__in=user_ids,
                    is_active=True
                ).values_list("token", flat=True)
            )
        else:
            logger.error("Either user_ids or tokens must be provided")
            return {
                "success": 0,
                "failure": 0,
                "error": "No users or tokens specified"
            }
    
    if not tokens:
        logger.warning("No active FCM tokens found")
        return {
            "success": 0,
            "failure": 0,
            "error": "No active tokens found"
        }
    
    # إعداد البيانات الإضافية
    notification_data = data or {}
    if click_action:
        notification_data["click_action"] = click_action
    
    # تحويل جميع القيم إلى strings (FCM requirement)
    notification_data = {k: str(v) for k, v in notification_data.items()}
    
    try:
        # إنشاء رسالة FCM
        fcm_message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=message,
                image=image_url if image_url else None,
            ),
            data=notification_data,
            tokens=tokens,
            # إعدادات إضافية
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    title=title,
                    body=message,
                    icon="/icon.png",  # أيقونة من public/
                    badge="/icon.png",
                    image=image_url if image_url else None,
                ),
                fcm_options=messaging.WebpushFCMOptions(
                    link=click_action if click_action else None,
                ),
            ),
        )
        
        # إرسال الإشعار
        response = messaging.send_multicast(fcm_message)
        
        # معالجة النتائج
        success_count = response.success_count
        failure_count = response.failure_count
        
        # تحديث last_used للـ tokens الناجحة
        if success_count > 0:
            from django.utils import timezone
            FCMToken.objects.filter(token__in=tokens).update(last_used=timezone.now())
        
        # التعامل مع الـ tokens الفاشلة
        if response.responses:
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    # إذا كان التوكن غير صالح، قم بإلغاء تفعيله
                    error_code = resp.exception.code if resp.exception else None
                    if error_code in ['invalid-registration-token', 'registration-token-not-registered']:
                        FCMToken.objects.filter(token=tokens[idx]).update(is_active=False)
                        logger.warning(f"Deactivated invalid token: {tokens[idx][:20]}...")
        
        logger.info(
            f"Push notification sent: {success_count} success, "
            f"{failure_count} failure"
        )
        
        return {
            "success": success_count,
            "failure": failure_count,
            "responses": response.responses,
        }
        
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        return {
            "success": 0,
            "failure": len(tokens),
            "error": str(e)
        }


def send_push_to_user(
    user_id: int,
    title: str,
    message: str,
    data: Optional[Dict] = None,
    image_url: Optional[str] = None,
) -> Dict[str, any]:
    """
    إرسال Push Notification لمستخدم واحد
    
    Args:
        user_id (int): معرف المستخدم
        title (str): عنوان الإشعار
        message (str): نص الإشعار
        data (Dict, optional): بيانات إضافية
        image_url (str, optional): رابط صورة
    
    Returns:
        Dict: نتيجة الإرسال
    
    Example:
        >>> result = send_push_to_user(
        ...     user_id=1,
        ...     title="رسالة جديدة",
        ...     message="لديك رسالة جديدة من المدير"
        ... )
    """
    return send_push_notification(
        title=title,
        message=message,
        user_ids=[user_id],
        data=data,
        image_url=image_url,
    )


def send_push_to_all_users(
    title: str,
    message: str,
    data: Optional[Dict] = None,
    image_url: Optional[str] = None,
) -> Dict[str, any]:
    """
    إرسال Push Notification لجميع المستخدمين
    
    Args:
        title (str): عنوان الإشعار
        message (str): نص الإشعار
        data (Dict, optional): بيانات إضافية
        image_url (str, optional): رابط صورة
    
    Returns:
        Dict: نتيجة الإرسال
    
    Example:
        >>> result = send_push_to_all_users(
        ...     title="إعلان مهم",
        ...     message="سيتم إيقاف الخدمة للصيانة غدًا"
        ... )
    """
    # الحصول على جميع الـ tokens النشطة
    tokens = list(
        FCMToken.objects.filter(is_active=True).values_list("token", flat=True)
    )
    
    return send_push_notification(
        title=title,
        message=message,
        tokens=tokens,
        data=data,
        image_url=image_url,
    )


def send_notification_with_push(
    user_id: int,
    title: str,
    message: str,
    extra: Optional[Dict] = None,
    image_url: Optional[str] = None,
    send_push: bool = True,
) -> Notification:
    """
    إنشاء إشعار في قاعدة البيانات وإرساله كـ Push Notification
    
    Args:
        user_id (int): معرف المستخدم
        title (str): عنوان الإشعار
        message (str): نص الإشعار
        extra (Dict, optional): بيانات إضافية
        image_url (str, optional): رابط صورة
        send_push (bool): هل يتم إرسال Push Notification؟ (افتراضي: True)
    
    Returns:
        Notification: الإشعار المُنشأ
    
    Example:
        >>> notification = send_notification_with_push(
        ...     user_id=1,
        ...     title="طلب جديد",
        ...     message="تم استلام طلبك بنجاح!",
        ...     extra={"order_id": 123}
        ... )
    """
    # إنشاء الإشعار في قاعدة البيانات
    notification = Notification.objects.create(
        user_id=user_id,
        title=title,
        message=message,
        extra=extra,
        image_url=image_url or "",
    )
    
    # إرسال Push Notification
    if send_push:
        send_push_to_user(
            user_id=user_id,
            title=title,
            message=message,
            data=extra,
            image_url=image_url,
        )
    
    return notification


# ═══════════════════════════════════════════════════════════════════
# دالة قديمة للتوافق (backward compatibility)
# ═══════════════════════════════════════════════════════════════════

def send_user_fcm_message(notification: Notification) -> None:
    """
    إرسال FCM message لمستخدم
    (دالة قديمة للتوافق مع الكود السابق)
    """
    if notification.user:
        send_push_to_user(
            user_id=notification.user.id,
            title=notification.title,
            message=notification.message,
            data=notification.extra,
            image_url=notification.image_url,
        )


# ═══════════════════════════════════════════════════════════════════
# دالة مساعدة لاختبار النظام
# ═══════════════════════════════════════════════════════════════════

def test_push_notification(user_id: int) -> Dict[str, any]:
    """
    اختبار إرسال Push Notification لمستخدم
    
    Args:
        user_id (int): معرف المستخدم
    
    Returns:
        Dict: نتيجة الاختبار
    
    Example:
        >>> from notifications.utils import test_push_notification
        >>> result = test_push_notification(user_id=1)
    """
    from django.utils import timezone
    
    return send_push_to_user(
        user_id=user_id,
        title="🎉 اختبار الإشعارات",
        message="هذا إشعار تجريبي للتأكد من عمل النظام بشكل صحيح!",
        data={
            "type": "test",
            "timestamp": str(timezone.now()),
            "url": "/notifications"
        },
    )
