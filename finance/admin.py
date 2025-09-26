from django.contrib import admin
from core.admin.abstract_admin import DefaultBaseAdminItems
from finance.models import Account, AccountTransaction, PurchasePayment, SalePayment


@admin.register(Account)
class AccountModelAdmin(DefaultBaseAdminItems):
    list_display = ["user", "balance", "credit_limit", "remaining_credit"]
    search_fields = ["user__username", "user__name"]
    list_filter = ["user__is_active", "user__role"]
    autocomplete_fields = ["user"]
    list_select_related = ["user"]


@admin.register(AccountTransaction)
class AccountTransactionModelAdmin(DefaultBaseAdminItems):
    list_display = ["account", "type", "amount", "at", "timestamp"]
    search_fields = ["account__user__username", "account__user__name"]
    list_filter = ["type", "account__user__is_active", "account__user__role"]
    autocomplete_fields = ["account"]
    list_select_related = ["account"]
    date_hierarchy = "at"


@admin.register(PurchasePayment)
class PurchasePaymentModelAdmin(DefaultBaseAdminItems):
    list_display = ["user", "amount", "method", "at", "timestamp"]
    search_fields = ["user__username", "user__name"]
    list_filter = ["method", "user__is_active", "user__role"]
    autocomplete_fields = ["user"]
    list_select_related = ["user"]
    date_hierarchy = "at"


@admin.register(SalePayment)
class SalePaymentModelAdmin(DefaultBaseAdminItems):
    list_display = ["user", "amount", "method", "at", "timestamp"]
    search_fields = ["user__username", "user__name"]
    list_filter = ["method", "user__is_active", "user__role"]
    autocomplete_fields = ["user"]
    list_select_related = ["user"]
    date_hierarchy = "at"
