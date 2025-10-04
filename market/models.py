from django.db import models
from accounts.models import Pharmacy, Store
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from market import managers
from market.choices import SHAPE_CHOICES, LETTER_CHOICES, UPLOAD_STATUS_CHOICES, ACTION_CHOICES
from market.validators import StoreProductCodeFileValidator, ProductMatchCacheValidator, store_product_code_file_validator


class Company(models.Model):
    name = models.CharField(max_length=50)
    e_name = models.CharField(max_length=50, blank=True, default="")
    image = models.ImageField(blank=True, null=True, default="")
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = _("Companies")

    def __str__(self):
        return f"{self.name}"


class Category(models.Model):
    name = models.CharField(max_length=50)
    e_name = models.CharField(max_length=50, blank=True, null=True, default="")
    image = models.ImageField(blank=True, null=True, default="")

    class Meta:
        verbose_name_plural = _("Categories")

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    def __str__(self):
        return f"{self.name}"

    class Meta:
        indexes = [models.Index(fields=["name", "e_name"], name="market_product_name_idx")]

    name = models.CharField(max_length=200)
    e_name = models.CharField(max_length=200)
    image = models.ImageField(blank=True, null=True, default="")
    public_price = models.DecimalField(max_digits=8, decimal_places=2)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    effective_material = models.CharField(max_length=300, default="المادة الفعالة")
    letter = models.CharField(max_length=20, default="")
    shape = models.CharField(max_length=20, choices=SHAPE_CHOICES)
    needed = models.BooleanField(default=False)
    alternatives = models.ManyToManyField("self", blank=True)
    instances = models.ManyToManyField("self", blank=True)
    is_illegal = models.BooleanField(default=False)
    fridge = models.BooleanField(default=False)

    objects = managers.ProductManager.from_queryset(managers.ProductQuerySet)()


class ProductCode(models.Model):
    def __str__(self) -> str:
        return f"{self.code} - {self.product}"

    class Meta:
        indexes = [
            models.Index(fields=["product", "user"]),
            models.Index(fields=["user", "code"]),
            models.Index(fields=["product"]),
            models.Index(fields=["user"]),
        ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_codes", related_query_name="product_codes"
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="product_codes",
        related_query_name="product_codes",
    )
    code = models.IntegerField()


class StoreProductCode(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, 
        related_name="store_product_codes", 
        related_query_name="store_product_codes"
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, 
        related_name="store_product_codes", 
        related_query_name="store_product_codes"
    )
    code = models.IntegerField()
    
    # حقول جديدة للتتبع
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    version = models.IntegerField(default=1)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['product', 'store']),
            models.Index(fields=['product']),
            models.Index(fields=['store']),
            models.Index(fields=['code', 'store']),
            models.Index(fields=['is_active']),
        ]
        unique_together = (('product', 'store'),)

    def __str__(self) -> str:
        return f"{self.code} - {self.product} - {self.store}"

    def clean(self):
        """Add model-level validation"""
        super().clean()
        
        # Validate that code is positive
        if self.code and self.code <= 0:
            raise ValidationError({'code': 'Code must be a positive number'})
        
        # Validate that product and store exist
        if not self.product_id:
            raise ValidationError({'product': 'Product is required'})
        if not self.store_id:
            raise ValidationError({'store': 'Store is required'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class CodeChangeLog(models.Model):
    
    store_product_code = models.ForeignKey(StoreProductCode, on_delete=models.CASCADE)
    old_code = models.IntegerField(null=True, blank=True)
    new_code = models.IntegerField(null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    changed_by = models.ForeignKey('accounts.User', null=True, on_delete=models.SET_NULL)
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-changed_at']


class StoreProductCodeUpload(models.Model):
    store = models.ForeignKey(
        Store, 
        on_delete=models.CASCADE,
        related_name='product_code_uploads',
        related_query_name='product_code_uploads'
    )
    file = models.FileField(
        upload_to='uploads/store_product_codes/',
        validators=[store_product_code_file_validator]
    )
    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_product_codes'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=UPLOAD_STATUS_CHOICES, default='pending')
    total_rows = models.IntegerField(default=0)
    successful_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    results = models.JSONField(default=dict, blank=True)
    error_log = models.TextField(blank=True)
    file_size = models.BigIntegerField(null=True, blank=True, help_text="File size in bytes")
    file_name = models.CharField(max_length=255, blank=True, help_text="Original file name")
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['uploaded_at']),
            models.Index(fields=['status']),
        ]
        verbose_name = "Store Product Code Upload"
        verbose_name_plural = "Store Product Code Uploads"
    
    def __str__(self):
        return f"{self.store.name} - {self.file_name} - {self.status}"
    
    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_rows == 0:
            return 0
        return round((self.successful_rows / self.total_rows) * 100, 2)
    
    def clean(self):
        """Validate the model instance"""
        super().clean()
        
        # Validate file if it exists and has been uploaded
        if self.file and hasattr(self.file, 'file') and self.file.file:
            try:
                validator = StoreProductCodeFileValidator()
                validator(self.file)
            except Exception as e:
                # Log the error but don't raise it during admin form validation
                # The file field validators will handle the validation
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"File validation error in clean(): {e}")
                # Only raise validation errors for critical issues
                if "file_too_large" in str(e) or "invalid_extension" in str(e):
                    raise
    
    def save(self, *args, **kwargs):
        # Auto-calculate file size and name if not provided
        if self.file and not self.file_size:
            try:
                self.file_size = self.file.size
            except (OSError, ValueError):
                pass
        
        if self.file and not self.file_name:
            self.file_name = self.file.name
        
        # Run validation
        self.clean()
        
        super().save(*args, **kwargs)


class ProductMatchCache(models.Model):
    search_name = models.CharField(max_length=200, db_index=True)
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='match_cache_entries',
        related_query_name='match_cache_entries'
    )
    confidence_score = models.FloatField(validators=[ProductMatchCacheValidator.validate_confidence_score])
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True, help_text="Last time this cache entry was used")
    access_count = models.PositiveIntegerField(default=0, help_text="Number of times this cache was accessed")
    
    class Meta:
        indexes = [
            models.Index(fields=['search_name']),
            models.Index(fields=['created_at']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['last_accessed']),
        ]
        unique_together = (('search_name', 'product'),)
        verbose_name = "Product Match Cache"
        verbose_name_plural = "Product Match Caches"
        ordering = ['-confidence_score', '-created_at']
    
    def __str__(self):
        return f"{self.search_name} -> {self.product.name} ({self.confidence_score:.2f})"
    
    def increment_access(self):
        """Increment access count and update last_accessed"""
        self.access_count += 1
        self.save(update_fields=['access_count', 'last_accessed'])


class PharmacyProductWishList(models.Model):
    pharmacy = models.ForeignKey(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name="product_wishlist",
        related_query_name="product_wishlist",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_wishlist",
        related_query_name="product_wishlist",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["pharmacy"]), models.Index(fields=["product"])]
        unique_together = (("product", "pharmacy"),)
