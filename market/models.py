from decimal import Decimal
from django.db import models
from accounts.models import Pharmacy, Store
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from market import managers
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


SHAPE_CHOICES = [
    ("افلام", "افلام"),
    ("شراب", "شراب"),
    ("اسبراي", "اسبراي"),
    ("استحلاب", "استحلاب"),
    ("اقراص", "اقراص"),
    ("اقماع", "اقماع"),
    ("اكياس", "اكياس"),
    ("اقراص", "اقراص"),
    ("امبولات", "امبولات"),
    ("برطمان", "برطمان"),
    ("بلسم", "بلسم"),
    ("بودرة", "بودرة"),
    ("جل", "جل"),
    ("حبيبات فوار", "حبيبات فوار"),
    ("زيت", "زيت"),
    ("زيت شعر", "زيت شعر"),
    ("سرنجة معبأه", "سرنجة معبأه"),
    ("سيرم", "سيرم"),
    ("شامبو", "شامبو"),
    ("صابون", "صابون"),
    ("غسول فم", "غسول فم"),
    ("غسول مهبلي", "غسول مهبلي"),
    ("غسول وجه", "غسول وجه"),
    ("فوم", "فوم"),
    ("فيال", "فيال"),
    ("قطرة أذن", "قطرة أذن"),
    ("قطرة للعين", "قطرة للعين"),
    ("قلم معبأ", "قلم معبأ"),
    ("قطعة", "قطعة"),
    ("كبسولات", "كبسولات"),
    ("كريم", "كريم"),
    ("لوشن", "لوشن"),
    ("محلول", "محلول"),
    ("محلول استنشاق", "محلول استنشاق"),
    ("مرهم", "مرهم"),
    ("مرهم للعين", "مرهم للعين"),
    ("مس", "مس"),
    ("معلق", "معلق"),
    ("نقط عين", "نقط عين"),
    ("نقط فم", "نقط فم"),
]

LETTER_CHOICES = [
    ("A", "A"),
    ("B", "B"),
    ("C", "C"),
    ("D", "D"),
    ("E", "E"),
    ("F", "F"),
    ("G", "G"),
    ("H", "H"),
    ("I", "I"),
    ("J", "J"),
    ("K", "K"),
    ("L", "L"),
    ("M", "M"),
    ("N", "N"),
    ("O", "O"),
    ("P", "P"),
    ("Q", "Q"),
    ("R", "R"),
    ("S", "S"),
    ("T", "T"),
    ("U", "U"),
    ("V", "V"),
    ("W", "W"),
    ("X", "X"),
    ("Y", "Y"),
    ("Z", "Z"),
]


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

class CodeChangeLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('deactivate', 'Deactivate'),
        ('reactivate', 'Reactivate'),
    ]
    
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
    UPLOAD_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/store_product_codes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=UPLOAD_STATUS, default='pending')
    total_rows = models.IntegerField(default=0)
    successful_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    results = models.JSONField(default=dict, blank=True)
    error_log = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']

class ProductMatchCache(models.Model):
    search_name = models.CharField(max_length=200, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    confidence_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['search_name']),
            models.Index(fields=['created_at']),
        ]
        unique_together = (('search_name', 'product'),)

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
