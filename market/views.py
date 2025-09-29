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
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from core.permissions import AllAuthenticatedUsers, SmartRolePermission
from accounts.choices import Role
from accounts.permissions import StaffRoleAuthentication, ManagerRoleAuthentication
from invoices.choices import (
    PurchaseInvoiceStatusChoice,
    SaleInvoiceStatusChoice, 
    PurchaseReturnInvoiceStatusChoice,
    SaleReturnInvoiceStatusChoice
)
from core.views.abstract_paginations import CustomPageNumberPagination, LargePageNumberPagination
from market.filters import ProductFilter, ProductCodeFilter
from market.models import Category, Company, PharmacyProductWishList, Product, ProductCode, StoreProductCodeUpload, Store
from market.serializers import (
    CategoryReadSerializer,
    CompanyReadSerializer,
    PharmacyProductWishListSerializer,
    ProductCodeReadSerializer,
    ProductCreateUpdateSerilizer,
    ProductReadSerializer,
    StoreProductCodeUploadSerializer,
    StoreProductCodeUploadCreateSerializer,
    BulkStoreProductCodeUploadSerializer,
    UploadProgressSerializer,
    StoreSerializer,
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
    permission_classes = [SmartRolePermission]
    required_roles = [Role.PHARMACY]
    serializer_class = CompanyReadSerializer
    ordering_fields = ["id", "name", "e_name", "last_updated_at"]
    ordering = ["-last_updated_at"]
    queryset = Company.objects.all()


class CategoryListAPIView(ListAPIView):
    """List all categories with pagination and filtering."""
    permission_classes = [SmartRolePermission]
    required_roles = [Role.PHARMACY]
    serializer_class = CategoryReadSerializer
    queryset = Category.objects.all()


class ProductListAPIView(ListAPIView):
    permission_classes = [AllAuthenticatedUsers]
    serializer_class = ProductReadSerializer
    pagination_class = CustomPageNumberPagination
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "e_name", "company__name", "effective_material"]
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

        # البحث اليدوي كبديل
        search_term = self.request.GET.get('search')
        if search_term:
            from django.db import models
            queryset = queryset.filter(
                models.Q(name__icontains=search_term) |
                models.Q(e_name__icontains=search_term) |
                models.Q(company__name__icontains=search_term) |
                models.Q(effective_material__icontains=search_term)
            )

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
    permission_classes = [SmartRolePermission]
    required_roles = [Role.PHARMACY]
    serializer_class = ProductReadSerializer
    pagination_class = CustomPageNumberPagination
    filterset_class = ProductFilter
    lookup_field = "pk"
    search_fields = ["name", "e_name"]
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
    permission_classes = [SmartRolePermission]
    required_roles = [Role.PHARMACY]
    serializer_class = ProductReadSerializer
    pagination_class = CustomPageNumberPagination
    filterset_class = ProductFilter
    search_fields = ["name", "e_name"]
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
    permission_classes = [SmartRolePermission]
    required_roles = [Role.PHARMACY]
    serializer_class = PharmacyProductWishListSerializer
    pagination_class = LargePageNumberPagination
    filterset_fields = ["product__name", "product__e_name"]
    search_fields = ["product__name", "product__e_name"]
    ordering_fields = ["id", "product__name", "product__e_name"]

    def get_queryset(self):
        return PharmacyProductWishList.objects.select_related("product").all()


class UserPharmacyProductWishListListAPIView(ListAPIView):
    permission_classes = [SmartRolePermission]
    required_roles = [Role.PHARMACY]
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
    permission_classes = [SmartRolePermission]
    required_roles = [Role.PHARMACY]
    serializer_class = PharmacyProductWishListSerializer
    queryset = PharmacyProductWishList.objects.none()




# API Views for Store Product Code Uploads
class StoreProductCodeUploadListAPIView(ListAPIView):
    """
    API view for listing store product code uploads
    """
    serializer_class = StoreProductCodeUploadSerializer
    permission_classes = [AllAuthenticatedUsers]
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        """Filter uploads based on user and query parameters"""
        queryset = StoreProductCodeUpload.objects.select_related('store', 'uploaded_by').order_by('-uploaded_at')
        
        # Filter by user if not staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(uploaded_by=self.request.user)
        
        # Apply filters from query parameters
        status = self.request.query_params.get('status')
        store_id = self.request.query_params.get('store')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        
        if date_from:
            queryset = queryset.filter(uploaded_at__date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(uploaded_at__date__lte=date_to)
        
        return queryset


class StoreProductCodeUploadCreateAPIView(CreateAPIView):
    """
    API view for creating store product code uploads
    """
    serializer_class = StoreProductCodeUploadCreateSerializer
    permission_classes = [AllAuthenticatedUsers]
    
    def perform_create(self, serializer):
        """Create upload and start processing"""
        upload = serializer.save()
        
        # Return the created upload with full details
        return upload


class StoreProductCodeUploadRetrieveAPIView(RetrieveAPIView):
    """
    API view for retrieving a specific store product code upload
    """
    serializer_class = StoreProductCodeUploadSerializer
    permission_classes = [AllAuthenticatedUsers]
    queryset = StoreProductCodeUpload.objects.select_related('store', 'uploaded_by')
    
    def get_queryset(self):
        """Filter based on user permissions"""
        queryset = super().get_queryset()
        
        # Filter by user if not staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(uploaded_by=self.request.user)
        
        return queryset


class BulkStoreProductCodeUploadCreateAPIView(CreateAPIView):
    """
    API view for bulk uploading store product codes
    """
    serializer_class = BulkStoreProductCodeUploadSerializer
    permission_classes = [AllAuthenticatedUsers]
    
    def create(self, request, *args, **kwargs):
        """Handle bulk upload creation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uploads = serializer.save()
        
        # Return list of created uploads
        upload_serializer = StoreProductCodeUploadSerializer(uploads, many=True, context={'request': request})
        
        return Response({
            'message': f'تم رفع {len(uploads)} ملف بنجاح',
            'uploads': upload_serializer.data
        }, status=201)


class StoreProductCodeUploadProgressAPIView(RetrieveAPIView):
    """
    API view for getting upload progress
    """
    serializer_class = UploadProgressSerializer
    permission_classes = [AllAuthenticatedUsers]
    queryset = StoreProductCodeUpload.objects.all()
    
    def get_queryset(self):
        """Filter based on user permissions"""
        queryset = super().get_queryset()
        
        # Filter by user if not staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(uploaded_by=self.request.user)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Return upload progress information"""
        upload = self.get_object()
        
        progress = 0
        if upload.status == 'completed':
            progress = 100
        elif upload.status == 'processing':
            progress = 50  # You can implement more sophisticated progress tracking
        elif upload.status == 'failed':
            progress = 0
        
        data = {
            'status': upload.status,
            'progress': progress,
            'total_rows': upload.total_rows,
            'successful_rows': upload.successful_rows,
            'failed_rows': upload.failed_rows,
            'success_rate': upload.success_rate,
            'error_log': upload.error_log or ''
        }
        
        serializer = self.get_serializer(data)
        return Response(serializer.data)


class StoreProductCodeUploadRetryAPIView(UpdateAPIView):
    """
    API view for retrying failed uploads
    """
    serializer_class = StoreProductCodeUploadSerializer
    permission_classes = [AllAuthenticatedUsers]
    queryset = StoreProductCodeUpload.objects.all()
    
    def get_queryset(self):
        """Filter based on user permissions"""
        queryset = super().get_queryset()
        
        # Filter by user if not staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(uploaded_by=self.request.user)
        
        return queryset
    
    def update(self, request, *args, **kwargs):
        """Retry upload processing"""
        upload = self.get_object()
        
        if upload.status not in ['failed', 'pending']:
            return Response(
                {'error': 'لا يمكن إعادة معالجة هذا الرفع'},
                status=400
            )
        
        try:
            # Reset upload status
            upload.status = 'pending'
            upload.error_log = ''
            upload.save()
            
            # Start processing again
            from .tasks import process_upload_file
            process_upload_file.delay(upload.id)
            
            serializer = self.get_serializer(upload)
            return Response({
                'message': 'تم بدء إعادة معالجة الملف',
                'upload': serializer.data
            })
            
        except Exception as e:
            return Response(
                {'error': f'حدث خطأ: {str(e)}'},
                status=500
            )


class StoreListAPIView(ListAPIView):
    """
    API view for listing stores
    """
    serializer_class = StoreSerializer
    permission_classes = [AllAuthenticatedUsers]
    queryset = Store.objects.all()


class StoreProductCodeUploadStatisticsAPIView(ListAPIView):
    """
    API view for getting upload statistics
    """
    permission_classes = [AllAuthenticatedUsers]
    
    def list(self, request, *args, **kwargs):
        """Return upload statistics"""
        queryset = StoreProductCodeUpload.objects.all()
        
        # Filter by user if not staff
        if not request.user.is_staff:
            queryset = queryset.filter(uploaded_by=request.user)
        
        # Apply filters
        status = request.query_params.get('status')
        store_id = request.query_params.get('store')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        
        if date_from:
            queryset = queryset.filter(uploaded_at__date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(uploaded_at__date__lte=date_to)
        
        # Calculate statistics
        total_uploads = queryset.count()
        completed_uploads = queryset.filter(status='completed').count()
        failed_uploads = queryset.filter(status='failed').count()
        pending_uploads = queryset.filter(status__in=['pending', 'processing']).count()
        
        # Calculate average success rate
        completed_with_stats = queryset.filter(status='completed', total_rows__gt=0)
        if completed_with_stats.exists():
            avg_success_rate = sum(upload.success_rate for upload in completed_with_stats) / completed_with_stats.count()
        else:
            avg_success_rate = 0
        
        return Response({
            'total_uploads': total_uploads,
            'completed_uploads': completed_uploads,
            'failed_uploads': failed_uploads,
            'pending_uploads': pending_uploads,
            'average_success_rate': round(avg_success_rate, 2)
        })
