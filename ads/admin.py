from django.contrib import admin
from core.admin.abstract_admin import DefaultBaseAdminItems

from ads.models import Advertisment


@admin.register(Advertisment)
class AdvertismentModelAdmin(DefaultBaseAdminItems):
    list_display = ("image", "redirect_type", "content_type", "object_id", "external_url", "created_at")
    list_filter = ("redirect_type", "created_at")
    list_select_related = ("content_type",)
    search_fields = ("external_url",)
    date_hierarchy = "created_at"
