from django.contrib import admin
from import_export.admin import ImportExportMixin


class DefaultBaseAdminItems(ImportExportMixin, admin.ModelAdmin):
    def __init__(self, model: type, admin_site: admin.AdminSite | None) -> None:
        super().__init__(model, admin_site)
        if self.search_fields is None:
            self.search_fields = ("id",)
        elif isinstance(self.search_fields, tuple):
            self.search_fields += ("id",)
        elif isinstance(self.search_fields, list):
            self.search_fields += ["id"]

    readonly_fields = ("id",)
