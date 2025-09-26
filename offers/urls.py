from django.urls import path
from offers import views

app_name = "offers"

urlpatterns = [
    path(
        "offers/",
        views.OffersListAPIView.as_view(),
        name="offers-list-view",
    ),
    path(
        "offers/create/",
        views.OfferCreateAPIView.as_view(),
        name="offers-create-view",
    ),
    path(
        "offers/<int:pk>/change/",
        views.OfferUpdateAPIView.as_view(),
        name="offers-update-view",
    ),
    path(
        "offers/<int:pk>/destroy/",
        views.OfferDestroyAPIView.as_view(),
        name="offers-delete-view",
    ),
    path(
        "max-offers/",
        views.MaxOfferListAPIView.as_view(),
        name="max-offers-list-view",
    ),
    path(
        "max-offers/excel/",
        views.OfferDownloadExcelAPIView.as_view(),
        name="max-offers-excel-list-view",
    ),
    path(
        "offers/upload/",
        views.OfferUploadAPIView.as_view(),
        name="offers-upload-view",
    ),
    path(
        "user/offers/",
        views.UserOfferListAPIView.as_view(),
        name="user-offers-list-view",
    ),
    path(
        "user/offers/create/",
        views.UserOfferCreateAPIView.as_view(),
        name="user-offers-create-view",
    ),
]
