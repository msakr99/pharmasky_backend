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
    Process uploaded file for store product codes with flexible matching
    """
    try:
        from .models import StoreProductCodeUpload, StoreProductCode, Product
        import pandas as pd
        from django.db import transaction
        from difflib import SequenceMatcher
        
        upload = StoreProductCodeUpload.objects.get(id=upload_id)
        upload.status = 'processing'
        upload.save()
        
        # Read the uploaded file
        if upload.file.name.endswith('.xlsx'):
            df = pd.read_excel(upload.file.path)
        elif upload.file.name.endswith('.csv'):
            df = pd.read_csv(upload.file.path)
        else:
            raise ValueError("Unsupported file format")
        
        successful_rows = 0
        failed_rows = 0
        errors = []
        results = []
        
        # Process each row
        for index, row in df.iterrows():
            try:
                product_name = str(row['product_name']).strip()
                code = int(row['code'])
                price = float(row['price']) if 'price' in row and pd.notna(row['price']) else None
                
                # Flexible search for product by name
                product, match_score = find_product_by_flexible_name(
                    product_name, 
                    threshold=0.8  # 80% match minimum
                )
                
                # Check if product exists
                if not product:
                    error_msg = f"المنتج '{product_name}' غير موجود في قاعدة البيانات"
                    errors.append(f"Row {index + 2}: {error_msg}")
                    failed_rows += 1
                    results.append({
                        'row': index + 2,
                        'product_name': product_name,
                        'code': code,
                        'status': 'failed',
                        'error': error_msg
                    })
                    continue
                
                # Check price match (if provided)
                if price is not None:
                    if not is_price_match(price, product.public_price, tolerance=0.1):
                        error_msg = f"السعر غير متطابق. السعر في الملف: {price}, السعر في النظام: {product.public_price}"
                        errors.append(f"Row {index + 2}: {error_msg}")
                        failed_rows += 1
                        results.append({
                            'row': index + 2,
                            'product_name': product_name,
                            'code': code,
                            'status': 'failed',
                            'error': error_msg
                        })
                        continue
                
                # Create or update product code
                with transaction.atomic():
                    store_code, created = StoreProductCode.objects.update_or_create(
                        product=product,
                        store=upload.store,
                        defaults={'code': code}
                    )
                
                successful_rows += 1
                results.append({
                    'row': index + 2,
                    'product_name': product_name,
                    'code': code,
                    'status': 'success',
                    'product_id': product.id,
                    'matched_name': product.name,
                    'match_score': round(match_score, 2),
                    'price': float(product.public_price),
                    'price_difference': round(abs(price - product.public_price), 2) if price else 0,
                    'flexibility_used': match_score < 1.0 or (price and abs(price - product.public_price) > 0.01)
                })
                
            except Exception as e:
                error_msg = f"خطأ في معالجة الصف: {str(e)}"
                errors.append(f"Row {index + 2}: {error_msg}")
                failed_rows += 1
                results.append({
                    'row': index + 2,
                    'product_name': str(row.get('product_name', '')),
                    'code': str(row.get('code', '')),
                    'status': 'failed',
                    'error': error_msg
                })
        
        # Update statistics
        upload.status = 'completed'
        upload.processed_at = timezone.now()
        upload.total_rows = len(df)
        upload.successful_rows = successful_rows
        upload.failed_rows = failed_rows
        upload.error_log = '\n'.join(errors)
        upload.results = results
        upload.save()
        
        logger.info(f"Successfully processed upload {upload_id}: {successful_rows}/{len(df)} successful")
        
        return {
            'success': True,
            'upload_id': upload_id,
            'total_rows': len(df),
            'successful_rows': successful_rows,
            'failed_rows': failed_rows
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


def find_product_by_flexible_name(product_name, threshold=0.8):
    """
    Find product with flexible name matching using fuzzy string matching
    """
    from .models import Product
    from difflib import SequenceMatcher
    
    products = Product.objects.all()
    best_match = None
    best_score = 0
    
    for product in products:
        # Compare Arabic name
        arabic_score = SequenceMatcher(None, product_name.lower(), product.name.lower()).ratio()
        
        # Compare English name
        english_score = SequenceMatcher(None, product_name.lower(), product.e_name.lower()).ratio()
        
        # Take the highest score
        score = max(arabic_score, english_score)
        
        if score > best_score and score >= threshold:
            best_score = score
            best_match = product
    
    return best_match, best_score


def is_price_match(file_price, system_price, tolerance=0.1):
    """
    Check if prices match within tolerance
    """
    price_difference = abs(system_price - file_price)
    return price_difference <= tolerance
