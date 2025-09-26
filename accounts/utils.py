from decimal import Decimal
from accounts.choices import AccountTransactionTypeChoice, FinancialAccountTransactionEffect
from accounts.models import User
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from rest_framework.exceptions import ValidationError

get_model = apps.get_model


def validate_user_role(user: User, role) -> bool:
    return bool(user.is_authenticated and (user.role == role or user.is_superuser))


def get_transaction_amount_sign(transaction_type: str):
    """
    Get the sign of the transaction amount based on the transaction type.
    :param transaction_type: The type of the transaction (e.g., 'invoice', 'payment', etc.)
    :return: 1 if the transaction is positive, -1 if negative
    """
    if transaction_type in [AccountTransactionTypeChoice.INVOICE, AccountTransactionTypeChoice.REFUND]:
        return 1
    elif transaction_type in [
        AccountTransactionTypeChoice.PAYMENT,
        AccountTransactionTypeChoice.RETURN,
        AccountTransactionTypeChoice.INITIAL_BALANCE,
    ]:
        return -1
    else:
        return 0


def create_pharmacy_account_transaction(account, type, value, ct, obj_id, at=None):
    if at is None:
        at = timezone.now()
    return get_model("accounts", "PharmacyFinancialAccountTransaction").objects.create(
        pharmacy_financial_account=account,
        transaction_type=type,
        transaction_value=value,
        content_type=ct,
        object_id=obj_id,
        transaction_at=at,
    )


def update_pharmacy_account_transaction(ct, obj_id, type, value):
    try:
        transaction = get_model("accounts", "PharmacyFinancialAccountTransaction").objects.get(
            content_type=ct, object_id=obj_id, transaction_type=type
        )
    except ObjectDoesNotExist:
        raise ValidationError({"detail": "Pharmacy Account Transaction not found."})
    else:
        old_value = transaction.transaction_value
        transaction.transaction_value = value
        transaction.save()
        return old_value, transaction


def delete_pharmacy_account_transaction(ct, obj_id, type):
    try:
        transaction = get_model("accounts", "PharmacyFinancialAccountTransaction").objects.get(
            content_type=ct, object_id=obj_id, transaction_type=type
        )
    except ObjectDoesNotExist:
        raise ValidationError({"detail": "Pharmacy Account Transaction not found."})
    else:
        transaction.delete()
        return None


def update_pharmacy_account(account, value):
    account.balance += value
    account.remaining_credit_limit = account.credit_limit - account.balance
    account.save()
    return account


def affect_pharmacy_account(effect, pharmacy, **kwargs):
    account = getattr(pharmacy, "pharmacy_financial_account", None)

    if account is None:
        account = get_model("accounts", "PharmacyFinancialAccount").objects.create(
            pharmacy=pharmacy,
            balance=Decimal("00.00"),
            credit_limit=Decimal("00.00"),
            remaining_credit_limit=Decimal("00.00"),
        )

    transaction = None

    match effect:
        case FinancialAccountTransactionEffect.ADD_INVOICE:
            pharmacy_invoice = kwargs.get("pharmacy_invoice", None)

            if pharmacy_invoice is None:
                raise ImproperlyConfigured("Couldn't Add transaction, Pharmacy invoice is not provided.")

            total_price = pharmacy_invoice.total_price
            ct = ContentType.objects.get_for_model(pharmacy_invoice)
            transaction = create_pharmacy_account_transaction(
                account,
                AccountTransactionTypeChoice.INVOICE,
                total_price,
                ct,
                pharmacy_invoice.pk,
                pharmacy_invoice.created_at,
            )
            account = update_pharmacy_account(account, total_price)

        case FinancialAccountTransactionEffect.UPDATE_INVOICE:
            pharmacy_invoice = kwargs.get("pharmacy_invoice", None)

            if pharmacy_invoice is None:
                raise ImproperlyConfigured("Couldn't update transaction, Pharmacy invoice is not provided.")

            ct = ContentType.objects.get_for_model(pharmacy_invoice)
            total_price = pharmacy_invoice.total_price
            old_price, transaction = update_pharmacy_account_transaction(
                ct, pharmacy_invoice.pk, AccountTransactionTypeChoice.INVOICE, total_price
            )
            account = update_pharmacy_account(account, total_price - old_price)

        case FinancialAccountTransactionEffect.DELETE_INVOICE:
            pharmacy_invoice = kwargs.get("pharmacy_invoice", None)

            if pharmacy_invoice is None:
                raise ImproperlyConfigured("Couldn't delete transaction, Pharmacy invoice is not provided.")

            ct = ContentType.objects.get_for_model(pharmacy_invoice)
            total_price = pharmacy_invoice.total_price
            transaction = delete_pharmacy_account_transaction(
                ct, pharmacy_invoice.pk, AccountTransactionTypeChoice.INVOICE
            )
            account = update_pharmacy_account(account, -1 * total_price)

        case FinancialAccountTransactionEffect.ADD_RETURN:
            pharamcy_return = kwargs.get("pharamcy_return", None)

            if pharamcy_return is None:
                raise ImproperlyConfigured("Couldn't Add transaction, Return is not provided.")

            total_price = pharamcy_return.total_price
            ct = ContentType.objects.get_for_model(pharamcy_return)
            transaction = create_pharmacy_account_transaction(
                account,
                AccountTransactionTypeChoice.RETURN,
                total_price,
                ct,
                pharamcy_return.pk,
                pharamcy_return.created_at,
            )
            account = update_pharmacy_account(account, -1 * total_price)

        case FinancialAccountTransactionEffect.UPDATE_RETURN:
            pharamcy_return = kwargs.get("pharamcy_return", None)

            if pharamcy_return is None:
                raise ImproperlyConfigured("Couldn't update transaction, Return is not provided.")

            ct = ContentType.objects.get_for_model(pharamcy_return)
            total_price = pharamcy_return.total_price
            old_price, transaction = update_pharmacy_account_transaction(
                ct, pharamcy_return.pk, AccountTransactionTypeChoice.RETURN, total_price
            )
            account = update_pharmacy_account(account, total_price - old_price)

        case FinancialAccountTransactionEffect.DELETE_RETURN:
            pharamcy_return = kwargs.get("pharamcy_return", None)

            if pharamcy_return is None:
                raise ImproperlyConfigured("Couldn't delete transaction, Return is not provided.")

            ct = ContentType.objects.get_for_model(pharamcy_return)
            total_price = pharamcy_return.total_price
            transaction = delete_pharmacy_account_transaction(
                ct, pharamcy_return.pk, AccountTransactionTypeChoice.RETURN
            )
            account = update_pharmacy_account(account, -1 * total_price)

        case FinancialAccountTransactionEffect.ADD_PAYMENT:
            payment = kwargs.get("payment", None)

            if payment is None:
                raise ImproperlyConfigured("Couldn't Add transaction, Payment is not provided.")

            total_price = payment.payment_value
            ct = ContentType.objects.get_for_model(payment)
            transaction = create_pharmacy_account_transaction(
                account,
                AccountTransactionTypeChoice.PAYMENT,
                total_price,
                ct,
                payment.pk,
                payment.created_at,
            )
            account = update_pharmacy_account(account, -1 * total_price)

        case FinancialAccountTransactionEffect.UPDATE_PAYMENT:
            payment = kwargs.get("payment", None)

            if payment is None:
                raise ImproperlyConfigured("Couldn't update transaction, Payment is not provided.")

            ct = ContentType.objects.get_for_model(payment)
            total_price = payment.payment_value
            old_price, transaction = update_pharmacy_account_transaction(
                ct, payment.pk, AccountTransactionTypeChoice.PAYMENT, total_price
            )
            account = update_pharmacy_account(account, old_price - total_price)

        case FinancialAccountTransactionEffect.DELETE_PAYMENT:
            payment = kwargs.get("payment", None)

            if payment is None:
                raise ImproperlyConfigured("Couldn't delete transaction, Payment is not provided.")

            ct = ContentType.objects.get_for_model(payment)
            total_price = payment.payment_value
            transaction = delete_pharmacy_account_transaction(ct, payment.pk, AccountTransactionTypeChoice.PAYMENT)
            account = update_pharmacy_account(account, total_price)

        case FinancialAccountTransactionEffect.ADD_REFUND:
            # Add refund logic
            pass
        case FinancialAccountTransactionEffect.UPDATE_REFUND:
            # Update refund logic
            pass
        case FinancialAccountTransactionEffect.DELETE_REFUND:
            # Delete refund logic
            pass

    return transaction, account


def create_seller_account_transaction(account, type, value, ct, obj_id, at=None):
    if at is None:
        at = timezone.now()
    return get_model("accounts", "SellerFinancialAccountTransaction").objects.create(
        seller_financial_account=account,
        transaction_type=type,
        transaction_value=value,
        content_type=ct,
        object_id=obj_id,
        transaction_at=at,
    )


def update_seller_account_transaction(ct, obj_id, type, value):
    try:
        transaction = get_model("accounts", "SellerFinancialAccountTransaction").objects.get(
            content_type=ct, object_id=obj_id, transaction_type=type
        )
    except ObjectDoesNotExist:
        raise ValidationError({"detail": "Seller Account Transaction not found."})
    else:
        old_value = transaction.transaction_value
        transaction.transaction_value = value
        transaction.save()
        return old_value, transaction


def delete_seller_account_transaction(ct, obj_id, type):
    try:
        transaction = get_model("accounts", "SellerFinancialAccountTransaction").objects.get(
            content_type=ct, object_id=obj_id, transaction_type=type
        )
    except ObjectDoesNotExist:
        raise ValidationError({"detail": "Seller Account Transaction not found."})
    else:
        transaction.delete()
        return None


def update_seller_account(account, value):
    account.balance += value
    account.save()
    return account


def affect_seller_account(effect, seller, **kwargs):
    account = getattr(seller, "seller_financial_account", None)

    if account is None:
        account = get_model("accounts", "SellerFinancialAccount").objects.create(
            seller=seller, balance=Decimal("00.00")
        )

    transaction = None

    match effect:
        case FinancialAccountTransactionEffect.ADD_INVOICE:
            seller_invoice = kwargs.get("seller_invoice", None)

            if seller_invoice is None:
                raise ImproperlyConfigured("Couldn't Add transaction, Seller invoice is not provided.")

            total_price = seller_invoice.total_price
            ct = ContentType.objects.get_for_model(seller_invoice)
            transaction = create_seller_account_transaction(
                account,
                AccountTransactionTypeChoice.INVOICE,
                total_price,
                ct,
                seller_invoice.pk,
                seller_invoice.created_at,
            )
            account = update_seller_account(account, -1 * total_price)

        case FinancialAccountTransactionEffect.UPDATE_INVOICE:
            seller_invoice = kwargs.get("seller_invoice", None)

            if seller_invoice is None:
                raise ImproperlyConfigured("Couldn't update transaction, Seller invoice is not provided.")

            ct = ContentType.objects.get_for_model(seller_invoice)
            total_price = seller_invoice.total_price
            old_price, transaction = update_seller_account_transaction(
                ct, seller_invoice.pk, AccountTransactionTypeChoice.INVOICE, total_price
            )
            account = update_seller_account(account, old_price - total_price)

        case FinancialAccountTransactionEffect.DELETE_INVOICE:
            seller_invoice = kwargs.get("seller_invoice", None)

            if seller_invoice is None:
                raise ImproperlyConfigured("Couldn't delete transaction, Seller invoice is not provided.")

            ct = ContentType.objects.get_for_model(seller_invoice)
            total_price = seller_invoice.total_price
            transaction = delete_seller_account_transaction(
                ct, seller_invoice.pk, AccountTransactionTypeChoice.INVOICE
            )
            account = update_seller_account(account, total_price)

        case FinancialAccountTransactionEffect.ADD_RETURN:
            pharamcy_return = kwargs.get("pharamcy_return", None)

            if pharamcy_return is None:
                raise ImproperlyConfigured("Couldn't Add transaction, Return is not provided.")

            total_price = pharamcy_return.total_price
            ct = ContentType.objects.get_for_model(pharamcy_return)
            transaction = create_seller_account_transaction(
                account,
                AccountTransactionTypeChoice.RETURN,
                total_price,
                ct,
                pharamcy_return.pk,
                pharamcy_return.created_at,
            )
            account = update_seller_account(account, total_price)

        case FinancialAccountTransactionEffect.UPDATE_RETURN:
            pharamcy_return = kwargs.get("pharamcy_return", None)

            if pharamcy_return is None:
                raise ImproperlyConfigured("Couldn't update transaction, Return is not provided.")

            ct = ContentType.objects.get_for_model(pharamcy_return)
            total_price = pharamcy_return.total_price
            old_price, transaction = update_seller_account_transaction(
                ct, pharamcy_return.pk, AccountTransactionTypeChoice.RETURN, total_price
            )
            account = update_seller_account(account, total_price - old_price)

        case FinancialAccountTransactionEffect.DELETE_RETURN:
            pharamcy_return = kwargs.get("pharamcy_return", None)

            if pharamcy_return is None:
                raise ImproperlyConfigured("Couldn't delete transaction, Return is not provided.")

            ct = ContentType.objects.get_for_model(pharamcy_return)
            total_price = pharamcy_return.total_price
            transaction = delete_seller_account_transaction(
                ct, pharamcy_return.pk, AccountTransactionTypeChoice.RETURN
            )
            account = update_seller_account(account, total_price)

        case FinancialAccountTransactionEffect.ADD_PAYMENT:
            payment = kwargs.get("payment", None)

            if payment is None:
                raise ImproperlyConfigured("Couldn't Add transaction, Payment is not provided.")

            total_price = payment.payment_value
            ct = ContentType.objects.get_for_model(payment)
            transaction = create_seller_account_transaction(
                account,
                AccountTransactionTypeChoice.PAYMENT,
                total_price,
                ct,
                payment.pk,
                payment.created_at,
            )
            account = update_seller_account(account, total_price)

        case FinancialAccountTransactionEffect.UPDATE_PAYMENT:
            payment = kwargs.get("payment", None)

            if payment is None:
                raise ImproperlyConfigured("Couldn't update transaction, Payment is not provided.")

            ct = ContentType.objects.get_for_model(payment)
            total_price = payment.payment_value
            old_price, transaction = update_seller_account_transaction(
                ct, payment.pk, AccountTransactionTypeChoice.PAYMENT, total_price
            )
            account = update_seller_account(account, total_price - old_price)

        case FinancialAccountTransactionEffect.DELETE_PAYMENT:
            payment = kwargs.get("payment", None)

            if payment is None:
                raise ImproperlyConfigured("Couldn't delete transaction, Payment is not provided.")

            ct = ContentType.objects.get_for_model(payment)
            total_price = payment.payment_value
            transaction = delete_seller_account_transaction(ct, payment.pk, AccountTransactionTypeChoice.PAYMENT)
            account = update_seller_account(account, -1 * total_price)

        case FinancialAccountTransactionEffect.ADD_REFUND:
            # Add refund logic
            pass
        case FinancialAccountTransactionEffect.UPDATE_REFUND:
            # Update refund logic
            pass
        case FinancialAccountTransactionEffect.DELETE_REFUND:
            # Delete refund logic
            pass

    return transaction, account
