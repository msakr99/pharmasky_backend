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
        "max-offers/pdf/",
        views.OfferDownloadPDFAPIView.as_view(),
        name="max-offers-pdf-list-view",
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
    
    # ==========================================
    # URLs خاصة بعروض الجملة (Wholesale Offers)
    # ==========================================
    path(
        "wholesale-offers/",
        views.WholesaleOffersListAPIView.as_view(),
        name="wholesale-offers-list-view",
    ),
    path(
        "max-wholesale-offers/",
        views.MaxWholesaleOfferListAPIView.as_view(),
        name="max-wholesale-offers-list-view",
    ),
    path(
        "wholesale-offers/create/",
        views.WholesaleOfferCreateAPIView.as_view(),
        name="wholesale-offers-create-view",
    ),
    path(
        "wholesale-offers/upload/",
        views.WholesaleOfferUploadAPIView.as_view(),
        name="wholesale-offers-upload-view",
    ),
    path(
        "wholesale-offers/<int:pk>/change/",
        views.WholesaleOfferUpdateAPIView.as_view(),
        name="wholesale-offers-update-view",
    ),
    path(
        "wholesale-offers/<int:pk>/destroy/",
        views.WholesaleOfferDestroyAPIView.as_view(),
        name="wholesale-offers-delete-view",
    ),
    path(
        "max-wholesale-offers/excel/",
        views.WholesaleOfferDownloadExcelAPIView.as_view(),
        name="max-wholesale-offers-excel-view",
    ),
]
