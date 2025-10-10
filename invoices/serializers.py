from decimal import Decimal
from itertools import product
from rest_framework import serializers
from accounts.serializers import UserReadSerializer, UserWithProfileReadSerializer
from core.serializers.abstract_serializers import (
    BaseModelSerializer,
    BaseSerializer,
    QueryParameterHyperlinkedIdentityField,
)
from invoices.choices import (
    PurchaseInvoiceItemStatusChoice,
    PurchaseInvoiceStatusChoice,
    PurchaseReturnInvoiceStatusChoice,
    SaleInvoiceItemStatusChoice,
    SaleInvoiceStatusChoice,
    SaleReturnInvoiceStatusChoice,
)
from invoices.models import (
    PurchaseInvoice,
    PurchaseInvoiceDeletedItem,
    PurchaseInvoiceItem,
    PurchaseReturnInvoice,
    PurchaseReturnInvoiceItem,
    SaleInvoice,
    SaleInvoiceDeletedItem,
    SaleInvoiceItem,
    SaleReturnInvoice,
    SaleReturnInvoiceItem,
)
from invoices.utils import (
    close_purchase_invoice,
    close_purchase_return_invoice,
    close_sale_invoice,
    close_sale_return_invoice,
    create_purchase_invoice,
    create_purchase_invoice_item,
    create_purchase_return_invoice,
    create_purchase_return_invoice_item,
    create_sale_invoice,
    create_sale_invoice_item,
    create_sale_return_invoice,
    create_sale_return_invoice_item,
    get_allowed_status_changes,
    lock_purchase_invoice,
    open_purchase_invoice,
    open_sale_invoice,
    unlock_purchase_invoice,
    update_purchase_invoice_item_state,
    update_purchase_return_invoice_item,
    update_sale_invoice_item,
    update_sale_invoice_item_state,
    update_sale_return_invoice_item,
)
from market.serializers import ProductReadSerializer
from django.apps import apps
from django.db import transaction, models
from django.conf import settings
from django.contrib.auth import get_user_model
from offers.utils import deconstuct_offer, delete_offer

get_model = apps.get_model


class PurchaseInvoiceReadSerializer(BaseModelSerializer):
    class PurchaseInvoiceItemSubReadSerializer(BaseModelSerializer):
        class SaleInvoiceItemSubReadSerializer(BaseModelSerializer):
            class Meta:
                model = SaleInvoiceItem
                fields = ["id", "invoice"]

        product = ProductReadSerializer()
        status_label = serializers.CharField(source="get_status_display", read_only=True)
        sale_invoice_item = SaleInvoiceItemSubReadSerializer()

        class Meta:
            model = PurchaseInvoiceItem
            fields = [
                "id",
                "offer",
                "product",
                "product_expiry_date",
                "operating_number",
                "purchase_discount_percentage",
                "purchase_price",
                "selling_discount_percentage",
                "selling_price",
                "quantity",
                "remaining_quantity",
                "sub_total",
                "status",
                "status_label",
                "sale_invoice_item",
            ]

    class PurchaseInvoiceDeletedItemSubReadSerializer(BaseModelSerializer):
        class SaleInvoiceItemSubReadSerializer(BaseModelSerializer):
            class Meta:
                model = SaleInvoiceItem
                fields = ["id", "invoice"]

        product = ProductReadSerializer()
        status_label = serializers.CharField(source="get_status_display", read_only=True)
        sale_invoice_item = SaleInvoiceItemSubReadSerializer()

        class Meta:
            model = PurchaseInvoiceDeletedItem
            fields = [
                "id",
                "product",
                "product_expiry_date",
                "operating_number",
                "purchase_discount_percentage",
                "purchase_price",
                "selling_discount_percentage",
                "selling_price",
                "quantity",
                "remaining_quantity",
                "sub_total",
                "status",
                "status_label",
                "timestamp",
                "sale_invoice_item",
            ]

    user = UserReadSerializer()
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    items = PurchaseInvoiceItemSubReadSerializer(many=True)
    deleted_items = PurchaseInvoiceDeletedItemSubReadSerializer(many=True)
    items_url = QueryParameterHyperlinkedIdentityField(
        view_name="invoices:purchase-invoice-items-list-view", query_param="invoice"
    )
    average_purchase_discount_percentage = serializers.SerializerMethodField()
    total_public_price = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseInvoice
        fields = [
            "id",
            "user",
            "supplier_invoice_number",
            "items_count",
            "total_quantity",
            "total_price",
            "total_public_price",
            "average_purchase_discount_percentage",
            "status",
            "status_label",
            "created_at",
            "items",
            "deleted_items",
            "items_url",
        ]

    def get_total_public_price(self, instance):
        """
        Calculate the total public price (before discount) for all items in the invoice.
        Formula: Sum(quantity × public_price)
        """
        from decimal import Decimal
        
        total = Decimal("0.00")
        for item in instance.items.select_related("product"):
            quantity_price = item.quantity * item.product.public_price
            total += quantity_price
        
        return total.quantize(Decimal("0.00"))

    def get_average_purchase_discount_percentage(self, instance):
        """
        Calculate the weighted average purchase discount percentage for the invoice.
        Formula: (Sum(quantity × purchase_discount_percentage × public_price) / Sum(quantity × public_price)) × 100
        """
        from decimal import Decimal
        
        total_public_price = Decimal("0.00")
        total_discount = Decimal("0.00")

        for item in instance.items.select_related("product"):
            quantity_price = item.quantity * item.product.public_price
            quantity_discount = quantity_price * (item.purchase_discount_percentage / 100)

            total_public_price += quantity_price
            total_discount += quantity_discount

        if total_public_price == 0:
            return Decimal("0.00")

        average_discount = (total_discount / total_public_price) * 100
        return Decimal(average_discount).quantize(Decimal("0.00"))


class PurchaseInvoiceCreateSerializer(BaseModelSerializer):
    class PurchaseInvoiceItemSubCreateSerializer(BaseModelSerializer):
        offer = serializers.PrimaryKeyRelatedField(
            queryset=get_model("offers", "Offer").objects.select_related("product_code", "user", "product").all(),
            write_only=True,
        )

        class Meta:
            model = PurchaseInvoiceItem
            fields = ["offer", "quantity"]

        def validate(self, attrs):
            offer = attrs.get("offer")
            quantity = attrs.get("quantity")

            attrs.update(deconstuct_offer(offer))
            attrs["remaining_quantity"] = quantity
            attrs["sub_total"] = Decimal(attrs["purchase_price"] * quantity).quantize(Decimal("0.00"))

            return super().validate(attrs)

    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model()
        .objects.select_related(
            "account", "profile", "profile__manager", "profile__area_manager", "profile__sales", "profile__data_entry"
        )
        .all(),
    )
    items = PurchaseInvoiceItemSubCreateSerializer(many=True, min_length=1)

    class Meta:
        model = PurchaseInvoice
        fields = ["user", "items"]

    def validate_user(self, value):
        user = self.request.user
        invoice_user_profile = getattr(value, "profile", None)

        if invoice_user_profile is None:
            raise serializers.ValidationError("User does not have a profile.")

        if user.is_superuser:
            return value

        if (
            invoice_user_profile.sales != user
            and invoice_user_profile.area_manager != user
            and invoice_user_profile.manager != user
            and invoice_user_profile.data_entry != user
        ):
            raise serializers.ValidationError("You are not allowed to create items for this invoice.")

        return value

    def validate_items(self, value):
        visited = set()
        errs = []
        raise_err = False

        for item in value:
            offer = item["offer"]

            if offer in visited:
                raise_err = True
                errs.append({"offer": f"Duplicate offers aren't allowed."})
            else:
                errs.append({})

            visited.add(offer)

        if raise_err:
            raise serializers.ValidationError(errs)

        return value

    def validate(self, attrs):
        items = attrs.get("items")

        attrs["total_price"] = Decimal(sum([item["sub_total"] for item in items])).quantize(Decimal("0.00"))
        attrs["items_count"] = len(items)
        attrs["total_quantity"] = sum([item["quantity"] for item in items])
        return super().validate(attrs)

    def create(self, validated_data):
        with transaction.atomic():
            instance = create_purchase_invoice(validated_data)
        return instance

    def to_representation(self, instance):
        return PurchaseInvoiceReadSerializer(instance, context=self.context).data


class PurchaseInvoiceStateUpdateSerializer(BaseModelSerializer):
    status = serializers.ChoiceField(choices=PurchaseInvoiceStatusChoice.choices)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = PurchaseInvoice
        fields = ["supplier_invoice_number", "status", "status_label"]

    def update(self, instance, validated_data):
        supplier_invoice_number = validated_data.get("supplier_invoice_number", instance.supplier_invoice_number)
        status = validated_data.get("status")

        fn = None

        if status == PurchaseInvoiceStatusChoice.PLACED:
            fn = unlock_purchase_invoice
        elif status == PurchaseInvoiceStatusChoice.LOCKED:
            if instance.status == PurchaseInvoiceStatusChoice.PLACED:
                fn = lock_purchase_invoice
            elif instance.status == PurchaseInvoiceStatusChoice.CLOSED:
                fn = open_purchase_invoice
        elif status == PurchaseInvoiceStatusChoice.CLOSED:
            if supplier_invoice_number is None or supplier_invoice_number == "":
                raise serializers.ValidationError({"supplier_invoice_number": "This field is required."})

            fn = close_purchase_invoice

        if instance.status == status:
            raise serializers.ValidationError({"detail": "Status is already set to this value."})

        if fn is not None:
            with transaction.atomic():
                if status == PurchaseInvoiceStatusChoice.CLOSED:
                    instance = fn(instance, supplier_invoice_number)
                else:
                    instance = fn(instance)

        return instance


class PurchaseInvoiceItemReadSerializer(BaseModelSerializer):
    class SaleInvoiceItemSubReadSerializer(BaseModelSerializer):
        class Meta:
            model = SaleInvoiceItem
            fields = ["id", "invoice"]

    invoice_obj = PurchaseInvoiceReadSerializer(
        fields=["id", "user", "status", "status_label", "supplier_invoice_number", "created_at"], source="invoice"
    )
    product = ProductReadSerializer()
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    sale_invoice_item = SaleInvoiceItemSubReadSerializer()

    class Meta:
        model = PurchaseInvoiceItem
        fields = [
            "id",
            "invoice",
            "invoice_obj",
            "offer",
            "product",
            "product_expiry_date",
            "operating_number",
            "purchase_discount_percentage",
            "purchase_price",
            "selling_discount_percentage",
            "selling_price",
            "quantity",
            "remaining_quantity",
            "sub_total",
            "status",
            "status_label",
            "sale_invoice_item",
        ]


class PurchaseInvoiceItemCreateSerializer(BaseModelSerializer):
    invoice = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseInvoice.objects.select_related(
            "user",
            "user__profile",
            "user__profile__manager",
            "user__profile__sales",
            "user__profile__area_manager",
            "user__profile__data_entry",
        ).all()
    )

    class Meta:
        model = PurchaseInvoiceItem
        fields = ["invoice", "offer", "quantity"]

    def validate_invoice(self, value):
        if value.status == PurchaseInvoiceStatusChoice.CLOSED:
            raise serializers.ValidationError("Invoice is closed!.")

        user = self.request.user
        invoice_user = value.user
        invoice_user_profile = getattr(invoice_user, "profile", None)

        if invoice_user_profile is None:
            raise serializers.ValidationError("Invoice user does not have a profile.")

        if user.is_superuser:
            return value

        if (
            invoice_user_profile.sales != user
            and invoice_user_profile.area_manager != user
            and invoice_user_profile.manager != user
            and invoice_user_profile.data_entry != user
        ):
            raise serializers.ValidationError("You are not allowed to create items for this invoice.")

        return value

    def validate(self, attrs):
        offer = attrs.get("offer")
        quantity = attrs.get("quantity")

        attrs.update(deconstuct_offer(offer))
        attrs["remaining_quantity"] = quantity
        attrs["sub_total"] = Decimal(attrs["purchase_price"] * quantity).quantize(Decimal("0.00"))
        return super().validate(attrs)

    def create(self, validated_data):
        with transaction.atomic():
            instance = create_purchase_invoice_item(validated_data)

        return instance

    def to_representation(self, instance):
        return PurchaseInvoiceItemReadSerializer(instance, exclude=["invoice_obj"], context=self.context).data


class PurchaseInvoiceItemStateListUpdateSerializer(serializers.ListSerializer):
    def validate(self, attrs):
        ids = set([item["id"] for item in attrs if "id" in item])
        _attrs = {item["id"]: item for item in attrs if "id" in item}
        queryset = self.instance.filter(pk__in=ids)
        validated_data = []

        raise_exception = False
        errs = {}

        for instance in queryset:
            f_allowed_statuses, b_allowed_statuses = get_allowed_status_changes(instance.status)
            instance_attrs = _attrs.get(instance.id)
            instance_errors = {}
            status = instance_attrs.get("status")

            if status not in f_allowed_statuses and status not in b_allowed_statuses:
                instance_errors["status"] = "Status is not allowed."
                raise_exception = True

            sale_invoice = instance.sale_invoice_item.invoice if instance.sale_invoice_item is not None else None

            if sale_invoice is not None and sale_invoice.status == SaleInvoiceStatusChoice.CLOSED:
                instance_errors["sale_invoice"] = (
                    "Cannot change status of invoice item, Related sale invoice is closed."
                )
                raise_exception = True

            errs[instance.id] = instance_errors

            if instance.status == status:
                continue

            validated_data.append({"id": instance.id, "status": status})

        if raise_exception:
            raise serializers.ValidationError(errs)

        return validated_data

    def update(self, queryset, validated_data):
        ids = set([item["id"] for item in validated_data if "id" in item])
        validated_data = {item["id"]: item for item in validated_data if "id" in item}
        queryset = PurchaseInvoiceItem.objects.filter(pk__in=ids)
        updated_instances = []

        with transaction.atomic():
            queryset = queryset.select_for_update()

            for instance in queryset:
                instance_data = validated_data.get(instance.id)
                status = instance_data.get("status")
                instance = update_purchase_invoice_item_state(instance, status, remove_offer=False)
                updated_instances.append(instance)

        return updated_instances


class PurchaseInvoiceItemStateUpdateSerializer(BaseModelSerializer):
    id = serializers.IntegerField(required=True)
    status = serializers.ChoiceField(choices=PurchaseInvoiceItemStatusChoice.choices)
    remove_offer = serializers.BooleanField(required=False, write_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = PurchaseInvoiceItem
        fields = ["id", "status", "remove_offer", "status_label"]
        list_serializer_class = PurchaseInvoiceItemStateListUpdateSerializer

    def validate_status(self, value):
        # Skip validation for QuerySet instances
        if isinstance(self.instance, models.QuerySet):
            return value

        f_allowed_statuses, b_allowed_statuses = get_allowed_status_changes(self.instance.status)

        if value not in f_allowed_statuses and value not in b_allowed_statuses:
            raise serializers.ValidationError("Status is not allowed.")

        return value

    def validate(self, attrs):
        status = attrs.get("status")
        remove_offer = attrs.get("remove_offer", False)
        instance = self.instance

        # Skip validation for QuerySet instances
        if isinstance(instance, models.QuerySet):
            return attrs

        if status == PurchaseInvoiceItemStatusChoice.REJECTED and remove_offer is None:
            raise serializers.ValidationError({"remove_offer": "This field is required."})

        sale_invoice = instance.sale_invoice_item.invoice if instance.sale_invoice_item is not None else None

        if sale_invoice is not None and sale_invoice.status == SaleInvoiceStatusChoice.CLOSED:
            raise serializers.ValidationError(
                {"detail": "Cannot change status of invoice item, Related sale invoice is closed."}
            )

        return attrs

    def update(self, instance, validated_data):
        status = validated_data.get("status")
        remove_offer = validated_data.get("remove_offer", False)

        if instance.status == status:
            raise serializers.ValidationError({"detail": "Status is already set to this value."})

        with transaction.atomic():
            instance = update_purchase_invoice_item_state(instance, status, remove_offer=remove_offer)

        return instance


class PurchaseReturnInvoiceReadSerializer(BaseModelSerializer):
    class PurchaseReturnInvoiceItemSubReadSerializer(BaseModelSerializer):
        purchase_invoice_item = PurchaseInvoiceItemReadSerializer(
            fields=["id", "product", "invoice", "remaining_quantity"]
        )

        class Meta:
            model = PurchaseReturnInvoiceItem
            fields = ["id", "purchase_invoice_item", "quantity", "sub_total"]

    user = UserReadSerializer()
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    items = PurchaseReturnInvoiceItemSubReadSerializer(many=True)

    class Meta:
        model = PurchaseReturnInvoice
        fields = [
            "id",
            "user",
            "items_count",
            "total_quantity",
            "total_price",
            "status",
            "status_label",
            "created_at",
            "items",
        ]


class PurchaseReturnInvoiceCreateSerializer(BaseModelSerializer):
    class PurchaseReturnInvoiceItemSubCreateSerializer(BaseModelSerializer):
        purchase_invoice_item = serializers.PrimaryKeyRelatedField(
            queryset=PurchaseInvoiceItem.objects.select_related("invoice", "invoice__user").filter(
                invoice__status=PurchaseInvoiceStatusChoice.CLOSED
            )
        )

        class Meta:
            model = PurchaseReturnInvoiceItem
            fields = ["id", "purchase_invoice_item", "quantity"]

        def validate(self, attrs):
            purchase_invoice_item = attrs.get("purchase_invoice_item")
            quantity = attrs.get("quantity")

            if purchase_invoice_item.remaining_quantity < quantity:
                raise serializers.ValidationError(
                    {"quantity": f"Quantity cannot exceed {purchase_invoice_item.remaining_quantity} for this item."}
                )

            attrs["sub_total"] = Decimal(purchase_invoice_item.purchase_price * quantity).quantize(Decimal("0.00"))

            return super().validate(attrs)

    items = PurchaseReturnInvoiceItemSubCreateSerializer(many=True, min_length=1)

    class Meta:
        model = PurchaseReturnInvoice
        fields = ["user", "items"]

    def validate_items_user(self, items, user):
        errs = []
        raise_err = False

        for item in items:
            if item["purchase_invoice_item"].invoice.user != user:
                errs.append({"purchase_invoice_item": "Selected items should be for the same user."})
                raise_err = True
            else:
                errs.append({})

        if raise_err:
            raise serializers.ValidationError(errs)

    def validate(self, attrs):
        user = attrs.get("user")
        items = attrs.get("items")

        self.validate_items_user(items, user)

        total_price = Decimal(sum([item["sub_total"] for item in items])).quantize(Decimal("0.00"))
        attrs["total_price"] = total_price
        attrs["items_count"] = len(items)
        attrs["total_quantity"] = sum([item["quantity"] for item in items])

        return super().validate(attrs)

    def create(self, validated_data):
        with transaction.atomic():
            instance = create_purchase_return_invoice(validated_data)
        return instance

    def to_representation(self, instance):
        return PurchaseReturnInvoiceReadSerializer(instance, context=self.context).data


class PurchaseReturnInvoiceStateUpdateSerializer(BaseModelSerializer):
    status = serializers.ChoiceField(choices=[PurchaseReturnInvoiceStatusChoice.CLOSED])
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = PurchaseReturnInvoice
        fields = ["status", "status_label"]

    def update(self, instance, validated_data):
        status = validated_data.get("status")

        if instance.status == status:
            raise serializers.ValidationError({"detail": "Status is already set to this value."})

        with transaction.atomic():
            instance = close_purchase_return_invoice(instance)

        return instance


class PurchaseReturnInvoiceItemReadSerializer(BaseModelSerializer):
    invoice_obj = PurchaseReturnInvoiceReadSerializer(
        fields=["id", "user", "status", "status_label", "created_at"], source="invoice"
    )
    purchase_invoice_item = PurchaseInvoiceItemReadSerializer(
        fields=["id", "product", "invoice", "remaining_quantity"]
    )

    class Meta:
        model = PurchaseReturnInvoiceItem
        fields = ["id", "invoice_obj", "purchase_invoice_item", "quantity", "sub_total"]


class PurchaseReturnInvoiceItemCreateSerializer(BaseModelSerializer):
    invoice = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseReturnInvoice.objects.exclude(status=PurchaseReturnInvoiceStatusChoice.CLOSED)
    )
    purchase_invoice_item = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseInvoiceItem.objects.select_related("invoice", "invoice__user").filter(
            invoice__status=PurchaseInvoiceStatusChoice.CLOSED, remaining_quantity__gt=0
        )
    )

    class Meta:
        model = PurchaseReturnInvoiceItem
        fields = ["invoice", "purchase_invoice_item", "quantity"]
        extra_kwargs = {"quantity": {"min_value": 1}}

    def validate(self, attrs):
        invoice = attrs.get("invoice")
        purchase_invoice_item = attrs.get("purchase_invoice_item")
        quantity = attrs.get("quantity")

        if purchase_invoice_item.invoice.user != invoice.user:
            raise serializers.ValidationError({"purchase_invoice_item": "Selected item should be for the same user."})

        if purchase_invoice_item.remaining_quantity < quantity:
            raise serializers.ValidationError(
                {"quantity": f"Quantity cannot exceed {purchase_invoice_item.remaining_quantity} for this item."}
            )

        attrs["sub_total"] = Decimal(purchase_invoice_item.purchase_price * quantity).quantize(Decimal("0.00"))

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            instance = create_purchase_return_invoice_item(validated_data)
        return instance

    def to_representation(self, instance):
        return PurchaseReturnInvoiceItemReadSerializer(instance, exclude=["invoice_obj"], context=self.context).data


class PurchaseReturnInvoiceItemUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = PurchaseReturnInvoiceItem
        fields = ["quantity"]
        extra_kwargs = {"quantity": {"min_value": 1}}

    def validate(self, attrs):
        instance = self.instance

        if instance is None:
            return attrs

        purchase_invoice_item = instance.purchase_invoice_item
        quantity = attrs.get("quantity")

        total_remaining_quantity = purchase_invoice_item.remaining_quantity + instance.quantity

        if total_remaining_quantity < quantity:
            raise serializers.ValidationError(
                {"quantity": f"Quantity cannot exceed {total_remaining_quantity} for this item."}
            )

        return super().validate(attrs)

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance = update_purchase_return_invoice_item(instance, validated_data)
        return instance

    def to_representation(self, instance):
        return PurchaseReturnInvoiceItemReadSerializer(instance, exclude=["invoice_obj"], context=self.context).data


class SaleInvoiceReadSerializer(BaseModelSerializer):
    class SaleInvoiceItemSubReadSerializer(BaseModelSerializer):
        product = ProductReadSerializer()
        status_label = serializers.CharField(source="get_status_display", read_only=True)

        class Meta:
            model = SaleInvoiceItem
            fields = [
                "id",
                "offer",
                "product",
                "product_expiry_date",
                "operating_number",
                "purchase_discount_percentage",
                "purchase_price",
                "selling_discount_percentage",
                "selling_price",
                "quantity",
                "remaining_quantity",
                "sub_total",
                "status",
                "status_label",
            ]

    class SaleInvoiceDeletedItemSubReadSerializer(BaseModelSerializer):
        product = ProductReadSerializer()
        status_label = serializers.CharField(source="get_status_display", read_only=True)

        class Meta:
            model = SaleInvoiceDeletedItem
            fields = [
                "id",
                "product",
                "product_expiry_date",
                "operating_number",
                "purchase_discount_percentage",
                "purchase_price",
                "selling_discount_percentage",
                "selling_price",
                "quantity",
                "remaining_quantity",
                "sub_total",
                "status",
                "status_label",
                "timestamp",
            ]

    seller = UserReadSerializer()
    user = UserWithProfileReadSerializer()
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    items = SaleInvoiceItemSubReadSerializer(many=True)
    deleted_items = SaleInvoiceDeletedItemSubReadSerializer(many=True)
    items_url = QueryParameterHyperlinkedIdentityField(
        view_name="invoices:sale-invoice-items-list-view", query_param="invoice"
    )
    average_discount_percentage = serializers.SerializerMethodField()
    total_public_price = serializers.SerializerMethodField()
    total_profit = serializers.SerializerMethodField()
    total_purchase_cost = serializers.SerializerMethodField()

    class Meta:
        model = SaleInvoice
        fields = [
            "id",
            "seller",
            "user",
            "items_count",
            "total_quantity",
            "total_price",
            "total_public_price",
            "total_purchase_cost",
            "total_profit",
            "status",
            "status_label",
            "created_at",
            "items",
            "deleted_items",
            "items_url",
            "average_discount_percentage",
        ]

    def get_average_discount_percentage(self, instance):
        """
        Calculate the weighted average discount percentage for the invoice.
        Formula: Sum(quantity * selling_discount_percentage * public_price) / Sum(quantity * public_price)
        """
        from market.models import Product
        
        items = instance.items.select_related("product").all()
        
        if not items:
            return Decimal("0.00")
        
        total_discount = Decimal("0.00")
        total_public_price = Decimal("0.00")
        
        for item in items:
            quantity_price = item.quantity * item.product.public_price
            quantity_discount = quantity_price * (item.selling_discount_percentage / 100)
            
            total_discount += quantity_discount
            total_public_price += quantity_price
        
        if total_public_price == 0:
            return Decimal("0.00")
        
        average_discount = (total_discount / total_public_price) * 100
        return Decimal(average_discount).quantize(Decimal("0.00"))

    def get_total_public_price(self, instance):
        """
        Calculate the total public price (before discount) for all items in the invoice.
        Formula: Sum(quantity * product.public_price)
        """
        items = instance.items.select_related("product").all()
        
        if not items:
            return Decimal("0.00")
        
        total = Decimal("0.00")
        
        for item in items:
            total += item.quantity * item.product.public_price
        
        return Decimal(total).quantize(Decimal("0.00"))

    def get_total_purchase_cost(self, instance):
        """
        Calculate the total purchase cost for all items in the invoice.
        Formula: Sum(quantity * purchase_price)
        """
        items = instance.items.select_related("product").all()
        
        if not items:
            return Decimal("0.00")
        
        total = Decimal("0.00")
        
        for item in items:
            total += item.quantity * item.purchase_price
        
        return Decimal(total).quantize(Decimal("0.00"))

    def get_total_profit(self, instance):
        """
        Calculate the total profit for the invoice.
        Profit = Total Selling Price - Total Purchase Cost
        Formula: Sum(quantity * (selling_price - purchase_price))
        """
        items = instance.items.select_related("product").all()
        
        if not items:
            return Decimal("0.00")
        
        total_profit = Decimal("0.00")
        
        for item in items:
            item_profit = (item.selling_price - item.purchase_price) * item.quantity
            total_profit += item_profit
        
        return Decimal(total_profit).quantize(Decimal("0.00"))


class SaleInvoiceCreateSerializer(BaseModelSerializer):
    class SaleInvoiceItemSubCreateSerializer(BaseModelSerializer):
        offer = serializers.PrimaryKeyRelatedField(
            queryset=get_model("offers", "Offer")
            .objects.select_related("product_code", "user", "user__account", "product")
            .filter(is_max=True)
        )

        class Meta:
            model = SaleInvoiceItem
            fields = ["offer", "quantity"]
            extra_kwargs = {"quantity": {"min_value": 1}}

        def validate(self, attrs):
            offer = attrs.get("offer")
            quantity = attrs.get("quantity")

            if offer.max_amount_per_invoice is not None and quantity > offer.max_amount_per_invoice:
                raise serializers.ValidationError(
                    {"quantity": f"Quantity cannot exceed {offer.max_amount_per_invoice} for this offer."}
                )

            if offer.remaining_amount < quantity:
                raise serializers.ValidationError(
                    {"quantity": f"Quantity cannot exceed {offer.remaining_amount} for this offer."}
                )

            attrs.update(deconstuct_offer(offer))

            return super().validate(attrs)

    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model()
        .objects.select_related("account", "profile", "profile__manager", "profile__area_manager", "profile__sales")
        .all(),
    )
    items = SaleInvoiceItemSubCreateSerializer(many=True, min_length=1)

    class Meta:
        model = SaleInvoice
        fields = ["user", "items"]

    def validate_user(self, value):
        user = self.request.user
        invoice_user_profile = getattr(value, "profile", None)

        if invoice_user_profile is None:
            raise serializers.ValidationError("User does not have a profile.")

        if user.is_superuser:
            return value

        if (
            invoice_user_profile.sales != user
            and invoice_user_profile.area_manager != user
            and invoice_user_profile.manager != user
            and user != value
        ):
            raise serializers.ValidationError("You are not allowed to create items for this invoice.")

        return value

    def validate_items(self, value):
        visited = set()
        errs = []
        raise_err = False

        for item in value:
            offer = item["offer"]

            if offer in visited:
                raise_err = True
                errs.append({"offer": f"Duplicate offers aren't allowed."})
            else:
                errs.append({})

            visited.add(offer)

        if raise_err:
            raise serializers.ValidationError(errs)

        return value

    def calculate_items_price(self, user, items):
        user_profile = getattr(user, "profile", None)

        if user_profile is None:
            raise serializers.ValidationError({"detail": "User does not have a profile."})

        payment_period = user_profile.payment_period

        if payment_period is None:
            raise serializers.ValidationError({"detail": "User does not have payment period."})

        for item in items:
            product = item.get("product")
            selling_discount_percentage = item.get("selling_discount_percentage")
            quantity = item.get("quantity")

            selling_discount_percentage = selling_discount_percentage - payment_period.addition_percentage
            selling_price = product.public_price * (1 - (selling_discount_percentage / 100))

            item["selling_discount_percentage"] = selling_discount_percentage
            item["selling_price"] = Decimal(selling_price).quantize(Decimal("0.00"))

            item["remaining_quantity"] = quantity
            item["sub_total"] = Decimal(selling_price * quantity).quantize(Decimal("0.00"))

        return items

    def validate(self, attrs):
        user = attrs.get("user")
        items = self.calculate_items_price(user, attrs.get("items"))

        total_min_purchase = sum(item["offer"].min_purchase for item in items)

        total_price = Decimal(sum([item["sub_total"] for item in items])).quantize(Decimal("0.00"))

        if total_min_purchase > total_price:
            raise serializers.ValidationError(
                {"total_price": f"Total price cannot be less than {total_min_purchase} for the selected items."}
            )

        if settings.MINIMUM_PHARMACY_INVOICE_SUB_TOTAL > total_price:
            raise serializers.ValidationError(
                {"total_price": f"Total price cannot be less than {settings.MINIMUM_PHARMACY_INVOICE_SUB_TOTAL}."}
            )

        attrs["items"] = items
        attrs["total_price"] = total_price
        attrs["items_count"] = len(items)
        attrs["total_quantity"] = sum([item["quantity"] for item in items])
        attrs["seller"] = self.request.user

        return super().validate(attrs)

    def create(self, validated_data):
        with transaction.atomic():
            instance = create_sale_invoice(validated_data)
        return instance

    def to_representation(self, instance):
        return SaleInvoiceReadSerializer(instance, context=self.context).data


class SaleInvoicePDFSerializer(BaseModelSerializer):
    class SaleInvoiceItemubReadSerializer(BaseModelSerializer):
        product = ProductReadSerializer()
        total_price = serializers.SerializerMethodField()
        average_discount_percentage = serializers.SerializerMethodField()

        class Meta:
            model = SaleInvoiceItem
            fields = (
                "product",
                "operating_number",
                "product_expiry_date",
                "selling_discount_percentage",
                "average_discount_percentage",
                "quantity",
                "total_price",
            )

        def get_average_discount_percentage(self, instance):
            average_discount_percentage = self.context.get("average_discount_percentage", 0)
            # Convert from decimal (0-1) to percentage (0-100)
            percentage = Decimal(average_discount_percentage) * 100
            return percentage.quantize(Decimal("0.00"))

        def get_total_price(self, instance):
            average_discount_percentage = self.context.get("average_discount_percentage", 0)
            # average_discount_percentage is already a decimal (0-1), not percentage
            total_price = instance.quantity * instance.product.public_price * (1 - Decimal(average_discount_percentage))
            return Decimal(total_price).quantize(Decimal("0.00"))

    details_serializer = SaleInvoiceItemubReadSerializer

    seller_name = serializers.CharField(read_only=True)
    user_name = serializers.CharField(read_only=True)
    user_mobile_number = serializers.CharField(read_only=True)
    delivery_name = serializers.CharField(read_only=True)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    prev_balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    average_discount_percentage = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    total_public_price = serializers.SerializerMethodField()

    class Meta:
        model = SaleInvoice
        fields = [
            "id",
            "seller_name",
            "user_name",
            "user_mobile_number",
            "delivery_name",
            "balance",
            "prev_balance",
            "created_at",
            "total_price",
            "items_count",
            "total_quantity",
            "average_discount_percentage",
            "items",
            "total_public_price",
        ]

    def get_average_discount_percentage(self, instance):
        average_discount = self.context.get("average_discount_percentage", 0)
        # Convert from decimal (0-1) to percentage (0-100)
        percentage = Decimal(average_discount) * 100
        return percentage.quantize(Decimal("0.00"))

    def get_items(self, instance):
        items = self.context.get("items", [])
        return self.details_serializer(items, many=True, context=self.context).data

    def get_total_public_price(self, instance):
        total_public_price = self.context.get("total_public_price", 0)
        return total_public_price


class SaleInvoiceStateUpdateSerializer(BaseModelSerializer):
    status = serializers.ChoiceField(choices=SaleInvoiceStatusChoice.choices)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SaleInvoice
        fields = ["status", "status_label"]

    def update(self, instance, validated_data):
        import traceback
        
        status = validated_data.get("status")

        fn = None

        if status == SaleInvoiceStatusChoice.PLACED and instance.status == SaleInvoiceStatusChoice.CLOSED:
            fn = open_sale_invoice
        elif status == SaleInvoiceStatusChoice.CLOSED and instance.status == SaleInvoiceStatusChoice.PLACED:
            fn = close_sale_invoice

        if instance.status == status:
            raise serializers.ValidationError({"detail": "Status is already set to this value."})

        if fn is not None:
            try:
                with transaction.atomic():
                    instance = fn(instance)
            except serializers.ValidationError:
                # Re-raise validation errors
                raise
            except Exception as e:
                # Catch any other error and provide details
                error_msg = f"Error closing invoice: {str(e)}"
                raise serializers.ValidationError({
                    "detail": error_msg,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                })

        return instance


class SaleInvoiceItemReadSerializer(BaseModelSerializer):
    invoice_obj = SaleInvoiceReadSerializer(
        fields=["id", "user", "status", "status_label", "created_at"], source="invoice"
    )
    product = ProductReadSerializer(fields=["id", "name", "e_name", "public_price"])
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SaleInvoiceItem
        fields = [
            "id",
            "invoice",
            "invoice_obj",
            "product",
            "product_expiry_date",
            "operating_number",
            "offer",
            "purchase_discount_percentage",
            "purchase_price",
            "selling_discount_percentage",
            "selling_price",
            "quantity",
            "remaining_quantity",
            "sub_total",
            "status",
            "status_label",
        ]


class SaleInvoiceItemCreateSerializer(BaseModelSerializer):
    invoice = serializers.PrimaryKeyRelatedField(
        queryset=SaleInvoice.objects.select_related(
            "user",
            "user__profile",
            "user__profile__manager",
            "user__profile__sales",
            "user__profile__area_manager",
        ).all()
    )
    offer = serializers.PrimaryKeyRelatedField(
        queryset=get_model("offers", "Offer")
        .objects.select_related("product_code", "user", "user__account", "product")
        .filter(is_max=True)
    )

    class Meta:
        model = SaleInvoiceItem
        fields = ["invoice", "offer", "quantity"]
        extra_kwargs = {"quantity": {"min_value": 1}}

    def validate_invoice(self, value):
        if value.status != SaleInvoiceStatusChoice.PLACED:
            raise serializers.ValidationError("Invoice is not in placed state.")

        user = self.request.user
        invoice_user = value.user
        invoice_user_profile = getattr(invoice_user, "profile", None)

        if invoice_user_profile is None:
            raise serializers.ValidationError("Invoice user does not have a profile.")

        if user.is_superuser:
            return value

        if (
            invoice_user_profile.sales != user
            and invoice_user_profile.area_manager != user
            and invoice_user_profile.manager != user
        ):
            raise serializers.ValidationError("You are not allowed to create items for this invoice.")

        return value

    def validate(self, attrs):
        invoice = attrs.get("invoice")
        offer = attrs.get("offer")
        quantity = attrs.get("quantity")

        user_profile = getattr(invoice.user, "profile", None)

        if user_profile is None:
            raise serializers.ValidationError({"detail": "User does not have a profile."})

        payment_period = user_profile.payment_period

        if payment_period is None:
            raise serializers.ValidationError({"detail": "User does not have a profile."})

        if offer.max_amount_per_invoice is not None and quantity > offer.max_amount_per_invoice:
            raise serializers.ValidationError(
                {"quantity": f"Quantity cannot exceed {offer.max_amount_per_invoice} for this offer."}
            )

        if offer.remaining_amount < quantity:
            raise serializers.ValidationError(
                {"quantity": f"Quantity cannot exceed {offer.remaining_amount} for this offer."}
            )

        attrs.update(deconstuct_offer(offer))

        selling_discount_percentage = attrs.get("selling_discount_percentage")
        selling_discount_percentage = selling_discount_percentage - payment_period.addition_percentage
        product = attrs.get("product")
        selling_price = product.public_price * (1 - (selling_discount_percentage / 100))

        attrs["selling_discount_percentage"] = selling_discount_percentage
        attrs["selling_price"] = Decimal(selling_price).quantize(Decimal("0.00"))

        attrs["remaining_quantity"] = quantity
        attrs["sub_total"] = Decimal(selling_price * quantity).quantize(Decimal("0.00"))

        return super().validate(attrs)

    def create(self, validated_data):
        with transaction.atomic():
            instance = create_sale_invoice_item(validated_data)
        return instance

    def to_representation(self, instance):
        return SaleInvoiceItemReadSerializer(instance, exclude=["invoice_obj"], context=self.context).data


class SaleInvoiceItemStateListUpdateSerializer(serializers.ListSerializer):
    def validate(self, attrs):
        ids = set([item["id"] for item in attrs if "id" in item])
        _attrs = {item["id"]: item for item in attrs if "id" in item}
        queryset = self.instance.filter(pk__in=ids)
        validated_data = []

        raise_exception = False
        errs = {}

        for instance in queryset:
            f_allowed_statuses, b_allowed_statuses = get_allowed_status_changes(instance.status)
            instance_attrs = _attrs.get(instance.id)
            instance_errors = {}
            status = instance_attrs.get("status")

            if status not in f_allowed_statuses and status not in b_allowed_statuses:
                instance_errors["status"] = "Status is not allowed."
                raise_exception = True

            purchase_invoice_item = getattr(instance, "purchase_invoice_item", None)
            if (
                purchase_invoice_item is not None
                and purchase_invoice_item.invoice.status == PurchaseInvoiceStatusChoice.CLOSED
            ):
                instance_errors["purchase_invoice"] = (
                    "Cannot change status of invoice item, Related purchase invoice is closed."
                )
                raise_exception = True

            errs[instance.id] = instance_errors

            if instance.status == status:
                continue

            validated_data.append({"id": instance.id, "status": status})

        if raise_exception:
            raise serializers.ValidationError(errs)

        return validated_data

    def update(self, queryset, validated_data):
        ids = set([item["id"] for item in validated_data if "id" in item])
        validated_data = {item["id"]: item for item in validated_data if "id" in item}
        queryset = SaleInvoiceItem.objects.filter(pk__in=ids)
        updated_instances = []

        with transaction.atomic():
            queryset = queryset.select_for_update()

            for instance in queryset:
                instance_data = validated_data.get(instance.id)
                status = instance_data.get("status")
                purchase_invoice_item = getattr(instance, "purchase_invoice_item", None)
                instance = update_sale_invoice_item_state(instance, status)

                if purchase_invoice_item is not None:
                    update_purchase_invoice_item_state(
                        purchase_invoice_item, status, update_sale_invoice_item=False, remove_offer=False
                    )

                updated_instances.append(instance)

        return updated_instances


class SaleInvoiceItemStateUpdateSerializer(BaseModelSerializer):
    id = serializers.IntegerField(required=True)
    status = serializers.ChoiceField(choices=SaleInvoiceItemStatusChoice.choices)
    remove_offer = serializers.BooleanField(required=False, write_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SaleInvoiceItem
        fields = ["id", "status", "remove_offer", "status_label"]
        list_serializer_class = SaleInvoiceItemStateListUpdateSerializer

    def validate_status(self, value):
        # Skip validation for QuerySet instances
        if isinstance(self.instance, models.QuerySet):
            return value
        f_allowed_statuses, b_allowed_statuses = get_allowed_status_changes(self.instance.status)

        if value not in f_allowed_statuses and value not in b_allowed_statuses:
            raise serializers.ValidationError("Status is not allowed.")

        return value

    def validate(self, attrs):
        status = attrs.get("status")
        remove_offer = attrs.get("remove_offer", False)
        instance = self.instance

        # Skip validation for QuerySet instances
        if isinstance(instance, models.QuerySet):
            return attrs

        if status == SaleInvoiceItemStatusChoice.REJECTED and remove_offer is None:
            raise serializers.ValidationError({"remove_offer": "This field is required."})
        elif status != SaleInvoiceItemStatusChoice.REJECTED:
            remove_offer = False

        return attrs

    def update(self, instance, validated_data):
        status = validated_data.get("status")
        remove_offer = validated_data.get("remove_offer", False)
        purchase_invoice_item = getattr(instance, "purchase_invoice_item", None)

        if instance.status == status:
            raise serializers.ValidationError({"detail": "Status is already set to this value."})

        with transaction.atomic():
            instance = update_sale_invoice_item_state(instance, status)

            if purchase_invoice_item is not None:
                if purchase_invoice_item.invoice.status == PurchaseInvoiceStatusChoice.CLOSED:
                    raise serializers.ValidationError(
                        {"detail": "Cannot change status of invoice item, Related purchase invoice is closed."}
                    )
                update_purchase_invoice_item_state(
                    purchase_invoice_item, status, update_sale_invoice_item=False, remove_offer=remove_offer
                )
            elif remove_offer and instance.offer is not None:
                delete_offer(instance.offer)

        return instance


class SaleInvoiceItemUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = SaleInvoiceItem
        fields = [
            "product_expiry_date",
            "operating_number",
            "selling_discount_percentage",
            "quantity",
        ]
        extra_kwargs = {
            "quantity": {"min_value": 1},
            "selling_discount_percentage": {"min_value": 0, "max_value": 99.99},
        }

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance = update_sale_invoice_item(instance, validated_data)
        return instance

    def to_representation(self, instance):
        return SaleInvoiceItemReadSerializer(instance, exclude=["invoice_obj"], context=self.context).data


class SaleReturnInvoiceReadSerializer(BaseModelSerializer):
    class SaleReturnInvoiceItemSubReadSerializer(BaseModelSerializer):
        sale_invoice_item = SaleInvoiceItemReadSerializer(fields=["id", "product", "invoice", "remaining_quantity"])

        class Meta:
            model = SaleReturnInvoiceItem
            fields = ["id", "sale_invoice_item", "quantity", "sub_total"]

    user = UserReadSerializer()
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    items = SaleReturnInvoiceItemSubReadSerializer(many=True)

    class Meta:
        model = SaleReturnInvoice
        fields = [
            "id",
            "user",
            "items_count",
            "total_quantity",
            "total_price",
            "status",
            "status_label",
            "created_at",
            "items",
        ]


class SaleReturnInvoiceCreateSerializer(BaseModelSerializer):
    class SaleReturnInvoiceItemSubCreateSerializer(BaseModelSerializer):
        sale_invoice_item = serializers.PrimaryKeyRelatedField(
            queryset=SaleInvoiceItem.objects.select_related("invoice", "invoice__user").filter(
                invoice__status=SaleInvoiceStatusChoice.CLOSED, remaining_quantity__gt=0, product__fridge=False
            )
        )

        class Meta:
            model = SaleReturnInvoiceItem
            fields = ["id", "sale_invoice_item", "quantity"]

        def validate(self, attrs):
            sale_invoice_item = attrs.get("sale_invoice_item")
            quantity = attrs.get("quantity")

            if sale_invoice_item.remaining_quantity < quantity:
                raise serializers.ValidationError(
                    {"quantity": f"Quantity cannot exceed {sale_invoice_item.remaining_quantity} for this item."}
                )

            attrs["sub_total"] = Decimal(sale_invoice_item.selling_price * quantity).quantize(Decimal("0.00"))

            return super().validate(attrs)

    items = SaleReturnInvoiceItemSubCreateSerializer(many=True, min_length=1)

    class Meta:
        model = SaleReturnInvoice
        fields = ["user", "items"]

    def validate_items_user(self, items, user):
        errs = []
        raise_err = False

        for item in items:
            if item["sale_invoice_item"].invoice.user != user:
                errs.append({"sale_invoice_item": "Selected items should be for the same user."})
                raise_err = True
            else:
                errs.append({})

        if raise_err:
            raise serializers.ValidationError(errs)

    def validate(self, attrs):
        user = attrs.get("user")
        items = attrs.get("items")

        self.validate_items_user(items, user)

        total_price = Decimal(sum([item["sub_total"] for item in items])).quantize(Decimal("0.00"))
        attrs["total_price"] = total_price
        attrs["items_count"] = len(items)
        attrs["total_quantity"] = sum([item["quantity"] for item in items])

        return super().validate(attrs)

    def create(self, validated_data):
        with transaction.atomic():
            instance = create_sale_return_invoice(validated_data)
        return instance

    def to_representation(self, instance):
        return SaleReturnInvoiceReadSerializer(instance, context=self.context).data


class SaleReturnInvoiceStateUpdateSerializer(BaseModelSerializer):
    status = serializers.ChoiceField(choices=[SaleReturnInvoiceStatusChoice.CLOSED])
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SaleReturnInvoice
        fields = ["status", "status_label"]

    def update(self, instance, validated_data):
        status = validated_data.get("status")

        if instance.status == status:
            raise serializers.ValidationError({"detail": "Status is already set to this value."})

        with transaction.atomic():
            instance = close_sale_return_invoice(instance)

        return instance


class SaleReturnInvoiceItemReadSerializer(BaseModelSerializer):
    invoice_obj = SaleReturnInvoiceReadSerializer(
        fields=["id", "user", "status", "status_label", "created_at"], source="invoice"
    )
    sale_invoice_item = SaleInvoiceItemReadSerializer(fields=["id", "product", "invoice", "remaining_quantity"])

    class Meta:
        model = SaleReturnInvoiceItem
        fields = ["id", "invoice_obj", "sale_invoice_item", "quantity", "sub_total"]


class SaleReturnInvoiceItemCreateSerializer(BaseModelSerializer):
    invoice = serializers.PrimaryKeyRelatedField(
        queryset=SaleReturnInvoice.objects.exclude(status=SaleReturnInvoiceStatusChoice.CLOSED)
    )
    sale_invoice_item = serializers.PrimaryKeyRelatedField(
        queryset=SaleInvoiceItem.objects.select_related("invoice", "invoice__user").filter(
            invoice__status=SaleInvoiceStatusChoice.CLOSED, remaining_quantity__gt=0, product__fridge=False
        )
    )

    class Meta:
        model = SaleReturnInvoiceItem
        fields = ["invoice", "sale_invoice_item", "quantity"]
        extra_kwargs = {"quantity": {"min_value": 1}}

    def validate(self, attrs):
        invoice = attrs.get("invoice")
        sale_invoice_item = attrs.get("sale_invoice_item")
        quantity = attrs.get("quantity")

        if sale_invoice_item.invoice.user != invoice.user:
            raise serializers.ValidationError({"sale_invoice_item": "Selected item should be for the same user."})

        if sale_invoice_item.remaining_quantity < quantity:
            raise serializers.ValidationError(
                {"quantity": f"Quantity cannot exceed {sale_invoice_item.remaining_quantity} for this item."}
            )

        attrs["sub_total"] = Decimal(sale_invoice_item.selling_price * quantity).quantize(Decimal("0.00"))

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            instance = create_sale_return_invoice_item(validated_data)
        return instance

    def to_representation(self, instance):
        return SaleReturnInvoiceItemReadSerializer(instance, exclude=["invoice_obj"], context=self.context).data


class SaleReturnInvoiceItemUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = SaleReturnInvoiceItem
        fields = ["quantity"]
        extra_kwargs = {"quantity": {"min_value": 1}}

    def validate(self, attrs):
        instance = self.instance

        if instance is None:
            return attrs

        sale_invoice_item = instance.sale_invoice_item
        quantity = attrs.get("quantity")

        total_remaining_quantity = sale_invoice_item.remaining_quantity + instance.quantity

        if total_remaining_quantity < quantity:
            raise serializers.ValidationError(
                {"quantity": f"Quantity cannot exceed {total_remaining_quantity} for this item."}
            )

        return super().validate(attrs)

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance = update_sale_return_invoice_item(instance, validated_data)
        return instance

    def to_representation(self, instance):
        return SaleReturnInvoiceItemReadSerializer(instance, exclude=["invoice_obj"], context=self.context).data
