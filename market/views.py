"""Market views for PharmaSky application.

This module contains API views for managing products, companies, categories,
and related market functionality.
"""

from django.apps import apps
from django.utils import timezone
from django.views.generic import TemplateView
from django.db import models
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    get_object_or_404,
    DestroyAPIView,
    UpdateAPIView,
)

from accounts.permissions import (
    DataEntryRoleAuthentication,
    ManagerRoleAuthentication,
    PharmacyRoleAuthentication,
    SalesRoleAuthentication,
)
from core.views.abstract_paginations import CustomPageNumberPagination
from market.filters import ProductFilter, ProductCodeFilter
from market.models import Category, Company, PharmacyProductWishList, Product, ProductCode
from market.serializers import (
    CategoryReadSerializer,
    CompanyReadSerializer,
    PharmacyProductWishListSerializer,
    ProductCodeReadSerializer,
    ProductCreateUpdateSerilizer,
    ProductReadSerializer,
)

get_model = apps.get_model


class TemplateTest(TemplateView):
    template_name = "reports/seller_financial_account_report.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        d = {
            # "data": SellerFinancialAccount.objects.prefetch_related("transactions")
            # .filter(transactions__isnull=False)
            # .first(),
            "now": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        ctx.update(d)
        return ctx


class CompanyListAPIView(ListAPIView):
    """List all companies with pagination and filtering."""
    permission_classes = [PharmacyRoleAuthentication]
    serializer_class = CompanyReadSerializer
    ordering_fields = ["id", "name", "e_name", "last_updated_at"]
    ordering = ["-last_updated_at"]
    queryset = Company.objects.all()


class CategoryListAPIView(ListAPIView):
    """List all categories with pagination and filtering."""
    permission_classes = [PharmacyRoleAuthentication]
    serializer_class = CategoryReadSerializer
    queryset = Category.objects.all()


class ProductListAPIView(ListAPIView):
    permission_classes = [
        SalesRoleAuthentication | DataEntryRoleAuthentication | PharmacyRoleAuthentication | ManagerRoleAuthentication
    ]
    serializer_class = ProductReadSerializer
    pagination_class = CustomPageNumberPagination
    filterset_class = ProductFilter
    search_fields = ["^name", "^e_name"]
    ordering_fields = [
        "id",
        "name",
        "e_name",
        "public_price",
        "company__name",
        "category__name",
        "effective_material",
        "letter",
        "shape",
        "needed",
        "has_image",
        "max_offer_discount_percentage",
    ]
    ordering = ["name"]

    def get_queryset(self):
        user = self.request.user
        queryset = Product.objects.with_has_image().all()

        if user.role == Role.PHARMACY:
            try:
                profile = getattr(user, "profile")
                payment_period = getattr(profile, "payment_period")
                additional_fees_percentage = payment_period.addition_percentage
            except Exception:
                raise ValidationError({"detail": "Couldn't get pharmacy payment period."})
            else:
                actual_discount_precentage = models.F("selling_discount_percentage") - additional_fees_percentage
                actual_offer_price = models.F("public_price") * (1 - (actual_discount_precentage / 100))

            max_offer_subquery = (
                get_model("offers", "Offer")
                .objects.filter(is_max=True, remaining_amount__gt=0, product=models.OuterRef("pk"))
                .order_by("-id")
            )
            queryset = queryset.annotate(
                max_offer_id=models.Subquery(max_offer_subquery.only("id").values("id")[:1]),
                selling_discount_percentage=models.Subquery(
                    max_offer_subquery.only("selling_discount_percentage").values("selling_discount_percentage")[:1]
                ),
                max_offer_actual_discount_percentage=actual_discount_precentage,
                max_offer_actual_offer_price=actual_offer_price,
                max_offer_remaining_amount=models.Subquery(
                    max_offer_subquery.only("remaining_amount").values("remaining_amount")[:1]
                ),
            )

        return queryset


class ProductAlternativeListAPIView(ListAPIView):
    permission_classes = [PharmacyRoleAuthentication]
    serializer_class = ProductReadSerializer
    pagination_class = CustomPageNumberPagination
    filterset_class = ProductFilter
    lookup_field = "pk"
    search_fields = ["^name", "^e_name"]
    ordering_fields = [
        "id",
        "name",
        "e_name",
    ]
    ordering = ["name"]

    def get_object(self):
        queryset = Product.objects.prefetch_related("alternatives").all()
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_field]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        return obj

    def get_queryset(self):
        obj = self.get_object()
        return obj.alternatives.all()

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page,
            exclude=["category", "effective_material", "letter", "shape", "needed"],
            many=True,
        )
        return self.get_paginated_response(serializer.data)


class ProductInstanceListAPIView(ListAPIView):
    permission_classes = [PharmacyRoleAuthentication]
    serializer_class = ProductReadSerializer
    pagination_class = CustomPageNumberPagination
    filterset_class = ProductFilter
    search_fields = ["^name", "^e_name"]
    ordering_fields = ["id", "name", "e_name"]
    ordering = ["name"]

    def get_object(self):
        queryset = Product.objects.prefetch_related("instances").all()
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_field]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        return obj

    def get_queryset(self):
        obj = self.get_object()
        return obj.instances.all()

    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page,
            exclude=["category", "effective_material", "letter", "shape", "needed"],
            many=True,
        )
        return self.get_paginated_response(serializer.data)


class ProductCreateAPIView(CreateAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = ProductCreateUpdateSerilizer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        return self.perform_create(serializer)


class ProductRetrieveAPIView(RetrieveAPIView):
    permission_classes = [StaffRoleAuthentication]
    serializer_class = ProductReadSerializer

    def get_queryset(self):
        purchases_subquery = (
            get_model("invoices", "PurchaseInvoiceItem")
            .objects.filter(
                invoice__status=PurchaseInvoiceStatusChoice.CLOSED,
                product=models.OuterRef("pk"),
            )
            .values("product")
            .annotate(total_purchased=models.Sum("quantity"))
            .values("total_purchased")
        )

        sales_subquery = (
            get_model("invoices", "SaleInvoiceItem")
            .objects.filter(
                invoice__status=SaleInvoiceStatusChoice.CLOSED,
                product=models.OuterRef("pk"),
            )
            .values("product")
            .annotate(total_sold=models.Sum("quantity"))
            .values("total_sold")
        )

        purchases_returns_subquery = (
            get_model("invoices", "PurchaseReturnInvoiceItem")
            .objects.filter(
                invoice__status=PurchaseReturnInvoiceStatusChoice.CLOSED,
                purchase_invoice_item__product=models.OuterRef("pk"),
            )
            .values("purchase_invoice_item__product")
            .annotate(total_purchases_returned=models.Sum("quantity"))
            .values("total_purchases_returned")
        )

        sales_returns_subquery = (
            get_model("invoices", "SaleReturnInvoiceItem")
            .objects.filter(
                invoice__status=SaleReturnInvoiceStatusChoice.CLOSED,
                sale_invoice_item__product=models.OuterRef("pk"),
            )
            .values("sale_invoice_item__product")
            .annotate(total_sales_returned=models.Sum("quantity"))
            .values("total_sales_returned")
        )

        total_in_stock_subquery = (
            get_model("inventory", "InventoryItem")
            .objects.filter(
                product=models.OuterRef("pk"),
            )
            .values("product")
            .annotate(total_in_stock=models.Sum("remaining_quantity"))
            .values("total_in_stock")
        )

        queryset = Product.objects.annotate(
            total_purchases=models.Subquery(purchases_subquery, output_field=models.IntegerField()),
            total_purchases_returned=models.Subquery(purchases_returns_subquery, output_field=models.IntegerField()),
            total_sold=models.Subquery(sales_subquery, output_field=models.IntegerField()),
            total_sales_returned=models.Subquery(sales_returns_subquery, output_field=models.IntegerField()),
            total_in_stock=models.Subquery(total_in_stock_subquery, output_field=models.IntegerField()),
        )
        return queryset


class ProductUpdateAPIView(UpdateAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = ProductCreateUpdateSerilizer
    queryset = Product.objects.all()


class ProductCodeListAPIView(ListAPIView):
    permission_classes = [StaffRoleAuthentication]
    serializer_class = ProductCodeReadSerializer
    filterset_class = ProductCodeFilter
    search_fields = ["product__name", "product__e_name", "code", "product__id", "user__name"]
    ordering_fields = [
        "id",
        "user__name",
        "code",
        "product__id",
        "product__name",
        "product__e_name",
        "product__public_price",
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = ProductCode.objects.select_related("product", "user").all()

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales=user))
            case Role.DATA_ENTRY:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__data_entry=user))
            case Role.DELIVERY:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__delivery=user))
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__area_manager=user))
            case _r:
                queryset = queryset.none()
        return queryset


class PharmacyProductWishListListAPIView(ListAPIView):
    permission_classes = [PharmacyRoleAuthentication]
    serializer_class = PharmacyProductWishListSerializer
    pagination_class = LargePageNumberPagination
    filterset_fields = ["product__name", "product__e_name"]
    search_fields = ["product__name", "product__e_name"]
    ordering_fields = ["id", "product__name", "product__e_name"]

    def get_queryset(self):
        return PharmacyProductWishList.objects.select_related("product").all()


class UserPharmacyProductWishListListAPIView(ListAPIView):
    permission_classes = [PharmacyRoleAuthentication]
    serializer_class = PharmacyProductWishListSerializer
    search_fields = ["product__name", "product__e_name"]
    ordering_fields = ["id", "product__name", "product__e_name"]

    def get_queryset(self):
        user = self.request.user
        return PharmacyProductWishList.objects.filter(pharmacy=user).select_related("product").all()

    def get_serializer(self, *args, **kwargs):
        kwargs.update({"exclude": ["pharmacy_id", "pharmacy"]})
        return super().get_serializer(*args, **kwargs)


class UserPharmacyProductWishListCreateAPIView(CreateAPIView):
    permission_classes = [PharmacyRoleAuthentication]
    serializer_class = PharmacyProductWishListSerializer
    queryset = PharmacyProductWishList.objects.none()
