"""
Views for work shift functionality.
"""

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import status
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Avg, F

from core.models import WorkShift
from core.serializers import (
    WorkShiftReadSerializer,
    WorkShiftStartSerializer,
    WorkShiftCloseSerializer
)
from core.responses import APIResponse
from core.views.abstract_paginations import CustomPageNumberPagination
from accounts.permissions import AdminRoleAuthentication, ManagerRoleAuthentication


class StartWorkShiftAPIView(APIView):
    """
    بدء وردية عمل جديدة.
    
    عند بدء الوردية:
    - يتم إنشاء سجل وردية جديد
    - إرسال إشعارات لجميع الصيدليات النشطة
    - تحديث حالة النظام
    
    Permission: Admin/Manager only
    """
    
    permission_classes = [AdminRoleAuthentication | ManagerRoleAuthentication]
    serializer_class = WorkShiftStartSerializer
    
    def post(self, request, *args, **kwargs):
        """بدء وردية جديدة."""
        serializer = WorkShiftStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # التحقق من عدم وجود وردية نشطة
        active_shift = WorkShift.objects.filter(status='ACTIVE').first()
        if active_shift:
            return APIResponse.error(
                message=_("يوجد وردية نشطة بالفعل. يجب إغلاقها أولاً."),
                error_code="SHIFT_ALREADY_ACTIVE",
                status_code=status.HTTP_400_BAD_REQUEST,
                data={
                    "active_shift_id": active_shift.pk,
                    "started_at": active_shift.start_time,
                    "started_by": active_shift.started_by.name if active_shift.started_by else None
                }
            )
        
        # إنشاء وردية جديدة
        shift = WorkShift.objects.create(
            started_by=request.user,
            status='ACTIVE'
        )
        
        # إرسال إشعارات للصيدليات
        if serializer.validated_data.get('send_notifications', True):
            from notifications.tasks import send_shift_notification
            
            custom_message = serializer.validated_data.get('notification_message', '')
            
            send_shift_notification.delay(
                shift_id=shift.pk,
                shift_type='start',
                custom_message=custom_message
            )
        
        return APIResponse.created(
            data=WorkShiftReadSerializer(shift).data,
            message=_("تم بدء الوردية بنجاح وإرسال الإشعارات للصيدليات.")
        )


class CloseWorkShiftAPIView(APIView):
    """
    إغلاق الوردية الحالية.
    
    عند إغلاق الوردية:
    - تحديث إحصائيات الوردية
    - إرسال إشعارات للصيدليات بإغلاق النظام
    - حفظ الملاحظات
    
    Permission: Admin/Manager only
    """
    
    permission_classes = [AdminRoleAuthentication | ManagerRoleAuthentication]
    serializer_class = WorkShiftCloseSerializer
    
    def post(self, request, *args, **kwargs):
        """إغلاق الوردية النشطة."""
        serializer = WorkShiftCloseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # البحث عن وردية نشطة
        active_shift = WorkShift.objects.filter(status='ACTIVE').first()
        if not active_shift:
            return APIResponse.error(
                message=_("لا توجد وردية نشطة لإغلاقها."),
                error_code="NO_ACTIVE_SHIFT",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # تحديث الإحصائيات
        active_shift.update_statistics()
        
        # إغلاق الوردية
        notes = serializer.validated_data.get('notes', '')
        active_shift.close_shift(user=request.user, notes=notes)
        
        # إرسال إشعارات للصيدليات
        if serializer.validated_data.get('send_notifications', True):
            from notifications.tasks import send_shift_notification
            
            custom_message = serializer.validated_data.get('notification_message', '')
            
            send_shift_notification.delay(
                shift_id=active_shift.pk,
                shift_type='close',
                custom_message=custom_message
            )
        
        return APIResponse.success(
            data=WorkShiftReadSerializer(active_shift).data,
            message=_("تم إغلاق الوردية بنجاح.")
        )


class CurrentWorkShiftAPIView(APIView):
    """
    الحصول على الوردية النشطة الحالية.
    
    Permission: Authenticated users
    """
    
    def get(self, request, *args, **kwargs):
        """جلب الوردية النشطة."""
        active_shift = WorkShift.objects.filter(status='ACTIVE').first()
        
        if not active_shift:
            return APIResponse.success(
                data=None,
                message=_("لا توجد وردية نشطة حالياً.")
            )
        
        # تحديث الإحصائيات للوردية النشطة
        active_shift.update_statistics()
        
        return APIResponse.success(
            data=WorkShiftReadSerializer(active_shift).data,
            message=_("الوردية النشطة الحالية.")
        )


class WorkShiftListAPIView(ListAPIView):
    """
    قائمة جميع الورديات.
    
    Permission: Admin/Manager only
    """
    
    permission_classes = [AdminRoleAuthentication | ManagerRoleAuthentication]
    serializer_class = WorkShiftReadSerializer
    pagination_class = CustomPageNumberPagination
    queryset = WorkShift.objects.all().select_related('started_by', 'closed_by')
    
    def get_queryset(self):
        """Return all shifts ordered by start time."""
        queryset = super().get_queryset()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset


class WorkShiftStatsAPIView(APIView):
    """
    إحصائيات الورديات.
    
    Permission: Admin/Manager only
    """
    
    permission_classes = [AdminRoleAuthentication | ManagerRoleAuthentication]
    
    def get(self, request, *args, **kwargs):
        """جلب إحصائيات عامة عن الورديات."""
        # إحصائيات عامة
        total_shifts = WorkShift.objects.count()
        active_shifts = WorkShift.objects.filter(status='ACTIVE').count()
        closed_shifts = WorkShift.objects.filter(status='CLOSED').count()
        
        # إحصائيات الورديات المغلقة
        closed_stats = WorkShift.objects.filter(status='CLOSED').aggregate(
            total_sales=Sum('total_sales_amount'),
            total_payments=Sum('total_payments_amount'),
            avg_sale_invoices=Avg('total_sale_invoices'),
            avg_duration=Avg(
                F('end_time') - F('start_time')
            )
        )
        
        stats = {
            "total_shifts": total_shifts,
            "active_shifts": active_shifts,
            "closed_shifts": closed_shifts,
            "total_sales_all_shifts": closed_stats.get('total_sales') or 0,
            "total_payments_all_shifts": closed_stats.get('total_payments') or 0,
            "average_invoices_per_shift": closed_stats.get('avg_sale_invoices') or 0,
        }
        
        return APIResponse.success(
            data=stats,
            message=_("إحصائيات الورديات.")
        )

