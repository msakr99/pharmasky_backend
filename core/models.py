"""
Core models for the project.

This module contains reusable abstract models and system-wide models.
"""

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model with timestamp fields.
    
    Provides created_at and updated_at fields for all models.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract base model with soft delete functionality.
    
    Provides is_deleted and deleted_at fields for soft deletion.
    """
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def delete(self, using=None, keep_parents=False):
        """Soft delete the object."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the object."""
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Restore a soft deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, SoftDeleteModel):
    """
    Abstract base model combining timestamp and soft delete functionality.
    """
    class Meta:
        abstract = True


class WorkShift(models.Model):
    """
    Work Shift Model - نظام الوردية.
    
    يسجل بداية ونهاية كل وردية عمل.
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'نشطة'),
        ('CLOSED', 'مغلقة'),
    ]
    
    class Meta:
        app_label = 'core'
        verbose_name = 'وردية'
        verbose_name_plural = 'الورديات'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['start_time']),
            models.Index(fields=['-start_time']),
        ]
    
    started_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='started_shifts',
        related_query_name='started_shifts',
        verbose_name='بدأها'
    )
    closed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='closed_shifts',
        related_query_name='closed_shifts',
        verbose_name='أغلقها'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        verbose_name='الحالة'
    )
    start_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='وقت البداية'
    )
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='وقت الإغلاق'
    )
    
    # إحصائيات الوردية
    total_sale_invoices = models.PositiveIntegerField(
        default=0,
        verbose_name='إجمالي فواتير البيع'
    )
    total_purchase_invoices = models.PositiveIntegerField(
        default=0,
        verbose_name='إجمالي فواتير الشراء'
    )
    total_payments = models.PositiveIntegerField(
        default=0,
        verbose_name='إجمالي الدفعات'
    )
    total_returns = models.PositiveIntegerField(
        default=0,
        verbose_name='إجمالي المرتجعات'
    )
    total_complaints = models.PositiveIntegerField(
        default=0,
        verbose_name='إجمالي الشكاوي'
    )
    total_new_registrations = models.PositiveIntegerField(
        default=0,
        verbose_name='إجمالي التسجيلات الجديدة'
    )
    
    # مبالغ مالية
    total_sales_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='إجمالي مبيعات الوردية'
    )
    total_payments_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='إجمالي المدفوعات'
    )
    
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name='ملاحظات'
    )
    
    def __str__(self):
        duration = self.get_duration()
        return f"وردية {self.start_time.strftime('%Y-%m-%d %H:%M')} ({duration})"
    
    def get_duration(self):
        """حساب مدة الوردية."""
        if self.end_time:
            delta = self.end_time - self.start_time
            hours = delta.total_seconds() / 3600
            return f"{hours:.1f} ساعة"
        else:
            delta = timezone.now() - self.start_time
            hours = delta.total_seconds() / 3600
            return f"{hours:.1f} ساعة (مستمرة)"
    
    def close_shift(self, user, notes=""):
        """إغلاق الوردية."""
        self.status = 'CLOSED'
        self.end_time = timezone.now()
        self.closed_by = user
        if notes:
            self.notes = notes
        self.save()
    
    def update_statistics(self):
        """تحديث إحصائيات الوردية."""
        from django.apps import apps
        
        SaleInvoice = apps.get_model('invoices', 'SaleInvoice')
        PurchaseInvoice = apps.get_model('invoices', 'PurchaseInvoice')
        SalePayment = apps.get_model('finance', 'SalePayment')
        PurchasePayment = apps.get_model('finance', 'PurchasePayment')
        SaleReturnInvoice = apps.get_model('invoices', 'SaleReturnInvoice')
        PurchaseReturnInvoice = apps.get_model('invoices', 'PurchaseReturnInvoice')
        Complaint = apps.get_model('profiles', 'Complaint')
        User = apps.get_model('accounts', 'User')
        
        # حساب الإحصائيات خلال فترة الوردية
        start = self.start_time
        end = self.end_time if self.end_time else timezone.now()
        
        # الفواتير
        self.total_sale_invoices = SaleInvoice.objects.filter(
            created_at__gte=start,
            created_at__lte=end
        ).count()
        
        self.total_purchase_invoices = PurchaseInvoice.objects.filter(
            created_at__gte=start,
            created_at__lte=end
        ).count()
        
        # الدفعات
        sale_payments = SalePayment.objects.filter(
            timestamp__gte=start,
            timestamp__lte=end
        )
        purchase_payments = PurchasePayment.objects.filter(
            timestamp__gte=start,
            timestamp__lte=end
        )
        
        self.total_payments = sale_payments.count() + purchase_payments.count()
        self.total_payments_amount = (
            sum(sale_payments.values_list('amount', flat=True)) +
            sum(purchase_payments.values_list('amount', flat=True))
        )
        
        # المرتجعات
        self.total_returns = (
            SaleReturnInvoice.objects.filter(created_at__gte=start, created_at__lte=end).count() +
            PurchaseReturnInvoice.objects.filter(created_at__gte=start, created_at__lte=end).count()
        )
        
        # الشكاوي
        self.total_complaints = Complaint.objects.filter(
            created_at__gte=start,
            created_at__lte=end
        ).count()
        
        # التسجيلات الجديدة
        self.total_new_registrations = User.objects.filter(
            role='PHARMACY',
            date_joined__gte=start,
            date_joined__lte=end
        ).count()
        
        # المبيعات
        self.total_sales_amount = sum(
            SaleInvoice.objects.filter(
                created_at__gte=start,
                created_at__lte=end
            ).values_list('total_price', flat=True)
        )
        
        self.save()
