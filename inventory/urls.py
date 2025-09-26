from django.urls import path
from inventory import views

app_name = "inventory"

urlpatterns = [
    path(
        "inventories/",
        views.InventoryListAPIView.as_view(),
        name="inventories-list-view",
    ),
    path(
        "inventories/create/",
        views.InventoryCreateAPIView.as_view(),
        name="inventories-create-view",
    ),
    path(
        "inventories/<int:pk>/",
        views.InventoryRetrieveAPIView.as_view(),
        name="inventories-object-view",
    ),
    path(
        "inventories/<int:pk>/change/",
        views.InventoryUpdateAPIView.as_view(),
        name="inventories-update-view",
    ),
    path(
        "inventory-items/",
        views.InventoryItemListAPIView.as_view(),
        name="inventory-items-list-view",
    ),
    path(
        "inventory-items/create/",
        views.InventoryItemCreateAPIView.as_view(),
        name="inventory-items-create-view",
    ),
    path(
        "inventory-items/<int:pk>/",
        views.InventoryItemRetrieveAPIView.as_view(),
        name="inventory-items-object-view",
    ),
    path(
        "inventory-items/<int:pk>/change/",
        views.InventoryItemUpdateAPIView.as_view(),
        name="inventory-items-update-view",
    ),
    path(
        "inventory-items/<int:pk>/change-inventory/",
        views.InventoryItemTransferAPIView.as_view(),
        name="inventory-items-inventory-update-view",
    ),
    path(
        "inventory-items/<int:pk>/destroy/",
        views.InventoryItemDestroyAPIView.as_view(),
        name="inventory-items-delete-view",
    ),
]
