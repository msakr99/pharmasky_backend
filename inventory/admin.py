from django.contrib import admin
from core.admin.abstract_admin import DefaultBaseAdminItems
from inventory.models import Inventory, InventoryItem


@admin.register(Inventory)
class InventoryModelAdmin(DefaultBaseAdminItems):
    list_display = ("name", "type", "total_items", "total_quantity", "total_purchase_price", "total_selling_price")
    search_fields = ("name",)
    list_filter = ("type",)


@admin.register(InventoryItem)
class InventoryItemModelAdmin(DefaultBaseAdminItems):
    list_display = (
        "inventory",
        "product",
        "product_expiry_date",
        "operating_number",
        "quantity",
        "remaining_quantity",
        "purchase_discount_percentage",
        "purchase_price",
        "purchase_sub_total",
        "selling_discount_percentage",
        "selling_price",
        "selling_sub_total",
    )
    search_fields = ("product__name",)
    date_hierarchy = "product_expiry_date"
    list_filter = ("inventory", "inventory__type")
    # autocomplete_fields = ("inventory", "product", "purchase_invoice_item")
    list_select_related = ("inventory", "product")
