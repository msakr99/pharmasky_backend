from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    get_object_or_404,
    GenericAPIView,
)
from accounts.permissions import *
from shop.models import Cart, CartItem
from shop.serializers import (
    CartCheckoutSerializer,
    CartItemCreateSerializer,
    CartItemReadSerializer,
    CartItemUpdateSerializer,
    CartReadSerializer,
)
from shop.utils import delete_cart_item
from rest_framework.response import Response
from rest_framework import status
from django.db import models


class CartRetrieveAPIView(RetrieveAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = CartReadSerializer
    lookup_field = "user__pk"
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        user = self.request.user

        queryset = Cart.objects.all().prefetch_related(
            models.Prefetch("items", queryset=CartItem.objects.select_related("product", "offer"))
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case _r:
                queryset = queryset.none()

        return queryset


class UserCartRetrieveAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartReadSerializer

    def get_object(self):
        user = self.request.user
        queryset = Cart.objects.all().prefetch_related(
            models.Prefetch("items", queryset=CartItem.objects.select_related("product", "offer"))
        )
        obj = get_object_or_404(queryset, user=user)
        return obj


class UserCartCheckoutAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartCheckoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCartItemCreateAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemCreateSerializer
    queryset = CartItem.objects.all()

    def get_serializer(self, *args, **kwargs):
        kwargs.update({"exclude": ["user"]})
        return super().get_serializer(*args, **kwargs)


class UserCartItemUpdateAPIView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = CartItem.objects.select_related("product").filter(cart__user=user, sold_out=False)
        return queryset


class UserCartItemDestroyAPIView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemReadSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = CartItem.objects.select_related("product").filter(cart__user=user)
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_cart_item(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
