from django.contrib import admin
from core.admin.abstract_admin import DefaultBaseAdminItems
from offers.models import Offer


@admin.register(Offer)
class OfferModelAdmin(DefaultBaseAdminItems):
    list_display = [
        "user",
        "product",
        "product_code",
        "available_amount",
        "remaining_amount",
        "min_purchase",
        "purchase_discount_percentage",
        "purchase_price",
        "selling_discount_percentage",
        "selling_price",
        "is_max",
        "is_wholesale",
        "wholesale_min_quantity",
        "is_max_wholesale",
        "created_at",
    ]
    search_fields = [
        "product__name",
        "product__e_name",
        "product_code__code",
        "user__username",
        "user__name",
        "operating_number",
    ]
    date_hierarchy = "created_at"
    list_filter = ["is_max", "is_wholesale", "is_max_wholesale"]
    list_select_related = ["product", "product_code", "user"]
    autocomplete_fields = ["product", "product_code", "user"]
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('user', 'product', 'product_code', 'operating_number')
        }),
        ('الكميات', {
            'fields': ('available_amount', 'remaining_amount', 'max_amount_per_invoice', 'product_expiry_date')
        }),
        ('الأسعار والخصومات', {
            'fields': (
                'min_purchase',
                'purchase_discount_percentage', 
                'purchase_price',
                'selling_discount_percentage', 
                'selling_price',
                'is_max'
            )
        }),
        ('إعدادات الجملة', {
            'fields': ('is_wholesale', 'wholesale_min_quantity', 'wholesale_increment', 'is_max_wholesale'),
            'classes': ('collapse',),
        }),
    )
