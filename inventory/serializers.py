from decimal import Decimal
from rest_framework import serializers
from core.serializers.abstract_serializers import BaseModelSerializer, QueryParameterHyperlinkedIdentityField
from inventory.models import Inventory, InventoryItem
from inventory.choices import InventoryTypeChoice
from django.apps import apps
from django.db import transaction

from inventory.utils import create_inventory_item, transfer_inventory_item, update_inventory_item
from market.serializers import ProductReadSerializer

get_model = apps.get_model


class InventoryReadSerializer(BaseModelSerializer):
    type_label = serializers.CharField(source="get_type_display", read_only=True)
    items_url = QueryParameterHyperlinkedIdentityField(
        view_name="inventory:inventory-items-list-view", query_param="inventory"
    )

    class Meta:
        model = Inventory
        fields = [
            "id",
            "name",
            "type",
            "type_label",
            "total_items",
            "total_quantity",
            "total_purchase_price",
            "total_selling_price",
            "items_url",
        ]


class InventoryCreateSerializer(BaseModelSerializer):
    type = serializers.ChoiceField(choices=InventoryTypeChoice.choices)

    class Meta:
        model = Inventory
        fields = ["name", "type"]

    def validate(self, attrs):
        attrs["total_items"] = 0
        attrs["total_quantity"] = 0
        attrs["total_purchase_price"] = Decimal("0.00")
        attrs["total_selling_price"] = Decimal("0.00")
        return super().validate(attrs)

    def to_representation(self, instance):
        return InventoryReadSerializer(instance, context=self.context).data


class InventoryUpdateSerializer(BaseModelSerializer):
    type = serializers.ChoiceField(choices=InventoryTypeChoice.choices)
    type_label = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Inventory
        fields = ["name", "type", "type_label"]


class InventoryItemReadSerializer(BaseModelSerializer):
    inventory = InventoryReadSerializer()
    product = ProductReadSerializer(fields=["id", "name", "public_price"])
    
    # معلومات المورد ورقم الفاتورة وتاريخ الشراء
    supplier_name = serializers.SerializerMethodField()
    supplier_invoice_number = serializers.SerializerMethodField()
    purchase_date = serializers.SerializerMethodField()

    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "inventory",
            "product",
            "product_expiry_date",
            "operating_number",
            "purchase_discount_percentage",
            "purchase_price",
            "selling_discount_percentage",
            "selling_price",
            "quantity",
            "remaining_quantity",
            "purchase_sub_total",
            "selling_sub_total",
            # الحقول الجديدة
            "supplier_name",
            "supplier_invoice_number",
            "purchase_date",
        ]
    
    def get_supplier_name(self, obj):
        """الحصول على اسم المورد من فاتورة الشراء"""
        if obj.purchase_invoice_item and obj.purchase_invoice_item.invoice:
            return obj.purchase_invoice_item.invoice.user.name
        return None
    
    def get_supplier_invoice_number(self, obj):
        """الحصول على رقم فاتورة المورد"""
        if obj.purchase_invoice_item and obj.purchase_invoice_item.invoice:
            return obj.purchase_invoice_item.invoice.supplier_invoice_number
        return None
    
    def get_purchase_date(self, obj):
        """الحصول على تاريخ الشراء"""
        if obj.purchase_invoice_item and obj.purchase_invoice_item.invoice:
            return obj.purchase_invoice_item.invoice.created_at
        return None


class InventoryItemCreateSerializer(BaseModelSerializer):
    class Meta:
        model = InventoryItem
        fields = [
            "inventory",
            "product",
            "product_expiry_date",
            "operating_number",
            "purchase_discount_percentage",
            "selling_discount_percentage",
            "quantity",
            "remaining_quantity",
        ]

    def validate(self, attrs):
        product = attrs.get("product")
        purchase_discount_percentage = attrs.get("purchase_discount_percentage")
        selling_discount_percentage = attrs.get("selling_discount_percentage")
        remaining_quantity = attrs.get("remaining_quantity")

        purchase_price = Decimal(
            product.public_price - (product.public_price * purchase_discount_percentage / 100)
        ).quantize(Decimal("0.00"))
        selling_price = Decimal(
            product.public_price - (product.public_price * selling_discount_percentage / 100)
        ).quantize(Decimal("0.00"))

        attrs["purchase_price"] = purchase_price
        attrs["selling_price"] = selling_price
        attrs["purchase_sub_total"] = Decimal(purchase_price * remaining_quantity).quantize(Decimal("0.00"))
        attrs["selling_sub_total"] = Decimal(selling_price * remaining_quantity).quantize(Decimal("0.00"))

        return super().validate(attrs)

    def create(self, validated_data):
        with transaction.atomic():
            instance = create_inventory_item(validated_data, raise_exception=True)

        return instance

    def to_representation(self, instance):
        return InventoryItemReadSerializer(instance, context=self.context).data


class InventoryItemUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = InventoryItem
        fields = [
            "product_expiry_date",
            "operating_number",
            "purchase_discount_percentage",
            "selling_discount_percentage",
            "quantity",
            "remaining_quantity",
        ]

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance = update_inventory_item(instance, validated_data)

        return instance

    def to_representation(self, instance):
        return InventoryItemReadSerializer(instance, context=self.context).data


class InventoryItemTransferSerializer(BaseModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ["inventory"]

    def update(self, instance, validated_data):
        new_inventory = validated_data.get("inventory")
        with transaction.atomic():
            instance = transfer_inventory_item(instance, new_inventory)
        return instance

    def to_representation(self, instance):
        return InventoryItemReadSerializer(instance, context=self.context).data
