from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveAPIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from profiles.models import Area, Complaint, Country, City, PaymentPeriod, UserProfile
from profiles.serializers import (
    AreaReadSerializer,
    CityReadSerializer,
    ComplaintCreateSerializer,
    CountryReadSerializer,
    PaymentPeriodReadSerializer,
    UserProfileCreateUpdateSerializer,
    ComplaintReadSerializer,
    UserProfileReadSerializer,
)
from accounts.permissions import *


class UserProfileListAPIView(ListAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication | StoreRoleAuthentication]
    serializer_class = UserProfileReadSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user__role", "category", "city", "city__country"]
    search_fields = ["user__name", "user__e_name", "user__username", "address", "key_person"]
    ordering_fields = ["user__name", "user__e_name", "category", "latest_invoice_date"]
    ordering = ["-latest_invoice_date"]

    def get_queryset(self):
        user = self.request.user
        queryset = UserProfile.objects.select_related(
            "user", "city", "city__country", "payment_period", 
            "data_entry", "sales", "manager", "area_manager", "delivery"
        ).all()

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(area_manager=user))
            case Role.SALES:
                queryset = queryset.filter(models.Q(user=user) | models.Q(sales=user))
            case Role.STORE:
                queryset = queryset.filter(user=user)
            case _r:
                queryset = queryset.none()

        return queryset


class StoreProfilesListAPIView(ListAPIView):
    """
    API View to get all profiles where user role is STORE
    """
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = UserProfileReadSerializer
    search_fields = ["user__name", "user__e_name", "user__username", "address", "key_person"]
    ordering_fields = ["user__name", "user__e_name", "category", "latest_invoice_date"]
    ordering = ["-latest_invoice_date"]

    def get_queryset(self):
        queryset = UserProfile.objects.select_related(
            "user", "city", "city__country", "payment_period", 
            "data_entry", "sales", "manager", "area_manager", "delivery"
        ).filter(user__role=Role.STORE)

        return queryset


class UserProfileRetrieveAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileReadSerializer

    def get_queryset(self):
        queryset = UserProfile.objects.select_related("city", "city__country", "payment_period").all()
        return queryset

    def get_object(self):
        try:
            obj = self.get_queryset().get(user=self.request.user)
            return obj
        except UserProfile.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj is None:
            return Response(
                {"detail": "User profile not found. Please create a profile first."},
                status=404
            )
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        kwargs.update({"exclude": ["data_entry", "sales", "delivery", "manager", "area_manager"]})
        return super().get_serializer(*args, **kwargs)


class UserProfileDetailAPIView(RetrieveAPIView):
    """
    API View to get a specific profile by ID
    """
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = UserProfileReadSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = UserProfile.objects.select_related(
            "user", "city", "city__country", "payment_period", 
            "data_entry", "sales", "manager", "area_manager", "delivery"
        ).all()

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(area_manager=user))
            case Role.SALES:
                queryset = queryset.filter(models.Q(user=user) | models.Q(sales=user))
            case _r:
                queryset = queryset.none()

        return queryset


class UserProfileCreateAPIView(CreateAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = UserProfileCreateUpdateSerializer
    queryset = UserProfile.objects.all()


class UserProfileUpdateAPIView(UpdateAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = UserProfileCreateUpdateSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = UserProfile.objects.select_related("payment_period").all()

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(area_manager=user))
            case Role.SALES:
                queryset = queryset.filter(models.Q(user=user) | models.Q(sales=user))
            case _r:
                queryset = queryset.none()

        return queryset

    def get_serializer(self, *args, **kwargs):
        kwargs.update({"exclude": ["user"]})
        return super().get_serializer(*args, **kwargs)


class AreaListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AreaReadSerializer
    queryset = Area.objects.all()


class CountryListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CountryReadSerializer
    queryset = Country.objects.all()


class CityListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CityReadSerializer
    queryset = City.objects.select_related("country").all()
    search_fields = ["name"]


class PaymentPeriodListAPIView(ListAPIView):
    permission_classes = [
        SalesRoleAuthentication
        | DataEntryRoleAuthentication
        | DeliveryRoleAuthentication
        | AreaManagerRoleAuthentication
        | ManagerRoleAuthentication
    ]
    serializer_class = PaymentPeriodReadSerializer
    queryset = PaymentPeriod.objects.all()
    search_fields = ["name"]


class ComplaintListAPIView(ListAPIView):
    permission_classes = [PharmacyRoleAuthentication | StoreRoleAuthentication | ManagerRoleAuthentication]
    serializer_class = ComplaintReadSerializer
    search_fields = ["subject", "body"]
    ordering_fields = ["subject", "mark_as_solved", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        queryset = Complaint.objects.select_related("user").all()

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case r if r in [Role.PHARMACY, Role.STORE]:
                queryset = queryset.filter(user=user)
            case _r:
                queryset = queryset.none()

        return queryset


class ComplaintCreateAPIView(CreateAPIView):
    permission_classes = [PharmacyRoleAuthentication | StoreRoleAuthentication]
    serializer_class = ComplaintCreateSerializer
    queryset = Complaint.objects.all()
