# Removed unused imports: Decimal, default, AccountTransactionTypeChoice, 
# FinancialAccountTransactionEffect, affect_pharmacy_account, affect_seller_account
from core.serializers.abstract_serializers import (
    BaseModelSerializer,
    BaseUserCreateSerializer,
    ExtendedPhoneNumberField,
    QueryParameterHyperlinkedIdentityField,
)
from accounts.models import Pharmacy, User
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.contrib.auth import authenticate

from finance.serializers import AccountReadSerializer
from profiles.serializers import UserProfileReadSerializer

get_model = apps.get_model


# Custom Login Serializer that only requires username and password
class CustomAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("Username"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


# NOTE:Tested and working fine
class UserReadSerializer(BaseModelSerializer):
    username = ExtendedPhoneNumberField()
    role_label = serializers.CharField(source="get_role_display", read_only=True)
    account = AccountReadSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "name", "e_name", "area", "role", "role_label", "is_superuser", "account"]


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
            "profile",
            "account",
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
