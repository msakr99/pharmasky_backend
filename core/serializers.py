"""
Serializers for core models.
"""

from rest_framework import serializers
from core.serializers.abstract_serializers import BaseModelSerializer
from core.models import WorkShift


class WorkShiftReadSerializer(BaseModelSerializer):
    """Serializer for reading WorkShift data."""
    
    class UserSubSerializer(BaseModelSerializer):
        class Meta:
            from accounts.models import User
            model = User
            fields = ["id", "username", "name"]
    
    started_by = UserSubSerializer(read_only=True)
    closed_by = UserSubSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkShift
        fields = [
            "id",
            "started_by",
            "closed_by",
            "status",
            "status_display",
            "start_time",
            "end_time",
            "duration",
            "total_sale_invoices",
            "total_purchase_invoices",
            "total_payments",
            "total_returns",
            "total_complaints",
            "total_new_registrations",
            "total_sales_amount",
            "total_payments_amount",
            "notes",
        ]
    
    def get_duration(self, obj):
        return obj.get_duration()


class WorkShiftStartSerializer(serializers.Serializer):
    """Serializer for starting a new shift."""
    
    send_notifications = serializers.BooleanField(
        default=True,
        help_text="إرسال إشعارات لجميع الصيدليات عند بدء الوردية"
    )
    notification_message = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="رسالة مخصصة للإشعار (اختياري)"
    )


class WorkShiftCloseSerializer(serializers.Serializer):
    """Serializer for closing a shift."""
    
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="ملاحظات عن الوردية"
    )
    send_notifications = serializers.BooleanField(
        default=True,
        help_text="إرسال إشعارات لجميع الصيدليات عند إغلاق الوردية"
    )
    notification_message = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="رسالة مخصصة للإشعار (اختياري)"
    )

