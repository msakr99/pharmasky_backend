from django.urls import path, include
from accounts import views, filter_views
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

app_name = "accounts"

urlpatterns = [
    path(
        "login/",
        views.LoginAPIView.as_view(),
        name="login-view",
    ),
    path(
        "users/",
        views.UserListAPIView.as_view(),
        name="users-list-view",
    ),
    path(
        "users/<int:pk>/",
        views.UserRetrieveAPIView.as_view(),
        name="users-object-view",
    ),
    path(
        "simple-users/",
        views.SimpleUserListAPIView.as_view(),
        name="simple-users-list-view",
    ),
    path(
        "register/pharmacy/",
        views.PharmacyCreateAPIView.as_view(),
        name="register-pharmacy-view",
    ),
    path(
        "whoami/",
        views.WhoAmIAPIView.as_view(),
        name="whoami-api-view",
    ),
]


filter_urlpatterns = []

urlpatterns += filter_urlpatterns
