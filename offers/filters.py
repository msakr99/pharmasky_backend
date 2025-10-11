from django_filters import rest_framework as filters
from django.db import models
from core.filters.abstract_filters import (
    ListBooleanFilter,
    ListCharFilter,
    ListIDFilter,
)
from offers.models import Offer


class OfferFilter(filters.FilterSet):
    id = ListIDFilter(field_name="pk")
    user = ListIDFilter(field_name="user__pk")
    product = ListIDFilter(field_name="product__pk")
    needed = ListBooleanFilter(field_name="product__needed")
    is_wholesale = filters.BooleanFilter(field_name="is_wholesale")
    is_max_wholesale = filters.BooleanFilter(field_name="is_max_wholesale")
    wholesale_min_quantity = filters.NumberFilter(field_name="wholesale_min_quantity")
    wholesale_min_quantity__gte = filters.NumberFilter(field_name="wholesale_min_quantity", lookup_expr='gte')
    wholesale_min_quantity__lte = filters.NumberFilter(field_name="wholesale_min_quantity", lookup_expr='lte')

    class Meta:
        model = Offer
        fields = [
            "id", 
            "user", 
            "product", 
            "needed", 
            "is_wholesale", 
            "is_max_wholesale",
            "wholesale_min_quantity",
        ]
