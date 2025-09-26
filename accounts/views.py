from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from accounts.choices import PaymentMethodChoice, Role
from accounts.serializers import (
    PharmacyCreateSerializer,
    UserFullReadSerializer,
    UserReadSerializer,
)
from accounts.filters import SimpleUserFilter
from accounts.permissions import *
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    GenericAPIView,
    get_object_or_404,
)
from core.views.abstract_paginations import CustomPageNumberPagination
from rest_framework.authtoken.views import ObtainAuthToken
from django.db.models import Prefetch, F, Sum
from django.apps import apps
from django.utils import timezone

from core.views.mixins import PDFFileMixin
from core.views.renderers import PDFRenderer
from django.utils.translation import activate

get_model = apps.get_model


class LoginAPIView(ObtainAuthToken):
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "role": user.role, "new_login": created})


class UserDataAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserReadSerializer

    def post(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class UserListAPIView(ListAPIView):
    permission_classes = [StaffRoleAuthentication]
    serializer_class = UserFullReadSerializer
    search_fields = ("name", "e_name", "username")
    ordering_fields = (
        "name",
        "e_name",
        "username",
        "profile__category",
        "profile__delivery__name",
        "profile__city__name",
        "profile__city__country__name",
        "financial_account__balance",
        "financial_account__credit_limit",
        "financial_account__remaining_credit_limit",
        "profile__orderbyphone",
        "profile__latest_invoice_date",
        "is_active",
        "role",
    )

    def get_queryset(self):
        user = self.request.user

        queryset = User.objects.exclude(is_superuser=True).select_related(
            "profile",
            "profile__sales",
            "profile__data_entry",
            "profile__area_manager",
            "profile__delivery",
            "profile__payment_period",
            "account",
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(profile__sales=user)
            case Role.MANAGER:
                queryset = queryset.filter(profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset


class UserRetrieveAPIView(RetrieveAPIView):
    permission_classes = [StaffRoleAuthentication]
    serializer_class = UserFullReadSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = User.objects.exclude(is_superuser=True).select_related(
            "profile",
            "profile__sales",
            "profile__data_entry",
            "profile__area_manager",
            "profile__delivery",
            "profile__payment_period",
            "account",
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(profile__sales=user)
            case Role.MANAGER:
                queryset = queryset.filter(profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset


class SimpleUserListAPIView(ListAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = UserReadSerializer
    pagination_class = CustomPageNumberPagination
    search_fields = ("name", "e_name", "username")
    ordering = ("name",)
    filterset_class = SimpleUserFilter

    def get_queryset(self):
        queryset = User.objects.all()
        return queryset

    def get_serializer(self, *args, **kwargs):
        kwargs.update({"fields": ["id", "name", "e_name", "username"]})
        return super().get_serializer(*args, **kwargs)


class PharmacyCreateAPIView(CreateAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = PharmacyCreateSerializer


class WhoAmIAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserReadSerializer

    def post(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)
