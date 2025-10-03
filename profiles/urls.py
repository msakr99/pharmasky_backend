from django.urls import path
from profiles import views

app_name = "profiles"

urlpatterns = [
    path(
        "user-profiles/",
        views.UserProfileListAPIView.as_view(),
        name="user-profiles-list-view",
    ),
    path(
        "store-profiles/",
        views.StoreProfilesListAPIView.as_view(),
        name="store-profiles-list-view",
    ),
    path(
        "user-profiles/create/",
        views.UserProfileCreateAPIView.as_view(),
        name="user-profiles-create-view",
    ),
    path(
        "user-profiles/<int:pk>/",
        views.UserProfileDetailAPIView.as_view(),
        name="user-profiles-detail-view",
    ),
    path(
        "user-profiles/<int:pk>/change/",
        views.UserProfileUpdateAPIView.as_view(),
        name="user-profiles-update-view",
    ),
    path(
        "areas/",
        views.AreaListAPIView.as_view(),
        name="areas-list-view",
    ),
    path(
        "countries/",
        views.CountryListAPIView.as_view(),
        name="countries-list-view",
    ),
    path(
        "cities/",
        views.CityListAPIView.as_view(),
        name="cities-list-view",
    ),
    path(
        "payment-periods/",
        views.PaymentPeriodListAPIView.as_view(),
        name="payment-periods-list-view",
    ),
    path(
        "complaints/",
        views.ComplaintListAPIView.as_view(),
        name="complaints-list-view",
    ),
    path(
        "complaints/create/",
        views.ComplaintCreateAPIView.as_view(),
        name="complaints-create-view",
    ),
    path(
        "user-profile/",
        views.UserProfileRetrieveAPIView.as_view(),
        name="user-profile-object-view",
    ),
]
