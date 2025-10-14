from django_filters import rest_framework as filters

from core.filters.abstract_filters import ListCharFilter, ListIDFilter
from invoices.models import (
    PurchaseInvoice,
    PurchaseInvoiceItem,
    PurchaseReturnInvoiceItem,
    SaleInvoice,
    SaleInvoiceItem,
    SaleReturnInvoice,
    SaleReturnInvoiceItem,
)


class SaleInvoiceFilter(filters.FilterSet):
    user = ListIDFilter(field_name="user__pk")
    status = ListCharFilter(field_name="status")

    class Meta:
        model = SaleInvoice
        fields = ["user", "status"]


class SaleInvoiceItemFilter(filters.FilterSet):
    invoice = ListIDFilter(field_name="invoice__pk")
    product = ListIDFilter(field_name="product__pk")
    has_remaining_quantity = filters.BooleanFilter(
        field_name="remaining_quantity",
        method="filter_has_remaining_quantity",
    )

    class Meta:
        model = SaleInvoiceItem
        fields = ["invoice", "product", "has_remaining_quantity"]

    def filter_has_remaining_quantity(self, queryset, name, value):
        if value:
            return queryset.filter(remaining_quantity__gt=0)
        elif value is False:
            return queryset.exclude(remaining_quantity__gt=0)

        return queryset


class PurchaseInvoiceFilter(filters.FilterSet):
    user = ListIDFilter(field_name="user__pk")
    status = ListCharFilter(field_name="status")

    class Meta:
        model = PurchaseInvoice
        fields = ["user", "status"]


class PurchaseInvoiceItemFilter(filters.FilterSet):
    invoice = ListIDFilter(field_name="invoice__pk")
    product = ListIDFilter(field_name="product__pk")

    class Meta:
        model = PurchaseInvoiceItem
        fields = ["invoice", "product"]


class PurchaseReturnInvoiceItemFilter(filters.FilterSet):
    invoice = ListIDFilter(field_name="invoice__pk")
    product = ListIDFilter(field_name="purchase_invoice_item__product__pk")

    class Meta:
        model = PurchaseReturnInvoiceItem
        fields = ["invoice", "product"]


class SaleReturnInvoiceFilter(filters.FilterSet):
    user = ListIDFilter(field_name="user__pk")
    status = ListCharFilter(field_name="status")

    class Meta:
        model = SaleReturnInvoice
        fields = ["user", "status"]


class SaleReturnInvoiceItemFilter(filters.FilterSet):
    invoice = ListIDFilter(field_name="invoice__pk")
    product = ListIDFilter(field_name="sale_invoice_item__product__pk")

    class Meta:
        model = SaleReturnInvoiceItem
        fields = ["invoice", "product"]
