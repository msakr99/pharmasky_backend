from django.urls import path
from ads import views

app_name = "ads"

urlpatterns = [
    path(
        "",
        views.AdvertismentListAPIView.as_view(),
        name="advertisment-list-view",
    ),
]
