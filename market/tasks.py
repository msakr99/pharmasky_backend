from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def cleanup_old_product_match_cache(self, days_old=30):
    """
    Clean up old ProductMatchCache entries that haven't been accessed recently
    
    Args:
        days_old (int): Number of days to consider cache entries as old
    """
    try:
        from .models import ProductMatchCache
        
        cutoff_date = timezone.now() - timedelta(days=days_old)
        
        # Delete cache entries that haven't been accessed in the specified days
        old_entries = ProductMatchCache.objects.filter(
            last_accessed__lt=cutoff_date
        )
        
        count = old_entries.count()
        old_entries.delete()
        
        logger.info(f"Cleaned up {count} old ProductMatchCache entries older than {days_old} days")
        
        return {
            'success': True,
            'deleted_count': count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Error cleaning up ProductMatchCache: {exc}")
        # Retry the task with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def cleanup_old_upload_files(self, days_old=90):
    """
    Clean up old StoreProductCodeUpload files and records
    
    Args:
        days_old (int): Number of days to consider upload records as old
    """
    try:
        from .models import StoreProductCodeUpload
        import os
        
        cutoff_date = timezone.now() - timedelta(days=days_old)
        
        # Get old upload records
        old_uploads = StoreProductCodeUpload.objects.filter(
            uploaded_at__lt=cutoff_date,
            status__in=['completed', 'failed']
        )
        
        deleted_count = 0
        for upload in old_uploads:
            # Delete the physical file
            if upload.file and os.path.exists(upload.file.path):
                try:
                    os.remove(upload.file.path)
                except OSError as e:
                    logger.warning(f"Could not delete file {upload.file.path}: {e}")
            
            # Delete the database record
            upload.delete()
            deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} old StoreProductCodeUpload records older than {days_old} days")
        
        return {
            'success': True,
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Error cleaning up StoreProductCodeUpload: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def process_upload_file(upload_id):
    """
    Process uploaded file for store product codes
    This is a placeholder - implement your file processing logic here
    """
    try:
        from .models import StoreProductCodeUpload
        
        upload = StoreProductCodeUpload.objects.get(id=upload_id)
        upload.status = 'processing'
        upload.save()
        
        # TODO: Implement your file processing logic here
        # Example:
        # - Read the uploaded file
        # - Parse the data
        # - Create/update StoreProductCode records
        # - Update upload statistics
        
        # Simulate processing
        import time
        time.sleep(2)  # Remove this in real implementation
        
        # Update status to completed
        upload.status = 'completed'
        upload.processed_at = timezone.now()
        upload.total_rows = 100  # Example
        upload.successful_rows = 95  # Example
        upload.failed_rows = 5  # Example
        upload.save()
        
        logger.info(f"Successfully processed upload {upload_id}")
        
        return {
            'success': True,
            'upload_id': upload_id,
            'total_rows': upload.total_rows,
            'successful_rows': upload.successful_rows,
            'failed_rows': upload.failed_rows
        }
        
    except Exception as exc:
        logger.error(f"Error processing upload {upload_id}: {exc}")
        
        # Update status to failed
        try:
            upload = StoreProductCodeUpload.objects.get(id=upload_id)
            upload.status = 'failed'
            upload.error_log = str(exc)
            upload.save()
        except:
            pass
        
        raise exc
