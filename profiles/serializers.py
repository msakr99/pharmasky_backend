from accounts.choices import Role
from core.serializers.abstract_serializers import BaseModelSerializer
from profiles.models import Complaint, PaymentPeriod, UserProfile, City, Country, Area
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction, models

from profiles.utils import update_user_profile


class AreaReadSerializer(BaseModelSerializer):
    class Meta:
        model = Area
        fields = ["id", "name"]


class CountryReadSerializer(BaseModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name"]


class CityReadSerializer(BaseModelSerializer):
    country = CountryReadSerializer()

    class Meta:
        model = City
        fields = ["id", "name", "country"]


class PaymentPeriodReadSerializer(BaseModelSerializer):
    class Meta:
        model = PaymentPeriod
        fields = ["id", "name", "period_in_days", "addition_percentage"]


class UserProfileReadSerializer(BaseModelSerializer):
    class UserSubReadSerializer(BaseModelSerializer):
        role_label = serializers.CharField(source="get_role_display", read_only=True)
        
        class Meta:
            model = get_user_model()
            fields = ["id", "name", "e_name", "username", "role", "role_label"]

    user = UserSubReadSerializer()
    data_entry = UserSubReadSerializer()
    sales = UserSubReadSerializer()
    manager = UserSubReadSerializer()
    area_manager = UserSubReadSerializer()
    delivery = UserSubReadSerializer()
    city = CityReadSerializer()
    payment_period = PaymentPeriodReadSerializer()
    category_label = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "data_entry",
            "sales",
            "manager",
            "area_manager",
            "delivery",
            "city",
            "category",
            "category_label",
            "license",
            "address",
            "remarks",
            "latest_invoice_date",
            "payment_period",
            "profit_percentage",
            "order_by_phone",
            "company",
            "key_person",
            "key_person_phone",
        ]


class UserProfileCreateUpdateSerializer(BaseModelSerializer):
    data_entry = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.filter(models.Q(role=Role.DATA_ENTRY) | models.Q(is_superuser=True)),
        required=False,
        allow_null=True,
    )
    sales = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.filter(models.Q(role=Role.SALES) | models.Q(is_superuser=True)),
        required=False,
        allow_null=True,
    )
    manager = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.filter(models.Q(role=Role.MANAGER) | models.Q(is_superuser=True)),
        required=False,
        allow_null=True,
    )
    area_manager = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.filter(models.Q(role=Role.AREA_MANAGER) | models.Q(is_superuser=True)),
        required=False,
        allow_null=True,
    )
    delivery = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.filter(models.Q(role=Role.DELIVERY) | models.Q(is_superuser=True)),
        required=False,
        allow_null=True,
    )
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "data_entry",
            "sales",
            "manager",
            "area_manager",
            "delivery",
            "city",
            "category",
            "license",
            "address",
            "remarks",
            "latest_invoice_date",
            "payment_period",
            "profit_percentage",
            "order_by_phone",
            "company",
            "key_person",
            "key_person_phone",
        ]

    def update(self, instance, validated_data):
        validated_data.pop("user", None)
        with transaction.atomic():
            instance = update_user_profile(instance, validated_data)
        return instance

    def to_representation(self, instance):
        return UserProfileReadSerializer(instance, context=self.context).data


class ComplaintReadSerializer(BaseModelSerializer):
    class UserSubReadSerializer(BaseModelSerializer):
        class Meta:
            model = get_user_model()
            fields = ["id", "name", "e_name", "username"]

    user = UserSubReadSerializer()

    class Meta:
        model = Complaint
        fields = ["user", "subject", "body", "mark_as_solved", "created_at"]


class ComplaintCreateSerializer(BaseModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Complaint
        fields = ["user", "subject", "body"]
