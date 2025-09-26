from django_filters import rest_framework as filters
from django.db import models
from core.filters.abstract_filters import (
    ListBooleanFilter,
    ListCharFilter,
    ListIDFilter,
)
from market.models import Product, ProductCode, StoreProductCode


class ProductFilter(filters.FilterSet):
    id = ListIDFilter(field_name="id")
    letter = ListCharFilter(field_name="letter")
    shape = ListCharFilter(field_name="shape")
    company = ListIDFilter(field_name="company__id")
    category = ListIDFilter(field_name="category__id")

    class Meta:
        model = Product
        fields = ["id", "company", "category", "letter", "shape"]


class StoreProductCodeFilter(filters.FilterSet):
    id = ListIDFilter(field_name="id")
    ex_id = ListCharFilter(field_name="id", exclude=True)
    store = ListIDFilter(field_name="store__pk")
    product = ListIDFilter(field_name="product__pk")

    class Meta:
        model = StoreProductCode
        fields = [
            "id",
            "ex_id",
            "store",
            "product",
        ]


class ProductCodeFilter(filters.FilterSet):
    id = ListIDFilter(field_name="id")
    user = ListIDFilter(field_name="user__pk")
    product = ListIDFilter(field_name="product__pk")

    class Meta:
        model = ProductCode
        fields = ["id", "user", "product"]
