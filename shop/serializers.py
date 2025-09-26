from accounts.serializers import UserReadSerializer
from shop.models import Cart, CartItem
from shop.utils import create_cart_item, reset_cart, update_cart_item
from core.serializers.abstract_serializers import BaseModelSerializer, BaseSerializer
from market.serializers import ProductReadSerializer
from rest_framework import serializers
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import transaction
from invoices.serializers import SaleInvoiceCreateSerializer

get_model = apps.get_model


class CartReadSerializer(BaseModelSerializer):
    class CartItemSubReadSerializer(BaseModelSerializer):
        product = ProductReadSerializer()

        class Meta:
            model = CartItem
            fields = [
                "id",
                "offer",
                "product",
                "quantity",
                "discount_percentage",
                "price",
                "sub_total",
                "sold_out",
                "created_at",
            ]

    items = CartItemSubReadSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items_count", "total_quantity", "total_price", "items"]


class CartCheckoutSerializer(BaseSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate(self, attrs):
        user = attrs.get("user")

        cart = getattr(user, "cart", None)

        if cart is None:
            raise serializers.ValidationError("User does not have a cart.")

        items = [*cart.items.filter(sold_out=False).values("offer", "quantity")]

        if len(items) == 0:
            raise serializers.ValidationError({"detail": "Cart is empty."})

        return {"cart": cart, "user": user.pk, "items": items}

    def create(self, validated_data):
        cart = validated_data.pop("cart")

        with transaction.atomic():
            serializer = SaleInvoiceCreateSerializer(data=validated_data, context=self.context)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            cart = reset_cart(cart)

        return cart

    def to_representation(self, instance):
        return CartReadSerializer(instance, context=self.context).data


class CartItemReadSerializer(BaseModelSerializer):
    product = ProductReadSerializer()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "offer",
            "product",
            "quantity",
            "discount_percentage",
            "price",
            "sub_total",
            "sold_out",
            "created_at",
        ]


class CartItemCreateSerializer(BaseModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    offer = serializers.PrimaryKeyRelatedField(queryset=get_model("offers", "Offer").objects.filter(is_max=True))

    class Meta:
        model = CartItem
        fields = ["user", "offer", "quantity"]
        extra_kwargs = {"quantity": {"min_value": 1}}

    def validate(self, attrs):
        user = attrs.pop("user", self.request.user)
        offer = attrs.get("offer", None)
        quantity = attrs.get("quantity", None)

        profile = getattr(user, "profile", None)

        if profile is None:
            raise serializers.ValidationError({"user": "User profile not found."})

        payment_period = profile.payment_period

        if payment_period is None:
            raise serializers.ValidationError({"user": "User payment period not found."})

        cart = getattr(user, "cart", None)

        if cart is None:

            raise serializers.ValidationError({"user": "User cart not found."})

        attrs["cart"] = cart
        attrs["product"] = offer.product
        attrs["discount_percentage"] = discount_percentage = (
            offer.selling_discount_percentage - payment_period.addition_percentage
        )
        attrs["price"] = price = offer.product.public_price * (1 - (discount_percentage / 100))
        attrs["sub_total"] = price * quantity

        attrs["existing_item"] = cart.items.filter(offer=offer, sold_out=False).first()

        return super().validate(attrs)

    def create(self, validated_data):
        existing_item = validated_data.pop("existing_item", None)

        with transaction.atomic():
            if existing_item:
                data = {"quantity": existing_item.quantity + validated_data["quantity"]}
                instance = update_cart_item(existing_item, data, update_cart=True)
            else:
                instance = create_cart_item(validated_data, update_cart=True)

        return instance

    def to_representation(self, instance):
        return CartItemReadSerializer(instance, context=self.context).data


class CartItemUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity", "sub_total"]
        read_only_fields = ["sub_total"]
        extra_kwargs = {"quantity": {"min_value": 1}}

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance = update_cart_item(instance, validated_data, update_cart=True)

        return instance
