from django.contrib import admin
from core.admin.abstract_admin import DefaultBaseAdminItems
from finance.models import Account, AccountTransaction, PurchasePayment, SalePayment, Expense


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


@admin.register(Expense)
class ExpenseModelAdmin(DefaultBaseAdminItems):
    list_display = ["category", "type", "amount", "recipient", "expense_date", "payment_method"]
    search_fields = ["description", "recipient"]
    list_filter = ["type", "category", "payment_method", "expense_date"]
    date_hierarchy = "expense_date"
    fieldsets = (
        ("معلومات أساسية", {
            "fields": ("type", "category", "amount", "payment_method")
        }),
        ("التفاصيل", {
            "fields": ("description", "recipient", "expense_date")
        }),
    )
