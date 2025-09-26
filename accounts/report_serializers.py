from accounts.choices import AccountTransactionTypeChoice
from accounts.models import Pharmacy, PharmacyFinancialAccount, PharmacyFinancialAccountTransaction
from accounts.utils import get_transaction_amount_sign
from core.serializers.abstract_serializers import BaseModelSerializer
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class PharmacyReportSerializer(BaseModelSerializer):
    class Meta:
        model = Pharmacy
        fields = ["name", "username"]


class PharmacyFinancialAccountReportSerializer(BaseModelSerializer):
    class PharmacyFinancialAccountTransactionSerializer(BaseModelSerializer):
        transaction_type = serializers.CharField(source="get_transaction_type_display")
        transaction_value = serializers.SerializerMethodField()

        class Meta:
            model = PharmacyFinancialAccountTransaction
            fields = ["id", "transaction_type", "transaction_value", "transaction_at"]

        def get_transaction_value(self, instance):
            sign = get_transaction_amount_sign(instance.transaction_type)
            return instance.transaction_value * sign

    class Meta:
        model = PharmacyFinancialAccount
        fields = ["id", "pharmacy", "balance", "credit_limit", "remaining_credit_limit", ""]
