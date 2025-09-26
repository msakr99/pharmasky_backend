from django.urls import path
from shop import views

app_name = "shop"

urlpatterns = [
    path(
        "carts/<int:pk>/",
        views.CartRetrieveAPIView.as_view(),
        name="carts-object-view",
    ),
    path(
        "user/cart/",
        views.UserCartRetrieveAPIView.as_view(),
        name="user-cart-object-view",
    ),
    path(
        "user/cart/checkout/",
        views.UserCartCheckoutAPIView.as_view(),
        name="user-cart-checkout-view",
    ),
    path(
        "user/cart-items/create/",
        views.UserCartItemCreateAPIView.as_view(),
        name="user-cart-items-create-view",
    ),
    path(
        "user/cart-items/<int:pk>/change/",
        views.UserCartItemUpdateAPIView.as_view(),
        name="user-cart-items-update-view",
    ),
    path(
        "user/cart-items/<int:pk>/destroy/",
        views.UserCartItemDestroyAPIView.as_view(),
        name="user-cart-items-delete-view",
    ),
]
