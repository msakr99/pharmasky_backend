# market/management/commands/upload_store_product_codes.py
import pandas as pd
import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from market.models import Store, StoreProductCodeUpload
from market.utils_pkg.advanced_uploader import AdvancedStoreProductCodeUploader

class Command(BaseCommand):
    help = 'رفع أكواد منتجات المخازن من ملف Excel مع معالجة التعارضات'
    
    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='مسار ملف Excel')
        parser.add_argument('store_id', type=int, help='معرف المخزن')
        parser.add_argument('--max-workers', type=int, default=3, help='أقصى عدد للعمليات المتوازية')
        parser.add_argument('--max-retries', type=int, default=3, help='أقصى عدد لإعادة المحاولة')
        parser.add_argument('--conflict-strategy', 
                          choices=['update', 'skip', 'create_new'],
                          default='update',
                          help='إستراتيجية معالجة التعارضات')
        parser.add_argument('--create-upload-record', action='store_true', help='إنشاء سجل الرفع في قاعدة البيانات')
        parser.add_argument('--dry-run', action='store_true', help='محاكاة الرفع بدون حفظ التغييرات')
    
    def handle(self, *args, **options):
        file_path = options['file_path']
        store_id = options['store_id']
        conflict_strategy = options['conflict_strategy']
        dry_run = options['dry_run']
        create_upload_record = options['create_upload_record']
        
        if dry_run:
            self.stdout.write(self.style.WARNING("🚧 وضع المحاكاة - لن يتم حفظ أي تغييرات"))
        
        # إنشاء سجل الرفع إذا طلب
        upload_record = None
        if create_upload_record and not dry_run:
            upload_record = StoreProductCodeUpload.objects.create(
                store_id=store_id,
                status='processing',
                total_rows=0
            )
        
        try:
            # قراءة الملف
            self.stdout.write(f"📖 جاري قراءة الملف: {file_path}")
            df = pd.read_excel(file_path)
            self.stdout.write(f"📊 تم العثور على {len(df)} سجل في الملف")
            
            # التحقق من المخزن
            store = Store.objects.get(id=store_id)
            self.stdout.write(f"🏪 جاري المعالجة للمخزن: {store.name}")
            self.stdout.write(f"⚡ إستراتيجية التعارض: {conflict_strategy}")
            
            # إنشاء المحمل
            uploader = AdvancedStoreProductCodeUploader(
                store_id=store_id,
                max_workers=options['max_workers'],
                max_retries=options['max_retries'],
                conflict_strategy=conflict_strategy
            )
            
            # التنفيذ الفعلي أو المحاكاة
            if dry_run:
                result = uploader.simulate_upload(df)
            else:
                result = uploader.upload_from_dataframe(df)
            
            # عرض النتائج
            if result['success']:
                self.stdout.write(self.style.SUCCESS("✅ اكتمل الرفع بنجاح!"))
                self._display_results(result, dry_run)
                
                # تحديث سجل الرفع
                if upload_record:
                    self._update_upload_record(upload_record, result, 'completed')
                
            else:
                self.stdout.write(self.style.ERROR("❌ فشل الرفع!"))
                self.stdout.write(f"الخطأ: {result['error']}")
                
                if upload_record:
                    self._update_upload_record(upload_record, result, 'failed')
            
            # حفظ التقرير
            self._save_detailed_report(result, store_id)
            
        except Store.DoesNotExist:
            error_msg = f"المخزن بالمعرف {store_id} غير موجود"
            self.stdout.write(self.style.ERROR(error_msg))
            
            if upload_record:
                self._update_upload_record(upload_record, {'error': error_msg}, 'failed')
                
        except Exception as e:
            error_msg = f"خطأ غير متوقع: {str(e)}"
            self.stdout.write(self.style.ERROR(error_msg))
            
            if upload_record:
                self._update_upload_record(upload_record, {'error': error_msg}, 'failed')
    
    def _display_results(self, result, dry_run=False):
        """عرض النتائج"""
        if 'report' not in result:
            return
        
        report = result['report']['summary']
        
        mode = " (محاكاة)" if dry_run else ""
        
        self.stdout.write(f"""
📈 ملخص الرفع{mode}:
   • إجمالي السجلات: {report['total_rows']}
   • الناجحة: {report['successful_rows']}
   • الفاشلة: {report['failed_rows']}
   • التعارضات: {report['conflict_rows']}
   • معدل النجاح: {report['success_rate']:.1f}%
   • المحاولات المتكررة: {report['retry_count']}
   
   • تم إنشاؤها: {report['created']}
   • تم تحديثها: {report['updated']}
   • تم تخطيها: {report['skipped']}
        """)
        
        # عرض التعارضات إذا وجدت
        if report['conflict_rows'] > 0:
            self.stdout.write(self.style.WARNING(f"⚠️  تم العثور على {report['conflict_rows']} تعارض"))
    
    def _update_upload_record(self, upload_record, result, status):
        """تحديث سجل الرفع"""
        try:
            upload_record.status = status
            upload_record.processed_at = timezone.now()
            
            if 'report' in result:
                report = result['report']['summary']
                upload_record.total_rows = report['total_rows']
                upload_record.successful_rows = report['successful_rows']
                upload_record.failed_rows = report['failed_rows']
                upload_record.results = result['report']
            
            if 'error' in result:
                upload_record.error_log = result['error']
            
            upload_record.save()
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"فشل تحديث سجل الرفع: {e}"))
    
    def _save_detailed_report(self, result, store_id):
        """حفظ التقرير المفصل"""
        try:
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"upload_report_{store_id}_{timestamp}.json"
            
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(result.get('report', {}), f, ensure_ascii=False, indent=2)
            
            self.stdout.write(f"📄 تم حفظ التقرير المفصل في: {report_filename}")
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"فشل حفظ التقرير: {e}"))