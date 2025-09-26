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

    class Meta:
        model = Offer
        fields = ["id", "user", "product", "needed"]
