from django.contrib import admin
from core.admin.abstract_admin import DefaultBaseAdminItems
from invoices.models import PurchaseInvoice, PurchaseInvoiceItem, SaleInvoice, SaleInvoiceItem


@admin.register(PurchaseInvoice)
class PurchaseInvoiceModelAdmin(DefaultBaseAdminItems):
    list_display = (
        "user",
        "supplier_invoice_number",
        "items_count",
        "total_quantity",
        "total_price",
        "status",
        "created_at",
    )
    search_fields = ("user__username",)
    date_hierarchy = "created_at"
    list_filter = ("status",)
    autocomplete_fields = ("user",)
    list_select_related = ("user",)


@admin.register(PurchaseInvoiceItem)
class PurchaseInvoiceItemModelAdmin(DefaultBaseAdminItems):
    list_display = (
        "invoice",
        "product",
        "product_expiry_date",
        "operating_number",
        "quantity",
        "purchase_discount_percentage",
        "purchase_price",
        "sub_total",
        "status",
    )
    search_fields = ("product__name",)
    date_hierarchy = "product_expiry_date"
    list_filter = ("invoice", "status")
    autocomplete_fields = ("invoice", "product")
    list_select_related = ("invoice", "product")


@admin.register(SaleInvoice)
class SaleInvoiceModelAdmin(DefaultBaseAdminItems):
    list_display = (
        "user",
        "items_count",
        "total_quantity",
        "total_price",
        "status",
        "seller",
        "created_at",
    )
    search_fields = ("user__username", "user__name", "seller__username", "seller__name")
    date_hierarchy = "created_at"
    list_filter = ("status",)
    autocomplete_fields = ("user", "seller")
    list_select_related = ("user", "seller")


@admin.register(SaleInvoiceItem)
class SaleInvoiceItemModelAdmin(DefaultBaseAdminItems):
    list_display = (
        "invoice",
        "product",
        "product_expiry_date",
        "operating_number",
        "quantity",
        "selling_discount_percentage",
        "selling_price",
        "sub_total",
        "status",
    )
    search_fields = (
        "invoice__user__name",
        "invoice__user__username",
        "product__name",
    )
    date_hierarchy = "product_expiry_date"
    list_filter = ("invoice", "status")
    autocomplete_fields = ("invoice", "product")
    list_select_related = ("invoice", "product")
