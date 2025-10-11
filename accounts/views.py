from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.choices import Role
from accounts.serializers import (
    CustomAuthTokenSerializer,
    PharmacyCreateSerializer,
    UserFullReadSerializer,
    UserReadSerializer,
)
from accounts.filters import SimpleUserFilter
from accounts.permissions import (
    StaffRoleAuthentication,
    SalesRoleAuthentication,
    ManagerRoleAuthentication,
    AreaManagerRoleAuthentication,
)
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    GenericAPIView,
)
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from core.views.abstract_paginations import CustomPageNumberPagination
from rest_framework.authtoken.views import ObtainAuthToken
from accounts.models import User
from django.apps import apps

get_model = apps.get_model


class BaseUserQuerysetMixin:
    """Mixin to handle common user queryset logic"""
    
    def get_base_user_queryset(self):
        """Get base queryset with common select_related optimizations"""
        return User.objects.exclude(is_superuser=True).select_related(
            "profile",
            "profile__sales",
            "profile__data_entry",
            "profile__area_manager",
            "profile__delivery",
            "profile__payment_period",
            "account",
        )
    
    def filter_queryset_by_user_role(self, queryset, user):
        """Filter queryset based on user role"""
        if user.is_superuser:
            return queryset
        
        match user.role:
            case Role.SALES:
                return queryset.filter(profile__sales=user)
            case Role.MANAGER:
                return queryset.filter(profile__manager=user)
            case _:
                return queryset.none()


class LoginAPIView(ObtainAuthToken):
    """
    Login API endpoint that accepts username and password and returns auth token
    """
    serializer_class = CustomAuthTokenSerializer
    
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


class UserListAPIView(BaseUserQuerysetMixin, ListAPIView):
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
        base_queryset = self.get_base_user_queryset()
        return self.filter_queryset_by_user_role(base_queryset, user)


class UserRetrieveAPIView(BaseUserQuerysetMixin, RetrieveAPIView):
    permission_classes = [StaffRoleAuthentication]
    serializer_class = UserFullReadSerializer

    def get_queryset(self):
        user = self.request.user
        base_queryset = self.get_base_user_queryset()
        return self.filter_queryset_by_user_role(base_queryset, user)


class SimpleUserListAPIView(ListAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = UserReadSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
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
