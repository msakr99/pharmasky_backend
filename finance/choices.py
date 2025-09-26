from django.db import models
from django.utils.translation import gettext_lazy as _


class SafeTransactionTypeChoice(models.TextChoices):
    DEPOSIT = "d", _("Deposit")
    WITHDRAWAL = "w", _("Withdrawal")


class PaymentMethodChoice(models.TextChoices):
    INSTAPAY = "ip", _("Instapay")
    CASH = "c", _("Cash")
    WALLET = "w", _("Wallet")
    PRODUCT = "p", _("Products")


class AccountTransactionTypeChoice(models.TextChoices):
    INITIAL_BALANCE = "ib", _("Initial balance")
    PURCHASE_INVOICE = "pi", _("Purchase Invoice")
    SALE_INVOICE = "si", _("Sale Invoice")  #
    PURCHASE_RETURN = "pr", _("Purchase Return")  #
    SALE_RETURN = "sr", _("Sale Return")
    PURCHASE_PAYMENT = "pp", _("Purchase Payment")  #
    SALE_PAYMENT = "sp", _("Sale Payment")
    REFUND = "f", _("Refund")


NEGATIVE_AFFECTING_TRANSACTIONS = [
    AccountTransactionTypeChoice.SALE_INVOICE,
    AccountTransactionTypeChoice.PURCHASE_RETURN,
    AccountTransactionTypeChoice.PURCHASE_PAYMENT,
]

POSTIVE_AFFECTING_TRANSACTIONS = [
    AccountTransactionTypeChoice.INITIAL_BALANCE,
    AccountTransactionTypeChoice.PURCHASE_INVOICE,
    AccountTransactionTypeChoice.SALE_RETURN,
    AccountTransactionTypeChoice.SALE_PAYMENT,
]
