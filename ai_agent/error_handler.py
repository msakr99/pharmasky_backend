"""
Enhanced error handling for AI Agent
"""
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def ai_agent_exception_handler(exc, context):
    """
    Custom exception handler for AI Agent
    Provides user-friendly messages for common errors
    """
    # Call DRF's default handler first
    response = drf_exception_handler(exc, context)
    
    # If DRF couldn't handle it, create our own response
    if response is None:
        # Log the error
        logger.error(f"AI Agent Error: {exc}", exc_info=True)
        
        # Check error type
        error_message = str(exc).lower()
        
        if "rate" in error_message and ("limit" in error_message or "429" in error_message):
            return Response({
                "error": "تم تجاوز حد الاستخدام المؤقت للخدمة",
                "message": "لقد تجاوزت الحد المسموح من الطلبات. يرجى الانتظار قليلاً والمحاولة مرة أخرى.",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "retry_after": 60  # seconds
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        elif "401" in error_message or "unauthorized" in error_message:
            return Response({
                "error": "خطأ في المصادقة",
                "message": "مفتاح API غير صالح أو منتهي الصلاحية. يرجى التواصل مع الدعم الفني.",
                "error_code": "AUTH_ERROR"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        elif any(code in error_message for code in ["502", "503", "504"]):
            return Response({
                "error": "الخدمة غير متاحة مؤقتاً",
                "message": "الخدمة مشغولة حالياً. يرجى المحاولة بعد قليل.",
                "error_code": "SERVICE_UNAVAILABLE"
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        else:
            return Response({
                "error": "حدث خطأ غير متوقع",
                "message": "نعتذر عن الإزعاج. يرجى المحاولة مرة أخرى أو التواصل مع الدعم الفني.",
                "error_code": "INTERNAL_ERROR"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Customize existing DRF responses
    if response.status_code == 429:
        response.data = {
            "error": "تم تجاوز حد الطلبات",
            "message": "لقد تجاوزت الحد المسموح من الطلبات. يرجى الانتظار قليلاً.",
            "error_code": "THROTTLED",
            "retry_after": response.data.get("detail", "").split("available in ")[1].split(" ")[0] if "available in" in str(response.data.get("detail", "")) else "60"
        }
    
    return response


def handle_openai_error(error):
    """
    Handle OpenAI specific errors and return user-friendly messages
    """
    error_str = str(error).lower()
    
    if "rate_limit" in error_str or "429" in error_str:
        return {
            "error": "تم تجاوز حد الاستخدام",
            "message": "تم تجاوز حد الاستخدام المؤقت للخدمة. يرجى المحاولة لاحقاً.",
            "error_code": "RATE_LIMIT",
            "status": 429
        }
    elif "invalid_api_key" in error_str or "401" in error_str:
        return {
            "error": "خطأ في المصادقة",
            "message": "مفتاح API غير صالح. يرجى التواصل مع الدعم الفني.",
            "error_code": "INVALID_API_KEY",
            "status": 401
        }
    elif "timeout" in error_str:
        return {
            "error": "انتهت مهلة الطلب",
            "message": "استغرق الطلب وقتاً طويلاً. يرجى المحاولة مرة أخرى.",
            "error_code": "TIMEOUT",
            "status": 504
        }
    else:
        return {
            "error": "خطأ في الخدمة",
            "message": "حدث خطأ أثناء معالجة طلبك. يرجى المحاولة لاحقاً.",
            "error_code": "SERVICE_ERROR",
            "status": 500
        }

