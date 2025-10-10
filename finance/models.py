from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from finance.choices import AccountTransactionTypeChoice, PaymentMethodChoice, SafeTransactionTypeChoice


class SafeTransaction(models.Model):
    """
    Safe Transaction Model
    This model is used to track transactions made in the safe.
    """

    type = models.CharField(choices=SafeTransactionTypeChoice.choices)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} | {self.amount} | {self.timestamp}"

    class Meta:
        indexes = [models.Index(fields=["type"])]


class Account(models.Model):
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="account",
        related_query_name="account",
    )
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    credit_limit = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    remaining_credit = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user}' Account"

    class Meta:
        indexes = [models.Index(fields=["user"])]


class AccountTransaction(models.Model):
    """
    Account Transaction Model
    This model is used to track transactions made by users.
    """

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="transactions",
        related_query_name="transactions",
    )
    type = models.CharField(choices=AccountTransactionTypeChoice.choices)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="account_transactions",
        related_query_name="account_transactions",
    )
    object_id = models.PositiveBigIntegerField(null=True, blank=True)
    related_object = GenericForeignKey("content_type", "object_id")
    at = models.DateTimeField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account} | {self.type} | {self.amount} | {self.at}"

    class Meta:
        indexes = [models.Index(fields=["account"]), models.Index(fields=["content_type", "object_id"])]
        ordering = ["-at"]


class PurchasePayment(models.Model):
    """
    Purchase Payment Model
    This model is used to track payments made by users for purchases.
    """

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="purchase_payments",
        related_query_name="purchase_payments",
    )
    method = models.CharField(choices=PaymentMethodChoice.choices)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    at = models.DateTimeField()
    remarks = models.TextField(default="", blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["user"])]
        ordering = ["-at"]

    @property
    def transaction_data(self):
        account, _ = Account.objects.get_or_create(user=self.user)
        return {
            "account": account,
            "type": AccountTransactionTypeChoice.PURCHASE_PAYMENT,
            "amount": self.amount,
            "content_type": ContentType.objects.get_for_model(self),
            "object_id": self.pk,
            "at": self.at,
        }


class SalePayment(models.Model):
    """
    Purchase Payment Model
    This model is used to track payments made by users for sellings.
    """

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="sale_payments",
        related_query_name="sale_payments",
    )
    method = models.CharField(choices=PaymentMethodChoice.choices)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    at = models.DateTimeField()
    remarks = models.TextField(default="", blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["user"])]
        ordering = ["-at"]

    @property
    def transaction_data(self):
        account, _ = Account.objects.get_or_create(user=self.user)
        return {
            "account": account,
            "type": AccountTransactionTypeChoice.SALE_PAYMENT,
            "amount": self.amount,
            "content_type": ContentType.objects.get_for_model(self),
            "object_id": self.pk,
            "at": self.at,
        }
