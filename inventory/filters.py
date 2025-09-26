from django_filters import rest_framework as filters

from core.filters.abstract_filters import ListIDFilter
from inventory.models import Inventory, InventoryItem


class InventoryFilter(filters.FilterSet):
    ex_id = ListIDFilter(field_name="id", exclude=True)

    class Meta:
        model = Inventory
        fields = ["ex_id"]


class InventoryItemFilter(filters.FilterSet):
    inventory = ListIDFilter(field_name="inventory__pk")
    product = ListIDFilter(field_name="product__pk")

    class Meta:
        model = InventoryItem
        fields = ["inventory", "product"]
