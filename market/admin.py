from typing import Any
from django.contrib import admin
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Upper, Substr
from django.db.models.query import QuerySet


from core.admin.abstract_admin import DefaultBaseAdminItems
from django.utils.translation import gettext_lazy as _
from .models import *


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
class StoreProductCodeModelAdmin(DefaultBaseAdminItems):
    list_display = (
        "product",
        "store",
        "code",
    )
    list_filter = ("store",)
    search_fields = ("code", "product__name", "store__name")
    search_help_text = _("Search by code, product name or store name.")


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
