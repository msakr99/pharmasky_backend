from itertools import product
from accounts.serializers import UserReadSerializer
from core.serializers.abstract_serializers import BaseModelSerializer, QueryParameterHyperlinkedIdentityField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.db import transaction
from market.models import Category, Company, PharmacyProductWishList, Product, ProductCode
from market.utils import update_product

get_model = apps.get_model


class CompanyReadSerializer(BaseModelSerializer):
    products_url = QueryParameterHyperlinkedIdentityField(view_name="market:products-list-view", query_param="company")

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "e_name",
            "image",
            "products_url",
        ]


class CategoryReadSerializer(BaseModelSerializer):
    products_url = QueryParameterHyperlinkedIdentityField(
        view_name="market:products-list-view", query_param="category"
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "e_name",
            "image",
            "products_url",
        ]


class ProductReadSerializer(BaseModelSerializer):
    company = CompanyReadSerializer()
    category = CategoryReadSerializer()
    alternative_products_url = serializers.HyperlinkedIdentityField(view_name="market:product-alternatives-list-view")
    instance_products_url = serializers.HyperlinkedIdentityField(view_name="market:product-instances-list-view")
    max_offer_id = serializers.IntegerField(read_only=True)
    max_offer_actual_discount_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    max_offer_actual_offer_price = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    max_offer_remaining_amount = serializers.IntegerField(read_only=True)
    max_offers_url = QueryParameterHyperlinkedIdentityField(
        view_name="offers:max-offers-list-view", query_param="product"
    )
    has_image = serializers.BooleanField(read_only=True)
    total_purchases = serializers.IntegerField(read_only=True)
    total_purchases_returned = serializers.IntegerField(read_only=True)
    total_sold = serializers.IntegerField(read_only=True)
    total_sales_returned = serializers.IntegerField(read_only=True)
    total_in_stock = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "e_name",
            "image",
            "has_image",
            "public_price",
            "company",
            "category",
            "effective_material",
            "letter",
            "shape",
            "alternative_products_url",
            "instance_products_url",
            "needed",
            "fridge",
            "total_purchases",
            "total_purchases_returned",
            "total_sold",
            "total_sales_returned",
            "total_in_stock",
            "max_offers_url",
            "max_offer_id",
            "max_offer_actual_discount_percentage",
            "max_offer_actual_offer_price",
            "max_offer_remaining_amount",
        ]


class ProductCreateUpdateSerilizer(BaseModelSerializer):
    class Meta:
        model = Product
        fields = [
            "name",
            "e_name",
            "image",
            "public_price",
            "company",
            "category",
            "effective_material",
            "shape",
            "needed",
            "is_illegal",
            "fridge",
        ]

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance = update_product(instance, validated_data)
        return instance


class ProductCodeReadSerializer(BaseModelSerializer):
    product = ProductReadSerializer(fields=["id", "name", "e_name", "public_price"])
    user = UserReadSerializer(fields=["id", "name", "e_name"])

    class Meta:
        model = ProductCode
        fields = ["id", "product", "user", "code"]


class ProductCodeCreateUpdateSerializer(BaseModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, required=False)
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_model("accounts", "User").objects.all(), write_only=True, required=False
    )

    class Meta:
        model = ProductCode
        fields = ["id", "product", "user", "code"]

    def validate(self, attrs):
        if not attrs.get("product") or not attrs.get("user"):
            raise ValidationError(_("Product and User are required to create a Product Code."))
        return super().validate(attrs)


class PharmacyProductWishListSerializer(BaseModelSerializer):
    pharmacy = UserReadSerializer(fields=["id", "name", "e_name"], read_only=True)
    pharmacy_id = serializers.HiddenField(default=serializers.CurrentUserDefault(), write_only=True, source="pharmacy")
    product = ProductReadSerializer(fields=["id", "name", "e_name", "public_price"], read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source="product",
        queryset=Product.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = PharmacyProductWishList
        fields = ["id", "pharmacy", "pharmacy_id", "product", "product_id", "created_at"]

    def validate(self, attrs):
        pharmacy = attrs.get("pharmacy")
        product = attrs.get("product")
        queryset = PharmacyProductWishList.objects.filter(pharmacy=pharmacy, product=product)

        instance = self.instance

        if instance is not None:
            queryset = queryset.exclude(id=instance.id)

        if queryset.exists():
            raise ValidationError({"product": _("This product is already in the pharmacy's wishlist.")})

        return super().validate(attrs)
