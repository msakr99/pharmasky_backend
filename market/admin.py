from typing import Any
from django.contrib import admin
from django import forms
from django.db import transaction
from django.db.models import Sum, Count, Avg
from django.db.models.functions import Upper, Substr
from django.db.models.query import QuerySet
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
import csv

from core.admin.abstract_admin import DefaultBaseAdminItems
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin
from import_export import resources
from .models import *


class StoreProductCodeResource(resources.ModelResource):
    """Resource for importing/exporting StoreProductCode data"""
    
    class Meta:
        model = StoreProductCode
        fields = (
            'id',
            'product',
            'store',
            'code',
            'is_active',
            'created_at',
            'updated_at'
        )
        export_order = fields
        import_id_fields = ['product', 'store']
        skip_unchanged = False
        report_skipped = True
        use_bulk = False
        
    def before_import_row(self, row, **kwargs):
        """Custom logic before importing each row"""
        # Clean and validate row data
        try:
            # Ensure code is properly formatted
            if 'code' in row:
                row['code'] = str(row['code']).strip()
            
            # Log processing with better formatting
            product_id = row.get('product', 'N/A')
            store_id = row.get('store', 'N/A')
            code = row.get('code', 'N/A')
            print(f"🔍 Processing: Product {product_id}, Store {store_id}, Code {code}")
            
        except Exception as e:
            print(f"❌ Error processing row: {e}")
            raise
        
    def after_import_row(self, row, row_result, **kwargs):
        """Custom logic after importing each row"""
        product_id = row.get('product', 'N/A')
        code = row.get('code', 'N/A')
        
        if row_result.import_type == row_result.IMPORT_TYPE_NEW:
            print(f"✅ Imported: Product {product_id}, Code {code}")
        elif row_result.import_type == row_result.IMPORT_TYPE_UPDATE:
            print(f"🔄 Updated: Product {product_id}, Code {code}")
        elif row_result.import_type == row_result.IMPORT_TYPE_SKIP:
            print(f"⏭️ Skipped: Product {product_id}, Code {code}")
        else:
            error_msg = row_result.errors[0].error if row_result.errors else "Unknown error"
            print(f"❌ Failed: Product {product_id}, Code {code} - {error_msg}")
    
    def get_import_id_fields(self):
        """Get import ID fields"""
        return self._meta.import_id_fields
    
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """Called before import starts"""
        print(f"📊 Dataset info: {len(dataset)} rows, {len(dataset.headers)} columns")
        print(f"📋 Headers: {dataset.headers}")
        
        if dry_run:
            print(f"🔍 Starting DRY RUN... (No data will be saved)")
        else:
            print(f"🚀 Starting REAL IMPORT... (Data will be saved)")
        
        # Log dry run status
        if dry_run:
            print("⚠️  WARNING: This is a DRY RUN - no data will be saved to database!")
        else:
            print("✅ This is a REAL IMPORT - data will be saved to database!")
        
    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        """Called after import completes"""
        totals = result.totals
        print(f"📈 Import Results:")
        print(f"   ✅ New: {totals.get('new', 0)}")
        print(f"   🔄 Updated: {totals.get('update', 0)}")
        print(f"   ⏭️ Skipped: {totals.get('skip', 0)}")
        print(f"   ❌ Errors: {totals.get('error', 0)}")
        
        if dry_run:
            print(f"🔍 DRY RUN completed! (No data was saved)")
            print("⚠️  To actually import data, uncheck the 'Dry run' checkbox and try again!")
        else:
            print(f"✅ IMPORT completed! (Data was saved)")
        
        # Print detailed error information
        if result.has_errors():
            print(f"❌ Import errors found:")
            for i, error in enumerate(result.errors[:10]):  # Show first 10 errors
                print(f"   Error {i+1}: {error}")
        
        if result.has_validation_errors():
            print(f"⚠️ Validation errors:")
            for i, error in enumerate(result.validation_errors[:10]):
                print(f"   Validation Error {i+1}: {error}")


@admin.register(Company)
class CompanyModelAdmin(DefaultBaseAdminItems):
    list_display = ("name", "e_name")
    search_fields = ("name", "e_name")
    search_help_text = _("Search by company name.")


@admin.register(Category)
class CategoryModelAdmin(DefaultBaseAdminItems):
    list_display = ("name", "e_name")
    search_fields = ("name", "e_name")
    search_help_text = _("Search by category name.")


@admin.register(Product)
class ProductModelAdmin(DefaultBaseAdminItems):
    @admin.action(description="Add letters")
    def update_seller_invoice_items_count(modeladmin, request, queryset):
        queryset.update(letter=Upper(Substr("e_name", 1, 1)))

    def company_name(self, obj: Product) -> str:
        return obj.company.name

    def category_name(self, obj: Product) -> str:
        return obj.category.name

    def has_store_code(self, obj: Product) -> bool:
        return obj.store_product_codes.exists()

    class ProductStoreCodeFilter(admin.SimpleListFilter):
        title = _("Has store product code")
        parameter_name = "has_store_code"

        def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
            return [("true", "True"), ("false", "False")]

        def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
            if self.value() == "true":
                return queryset.filter(store_product_codes__isnull=False)
            elif self.value() == "false":
                return queryset.filter(store_product_codes__isnull=True)
            return queryset

    list_display = (
        "name",
        "e_name",
        "letter",
        "public_price",
        "company_name",
        "category_name",
        "has_store_code",
    )
    list_filter = (
        ProductStoreCodeFilter,
        "needed",
        "company",
        "category",
        "shape",
        "letter",
    )
    actions = (update_seller_invoice_items_count,)
    search_fields = ("name", "e_name")
    search_help_text = _("Search by product name, company, category, or effective material.")
    list_select_related = ("company", "category")
    autocomplete_fields = ("company", "category")


@admin.register(StoreProductCode)
class StoreProductCodeModelAdmin(ImportExportMixin, admin.ModelAdmin):
    """Admin for StoreProductCode with Import/Export functionality"""
    
    resource_class = StoreProductCodeResource
    
    # Import/Export permissions
    def has_import_permission(self, request):
        # Allow import for superusers or users with add permission
        return request.user.is_superuser or request.user.has_perm('market.add_storeproductcode')
    
    def has_export_permission(self, request):
        # Allow export for superusers or users with view permission
        return request.user.is_superuser or request.user.has_perm('market.view_storeproductcode')
    
    def changelist_view(self, request, extra_context=None):
        try:
            # Add debug info
            if extra_context is None:
                extra_context = {}
            extra_context['has_import_permission'] = self.has_import_permission(request)
            extra_context['has_export_permission'] = self.has_export_permission(request)
            print(f"DEBUG: has_import_permission = {extra_context['has_import_permission']}")
            print(f"DEBUG: has_export_permission = {extra_context['has_export_permission']}")
            print(f"DEBUG: user = {request.user}")
            print(f"DEBUG: user.is_superuser = {request.user.is_superuser}")
            return super().changelist_view(request, extra_context)
        except Exception as e:
            print(f"Error in StoreProductCode admin: {e}")
            import traceback
            traceback.print_exc()
            raise

    list_display = (
        "product",
        "store", 
        "code",
        "is_active",
        "updated_at",
    )
    list_filter = ("store", "is_active", "product__company", "product__category")
    search_fields = ("code", "product__name", "product__e_name", "store__name", "store__e_name", "id")
    list_select_related = ("product", "product__company", "product__category", "store")
    readonly_fields = ("id", "created_at", "updated_at")
    
    # Import/Export settings - use default templates
    import_template_name = 'admin/import_export/import.html'
    export_template_name = 'admin/import_export/export.html'
    
    # Override the default template for change_list
    change_list_template = 'admin/import_export/change_list_import_export.html'
    
    # Ensure the template context has the right variables
    def changelist_view(self, request, extra_context=None):
        try:
            # Add debug info
            if extra_context is None:
                extra_context = {}
            extra_context['has_import_permission'] = self.has_import_permission(request)
            extra_context['has_export_permission'] = self.has_export_permission(request)
            print(f"DEBUG: has_import_permission = {extra_context['has_import_permission']}")
            print(f"DEBUG: has_export_permission = {extra_context['has_export_permission']}")
            print(f"DEBUG: user = {request.user}")
            print(f"DEBUG: user.is_superuser = {request.user.is_superuser}")
            return super().changelist_view(request, extra_context)
        except Exception as e:
            print(f"Error in StoreProductCode admin: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    # Ensure import/export URLs are available
    def get_import_url(self):
        return f"{self.model._meta.model_name}/import/"
    
    def get_export_url(self):
        return f"{self.model._meta.model_name}/export/"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'product', 'product__company', 'product__category', 'store'
        )
    
    def get_import_resource_kwargs(self, request, **kwargs):
        """Customize import resource kwargs"""
        return {
            'request': request,
            'user': request.user,
        }
    
    def get_export_resource_kwargs(self, request, **kwargs):
        """Customize export resource kwargs"""
        return {
            'request': request,
            'user': request.user,
        }
    
    def get_import_resource_kwargs(self, request, **kwargs):
        """Customize import resource kwargs"""
        return {
            'request': request,
            'user': request.user,
        }
    
    def get_import_resource_class(self):
        """Return the resource class for import"""
        return StoreProductCodeResource
    
    def get_export_resource_class(self):
        """Return the resource class for export"""
        return StoreProductCodeResource
    
    def import_action(self, request, *args, **kwargs):
        """Custom import action with better logging"""
        print(f"🎯 Import action called by user: {request.user}")
        print(f"📁 Request files: {list(request.FILES.keys())}")
        
        if 'import_file' in request.FILES:
            file = request.FILES['import_file']
            print(f"📄 File name: {file.name}")
            print(f"📏 File size: {file.size} bytes")
            print(f"📋 Content type: {file.content_type}")
        
        # Call parent import action
        result = super().import_action(request, *args, **kwargs)
        print(f"🎉 Import action completed: {result}")
        return result
    
    def get_import_form(self):
        """Return the import form class"""
        from import_export.forms import ImportForm
        return ImportForm
    
    def get_import_resource(self):
        """Return the import resource instance"""
        resource_class = self.get_import_resource_class()
        return resource_class()
    
    def get_export_resource(self):
        """Return the export resource instance"""
        resource_class = self.get_export_resource_class()
        return resource_class()
    
    def get_import_resource_kwargs(self, request, **kwargs):
        """Customize import resource kwargs"""
        return {
            'request': request,
            'user': request.user,
        }
    
    def get_urls(self):
        """Add custom URLs for template download"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('download-template/', 
                 self.admin_site.admin_view(self.download_template_view),
                 name='%s_%s_download_template' % (self.model._meta.app_label, self.model._meta.model_name)),
        ]
        return custom_urls + urls
    
    def download_template_view(self, request):
        """Download CSV template for import with better instructions"""
        from django.http import HttpResponse
        
        template_content = """# Store Product Codes Import Template
# Required columns: product, store, code
# Optional columns: is_active
#
# Instructions:
# 1. product: Product ID (must exist in database)
# 2. store: Store ID (must exist in database)  
# 3. code: Product code for this store (numeric)
# 4. is_active: true/false (default: true)
#
# Example:
product,store,code,is_active
68,4,1001,true
69,4,1002,true
70,4,1003,true

# Common issues to avoid:
# - Product ID must exist in the Products table
# - Store ID must exist in the Stores table
# - Code must be unique per product-store combination
# - Code must be numeric and positive
"""
        
        response = HttpResponse(template_content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="storeproductcode_import_template.csv"'
        return response

    def analyze_import_errors(self, result):
        """Analyze and categorize import errors"""
        if not result.has_errors():
            return "No errors found"
        
        error_categories = {
            'product_not_found': [],
            'store_not_found': [], 
            'duplicate_codes': [],
            'invalid_data': [],
            'other_errors': []
        }
        
        for error in result.errors:
            error_msg = str(error.error).lower()
            
            if 'product' in error_msg and ('not found' in error_msg or 'does not exist' in error_msg):
                error_categories['product_not_found'].append(error)
            elif 'store' in error_msg and ('not found' in error_msg or 'does not exist' in error_msg):
                error_categories['store_not_found'].append(error)
            elif 'duplicate' in error_msg or 'unique' in error_msg:
                error_categories['duplicate_codes'].append(error)
            elif 'invalid' in error_msg or 'valid' in error_msg:
                error_categories['invalid_data'].append(error)
            else:
                error_categories['other_errors'].append(error)
        
        # Print analysis
        print("🔍 Error Analysis:")
        for category, errors in error_categories.items():
            if errors:
                print(f"   {category}: {len(errors)} errors")
        
        return error_categories


@admin.register(ProductCode)
class ProductCodeModelAdmin(DefaultBaseAdminItems):
    list_display = (
        "product",
        "user",
        "code",
    )
    list_filter = ("user",)
    search_fields = ("code", "product__name", "user__name")
    search_help_text = _("Search by code, product name or user name.")
    autocomplete_fields = ("product", "user")


@admin.register(PharmacyProductWishList)
class PharmcyProductWishListModelAdmin(DefaultBaseAdminItems):
    list_display = (
        "product",
        "pharmacy",
        "created_at",
    )
    list_filter = (
        "created_at",
        "pharmacy",
        "product",
    )
    search_fields = (
        "product__name",
        "product__e_name",
        "pharmacy__name",
        "pharmacy__e_name",
    )
    search_help_text = _("Search by pharmacy name or product name.")


class StoreProductCodeUploadForm(forms.ModelForm):
    """Custom form for StoreProductCodeUpload to handle file validation better"""
    
    class Meta:
        model = StoreProductCodeUpload
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Only validate file content if a new file is being uploaded
        file = cleaned_data.get('file')
        if file and hasattr(file, 'file') and file.file:
            try:
                from .validators import StoreProductCodeFileValidator
                validator = StoreProductCodeFileValidator()
                validator(file)
            except Exception as e:
                # Log the error but don't break the admin form
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"File validation error in admin form: {e}")
                # Only raise validation errors for critical issues
                if "file_too_large" in str(e) or "invalid_extension" in str(e):
                    raise
        
        return cleaned_data


@admin.register(StoreProductCodeUpload)
class StoreProductCodeUploadAdmin(admin.ModelAdmin):
    form = StoreProductCodeUploadForm
    list_display = (
        'store',
        'file_name',
        'status',
        'uploaded_at',
        'processed_at',
        'total_rows',
        'successful_rows',
        'failed_rows',
        'success_rate_display',
        'file_size_display',
        'uploaded_by'
    )
    
    list_filter = (
        'status',
        'uploaded_at',
        'processed_at',
        'store',
        'uploaded_by'
    )
    
    search_fields = (
        'file_name',
        'store__name',
        'uploaded_by__username',
        'uploaded_by__email'
    )
    
    readonly_fields = (
        'uploaded_at',
        'processed_at',
        'file_size',
        'total_rows',
        'successful_rows',
        'failed_rows',
        'success_rate_display',
        'file_size_display',
        'error_log_display'
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('store', 'uploaded_by', 'file', 'file_name', 'file_size_display')
        }),
        ('Processing Status', {
            'fields': ('status', 'uploaded_at', 'processed_at')
        }),
        ('Statistics', {
            'fields': ('total_rows', 'successful_rows', 'failed_rows', 'success_rate_display')
        }),
        ('Results & Errors', {
            'fields': ('results', 'error_log_display'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['retry_processing', 'export_results', 'mark_as_completed']
    
    def success_rate_display(self, obj):
        """Display success rate with color coding"""
        if obj is None:
            return "N/A"
        rate = obj.success_rate
        try:
            rate_float = float(rate)
        except (TypeError, ValueError):
            return "N/A"
        if rate >= 90:
            color = 'green'
        elif rate >= 70:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, f"{rate_float:.1f}"
        )
    success_rate_display.short_description = 'Success Rate'
    success_rate_display.admin_order_field = 'successful_rows'
    
    def file_size_display(self, obj):
        """Display file size in human readable format"""
        if obj is None:
            return 'N/A'

        if not obj.file_size:
            return 'N/A'
        
        size_mb = obj.file_size / (1024 * 1024)
        return f"{size_mb:.2f} MB"
    file_size_display.short_description = 'File Size'
    
    def error_log_display(self, obj):
        """Display error log in a formatted way"""
        if obj is None:
            return 'No errors'

        if not obj.error_log:
            return 'No errors'
        
        return format_html(
            '<pre style="white-space: pre-wrap; max-height: 200px; overflow-y: auto;">{}</pre>',
            obj.error_log
        )
    error_log_display.short_description = 'Error Log'
    
    @admin.action(description="Retry processing selected uploads")
    def retry_processing(self, request, queryset):
        """Retry processing for selected uploads"""
        from .tasks import process_upload_file
        
        count = 0
        for upload in queryset.filter(status__in=['failed', 'pending']):
            upload.status = 'pending'
            upload.error_log = ''
            upload.save()
            process_upload_file.delay(upload.id)
            count += 1
        
        self.message_user(request, f"Retried processing for {count} uploads.")
    
    @admin.action(description="Export results as CSV")
    def export_results(self, request, queryset):
        """Export upload results as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="upload_results.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Store', 'File Name', 'Status', 'Uploaded At', 'Processed At',
            'Total Rows', 'Successful Rows', 'Failed Rows', 'Success Rate'
        ])
        
        for upload in queryset:
            writer.writerow([
                upload.store.name,
                upload.file_name,
                upload.status,
                upload.uploaded_at,
                upload.processed_at,
                upload.total_rows,
                upload.successful_rows,
                upload.failed_rows,
                f"{upload.success_rate:.1f}%"
            ])
        
        return response
    
    @admin.action(description="Mark as completed")
    def mark_as_completed(self, request, queryset):
        """Mark selected uploads as completed"""
        count = queryset.filter(status='processing').update(
            status='completed',
            processed_at=timezone.now()
        )
        self.message_user(request, f"Marked {count} uploads as completed.")
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('store', 'uploaded_by')


@admin.register(ProductMatchCache)
class ProductMatchCacheAdmin(admin.ModelAdmin):
    list_display = (
        'search_name',
        'product_link',
        'confidence_score_display',
        'created_at',
        'last_accessed',
        'access_count',
        'cache_age'
    )
    
    list_filter = (
        'created_at',
        'last_accessed',
        'confidence_score',
        'product__company',
        'product__category'
    )
    
    search_fields = (
        'search_name',
        'product__name',
        'product__e_name'
    )
    
    readonly_fields = (
        'created_at',
        'last_accessed',
        'access_count',
        'cache_age'
    )
    
    fieldsets = (
        ('Cache Information', {
            'fields': ('search_name', 'product', 'confidence_score')
        }),
        ('Usage Statistics', {
            'fields': ('created_at', 'last_accessed', 'access_count', 'cache_age')
        }),
    )
    
    actions = ['clear_old_cache', 'export_cache_stats']
    
    def product_link(self, obj):
        """Display product as a link"""
        url = reverse('admin:market_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'
    product_link.admin_order_field = 'product__name'
    
    def confidence_score_display(self, obj):
        """Display confidence score with color coding"""
        score = obj.confidence_score
        if score >= 0.8:
            color = 'green'
        elif score >= 0.6:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}</span>',
            color, score
        )
    confidence_score_display.short_description = 'Confidence'
    confidence_score_display.admin_order_field = 'confidence_score'
    
    def cache_age(self, obj):
        """Display cache age in days"""
        from django.utils import timezone
        age = timezone.now() - obj.created_at
        return f"{age.days} days"
    cache_age.short_description = 'Age'
    
    @admin.action(description="Clear old cache entries")
    def clear_old_cache(self, request, queryset):
        """Clear old cache entries"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=30)
        old_entries = ProductMatchCache.objects.filter(
            last_accessed__lt=cutoff_date
        )
        
        count = old_entries.count()
        old_entries.delete()
        
        self.message_user(request, f"Cleared {count} old cache entries.")
    
    @admin.action(description="Export cache statistics")
    def export_cache_stats(self, request, queryset):
        """Export cache statistics as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="cache_statistics.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Search Name', 'Product', 'Confidence Score', 'Created At',
            'Last Accessed', 'Access Count', 'Cache Age (days)'
        ])
        
        for cache in queryset:
            age = (timezone.now() - cache.created_at).days
            writer.writerow([
                cache.search_name,
                cache.product.name,
                cache.confidence_score,
                cache.created_at,
                cache.last_accessed,
                cache.access_count,
                age
            ])
        
        return response
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('product', 'product__company', 'product__category')


@admin.register(CodeChangeLog)
class CodeChangeLogAdmin(admin.ModelAdmin):
    list_display = (
        'store_product_code',
        'action',
        'old_code',
        'new_code',
        'changed_by',
        'changed_at',
        'reason_short'
    )
    
    list_filter = (
        'action',
        'changed_at',
        'changed_by'
    )
    
    search_fields = (
        'store_product_code__product__name',
        'store_product_code__store__name',
        'changed_by__username',
        'reason'
    )
    
    readonly_fields = (
        'changed_at',
        'reason_display'
    )
    
    fieldsets = (
        ('Change Information', {
            'fields': ('store_product_code', 'action', 'old_code', 'new_code', 'changed_by')
        }),
        ('Details', {
            'fields': ('changed_at', 'reason_display')
        }),
    )
    
    def reason_short(self, obj):
        """Display shortened reason"""
        if not obj.reason:
            return 'No reason provided'
        
        return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
    reason_short.short_description = 'Reason'
    
    def reason_display(self, obj):
        """Display full reason"""
        if not obj.reason:
            return 'No reason provided'
        
        return format_html(
            '<pre style="white-space: pre-wrap;">{}</pre>',
            obj.reason
        )
    reason_display.short_description = 'Full Reason'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related(
            'store_product_code__product',
            'store_product_code__store',
            'changed_by'
        )
