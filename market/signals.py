from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender='market.StoreProductCodeUpload')
def handle_upload_status_change(sender, instance, created, **kwargs):
    """
    Handle upload status changes and send notifications
    """
    if created:
        # New upload created
        logger.info(f"New upload created: {instance.id} for store {instance.store.name}")
        
        # Start processing the file asynchronously
        from .tasks import process_upload_file
        process_upload_file.delay(instance.id)
        
    else:
        # Upload status changed
        if instance.status == 'completed':
            handle_upload_completed(instance)
        elif instance.status == 'failed':
            handle_upload_failed(instance)


def handle_upload_completed(upload):
    """
    Handle successful upload completion
    """
    logger.info(f"Upload {upload.id} completed successfully")
    
    # Send success notification
    if upload.uploaded_by and upload.uploaded_by.email:
        try:
            send_mail(
                subject='تم رفع ملف أكواد المنتجات بنجاح',
                message=f'''
                تم معالجة ملف أكواد المنتجات بنجاح:
                
                المتجر: {upload.store.name}
                الملف: {upload.file_name}
                إجمالي الصفوف: {upload.total_rows}
                الصفوف الناجحة: {upload.successful_rows}
                الصفوف الفاشلة: {upload.failed_rows}
                نسبة النجاح: {upload.success_rate}%
                وقت المعالجة: {upload.processed_at}
                
                شكراً لاستخدامك النظام.
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[upload.uploaded_by.email],
                fail_silently=True,
            )
            logger.info(f"Success notification sent to {upload.uploaded_by.email}")
        except Exception as e:
            logger.error(f"Failed to send success notification: {e}")
    
    # Log completion
    logger.info(f"Upload {upload.id} processing completed: {upload.successful_rows}/{upload.total_rows} rows successful")


def handle_upload_failed(upload):
    """
    Handle failed upload
    """
    logger.error(f"Upload {upload.id} failed: {upload.error_log}")
    
    # Send failure notification
    if upload.uploaded_by and upload.uploaded_by.email:
        try:
            send_mail(
                subject='فشل في معالجة ملف أكواد المنتجات',
                message=f'''
                فشل في معالجة ملف أكواد المنتجات:
                
                المتجر: {upload.store.name}
                الملف: {upload.file_name}
                سبب الفشل: {upload.error_log}
                وقت المحاولة: {timezone.now()}
                
                يرجى مراجعة الملف وإعادة المحاولة.
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[upload.uploaded_by.email],
                fail_silently=True,
            )
            logger.info(f"Failure notification sent to {upload.uploaded_by.email}")
        except Exception as e:
            logger.error(f"Failed to send failure notification: {e}")


@receiver(post_save, sender='market.StoreProductCode')
def handle_store_product_code_change(sender, instance, created, **kwargs):
    """
    Handle store product code changes
    """
    if created:
        logger.info(f"New store product code created: {instance.code} for product {instance.product.name}")
    else:
        logger.info(f"Store product code updated: {instance.code} for product {instance.product.name}")


@receiver(post_save, sender='market.CodeChangeLog')
def handle_code_change_log(sender, instance, created, **kwargs):
    """
    Handle code change log entries
    """
    if created:
        logger.info(f"Code change logged: {instance.action} for code {instance.store_product_code.code}")


@receiver(post_save, sender='market.ProductMatchCache')
def handle_cache_entry_created(sender, instance, created, **kwargs):
    """
    Handle new cache entries
    """
    if created:
        logger.debug(f"New cache entry created: {instance.search_name} -> {instance.product.name}")


@receiver(post_delete, sender='market.ProductMatchCache')
def handle_cache_entry_deleted(sender, instance, **kwargs):
    """
    Handle cache entry deletion
    """
    logger.debug(f"Cache entry deleted: {instance.search_name} -> {instance.product.name}")


# Signal for cleanup tasks
@receiver(post_save, sender='market.ProductMatchCache')
def schedule_cache_cleanup(sender, instance, created, **kwargs):
    """
    Schedule cache cleanup when cache grows too large
    """
    if created:
        # Check if we need to schedule cleanup
        cache_count = sender.objects.count()
        
        # If cache has more than 10000 entries, schedule cleanup
        if cache_count > 10000:
            from .tasks import cleanup_old_product_match_cache
            cleanup_old_product_match_cache.delay(days_old=7)  # Clean entries older than 7 days
            logger.info(f"Cache cleanup scheduled due to large cache size: {cache_count} entries")


# Signal for monitoring upload file sizes
@receiver(pre_save, sender='market.StoreProductCodeUpload')
def monitor_upload_file_size(sender, instance, **kwargs):
    """
    Monitor upload file sizes and log warnings for large files
    """
    if instance.file and hasattr(instance.file, 'size'):
        file_size_mb = instance.file.size / (1024 * 1024)
        
        if file_size_mb > 5:  # Log warning for files larger than 5MB
            logger.warning(f"Large file upload detected: {file_size_mb:.2f}MB for store {instance.store.name}")
        
        if file_size_mb > 10:  # Log error for files larger than 10MB
            logger.error(f"Very large file upload detected: {file_size_mb:.2f}MB for store {instance.store.name}")


# Signal for tracking cache performance
@receiver(post_save, sender='market.ProductMatchCache')
def track_cache_performance(sender, instance, created, **kwargs):
    """
    Track cache performance metrics
    """
    if created:
        # Log cache hit rate statistics
        total_cache_entries = sender.objects.count()
        high_confidence_entries = sender.objects.filter(confidence_score__gte=0.8).count()
        
        if total_cache_entries > 0:
            high_confidence_rate = (high_confidence_entries / total_cache_entries) * 100
            
            if high_confidence_rate < 50:  # Log warning if less than 50% high confidence
                logger.warning(f"Low cache confidence rate: {high_confidence_rate:.1f}% of entries have high confidence")
            
            logger.info(f"Cache statistics: {total_cache_entries} total entries, {high_confidence_rate:.1f}% high confidence")