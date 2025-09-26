from django.apps import apps
from django.db import models

from finance.choices import (
    NEGATIVE_AFFECTING_TRANSACTIONS,
    POSTIVE_AFFECTING_TRANSACTIONS,
)

get_model = apps.get_model


def get_arithmatic_operation(transaction):
    type = transaction.type

    if type in POSTIVE_AFFECTING_TRANSACTIONS:
        return "add"
    elif type in NEGATIVE_AFFECTING_TRANSACTIONS:
        return "subtract"


def affect_account(account, operation, transaction, old_amount=None):
    arethmatic_operation = get_arithmatic_operation(transaction)

    if operation == "add":
        if arethmatic_operation == "add":
            account.balance += transaction.amount
        else:
            account.balance -= transaction.amount

    elif operation == "update":
        if old_amount is not None:
            if arethmatic_operation == "add":
                account.balance += transaction.amount - old_amount
            else:
                account.balance += old_amount - transaction.amount

    elif operation == "remove":
        if arethmatic_operation == "add":
            account.balance -= transaction.amount
        else:
            account.balance += transaction.amount

    if account.credit_limit is not None:
        account.remaining_credit = account.credit_limit + account.balance
    else:
        account.remaining_credit = None

    account.save()
    return account


def update_account(account, data):
    data.pop("user", None)
    data.pop("balance", None)
    data.pop("remaining_credit", None)

    credit_limit = data.get("credit_limit", None)

    if credit_limit is not None:
        if account.balance is not None:
            account.remaining_credit = credit_limit + account.balance
        else:
            account.remaining_credit = credit_limit
    else:
        account.remaining_credit = None

    for key, value in data.items():
        setattr(account, key, value)

    account.save()

    return account


def get_transaction(instance: models.Model):
    model_name = instance._meta.model_name
    AccountTransaction = get_model("finance", "AccountTransaction")
    try:
        transaction = AccountTransaction.objects.select_related("account").get(
            content_type__model=model_name, object_id=instance.pk
        )
    except AccountTransaction.DoesNotExist:
        return None

    return transaction


def create_transaction(data, update_account=True):
    AccountTransaction = get_model("finance", "AccountTransaction")
    transaction = AccountTransaction.objects.create(**data)

    if update_account:
        account = transaction.account
        affect_account(account, "add", transaction)

    return transaction


def update_transaction(transaction, amount, update_account=True):
    old_amount = transaction.amount

    transaction.amount = amount
    transaction.save()

    if update_account:
        account = transaction.account
        affect_account(account, "update", transaction, old_amount)

    return transaction


def delete_trasaction(transaction, update_account=True):
    if update_account:
        account = transaction.account
        affect_account(account, "remove", transaction)

    transaction.delete()


def create_puchase_payment(data, update_account=True):
    PurchasePayment = get_model("finance", "PurchasePayment")
    payment = PurchasePayment.objects.create(**data)

    if update_account:
        create_transaction(payment.transaction_data)

    return payment


def create_sale_payment(data, update_account=True):
    SalePayment = get_model("finance", "SalePayment")
    payment = SalePayment.objects.create(**data)

    if update_account:
        create_transaction(payment.transaction_data)

    return payment


def update_payment(payment, data, update_account=True):
    data.pop("user", None)
    data.pop("timestamp", None)

    amount = data.get("amount", None)
    old_amount = None
    needs_update = False

    if amount is not None:
        old_amount = payment.amount
        needs_update = amount != old_amount

    for key, value in data.items():
        setattr(payment, key, value)

    payment.save()

    if update_account and needs_update:
        transaction = get_transaction(payment)

        if transaction is not None:
            update_transaction(transaction, amount)

    return payment


def delete_payment(payment, update_account=True):
    if update_account:
        transaction = get_transaction(payment)

        if transaction is not None:
            delete_trasaction(transaction)

    payment.delete()
