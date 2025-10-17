"""
Admin configuration for core app.
"""

from django.contrib import admin
from core.admin.abstract_admin import DefaultBaseAdminItems
from core.models import WorkShift


@admin.register(WorkShift)
class WorkShiftAdmin(DefaultBaseAdminItems):
    """Admin interface for WorkShift model."""
    
    list_display = [
        'id',
        'status',
        'started_by',
        'start_time',
        'end_time',
        'get_duration_display',
        'total_sale_invoices',
        'total_sales_amount',
    ]
    
    list_filter = [
        'status',
        'start_time',
    ]
    
    search_fields = [
        'started_by__name',
        'closed_by__name',
    ]
    
    readonly_fields = [
        'start_time',
        'end_time',
        'total_sale_invoices',
        'total_purchase_invoices',
        'total_payments',
        'total_returns',
        'total_complaints',
        'total_new_registrations',
        'total_sales_amount',
        'total_payments_amount',
        'get_duration_display',
    ]
    
    autocomplete_fields = ['started_by', 'closed_by']
    
    date_hierarchy = 'start_time'
    
    ordering = ['-start_time']
    
    fieldsets = (
        ('معلومات الوردية', {
            'fields': (
                'status',
                'started_by',
                'closed_by',
                'start_time',
                'end_time',
                'get_duration_display',
            )
        }),
        ('إحصائيات العمليات', {
            'fields': (
                'total_sale_invoices',
                'total_purchase_invoices',
                'total_payments',
                'total_returns',
                'total_complaints',
                'total_new_registrations',
            )
        }),
        ('إحصائيات مالية', {
            'fields': (
                'total_sales_amount',
                'total_payments_amount',
            )
        }),
        ('ملاحظات', {
            'fields': ('notes',)
        }),
    )
    
    def get_duration_display(self, obj):
        """عرض مدة الوردية."""
        return obj.get_duration()
    get_duration_display.short_description = 'المدة'
    
    def has_add_permission(self, request):
        """منع إضافة يدوية - يجب استخدام API."""
        return False

