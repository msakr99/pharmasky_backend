from django.contrib import admin
from accounts import models
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportMixin
from django.utils.translation import gettext_lazy as _
from accounts.forms import BaseUserCreationForm, UserChangeForm

from django.apps import apps

get_model = apps.get_model


@admin.register(models.DataEntry)
@admin.register(models.Manager)
@admin.register(models.Sales)
@admin.register(models.Store)
@admin.register(models.Pharmacy)
@admin.register(models.User)
@admin.register(models.AreaManager)
@admin.register(models.Delivery)
class UserModelAdmin(ImportExportMixin, UserAdmin):
    @admin.action(description="Activate selected users")
    def activate_users(modeladmin, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Deactivate selected users")
    def deactivate_users(modeladmin, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Create carts")
    def create_carts(modeladmin, request, queryset):
        for item in queryset:
            get_model("shop", "Cart").objects.get_or_create(user=item)

    @admin.action(description="Create finance accounts")
    def create_accounts(modeladmin, request, queryset):
        for item in queryset:
            get_model("finance", "Account").objects.get_or_create(user=item)

    list_display = ("username", "name", "role", "is_active")
    list_filter = ("role", "is_active", "is_superuser", "is_staff")
    search_fields = ("name", "username")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "name",
                    "e_name",
                    "role",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "name",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    add_form = BaseUserCreationForm
    form = UserChangeForm
    list_filter = ("role", "is_active", "is_superuser", "is_staff")
    actions = [activate_users, deactivate_users, create_carts, create_accounts]
