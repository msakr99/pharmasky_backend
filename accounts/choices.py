from enum import Enum
from django.db import models
from django.utils.translation import gettext_lazy as _


class FinancialAccountTransactionEffect(Enum):
    ADD_BALANCE = "add_balance"
    ADD_INVOICE = "add_invoice"
    UPDATE_INVOICE = "update_invoice"
    DELETE_INVOICE = "delete_invoice"
    ADD_RETURN = "add_return"
    UPDATE_RETURN = "update_return"
    DELETE_RETURN = "delete_return"
    ADD_PAYMENT = "add_payment"
    UPDATE_PAYMENT = "update_payment"
    DELETE_PAYMENT = "delete_payment"
    ADD_REFUND = "add_refund"
    UPDATE_REFUND = "update_refund"
    DELETE_REFUND = "delete_refund"


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    PHARMACY = "PHARMACY", "Pharmacy"
    DELIVERY = "DELIVERY", "Delivery"
    STORE = "STORE", "Store"
    MANAGER = "MANAGER", "Manager"
    SALES = "SALES", "Sales"
    DATA_ENTRY = "DATA_ENTRY", "Data entry"
    AREA_MANAGER = "AREA_MANAGER", "Area manager"


class PaymentMethodChoice(models.TextChoices):
    INSTAPAY = "ip", _("Instapay")
    CASH = "c", _("Cash")
    WALLET = "w", _("Wallet")
    PRODUCT = "p", _("Products")


class AccountTransactionTypeChoice(models.TextChoices):
    INITIAL_BALANCE = "ib", _("Initial balance")
    INVOICE = "i", _("Invoice")
    RETURN = "r", _("Return")
    PAYMENT = "p", _("Payment")
    REFUND = "f", _("Refund")
