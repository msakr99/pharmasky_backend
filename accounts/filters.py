from django_filters import rest_framework as filters
from accounts.choices import Role
from core.filters.abstract_filters import ListBooleanFilter, ListCharFilter, ListIDFilter
from django.contrib.auth import get_user_model
from django.db import models


class SimpleUserFilter(filters.FilterSet):
    role = filters.ChoiceFilter(choices=Role.choices, method="filter_by_role")

    class Meta:
        model = get_user_model()
        fields = ["role"]

    def filter_by_role(self, queryset, name, value):
        if value:
            return queryset.filter(models.Q(role=value) | models.Q(is_superuser=True))
        return queryset
