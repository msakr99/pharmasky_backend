from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from market.models import ProductMatchCache, StoreProductCodeUpload
import os


class Command(BaseCommand):
    help = 'Clean up old cache entries and upload files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cache-days',
            type=int,
            default=30,
            help='Number of days to keep cache entries (default: 30)'
        )
        parser.add_argument(
            '--upload-days',
            type=int,
            default=90,
            help='Number of days to keep upload files (default: 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        cache_days = options['cache_days']
        upload_days = options['upload_days']
        dry_run = options['dry_run']

        self.stdout.write(
            self.style.SUCCESS(f'Starting cleanup process...')
        )

        # Clean up cache entries
        self.cleanup_cache_entries(cache_days, dry_run)

        # Clean up upload files
        self.cleanup_upload_files(upload_days, dry_run)

        self.stdout.write(
            self.style.SUCCESS('Cleanup process completed!')
        )

    def cleanup_cache_entries(self, days, dry_run):
        """Clean up old cache entries"""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        old_entries = ProductMatchCache.objects.filter(
            last_accessed__lt=cutoff_date
        )
        
        count = old_entries.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'Would delete {count} cache entries older than {days} days')
            )
        else:
            deleted_count = old_entries.delete()[0]
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {deleted_count} cache entries older than {days} days')
            )

    def cleanup_upload_files(self, days, dry_run):
        """Clean up old upload files"""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        old_uploads = StoreProductCodeUpload.objects.filter(
            uploaded_at__lt=cutoff_date,
            status__in=['completed', 'failed']
        )
        
        count = old_uploads.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'Would delete {count} upload files older than {days} days')
            )
        else:
            deleted_count = 0
            for upload in old_uploads:
                # Delete the physical file
                if upload.file and os.path.exists(upload.file.path):
                    try:
                        os.remove(upload.file.path)
                        self.stdout.write(f'Deleted file: {upload.file.path}')
                    except OSError as e:
                        self.stdout.write(
                            self.style.ERROR(f'Could not delete file {upload.file.path}: {e}')
                        )
                
                # Delete the database record
                upload.delete()
                deleted_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {deleted_count} upload files older than {days} days')
            )
