from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveAPIView

from accounts.permissions import SalesRoleAuthentication, DataEntryRoleAuthentication, ManagerRoleAuthentication
from inventory.filters import InventoryFilter, InventoryItemFilter
from inventory.models import Inventory, InventoryItem
from inventory.serializers import (
    InventoryCreateSerializer,
    InventoryItemCreateSerializer,
    InventoryItemReadSerializer,
    InventoryItemTransferSerializer,
    InventoryItemUpdateSerializer,
    InventoryReadSerializer,
    InventoryUpdateSerializer,
)
from inventory.utils import delete_inventory_item
from django.db import transaction


class InventoryListAPIView(ListAPIView):
    permission_classes = [SalesRoleAuthentication | DataEntryRoleAuthentication | ManagerRoleAuthentication]
    serializer_class = InventoryReadSerializer
    filterset_class = InventoryFilter
    search_fields = ["^name"]
    ordering_fields = ["name", "type"]

    def get_queryset(self):
        queryset = Inventory.objects.all()
        return queryset


class InventoryCreateAPIView(CreateAPIView):
    permission_classes = [ManagerRoleAuthentication]
    queryset = Inventory.objects.all()
    serializer_class = InventoryCreateSerializer


class InventoryRetrieveAPIView(RetrieveAPIView):
    permission_classes = [SalesRoleAuthentication | DataEntryRoleAuthentication | ManagerRoleAuthentication]
    serializer_class = InventoryReadSerializer

    def get_queryset(self):
        queryset = Inventory.objects.all()
        return queryset


class InventoryUpdateAPIView(UpdateAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = InventoryUpdateSerializer

    def get_queryset(self):
        queryset = Inventory.objects.all()
        return queryset


class InventoryItemListAPIView(ListAPIView):
    permission_classes = [SalesRoleAuthentication | DataEntryRoleAuthentication | ManagerRoleAuthentication]
    serializer_class = InventoryItemReadSerializer
    filterset_class = InventoryItemFilter
    search_fields = ["^product__name"]
    ordering_fields = (
        "product__name",
        "product__public_price",
        "product_expiry_date",
        "operating_number",
        "purchase_discount_percentage",
        "purchase_price",
        "selling_discount_percentage",
        "selling_price",
        "quantity",
        "remaining_quantity",
    )

    def get_queryset(self):
        queryset = InventoryItem.objects.select_related("inventory", "product", "purchase_invoice_item").all()
        return queryset


class InventoryItemCreateAPIView(CreateAPIView):
    permission_classes = [ManagerRoleAuthentication]
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemCreateSerializer


class InventoryItemRetrieveAPIView(RetrieveAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = InventoryItemReadSerializer

    def get_queryset(self):
        queryset = InventoryItem.objects.all()
        return queryset


class InventoryItemUpdateAPIView(UpdateAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = InventoryItemUpdateSerializer

    def get_queryset(self):
        queryset = InventoryItem.objects.all()
        return queryset


class InventoryItemTransferAPIView(UpdateAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = InventoryItemTransferSerializer

    def get_queryset(self):
        queryset = InventoryItem.objects.all()
        return queryset


class InventoryItemDestroyAPIView(DestroyAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = InventoryItemReadSerializer

    def get_queryset(self):
        queryset = InventoryItem.objects.all()
        return queryset

    def perform_destroy(self, instance):
        with transaction.atomic():
            delete_inventory_item(instance)
