from django.contrib import admin
from core.admin.abstract_admin import DefaultBaseAdminItems
from profiles.models import Area, Country, City, PaymentPeriod, UserProfile


@admin.register(Area)
class AreaModelAdmin(DefaultBaseAdminItems):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Country)
class CountryModelAdmin(DefaultBaseAdminItems):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(City)
class CityModelAdmin(DefaultBaseAdminItems):
    list_display = ["name", "country"]
    search_fields = ["name", "country__name"]
    list_select_related = ["country"]
    autocomplete_fields = ["country"]


@admin.register(PaymentPeriod)
class PaymentPeriodModelAdmin(DefaultBaseAdminItems):
    list_display = ["name", "period_in_days", "addition_percentage"]
    search_fields = ["name"]
    list_filter = ["period_in_days", "addition_percentage"]


@admin.register(UserProfile)
class UserProfileModelAdmin(DefaultBaseAdminItems):
    list_display = [
        "user",
        "sales",
        "data_entry",
        "manager",
        "area_manager",
        "delivery",
        "profit_percentage",
        "payment_period",
        "latest_invoice_date",
        "order_by_phone",
        "company",
    ]
    date_hierarchy = "latest_invoice_date"
    search_fields = ["user__username", "user__name"]
    list_filter = ["order_by_phone", "company", "category", "city", "city__country"]
    list_select_related = ["user", "data_entry", "sales", "manager", "area_manager", "delivery", "city"]
    autocomplete_fields = ["user", "manager", "area_manager", "data_entry", "sales", "delivery", "city"]
