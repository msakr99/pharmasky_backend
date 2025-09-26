from django.contrib import admin
from core.admin.abstract_admin import DefaultBaseAdminItems

from ads.models import Advertisment


@admin.register(Advertisment)
class AdvertismentModelAdmin(DefaultBaseAdminItems):
    list_display = ("image", "redirect_type", "content_type", "object_id", "external_url")
    list_filter = ("redirect_type",)
    list_select_related = ("content_type",)
