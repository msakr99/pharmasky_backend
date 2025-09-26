from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from push_notifications.api.rest_framework import GCMDeviceAuthorizedViewSet

admin.site.site_header = "Pharmasky"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
    path("accounts/", include("accounts.urls")),
    path("market/", include("market.urls")),
    path("finance/", include("finance.urls")),
    path("ads/", include("ads.urls")),
    path("offers/", include("offers.urls")),
    path("invoices/", include("invoices.urls")),
    path("shop/", include("shop.urls")),
    path("inventory/", include("inventory.urls")),
    path("profiles/", include("profiles.urls")),
    path(
        "push-notifications/devices/fcm/register/",
        GCMDeviceAuthorizedViewSet.as_view({"post": "create"}),
        name="gcm-device-create",
    ),
    path(
        "push-notifications/devices/fcm/unregister/",
        GCMDeviceAuthorizedViewSet.as_view({"delete": "destroy"}),
        name="gcm-device-delete",
    ),
]


urlpatterns += [re_path(r"^rosetta/", include("rosetta.urls"))]

urlpatterns += [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
