from django.db import transaction
from rest_framework import serializers
from core.serializers.abstract_serializers import (
    BaseModelSerializer,
    BaseSerializer,
    QueryParameterHyperlinkedIdentityField,
)
from django.contrib.auth import get_user_model
from django.db import models
from django.apps import apps
from finance.choices import NEGATIVE_AFFECTING_TRANSACTIONS, AccountTransactionTypeChoice
from finance.expense_choices import ExpenseTypeChoice, ExpenseCategoryChoice
from finance.models import (
    Account,
    AccountTransaction,
    PurchasePayment,
    SafeTransaction,
    SalePayment,
    Expense,
)
from finance.utils import create_puchase_payment, create_sale_payment, update_account, update_payment
from invoices.choices import PurchaseInvoiceStatusChoice, SaleInvoiceStatusChoice
from django.utils import timezone
from datetime import timedelta

get_model = apps.get_model


class AccountReadSerializer(BaseModelSerializer):
    transactions_url = QueryParameterHyperlinkedIdentityField(
        view_name="finance:account-transactions-list-view", query_param="account"
    )

    class Meta:
        model = Account
        fields = ["id", "balance", "credit_limit", "remaining_credit", "transactions_url"]


class AccountUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Account
        fields = ["credit_limit"]

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance = update_account(instance, validated_data)

        return instance

    def to_representation(self, instance):
        return AccountReadSerializer(instance, context=self.context).data


class AccountTransactionReadSerializer(BaseModelSerializer):
    type_label = serializers.CharField(source="get_type_display", read_only=True)
    ct = serializers.CharField(source="content_type.model", read_only=True)
    balance_after = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True, required=False)

    class Meta:
        model = AccountTransaction
        fields = ["id", "type", "type_label", "amount", "at", "ct", "object_id", "balance_after", "timestamp"]


class PurchasePaymentReadSerializer(BaseModelSerializer):
    method_label = serializers.CharField(source="get_method_display", read_only=True)

    class Meta:
        model = PurchasePayment
        fields = ["id", "amount", "method", "method_label", "remarks", "at", "timestamp"]


class PurchasePaymentCreateSerializer(BaseModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.select_related("account").prefetch_related("purchase_invoices").all(),
    )

    class Meta:
        model = PurchasePayment
        fields = ["user", "method", "amount", "remarks", "at"]

    def create(self, validated_data):
        with transaction.atomic():
            instance = create_puchase_payment(validated_data)
        return instance

    def to_representation(self, instance):
        return PurchasePaymentReadSerializer(instance, context=self.context).data


class PurchasePaymentUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = PurchasePayment
        fields = ["method", "amount", "remarks", "at"]

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance = update_payment(instance, validated_data)
        return instance

    def to_representation(self, instance):
        return PurchasePaymentReadSerializer(instance, context=self.context).data


class SalePaymentReadSerializer(BaseModelSerializer):
    method_label = serializers.CharField(source="get_method_display", read_only=True)

    class Meta:
        model = SalePayment
        fields = ["id", "amount", "method", "method_label", "at", "remarks", "timestamp"]


class SalePaymentCreateSerializer(BaseModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model()
        .objects.select_related("account", "profile", "profile__payment_period")
        .prefetch_related("sale_invoices")
        .all(),
    )

    class Meta:
        model = SalePayment
        fields = ["user", "method", "amount", "remarks", "at"]

    def validate(self, attrs):
        user = attrs.get("user")
        account = getattr(user, "account", None)
        amount = attrs.get("amount", 0)

        if account is None:
            raise serializers.ValidationError({"user": "User does not have an account."})

        payment_period = getattr(user.profile, "payment_period", None)

        if payment_period is None:
            raise serializers.ValidationError({"detail": "User does not have a payment period."})

        period_in_days = payment_period.period_in_days
        TODAY = timezone.now().date()
        min_date = TODAY - timezone.timedelta(days=period_in_days)

        total_consumption_in_payment_period = (
            account.transactions.filter(type__in=NEGATIVE_AFFECTING_TRANSACTIONS, at__gte=min_date).aggregate(
                total_amount=models.Sum("amount")
            )["total_amount"]
            or 0
        )

        total_must_pay = account.balance + total_consumption_in_payment_period

        # We multiply by -1 because the amount is negative for payments or inbound transactions
        if amount < -1 * total_must_pay:
            raise serializers.ValidationError(
                {
                    "amount": f"Amount should be greater than or equal to the total unpaid amount for invoices older than {period_in_days} days, which is {-1 * total_must_pay}."
                }
            )

        return super().validate(attrs)

    def create(self, validated_data):
        with transaction.atomic():
            instance = create_sale_payment(validated_data)

        return instance

    def to_representation(self, instance):
        return SalePaymentReadSerializer(instance, context=self.context).data


class SalePaymentUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = SalePayment
        fields = ["method", "amount", "remarks", "at"]

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance = update_payment(instance, validated_data)

        return instance

    def to_representation(self, instance):
        return SalePaymentReadSerializer(instance, context=self.context).data


class SafeTransactionSerializer(BaseModelSerializer):
    type_label = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = SafeTransaction
        fields = ["id", "type", "type_label", "amount", "timestamp"]


class ExpenseSerializer(BaseModelSerializer):
    type_label = serializers.CharField(source="get_type_display", read_only=True)
    category_label = serializers.CharField(source="get_category_display", read_only=True)
    payment_method_label = serializers.CharField(source="get_payment_method_display", read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id",
            "type",
            "type_label",
            "category",
            "category_label",
            "amount",
            "description",
            "recipient",
            "payment_method",
            "payment_method_label",
            "expense_date",
            "created_at",
        ]


class SafeSerializer(BaseSerializer):
    safe_total_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    credit_total_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    debt_total_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    inventory_total_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    expenses_total_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    total_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)


class CollectionScheduleSerializer(BaseSerializer):
    """
    Serializer for collection schedule showing expected payment dates
    based on payment period (شريحة) for each pharmacy.
    """
    user_id = serializers.IntegerField(read_only=True)
    customer_name = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    payment_period_name = serializers.CharField(read_only=True)
    period_in_days = serializers.IntegerField(read_only=True)
    latest_invoice_date = serializers.DateTimeField(read_only=True)
    expected_collection_date = serializers.DateTimeField(read_only=True)
    days_until_collection = serializers.IntegerField(read_only=True)
    outstanding_balance = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    # Penalty and Cashback
    penalty_percentage = serializers.DecimalField(max_digits=4, decimal_places=2, read_only=True)
    penalty_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    total_with_penalty = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    
    cashback_percentage = serializers.DecimalField(max_digits=4, decimal_places=2, read_only=True)
    cashback_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    total_with_cashback = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)


class AccountsPayableSerializer(BaseSerializer):
    """
    Serializer for accounts payable (الحسابات الدائنة - الفلوس اللي علينا)
    Shows stores/suppliers we owe money to
    """
    user_id = serializers.IntegerField(read_only=True)
    supplier_name = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    role_label = serializers.CharField(read_only=True)
    amount_owed = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    last_payment_date = serializers.DateTimeField(read_only=True, required=False, allow_null=True)
    last_purchase_date = serializers.DateTimeField(read_only=True, required=False, allow_null=True)
    days_since_last_payment = serializers.IntegerField(read_only=True, required=False)
