from decimal import Decimal
import logging
from accounts.permissions import *
from accounts.choices import Role
from drf_excel.mixins import XLSXFileMixin
from drf_excel.renderers import XLSXRenderer
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from offers.filters import OfferFilter
from offers.models import Offer
from offers.serializers import (
    OfferCreateSerializer,
    OfferUpdateSerializer,
    OfferExcelReadSerialzier,
    OfferPDFReadSerializer,
    OfferReadSerializer,
    OfferUploaderSerializer,
    UserOfferCreateSerializer,
)
from django.utils import timezone
from core.utils import get_excel_body, get_excel_header, get_excel_column_header
from core.views.mixins import PDFFileMixin
from core.views.renderers import PDFRenderer
from django.utils.translation import activate
from rest_framework.response import Response
from core.views.abstract_paginations import CustomPageNumberPagination, LargePageNumberPagination
from rest_framework.exceptions import ValidationError

from offers.utils import delete_offer

logger = logging.getLogger(__name__)


class OffersListAPIView(ListAPIView):
    permission_classes = [SalesRoleAuthentication | DataEntryRoleAuthentication | ManagerRoleAuthentication]
    serializer_class = OfferReadSerializer
    pagination_class = CustomPageNumberPagination
    filterset_class = OfferFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["product__name", "product__e_name"]
    ordering_fields = [
        "product__name",
        "product__e_name",
        "product__public_price",
        "purchase_discount_percentage",
        "purchase_price",
        "selling_discount_percentage",
        "selling_price",
        "user__name",
        "selling_price",
        "product__needed",
        "min_purchase",
    ]

    def get_queryset(self):
        queryset = Offer.objects.select_related("product_code", "product", "user")
        return queryset


class MaxOfferListAPIView(ListAPIView):
    permission_classes = [
        SalesRoleAuthentication | DataEntryRoleAuthentication | PharmacyRoleAuthentication | ManagerRoleAuthentication
    ]
    serializer_class = OfferReadSerializer
    pagination_class = CustomPageNumberPagination
    filterset_class = OfferFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = [
        "product__name",
        "product__e_name",
        "product__public_price",
        "selling_discount_percentage",
        "user__name",
        "selling_price",
        "product__needed",
        "min_purchase",
    ]

    def get_queryset(self):
        user = self.request.user
        search_term = self.request.query_params.get('search', '').strip()
        
        logger.info(f"[MaxOfferListAPIView] User: {user.username}, Search term: '{search_term}'")

        actual_discount_precentage = models.F("selling_discount_percentage") - Decimal("0.00")
        actual_offer_price = models.F("selling_price")

        if user.role == Role.PHARMACY:
            try:
                profile = getattr(user, "profile")
                payment_period = getattr(profile, "payment_period")
                additional_fees_percentage = payment_period.addition_percentage
            except Exception:
                raise ValidationError({"detail": "Couldn't get pharmacy payment period."})
            else:
                actual_discount_precentage = models.F("selling_discount_percentage") - additional_fees_percentage
                actual_offer_price = models.F("product__public_price") * (1 - (actual_discount_precentage / 100))

        queryset = (
            Offer.objects.filter(remaining_amount__gt=0, is_max=True)
            .select_related("product_code", "product", "user")
            .annotate(
                actual_discount_precentage=actual_discount_precentage,
                actual_offer_price=actual_offer_price,
            )
        )
        
        initial_count = queryset.count()
        logger.info(f"[MaxOfferListAPIView] Initial queryset count: {initial_count}")

        # Apply search filter manually
        if search_term:
            queryset = queryset.filter(
                models.Q(product__name__icontains=search_term) |
                models.Q(product__e_name__icontains=search_term)
            )
            final_count = queryset.count()
            logger.info(f"[MaxOfferListAPIView] After search filter count: {final_count}")

        return queryset


class OfferCreateAPIView(CreateAPIView):
    permission_classes = [SalesRoleAuthentication | DataEntryRoleAuthentication | ManagerRoleAuthentication | AdminRoleAuthentication]
    serializer_class = OfferCreateSerializer
    queryset = Offer.objects.none()


class OfferUploadAPIView(CreateAPIView):
    """
    API View for uploading offers via Excel file
    """
    permission_classes = [SalesRoleAuthentication | DataEntryRoleAuthentication | ManagerRoleAuthentication | AdminRoleAuthentication]
    serializer_class = OfferUploaderSerializer
    queryset = Offer.objects.none()

    def post(self, request, *args, **kwargs):
        """
        Handle Excel file upload for offers
        """
        try:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            
            # Process the uploaded offers
            offers = serializer.save()
            
            return Response({
                'message': f'تم رفع {len(offers)} عرض بنجاح',
                'count': len(offers),
                'offers': [offer.id for offer in offers]
            }, status=201)
            
        except Exception as e:
            return Response({
                'error': 'حدث خطأ أثناء رفع العروض',
                'details': str(e)
            }, status=400)


class OfferUpdateAPIView(UpdateAPIView):
    permission_classes = [SalesRoleAuthentication | DataEntryRoleAuthentication | ManagerRoleAuthentication]
    serializer_class = OfferUpdateSerializer
    queryset = Offer.objects.select_related("product_code", "product", "user").all()


class OfferDestroyAPIView(DestroyAPIView):
    permission_classes = [SalesRoleAuthentication | DataEntryRoleAuthentication | ManagerRoleAuthentication]
    serializer_class = OfferReadSerializer
    queryset = Offer.objects.select_related("product").all()

    def perform_destroy(self, instance):
        delete_offer(instance)


class OfferDownloadExcelAPIView(XLSXFileMixin, ListAPIView):
    permission_classes = [SalesRoleAuthentication | DataEntryRoleAuthentication | ManagerRoleAuthentication]
    serializer_class = OfferExcelReadSerialzier
    renderer_classes = [XLSXRenderer]
    filterset_class = OfferFilter
    pagination_class = None
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["product__name", "product__e_name"]
    ordering_fields = [
        "id",
        "product__name",
        "product__public_price",
        "discount_precentage",
        "user__name",
        "offer_price",
        "product__needed",
        "min_purchase",
    ]
    body = get_excel_body()

    def get_header(self):
        return get_excel_header(tab_name="Max Offers Report", header_title="Max Offers Report")

    def get_column_header(self):
        titles = ["Product code", "Product name", "Seller", "Price", "Discount %", "Actual Discount %", "Actual Price", "Payment Period"]
        return get_excel_column_header(titles=titles)

    def get_filename(self, request=None, *args, **kwargs):
        NOW = timezone.now().strftime("%d-%m-%Y-%H-%M-%S")
        return f"Pharmasky Max offers report - {NOW}.xlsx"

    def get_queryset(self):
        # Get payment_period from query params
        payment_period_id = self.request.query_params.get('payment_period', None)
        
        # Start building the queryset
        queryset = Offer.objects.select_related("product_code", "product", "user").filter(is_max=True)
        
        # Calculate actual discount and price if payment_period is provided
        if payment_period_id:
            try:
                from profiles.models import PaymentPeriod
                payment_period = PaymentPeriod.objects.get(id=payment_period_id)
                additional_fees_percentage = payment_period.addition_percentage
                
                queryset = queryset.annotate(
                    product_seller_code=models.F("product_code__code"),
                    product_name=models.F("product__name"),
                    seller_name=models.F("user__name"),
                    public_price=models.F("product__public_price"),
                    actual_discount_percentage=models.F("selling_discount_percentage") - additional_fees_percentage,
                    actual_offer_price=models.F("product__public_price") * (1 - ((models.F("selling_discount_percentage") - additional_fees_percentage) / 100)),
                    payment_period_name=models.Value(payment_period.name, output_field=models.CharField()),
                )
            except Exception:
                # If payment_period not found, proceed without it
                queryset = queryset.annotate(
                    product_seller_code=models.F("product_code__code"),
                    product_name=models.F("product__name"),
                    seller_name=models.F("user__name"),
                    public_price=models.F("product__public_price"),
                    actual_discount_percentage=models.F("selling_discount_percentage"),
                    actual_offer_price=models.F("selling_price"),
                    payment_period_name=models.Value("", output_field=models.CharField()),
                )
        else:
            # No payment period, use default values
            queryset = queryset.annotate(
                product_seller_code=models.F("product_code__code"),
                product_name=models.F("product__name"),
                seller_name=models.F("user__name"),
                public_price=models.F("product__public_price"),
                actual_discount_percentage=models.F("selling_discount_percentage"),
                actual_offer_price=models.F("selling_price"),
                payment_period_name=models.Value("", output_field=models.CharField()),
            )
        
        queryset = queryset.values(
            "product_seller_code",
            "product_name",
            "seller_name",
            "public_price",
            "selling_discount_percentage",
            "actual_discount_percentage",
            "actual_offer_price",
            "payment_period_name",
            "created_at",
        )
        
        return queryset


class OfferDownloadPDFAPIView(PDFFileMixin, ListAPIView):
    permission_classes = [SalesRoleAuthentication | DataEntryRoleAuthentication | ManagerRoleAuthentication]
    renderer_classes = [PDFRenderer]
    serializer_class = OfferPDFReadSerializer
    template_name = "market/pdf/store_offers.html"
    template_context = {"timestamp": timezone.now().strftime("%d-%m-%Y")}
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["product__name", "product__e_name"]

    def get_queryset(self):
        # Get payment_period from query params
        payment_period_id = self.request.query_params.get('payment_period', None)
        
        # Start building the queryset
        queryset = Offer.objects.select_related("product_code", "product", "user").filter(is_max=True)
        
        # Calculate actual discount and price if payment_period is provided
        if payment_period_id:
            try:
                from profiles.models import PaymentPeriod
                payment_period = PaymentPeriod.objects.get(id=payment_period_id)
                additional_fees_percentage = payment_period.addition_percentage
                
                queryset = queryset.annotate(
                    product_name=models.F("product__name"),
                    seller_name=models.F("user__name"),
                    public_price=models.F("product__public_price"),
                    actual_discount_percentage=models.F("selling_discount_percentage") - additional_fees_percentage,
                    actual_offer_price=models.F("product__public_price") * (1 - ((models.F("selling_discount_percentage") - additional_fees_percentage) / 100)),
                    payment_period_name=models.Value(payment_period.name, output_field=models.CharField()),
                )
            except Exception:
                # If payment_period not found, proceed without it
                queryset = queryset.annotate(
                    product_name=models.F("product__name"),
                    seller_name=models.F("user__name"),
                    public_price=models.F("product__public_price"),
                    actual_discount_percentage=models.F("selling_discount_percentage"),
                    actual_offer_price=models.F("selling_price"),
                    payment_period_name=models.Value("", output_field=models.CharField()),
                )
        else:
            # No payment period, use default values
            queryset = queryset.annotate(
                product_name=models.F("product__name"),
                seller_name=models.F("user__name"),
                public_price=models.F("product__public_price"),
                actual_discount_percentage=models.F("selling_discount_percentage"),
                actual_offer_price=models.F("selling_price"),
                payment_period_name=models.Value("", output_field=models.CharField()),
            )
        
        queryset = queryset.values(
            "product_name",
            "seller_name",
            "public_price",
            "selling_discount_percentage",
            "actual_discount_percentage",
            "actual_offer_price",
            "payment_period_name",
        )
        
        return queryset

    def get_filename(self, request=None, *args, **kwargs):
        NOW = timezone.now().strftime("%d-%m-%Y")
        return f"Pharmasky Max offers report - {NOW}.pdf"

    def get(self, request, *args, **kwargs):
        activate("ar")
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserOfferListAPIView(ListAPIView):
    permission_classes = [PharmacyRoleAuthentication]
    serializer_class = OfferReadSerializer
    filterset_class = OfferFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["product__name", "product__e_name"]
    ordering_fields = [
        "product__name",
        "product__e_name",
        "product__public_price",
        "selling_discount_percentage",
        "selling_price",
        "product__needed",
        "min_purchase",
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = Offer.objects.select_related("product").filter(user=user)
        return queryset

    def get_serializer(self, *args, **kwargs):
        kwargs.update({"exclude": ["user", "product_code"]})
        return super().get_serializer(*args, **kwargs)


class UserOfferCreateAPIView(CreateAPIView):
    permission_classes = [PharmacyRoleAuthentication]
    serializer_class = UserOfferCreateSerializer
    queryset = Offer.objects.none()
