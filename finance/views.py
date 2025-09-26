from decimal import Decimal
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, GenericAPIView
from django.db import models
from django.apps import apps
from accounts.permissions import *
from finance.choices import NEGATIVE_AFFECTING_TRANSACTIONS, POSTIVE_AFFECTING_TRANSACTIONS, SafeTransactionTypeChoice
from finance.filters import AccountTransactionFilter, PurchasePaymentFilter, SalePaymentFilter
from finance.models import Account, AccountTransaction, PurchasePayment, SafeTransaction, SalePayment
from finance.serializers import (
    AccountTransactionReadSerializer,
    AccountUpdateSerializer,
    PurchasePaymentCreateSerializer,
    PurchasePaymentReadSerializer,
    PurchasePaymentUpdateSerializer,
    SafeSerializer,
    SafeTransactionSerializer,
    SalePaymentCreateSerializer,
    SalePaymentReadSerializer,
    SalePaymentUpdateSerializer,
)
from finance.utils import delete_payment
from rest_framework.response import Response

get_model = apps.get_model


class AccountUpdateAPIView(UpdateAPIView):
    permission_classes = [ManagerRoleAuthentication, AreaManagerRoleAuthentication]
    serializer_class = AccountUpdateSerializer
    queryset = AccountTransaction.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = Account.objects.all()

        if user.is_superuser:
            return queryset

        user_role = user.role

        match user_role:
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__area_manager=user))
            case _r:
                queryset = queryset.none()

        return queryset


class AccountTransactionListAPIView(ListAPIView):
    permission_classes = [StaffRoleAuthentication]
    serializer_class = AccountTransactionReadSerializer
    filterset_class = AccountTransactionFilter
    oredering = ("-at",)

    def get_queryset(self):
        user = self.request.user

        queryset = AccountTransaction.objects.all()

        if user.is_superuser:
            return queryset

        user_role = user.role

        match user_role:
            case Role.SALES:
                queryset = queryset.filter(models.Q(account__user=user) | models.Q(account__user__profile__sales=user))
            case Role.DATA_ENTRY:
                queryset = queryset.filter(
                    models.Q(account__user=user) | models.Q(account__user__profile__data_entry=user)
                )
            case Role.DELIVERY:
                queryset = queryset.filter(
                    models.Q(account__user=user) | models.Q(account__user__profile__delivery=user)
                )
            case Role.MANAGER:
                queryset = queryset.filter(
                    models.Q(account__user=user) | models.Q(account__user__profile__manager=user)
                )
            case Role.AREA_MANAGER:
                queryset = queryset.filter(
                    models.Q(account__user=user) | models.Q(account__user__profile__area_manager=user)
                )

        return queryset


class PurchasePaymentListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PurchasePaymentReadSerializer
    filterset_class = PurchasePaymentFilter

    def get_queryset(self):
        user = self.request.user
        queryset = PurchasePayment.objects.all()

        if user.is_superuser:
            return queryset

        user_role = user.role

        match user_role:
            case Role.SALES:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales=user))
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__area_manager=user))
            case r:
                queryset = queryset.filter(models.Q(user=user))

        return queryset


class PurchasePaymentCreateView(CreateAPIView):
    permission_classes = [SalesRoleAuthentication, ManagerRoleAuthentication, AreaManagerRoleAuthentication]
    serializer_class = PurchasePaymentCreateSerializer
    queryset = PurchasePayment.objects.all()


class PurchasePaymentUpdateAPIView(UpdateAPIView):
    permission_classes = [SalesRoleAuthentication, ManagerRoleAuthentication, AreaManagerRoleAuthentication]
    serializer_class = PurchasePaymentUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = PurchasePayment.objects.select_related("user", "user__account").all()

        if user.is_superuser:
            return queryset

        user_role = user.role

        match user_role:
            case Role.SALES:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales=user))
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__area_manager=user))
            case _r:
                queryset = queryset.none()

        return queryset


class PurchasePaymentDestroyAPIView(DestroyAPIView):
    permission_classes = [SalesRoleAuthentication, ManagerRoleAuthentication, AreaManagerRoleAuthentication]

    def get_queryset(self):
        user = self.request.user
        queryset = PurchasePayment.objects.select_related("user", "user__account").all()

        if user.is_superuser:
            return queryset

        user_role = user.role

        match user_role:
            case Role.SALES:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales=user))
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__area_manager=user))
            case _r:
                queryset = queryset.none()

        return queryset

    def perform_destroy(self, instance):
        delete_payment(instance)


class SalePaymentListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SalePaymentReadSerializer
    filterset_class = SalePaymentFilter

    def get_queryset(self):
        user = self.request.user
        queryset = SalePayment.objects.all()

        if user.is_superuser:
            return queryset

        user_role = user.role

        match user_role:
            case Role.SALES:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales=user))
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__area_manager=user))
            case r:
                queryset = queryset.filter(models.Q(user=user))

        return queryset


class SalePaymentCreateView(CreateAPIView):
    permission_classes = [SalesRoleAuthentication, ManagerRoleAuthentication, AreaManagerRoleAuthentication]
    serializer_class = SalePaymentCreateSerializer
    queryset = SalePayment.objects.all()


class SalePaymentUpdateAPIView(UpdateAPIView):
    permission_classes = [SalesRoleAuthentication, ManagerRoleAuthentication, AreaManagerRoleAuthentication]
    serializer_class = SalePaymentUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = SalePayment.objects.select_related("user", "user__account").all()

        if user.is_superuser:
            return queryset

        user_role = user.role

        match user_role:
            case Role.SALES:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales=user))
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__area_manager=user))
            case _r:
                queryset = queryset.none()

        return queryset


class SalePaymentDestroyAPIView(DestroyAPIView):
    permission_classes = [SalesRoleAuthentication, ManagerRoleAuthentication, AreaManagerRoleAuthentication]

    def get_queryset(self):
        user = self.request.user
        queryset = SalePayment.objects.select_related("user", "user__account").all()

        if user.is_superuser:
            return queryset

        user_role = user.role

        match user_role:
            case Role.SALES:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales=user))
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__area_manager=user))
            case _r:
                queryset = queryset.none()

        return queryset

    def perform_destroy(self, instance):
        delete_payment(instance)


class SafeTransactionListAPIView(ListAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = SafeTransactionSerializer

    def get_queryset(self):
        queryset = SafeTransaction.objects.all()
        return queryset


class SafeTransactionCreateAPIView(CreateAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = SafeTransactionSerializer
    queryset = SafeTransaction.objects.all()


class SafeRetrieveAPIView(GenericAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = SafeSerializer

    def get_queryset(self):
        sale_payment_total_amount = SalePayment.objects.aggregate(total_amount=models.Sum("amount"))[
            "total_amount"
        ] or Decimal("0.00")

        purchase_payment_total_amount = PurchasePayment.objects.aggregate(total_amount=models.Sum("amount"))[
            "total_amount"
        ] or Decimal("0.00")

        safe_total_amount = (
            (
                SafeTransaction.objects.annotate(
                    signed_amount=models.Case(
                        models.When(type=SafeTransactionTypeChoice.WITHDRAWAL, then=models.F("amount") * -1),
                        default=models.F("amount"),
                    )
                ).aggregate(total_amount=models.Sum("signed_amount"))["total_amount"]
                or Decimal("0.00")
            )
            + sale_payment_total_amount
            - purchase_payment_total_amount
        )

        debt_total_amount = Account.objects.filter(balance__gte=0).aggregate(total_amount=models.Sum("balance"))[
            "total_amount"
        ] or Decimal("0.00")

        credit_total_amount = Account.objects.filter(balance__lt=0).aggregate(total_amount=models.Sum("balance") * -1)[
            "total_amount"
        ] or Decimal("0.00")

        inventory_total_amount = get_model("inventory", "InventoryItem").objects.aggregate(
            total_amount=models.Sum("purchase_sub_total")
        )["total_amount"] or Decimal("0.00")

        return {
            "safe_total_amount": safe_total_amount,
            "debt_total_amount": debt_total_amount,
            "credit_total_amount": credit_total_amount,
            "inventory_total_amount": inventory_total_amount,
            "total_amount": safe_total_amount + credit_total_amount + inventory_total_amount - debt_total_amount,
        }

    def get(self, request, *args, **kwargs):
        data = self.get_queryset()
        serializer = self.get_serializer(data)
        return Response(serializer.data)
