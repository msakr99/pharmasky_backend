from decimal import Decimal
from email.policy import default
from accounts.choices import AccountTransactionTypeChoice, FinancialAccountTransactionEffect
from accounts.utils import affect_pharmacy_account, affect_seller_account
from core.serializers.abstract_serializers import (
    BaseModelSerializer,
    BaseUserCreateSerializer,
    ExtendedPhoneNumberField,
    QueryParameterHyperlinkedIdentityField,
)
from accounts.models import AreaManager, DataEntry, Delivery, Pharmacy, Sales, Store, User
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.db import transaction
from django.utils import timezone

from finance.serializers import AccountReadSerializer
from profiles.serializers import UserProfileReadSerializer

get_model = apps.get_model


# NOTE:Tested and working fine
class UserReadSerializer(BaseModelSerializer):
    username = ExtendedPhoneNumberField()
    role_label = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "name", "e_name", "area", "role", "role_label", "is_superuser"]


class UserWithProfileReadSerializer(BaseModelSerializer):
    class UserProfileSubReadSerializer(BaseModelSerializer):
        class PaymentPeriodSubReadSerializer(BaseModelSerializer):
            class Meta:
                model = get_model("profiles", "PaymentPeriod")
                fields = ["id", "name", "period_in_days", "addition_percentage"]

        payment_period = PaymentPeriodSubReadSerializer()

        class Meta:
            model = get_model("profiles", "UserProfile")
            fields = ["id", "payment_period"]

    username = ExtendedPhoneNumberField()
    role_label = serializers.CharField(source="get_role_display", read_only=True)
    profile = UserProfileSubReadSerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "name",
            "e_name",
            "area",
            "role",
            "role_label",
            "is_superuser",
            "profile",
        ]


class UserFullReadSerializer(BaseModelSerializer):
    username = ExtendedPhoneNumberField()
    role_label = serializers.CharField(source="get_role_display", read_only=True)
    profile = UserProfileReadSerializer()
    account = AccountReadSerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "name",
            "e_name",
            "area",
            "role",
            "role_label",
            "is_superuser",
            "is_active",
            "profile",
            "account",
        ]


# NOTE:Tested and working fine
class PharmacyCreateSerializer(BaseUserCreateSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Pharmacy
        fields = [
            "username",
            "name",
            "e_name",
            "area",
            "password",
            "confirm_password",
        ]
