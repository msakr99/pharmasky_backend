from django.contrib import admin

from shop.models import Cart, CartItem


@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "items_count", "total_quantity", "total_price")
    search_fields = ("user__username", "user__name")


@admin.register(CartItem)
class CartItemModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cart",
        "offer",
        "product",
        "quantity",
        "discount_percentage",
        "price",
        "sub_total",
        "sold_out",
        "created_at",
    )
    list_select_related = ("cart", "offer", "product")
    search_fields = ("cart__user__username", "cart__user__name", "product__name")
    list_filter = ("sold_out",)
