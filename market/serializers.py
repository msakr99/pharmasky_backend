from itertools import product
from accounts.serializers import UserReadSerializer
from core.serializers.abstract_serializers import BaseModelSerializer, QueryParameterHyperlinkedIdentityField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.db import transaction
from market.models import Category, Company, PharmacyProductWishList, Product, ProductCode, StoreProductCodeUpload, Store
from market.utils import update_product

get_model = apps.get_model


class CompanyReadSerializer(BaseModelSerializer):
    products_url = QueryParameterHyperlinkedIdentityField(view_name="market:products-list-view", query_param="company")

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "e_name",
            "image",
            "products_url",
        ]


class CategoryReadSerializer(BaseModelSerializer):
    products_url = QueryParameterHyperlinkedIdentityField(
        view_name="market:products-list-view", query_param="category"
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "e_name",
            "image",
            "products_url",
        ]


class ProductReadSerializer(BaseModelSerializer):
    company = CompanyReadSerializer()
    category = CategoryReadSerializer()
    alternative_products_url = serializers.HyperlinkedIdentityField(view_name="market:product-alternatives-list-view")
    instance_products_url = serializers.HyperlinkedIdentityField(view_name="market:product-instances-list-view")
    max_offer_id = serializers.IntegerField(read_only=True)
    max_offer_actual_discount_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    max_offer_actual_offer_price = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    max_offer_remaining_amount = serializers.IntegerField(read_only=True)
    max_offers_url = QueryParameterHyperlinkedIdentityField(
        view_name="offers:max-offers-list-view", query_param="product"
    )
    has_image = serializers.BooleanField(read_only=True)
    total_purchases = serializers.IntegerField(read_only=True)
    total_purchases_returned = serializers.IntegerField(read_only=True)
    total_sold = serializers.IntegerField(read_only=True)
    total_sales_returned = serializers.IntegerField(read_only=True)
    total_in_stock = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "e_name",
            "image",
            "has_image",
            "public_price",
            "company",
            "category",
            "effective_material",
            "letter",
            "shape",
            "alternative_products_url",
            "instance_products_url",
            "needed",
            "fridge",
            "total_purchases",
            "total_purchases_returned",
            "total_sold",
            "total_sales_returned",
            "total_in_stock",
            "max_offers_url",
            "max_offer_id",
            "max_offer_actual_discount_percentage",
            "max_offer_actual_offer_price",
            "max_offer_remaining_amount",
        ]


class ProductCreateUpdateSerilizer(BaseModelSerializer):
    class Meta:
        model = Product
        fields = [
            "name",
            "e_name",
            "image",
            "public_price",
            "company",
            "category",
            "effective_material",
            "shape",
            "needed",
            "is_illegal",
            "fridge",
        ]

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance = update_product(instance, validated_data)
        return instance


class ProductCodeReadSerializer(BaseModelSerializer):
    product = ProductReadSerializer(fields=["id", "name", "e_name", "public_price"])
    user = UserReadSerializer(fields=["id", "name", "e_name"])

    class Meta:
        model = ProductCode
        fields = ["id", "product", "user", "code"]


class ProductCodeCreateUpdateSerializer(BaseModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, required=False)
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_model("accounts", "User").objects.all(), write_only=True, required=False
    )

    class Meta:
        model = ProductCode
        fields = ["id", "product", "user", "code"]

    def validate(self, attrs):
        if not attrs.get("product") or not attrs.get("user"):
            raise ValidationError(_("Product and User are required to create a Product Code."))
        return super().validate(attrs)


class PharmacyProductWishListSerializer(BaseModelSerializer):
    pharmacy = UserReadSerializer(fields=["id", "name", "e_name"], read_only=True)
    pharmacy_id = serializers.HiddenField(default=serializers.CurrentUserDefault(), write_only=True, source="pharmacy")
    product = ProductReadSerializer(fields=["id", "name", "e_name", "public_price"], read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source="product",
        queryset=Product.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = PharmacyProductWishList
        fields = ["id", "pharmacy", "pharmacy_id", "product", "product_id", "created_at"]

    def validate(self, attrs):
        pharmacy = attrs.get("pharmacy")
        product = attrs.get("product")
        queryset = PharmacyProductWishList.objects.filter(pharmacy=pharmacy, product=product)

        instance = self.instance

        if instance is not None:
            queryset = queryset.exclude(id=instance.id)

        if queryset.exists():
            raise ValidationError({"product": _("This product is already in the pharmacy's wishlist.")})

        return super().validate(attrs)


# Store Product Code Upload Serializers
class StoreProductCodeUploadSerializer(BaseModelSerializer):
    """Serializer for store product code uploads"""
    
    store_name = serializers.CharField(source='store.name', read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    success_rate = serializers.ReadOnlyField()
    file_size_display = serializers.SerializerMethodField()
    file_name = serializers.CharField(read_only=True)
    results_summary = serializers.SerializerMethodField()
    flexibility_used = serializers.SerializerMethodField()
    
    class Meta:
        model = StoreProductCodeUpload
        fields = [
            'id',
            'store',
            'store_name',
            'file',
            'file_name',
            'file_size',
            'file_size_display',
            'uploaded_by',
            'uploaded_by_username',
            'uploaded_at',
            'processed_at',
            'status',
            'total_rows',
            'successful_rows',
            'failed_rows',
            'success_rate',
            'results',
            'results_summary',
            'flexibility_used',
            'error_log'
        ]
        read_only_fields = [
            'id',
            'file_name',
            'file_size',
            'uploaded_by',
            'uploaded_at',
            'processed_at',
            'status',
            'total_rows',
            'successful_rows',
            'failed_rows',
            'results',
            'error_log'
        ]
    
    def get_file_size_display(self, obj):
        """Return human readable file size"""
        if not obj.file_size:
            return None
        size_mb = obj.file_size / (1024 * 1024)
        return f"{size_mb:.2f} MB"
    
    def get_results_summary(self, obj):
        """Return summary of processing results"""
        if not obj.results:
            return {}
        
        summary = {
            'total_rows': len(obj.results),
            'successful': len([r for r in obj.results if r.get('status') == 'success']),
            'failed': len([r for r in obj.results if r.get('status') == 'failed']),
            'flexible_matches': len([r for r in obj.results if r.get('flexibility_used', False)]),
            'average_match_score': 0,
            'price_differences': []
        }
        
        # Calculate average match score for successful matches
        successful_results = [r for r in obj.results if r.get('status') == 'success']
        if successful_results:
            scores = [r.get('match_score', 1.0) for r in successful_results]
            summary['average_match_score'] = round(sum(scores) / len(scores), 2)
            
            # Collect price differences
            price_diffs = [r.get('price_difference', 0) for r in successful_results if r.get('price_difference', 0) > 0]
            summary['price_differences'] = price_diffs
        
        return summary
    
    def get_flexibility_used(self, obj):
        """Check if flexibility was used in any matches"""
        if not obj.results:
            return False
        
        return any(r.get('flexibility_used', False) for r in obj.results)
    
    def create(self, validated_data):
        """Create upload record and start processing"""
        # Set uploaded_by from request user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['uploaded_by'] = request.user
        
        # Create the upload record
        upload = super().create(validated_data)
        
        # Start processing the file asynchronously
        from .tasks import process_upload_file
        process_upload_file.delay(upload.id)
        
        return upload


class StoreProductCodeUploadCreateSerializer(serializers.Serializer):
    """Serializer for creating store product code uploads"""
    
    store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())
    file = serializers.FileField()
    
    def validate_file(self, value):
        """Validate uploaded file"""
        from .validators import StoreProductCodeFileValidator
        
        validator = StoreProductCodeFileValidator()
        try:
            validator(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        return value
    
    def create(self, validated_data):
        """Create upload record"""
        request = self.context.get('request')
        
        upload = StoreProductCodeUpload.objects.create(
            store=validated_data['store'],
            file=validated_data['file'],
            uploaded_by=request.user if request else None,
            status='pending'
        )
        
        # Start processing the file asynchronously
        from .tasks import process_upload_file
        process_upload_file.delay(upload.id)
        
        return upload


class BulkStoreProductCodeUploadSerializer(serializers.Serializer):
    """Serializer for bulk uploading store product codes"""
    
    store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
        max_length=10
    )
    conflict_strategy = serializers.ChoiceField(
        choices=[
            ('update', 'تحديث الأكواد الموجودة'),
            ('skip', 'تجاهل الأكواد الموجودة'),
            ('create_new', 'إنشاء أكواد جديدة فقط')
        ],
        default='update'
    )
    
    def validate_files(self, value):
        """Validate uploaded files"""
        from .validators import StoreProductCodeFileValidator
        
        if len(value) > 10:
            raise serializers.ValidationError("لا يمكن رفع أكثر من 10 ملفات في نفس الوقت")
        
        validator = StoreProductCodeFileValidator()
        for file in value:
            try:
                validator(file)
            except ValidationError as e:
                raise serializers.ValidationError(f'خطأ في الملف {file.name}: {str(e)}')
        
        return value
    
    def create(self, validated_data):
        """Create multiple upload records"""
        request = self.context.get('request')
        store = validated_data['store']
        files = validated_data['files']
        conflict_strategy = validated_data['conflict_strategy']
        
        uploads = []
        for file in files:
            upload = StoreProductCodeUpload.objects.create(
                store=store,
                file=file,
                uploaded_by=request.user if request else None,
                status='pending'
            )
            uploads.append(upload)
            
            # Start processing the file asynchronously
            from .tasks import process_upload_file
            process_upload_file.delay(upload.id)
        
        return uploads


class StoreProductCodeUploadStatusSerializer(serializers.Serializer):
    """Serializer for filtering upload status"""
    
    status = serializers.ChoiceField(
        choices=[
            ('', 'جميع الحالات'),
            ('pending', 'في الانتظار'),
            ('processing', 'قيد المعالجة'),
            ('completed', 'مكتمل'),
            ('failed', 'فاشل')
        ],
        required=False
    )
    store = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(),
        required=False
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)


class UploadProgressSerializer(serializers.Serializer):
    """Serializer for upload progress information"""
    
    status = serializers.CharField()
    progress = serializers.IntegerField()
    total_rows = serializers.IntegerField()
    successful_rows = serializers.IntegerField()
    failed_rows = serializers.IntegerField()
    success_rate = serializers.FloatField()
    error_log = serializers.CharField(allow_blank=True)


class StoreSerializer(BaseModelSerializer):
    """Simple serializer for Store model"""
    
    class Meta:
        model = Store
        fields = ['id', 'name', 'e_name']


class SimpleStoreProductCodeUploadSerializer(serializers.Serializer):
    """Serializer for simple store product code upload with product_id, store_id, code"""
    
    store_id = serializers.IntegerField()
    file = serializers.FileField()
    
    def validate_store_id(self, value):
        """Validate store exists"""
        from accounts.models import Store
        try:
            Store.objects.get(id=value)
        except Store.DoesNotExist:
            raise serializers.ValidationError("Store not found")
        return value
    
    def validate_file(self, value):
        """Validate uploaded file"""
        # Check file extension
        if not value.name.endswith(('.xlsx', '.xls')):
            raise serializers.ValidationError("Only Excel files (.xlsx, .xls) are allowed")
        
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        return value
    
    def create(self, validated_data):
        """Create upload record and start processing"""
        request = self.context.get('request')
        
        # Create upload record
        upload = StoreProductCodeUpload.objects.create(
            store_id=validated_data['store_id'],
            file=validated_data['file'],
            uploaded_by=request.user if request else None,
            status='pending'
        )
        
        # Process the file synchronously (without Celery)
        try:
            from .tasks import process_simple_upload_file_sync
            result = process_simple_upload_file_sync(upload.id)
            
            # Update upload with results
            upload.refresh_from_db()
            
        except Exception as e:
            # If processing fails, mark as failed
            upload.status = 'failed'
            upload.error_log = str(e)
            upload.save()
        
        return upload
