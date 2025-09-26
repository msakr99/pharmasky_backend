from django_filters import rest_framework as filters

from finance.choices import AccountTransactionTypeChoice
from core.filters.abstract_filters import ListIDFilter
from finance.choices import PaymentMethodChoice
from finance.models import AccountTransaction, PurchasePayment, SalePayment


class AccountTransactionFilter(filters.FilterSet):
    account = ListIDFilter(field_name="account__pk")
    type = filters.ChoiceFilter(field_name="type", choices=AccountTransactionTypeChoice.choices)

    class Meta:
        model = AccountTransaction
        fields = ["account", "type"]


class PurchasePaymentFilter(filters.FilterSet):
    user = ListIDFilter(field_name="user__pk")
    method = filters.ChoiceFilter(field_name="method", choices=PaymentMethodChoice.choices)
    at = filters.DateFromToRangeFilter(field_name="at")
    timestamp = filters.DateFromToRangeFilter(field_name="timestamp")

    class Meta:
        model = PurchasePayment
        fields = ["user", "method", "at", "timestamp"]


class SalePaymentFilter(filters.FilterSet):
    user = ListIDFilter(field_name="user__pk")
    method = filters.ChoiceFilter(field_name="method", choices=PaymentMethodChoice.choices)
    at = filters.DateFromToRangeFilter(field_name="at")
    timestamp = filters.DateFromToRangeFilter(field_name="timestamp")

    class Meta:
        model = SalePayment
        fields = ["user", "method", "at", "timestamp"]
