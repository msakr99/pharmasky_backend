from operator import inv
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
    get_object_or_404,
)
from accounts.permissions import *
from core.views.abstract_api_views import BulkUpdateAPIView
from core.views.mixins import PDFFileMixin
from core.views.renderers import PDFRenderer
from invoices.choices import (
    PurchaseInvoiceStatusChoice,
    PurchaseReturnInvoiceStatusChoice,
    SaleInvoiceStatusChoice,
    SaleReturnInvoiceStatusChoice,
)
from invoices.filters import (
    PurchaseInvoiceFilter,
    PurchaseInvoiceItemFilter,
    PurchaseReturnInvoiceItemFilter,
    SaleInvoiceFilter,
    SaleInvoiceItemFilter,
    SaleReturnInvoiceFilter,
    SaleReturnInvoiceItemFilter,
)
from invoices.models import (
    PurchaseInvoice,
    PurchaseInvoiceDeletedItem,
    PurchaseInvoiceItem,
    PurchaseReturnInvoice,
    PurchaseReturnInvoiceItem,
    SaleInvoice,
    SaleInvoiceDeletedItem,
    SaleInvoiceItem,
    SaleReturnInvoice,
    SaleReturnInvoiceItem,
)
from invoices.serializers import (
    PurchaseInvoiceCreateSerializer,
    PurchaseInvoiceItemCreateSerializer,
    PurchaseInvoiceItemReadSerializer,
    PurchaseInvoiceItemStateUpdateSerializer,
    PurchaseInvoiceReadSerializer,
    PurchaseInvoiceStateUpdateSerializer,
    PurchaseReturnInvoiceCreateSerializer,
    PurchaseReturnInvoiceItemCreateSerializer,
    PurchaseReturnInvoiceItemReadSerializer,
    PurchaseReturnInvoiceItemUpdateSerializer,
    PurchaseReturnInvoiceReadSerializer,
    PurchaseReturnInvoiceStateUpdateSerializer,
    SaleInvoiceCreateSerializer,
    SaleInvoiceItemCreateSerializer,
    SaleInvoiceItemReadSerializer,
    SaleInvoiceItemStateUpdateSerializer,
    SaleInvoiceItemUpdateSerializer,
    SaleInvoicePDFSerializer,
    SaleInvoiceStateUpdateSerializer,
    SaleInvoiceReadSerializer,
    SaleReturnInvoiceCreateSerializer,
    SaleReturnInvoiceItemCreateSerializer,
    SaleReturnInvoiceItemReadSerializer,
    SaleReturnInvoiceItemUpdateSerializer,
    SaleReturnInvoiceReadSerializer,
    SaleReturnInvoiceStateUpdateSerializer,
)
from invoices.utils import (
    delete_purchase_invoice_item,
    delete_purchase_return_invoice_item,
    delete_sale_invoice_item,
    delete_sale_return_invoice_item,
)
from rest_framework.response import Response
from rest_framework import status
from django.db import models
from django.utils.translation import activate
from django.db import transaction


class PurchaseInvoiceListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PurchaseInvoiceReadSerializer
    search_fields = ["user__username", "supplier_invoice_number"]
    ordering_fields = ["created_at", "total_price"]
    filterset_class = PurchaseInvoiceFilter

    def get_queryset(self):
        user = self.request.user
        queryset = PurchaseInvoice.objects.select_related("user").all()

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.DATA_ENTRY:
                queryset = queryset.filter(user__profile__data_entry=user)
            case Role.DELIVERY:
                queryset = queryset.filter(user__profile__delivery=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case r if r in [Role.STORE, Role.PHARMACY]:
                queryset = queryset.filter(user=user)
            case _r:
                queryset = queryset.none()

        return queryset

    def get_serializer(self, *args, **kwargs):
        kwargs.update({"exclude": ["items", "deleted_items"]})
        return super().get_serializer(*args, **kwargs)


class PurchaseInvoiceCreateAPIView(CreateAPIView):
    permission_classes = [
        SalesRoleAuthentication
        | ManagerRoleAuthentication
        | AreaManagerRoleAuthentication
        | DataEntryRoleAuthentication
    ]
    serializer_class = PurchaseInvoiceCreateSerializer
    queryset = PurchaseInvoice.objects.all()


class PurchaseInvoiceRetrieveAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PurchaseInvoiceReadSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = (
            PurchaseInvoice.objects.select_related("user", "user__profile", "user__profile__payment_period")
            .prefetch_related(
                models.Prefetch("items", queryset=PurchaseInvoiceItem.objects.select_related("product", "offer")),
                models.Prefetch(
                    "deleted_items", queryset=PurchaseInvoiceDeletedItem.objects.select_related("product", "offer")
                ),
            )
            .all()
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.DATA_ENTRY:
                queryset = queryset.filter(user__profile__data_entry=user)
            case Role.DELIVERY:
                queryset = queryset.filter(user__profile__delivery=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case r if r in [Role.STORE, Role.PHARMACY]:
                queryset = queryset.filter(user=user)
            case _r:
                queryset = queryset.none()

        return queryset


class PurchaseInvoiceStateUpdateAPIView(UpdateAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = PurchaseInvoiceStateUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = PurchaseInvoice.objects.select_related("user").all()

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset


class PurchaseInvoiceItemListAPIView(ListAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = PurchaseInvoiceItemReadSerializer
    search_fields = ["product__name", "product__e_name"]
    filterset_class = PurchaseInvoiceItemFilter

    def get_queryset(self):
        user = self.request.user
        queryset = PurchaseInvoiceItem.objects.select_related("product").all()

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(invoice__user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(invoice__user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(invoice__user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset

    def get(self, request, *args, **kwargs):
        kwargs.update({"fields": ["id", "product"]})
        return super().get(request, *args, **kwargs)


class PurchaseInvoiceItemCreateAPIView(CreateAPIView):
    permission_classes = [
        SalesRoleAuthentication
        | ManagerRoleAuthentication
        | AreaManagerRoleAuthentication
        | DataEntryRoleAuthentication
    ]
    serializer_class = PurchaseInvoiceItemCreateSerializer
    queryset = PurchaseInvoiceItem.objects.all()


class PurchaseInvoiceItemStateUpdateAPIView(UpdateAPIView):
    permission_classes = [
        SalesRoleAuthentication
        | ManagerRoleAuthentication
        | AreaManagerRoleAuthentication
        | DataEntryRoleAuthentication
    ]
    serializer_class = PurchaseInvoiceItemStateUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = PurchaseInvoiceItem.objects.select_related(
            "product", "offer", "sale_invoice_item", "sale_invoice_item__invoice"
        ).exclude(invoice__status=PurchaseInvoiceStatusChoice.CLOSED)

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.DATA_ENTRY:
                queryset = queryset.filter(user__profile__data_entry=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset

    def get_serializer(self, *args, **kwargs):
        kwargs.update({"exclude": ["id"]})
        return super().get_serializer(*args, **kwargs)


class PurchaseInvoiceItemBulkStateUpdateAPIView(BulkUpdateAPIView):
    permission_classes = [
        SalesRoleAuthentication
        | ManagerRoleAuthentication
        | AreaManagerRoleAuthentication
        | DataEntryRoleAuthentication
    ]
    serializer_class = PurchaseInvoiceItemStateUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = PurchaseInvoiceItem.objects.select_related(
            "product", "offer", "sale_invoice_item", "sale_invoice_item__invoice"
        ).exclude(invoice__status=PurchaseInvoiceStatusChoice.CLOSED)

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.DATA_ENTRY:
                queryset = queryset.filter(user__profile__data_entry=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset


class PurchaseInvoiceItemDestroyAPIView(DestroyAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]

    def get_queryset(self):
        user = self.request.user
        queryset = PurchaseInvoiceItem.objects.select_related(
            "invoice", "invoice__user", "invoice__user__account"
        ).exclude(invoice__status=PurchaseInvoiceStatusChoice.CLOSED)

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(invoice__user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(invoice__user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(invoice__user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        delete_purchase_invoice_item(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PurchaseReturnInvoiceListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PurchaseReturnInvoiceReadSerializer
    search_fields = ["user__username"]
    ordering_fields = ["created_at", "total_price"]

    def get_queryset(self):
        user = self.request.user
        queryset = PurchaseReturnInvoice.objects.select_related("user").all()

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.DATA_ENTRY:
                queryset = queryset.filter(user__profile__data_entry=user)
            case Role.DELIVERY:
                queryset = queryset.filter(user__profile__delivery=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case r if r in [Role.STORE, Role.PHARMACY]:
                queryset = queryset.filter(user=user)
            case _r:
                queryset = queryset.none()

        return queryset

    def get_serializer(self, *args, **kwargs):
        kwargs.update({"exclude": ["items"]})
        return super().get_serializer(*args, **kwargs)


class PurchaseReturnInvoiceCreateAPIView(CreateAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = PurchaseReturnInvoiceCreateSerializer
    queryset = PurchaseReturnInvoice.objects.all()


class PurchaseReturnInvoiceRetrieveAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PurchaseReturnInvoiceReadSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = (
            PurchaseReturnInvoice.objects.select_related("user", "user__profile")
            .prefetch_related(
                models.Prefetch(
                    "items",
                    queryset=PurchaseReturnInvoiceItem.objects.select_related(
                        "purchase_invoice_item", "purchase_invoice_item__invoice", "purchase_invoice_item__product"
                    ),
                )
            )
            .all()
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.DATA_ENTRY:
                queryset = queryset.filter(user__profile__data_entry=user)
            case Role.DELIVERY:
                queryset = queryset.filter(user__profile__delivery=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case r if r in [Role.STORE, Role.PHARMACY]:
                queryset = queryset.filter(user=user)
            case _r:
                queryset = queryset.none()

        return queryset


class PurchaseReturnInvoiceStateUpdateAPIView(UpdateAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = PurchaseReturnInvoiceStateUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = (
            PurchaseReturnInvoice.objects.select_related("user", "user__account")
            .prefetch_related(
                models.Prefetch(
                    "items",
                    queryset=PurchaseReturnInvoiceItem.objects.select_related(
                        "purchase_invoice_item", "purchase_invoice_item__product"
                    ),
                )
            )
            .exclude(status=PurchaseReturnInvoiceStatusChoice.CLOSED)
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset


class PurchaseReturnInvoiceItemListAPIView(ListAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = PurchaseReturnInvoiceItemReadSerializer
    search_fields = ["purchase_invoice_item__product__name", "purchase_invoice_item__product__e_name"]
    filterset_class = PurchaseReturnInvoiceItemFilter

    def get_queryset(self):
        user = self.request.user
        queryset = PurchaseReturnInvoiceItem.objects.select_related("purchase_invoice_item", "invoice").all()

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(invoice__user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(invoice__user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(invoice__user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset


class PurchaseReturnInvoiceItemCreateAPIView(CreateAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = PurchaseReturnInvoiceItemCreateSerializer
    queryset = PurchaseReturnInvoiceItem.objects.all()


class PurchaseReturnInvoiceItemUpdateAPIView(UpdateAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = PurchaseReturnInvoiceItemUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = PurchaseReturnInvoiceItem.objects.select_related("purchase_invoice_item", "invoice").exclude(
            invoice__status=PurchaseReturnInvoiceStatusChoice.CLOSED
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(invoice__user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(invoice__user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(invoice__user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset


class PurchaseReturnInvoiceItemDestroyAPIView(DestroyAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]

    def get_queryset(self):
        user = self.request.user
        queryset = PurchaseReturnInvoiceItem.objects.select_related("invoice", "purchase_invoice_item").exclude(
            invoice__status=PurchaseReturnInvoiceStatusChoice.CLOSED
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(invoice__user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(invoice__user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(invoice__user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset

    def perform_destroy(self, instance):
        with transaction.atomic():
            delete_purchase_return_invoice_item(instance)


class SaleInvoiceListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SaleInvoiceReadSerializer
    search_fields = ["user__username", "user__name"]
    filterset_class = SaleInvoiceFilter

    def get_queryset(self):
        user = self.request.user
        queryset = SaleInvoice.objects.select_related(
            "user", "user__profile", "user__profile__payment_period", "seller"
        ).prefetch_related(
            models.Prefetch(
                "items", 
                queryset=SaleInvoiceItem.objects.select_related("product")
            )
        ).all()

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.DATA_ENTRY:
                queryset = queryset.filter(user__profile__data_entry=user)
            case Role.DELIVERY:
                queryset = queryset.filter(user__profile__delivery=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case r if r in [Role.STORE, Role.PHARMACY]:
                queryset = queryset.filter(user=user)
            case _r:
                queryset = queryset.none()

        return queryset

    def get_serializer(self, *args, **kwargs):
        kwargs.update({"exclude": ["items", "deleted_items"]})
        return super().get_serializer(*args, **kwargs)


class SaleInvoiceCreateAPIView(CreateAPIView):
    permission_classes = [
        SalesRoleAuthentication 
        | ManagerRoleAuthentication 
        | AreaManagerRoleAuthentication 
        | PharmacyRoleAuthentication 
        | StoreRoleAuthentication
    ]
    serializer_class = SaleInvoiceCreateSerializer
    queryset = SaleInvoice.objects.all()
    
    def create(self, request, *args, **kwargs):
        from rest_framework.exceptions import ValidationError as DRFValidationError
        import traceback
        
        try:
            # Validation: If user is PHARMACY or STORE, they can only create invoices for themselves
            user = request.user
            user_id_in_request = request.data.get('user')
            
            if user.role in [Role.PHARMACY, Role.STORE]:
                if user_id_in_request and int(user_id_in_request) != user.id:
                    return Response({
                        "error": "الصيدليات والمخازن يمكنها فقط إنشاء فواتير لأنفسها / Pharmacies and stores can only create invoices for themselves",
                        "detail": f"يجب أن يكون user = {user.id}"
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Force user to be the current user
                request.data['user'] = user.id
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except DRFValidationError as e:
            # Re-raise DRF validation errors (will be 400)
            raise
        except Exception as e:
            # Catch any other errors and return detailed information
            return Response({
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            }, status=status.HTTP_400_BAD_REQUEST)


class SaleInvoiceRetrieveAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SaleInvoiceReadSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = (
            SaleInvoice.objects.select_related("user", "user__profile", "user__profile__payment_period", "seller")
            .prefetch_related(
                models.Prefetch("items", queryset=SaleInvoiceItem.objects.select_related("product", "offer")),
                models.Prefetch(
                    "deleted_items", queryset=SaleInvoiceDeletedItem.objects.select_related("product", "offer")
                ),
            )
            .all()
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.DATA_ENTRY:
                queryset = queryset.filter(user__profile__data_entry=user)
            case Role.DELIVERY:
                queryset = queryset.filter(user__profile__delivery=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case r if r in [Role.STORE, Role.PHARMACY]:
                queryset = queryset.filter(user=user)
            case _r:
                queryset = queryset.none()

        return queryset


class SaleInvoiceDownloadAPIView(PDFFileMixin, RetrieveAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication]
    renderer_classes = [PDFRenderer]
    serializer_class = SaleInvoicePDFSerializer
    template_name = "invoices/sale_invoice.html"
    template_context = {}

    def get_queryset(self):
        user = self.request.user

        queryset = SaleInvoice.objects.annotate(
            seller_name=models.F("seller__name"),
            user_name=models.F("user__name"),
            user_mobile_number=models.F("user__username"),
            delivery_name=models.F("user__profile__delivery__name"),
            balance=models.F("user__account__balance"),
            prev_balance=models.F("balance") - models.F("total_price"),
        ).values(
            "id",
            "seller_name",
            "user_name",
            "user_mobile_number",
            "delivery_name",
            "balance",
            "prev_balance",
            "created_at",
            "total_price",
            "items_count",
            "total_quantity",
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(sales=user)
            case Role.MANAGER:
                queryset = queryset
            case _r:
                queryset = queryset.none()

        return queryset

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        items = (
            SaleInvoiceItem.objects.select_related("product")
            .annotate(
                quantity_discount=models.F("quantity")
                * models.F("selling_discount_percentage")
                * models.F("product__public_price"),
                quantity_price=models.F("quantity") * models.F("product__public_price"),
            )
            .filter(invoice_id=self.kwargs.get(self.lookup_field))
        )
        aggregates = items.aggregate(models.Sum("quantity_discount"), models.Sum("quantity_price"))
        total_public_price = aggregates["quantity_price__sum"] or 0
        total_discount = aggregates["quantity_discount__sum"] or 0
        
        # Calculate average discount safely
        if total_public_price > 0:
            average_discount = total_discount / total_public_price
        else:
            average_discount = 0

        ctx.update(
            {
                "items": items,
                "total_public_price": total_public_price,
                "average_discount_percentage": average_discount,
            }
        )

        return ctx

    def get_filename(self, request=None, *args, **kwargs):
        from datetime import datetime
        
        # Get the invoice to access customer name and date
        invoice_id = self.kwargs.get(self.lookup_field)
        try:
            invoice = SaleInvoice.objects.select_related('user').get(id=invoice_id)
            customer_name = invoice.user.name
            invoice_date = invoice.created_at.strftime('%Y-%m-%d')
            
            # Clean customer name for filename (remove invalid characters)
            import re
            clean_name = re.sub(r'[<>:"/\\|?*]', '', customer_name)
            clean_name = clean_name.strip()[:50]  # Limit length
            
            filename = f"فاتورة_{clean_name}_{invoice_date}.pdf"
            return filename
        except:
            # Fallback to invoice number if something goes wrong
            return f"Invoice_{invoice_id}.pdf"

    def get(self, request, *args, **kwargs):
        activate("ar")
        return super().get(request, *args, **kwargs)


class SaleInvoiceCheckCloseabilityAPIView(RetrieveAPIView):
    """
    Check if invoice can be closed and return detailed information
    """
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = SaleInvoiceReadSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = SaleInvoice.objects.select_related("user", "seller").prefetch_related("items__product").all()

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        from inventory.models import InventoryItem
        from inventory.utils import get_or_create_main_inventory
        from django.db.models import Sum
        from invoices.choices import SaleInvoiceItemStatusChoice
        
        try:
            invoice = self.get_object()
            
            result = {
                "invoice_id": invoice.id,
                "current_status": invoice.status,
                "can_close": True,
                "issues": []
            }
            
            # Check items status
            pending_items = invoice.items.select_related('product').exclude(
                status=SaleInvoiceItemStatusChoice.RECEIVED
            )
            
            if pending_items.exists():
                result["can_close"] = False
                result["issues"].append({
                    "type": "pending_items",
                    "message": "Not all items are in Received status",
                    "details": [
                        {
                            "item_id": item.id,
                            "product_name": item.product.name,
                            "current_status": item.status,
                            "required_status": "received"
                        }
                        for item in pending_items
                    ]
                })
            
            # Check inventory
            inventory = get_or_create_main_inventory()
            inventory_issues = []
            
            for item in invoice.items.select_related('product').all():
                available_quantity = InventoryItem.objects.filter(
                    inventory=inventory,
                    product=item.product
                ).aggregate(total=Sum('remaining_quantity'))['total'] or 0
                
                if available_quantity < item.quantity:
                    inventory_issues.append({
                        "product_id": item.product.id,
                        "product_name": item.product.name,
                        "required": item.quantity,
                        "available": available_quantity,
                        "shortage": item.quantity - available_quantity
                    })
            
            if inventory_issues:
                result["can_close"] = False
                result["issues"].append({
                    "type": "insufficient_inventory",
                    "message": "Not enough inventory available",
                    "details": inventory_issues
                })
            
            return Response(result)
            
        except Exception as e:
            # Return detailed error instead of 500
            import traceback
            return Response({
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            }, status=status.HTTP_400_BAD_REQUEST)


class SaleInvoiceStateUpdateAPIView(UpdateAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = SaleInvoiceStateUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = SaleInvoice.objects.select_related("user", "seller").prefetch_related("items__product").all()

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset
    
    def update(self, request, *args, **kwargs):
        from rest_framework.exceptions import ValidationError as DRFValidationError
        import traceback
        
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            # Success response
            return Response(serializer.data)
            
        except DRFValidationError as e:
            # Re-raise DRF validation errors (will be 400)
            raise
        except Exception as e:
            # Catch any other errors and return detailed information
            return Response({
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            }, status=status.HTTP_400_BAD_REQUEST)


class SaleInvoiceItemListAPIView(ListAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = SaleInvoiceItemReadSerializer
    search_fields = ["product__name", "product__e_name"]
    filterset_class = SaleInvoiceItemFilter

    def get_queryset(self):
        user = self.request.user
        queryset = SaleInvoiceItem.objects.select_related("product", "invoice", "invoice__user").all()

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(invoice__user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(invoice__user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(invoice__user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset


class SaleInvoiceItemCreateAPIView(CreateAPIView):
    permission_classes = [
        SalesRoleAuthentication 
        | ManagerRoleAuthentication 
        | AreaManagerRoleAuthentication 
        | PharmacyRoleAuthentication 
        | StoreRoleAuthentication
    ]
    serializer_class = SaleInvoiceItemCreateSerializer
    queryset = SaleInvoiceItem.objects.all()
    
    def create(self, request, *args, **kwargs):
        # Validation: If user is PHARMACY or STORE, they can only add items to their own invoices
        user = request.user
        
        if user.role in [Role.PHARMACY, Role.STORE]:
            sale_invoice_id = request.data.get('sale_invoice')
            if sale_invoice_id:
                try:
                    invoice = SaleInvoice.objects.get(id=sale_invoice_id)
                    if invoice.user_id != user.id:
                        return Response({
                            "error": "لا يمكنك إضافة بنود لفواتير مستخدمين آخرين / You cannot add items to other users' invoices"
                        }, status=status.HTTP_403_FORBIDDEN)
                except SaleInvoice.DoesNotExist:
                    return Response({
                        "error": "الفاتورة غير موجودة / Invoice not found"
                    }, status=status.HTTP_404_NOT_FOUND)
        
        return super().create(request, *args, **kwargs)


class SaleInvoiceItemStateUpdateAPIView(UpdateAPIView):
    permission_classes = [
        SalesRoleAuthentication
        | ManagerRoleAuthentication
        | AreaManagerRoleAuthentication
        | DataEntryRoleAuthentication
    ]
    serializer_class = SaleInvoiceItemStateUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = SaleInvoiceItem.objects.select_related("purchase_invoice_item").exclude(
            invoice__status=SaleInvoiceStatusChoice.CLOSED
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.DATA_ENTRY:
                queryset = queryset.filter(user__profile__data_entry=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset


class SaleInvoiceItemUpdateAPIView(UpdateAPIView):
    permission_classes = [
        SalesRoleAuthentication 
        | ManagerRoleAuthentication 
        | AreaManagerRoleAuthentication 
        | PharmacyRoleAuthentication 
        | StoreRoleAuthentication
    ]
    serializer_class = SaleInvoiceItemUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = SaleInvoiceItem.objects.select_related("invoice", "purchase_invoice_item").filter(
            invoice__status=SaleInvoiceStatusChoice.PLACED
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(invoice__user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(invoice__user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(invoice__user__profile__manager=user)
            case Role.PHARMACY | Role.STORE:
                # Pharmacies and stores can only update items in their own invoices
                queryset = queryset.filter(invoice__user=user)
            case _r:
                queryset = queryset.none()

        return queryset

    def get_serializer(self, *args, **kwargs):
        kwargs.update({"exclude": ["id"]})
        return super().get_serializer(*args, **kwargs)


class SaleInvoiceItemBulkStateUpdateAPIView(BulkUpdateAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = SaleInvoiceItemStateUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = SaleInvoiceItem.objects.select_related("invoice", "purchase_invoice_item").exclude(
            invoice__status=SaleInvoiceStatusChoice.CLOSED
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(invoice__user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(invoice__user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(invoice__user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset


class SaleInvoiceItemDestroyAPIView(DestroyAPIView):
    permission_classes = [
        SalesRoleAuthentication 
        | ManagerRoleAuthentication 
        | AreaManagerRoleAuthentication 
        | PharmacyRoleAuthentication 
        | StoreRoleAuthentication
    ]
    serializer_class = SaleInvoiceItemCreateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = SaleInvoiceItem.objects.select_related("invoice", "invoice__user", "invoice__user__account").filter(
            invoice__status=SaleInvoiceStatusChoice.PLACED
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(invoice__user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(invoice__user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(invoice__user__profile__manager=user)
            case Role.PHARMACY | Role.STORE:
                # Pharmacies and stores can only delete items from their own invoices
                queryset = queryset.filter(invoice__user=user)
            case _r:
                queryset = queryset.none()

        return queryset

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        delete_sale_invoice_item(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SaleReturnInvoiceListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SaleReturnInvoiceReadSerializer
    search_fields = ["user__username", "user__name"]
    ordering_fields = ["created_at", "total_price"]
    filterset_class = SaleReturnInvoiceFilter

    def get_queryset(self):
        user = self.request.user
        queryset = SaleReturnInvoice.objects.select_related("user").all()

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.DATA_ENTRY:
                queryset = queryset.filter(user__profile__data_entry=user)
            case Role.DELIVERY:
                queryset = queryset.filter(user__profile__delivery=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case r if r in [Role.STORE, Role.PHARMACY]:
                queryset = queryset.filter(user=user)
            case _r:
                queryset = queryset.none()

        return queryset

    def get_serializer(self, *args, **kwargs):
        kwargs.update({"exclude": ["items"]})
        return super().get_serializer(*args, **kwargs)


class SaleReturnInvoiceCreateAPIView(CreateAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = SaleReturnInvoiceCreateSerializer
    queryset = SaleReturnInvoice.objects.all()


class SaleReturnInvoiceRetrieveAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SaleReturnInvoiceReadSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = (
            SaleReturnInvoice.objects.select_related("user", "user__profile")
            .prefetch_related(
                models.Prefetch(
                    "items",
                    queryset=SaleReturnInvoiceItem.objects.select_related(
                        "sale_invoice_item", "sale_invoice_item__invoice", "sale_invoice_item__product"
                    ),
                )
            )
            .all()
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.DATA_ENTRY:
                queryset = queryset.filter(user__profile__data_entry=user)
            case Role.DELIVERY:
                queryset = queryset.filter(user__profile__delivery=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case r if r in [Role.STORE, Role.PHARMACY]:
                queryset = queryset.filter(user=user)
            case _r:
                queryset = queryset.none()

        return queryset


class SaleReturnInvoiceStateUpdateAPIView(UpdateAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = SaleReturnInvoiceStateUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = (
            SaleReturnInvoice.objects.select_related("user", "user__account")
            .prefetch_related(
                models.Prefetch(
                    "items",
                    queryset=SaleReturnInvoiceItem.objects.select_related(
                        "sale_invoice_item", "sale_invoice_item__product"
                    ),
                )
            )
            .exclude(status=SaleReturnInvoiceStatusChoice.CLOSED)
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset


class SaleReturnInvoiceItemListAPIView(ListAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = SaleReturnInvoiceItemReadSerializer
    search_fields = ["sale_invoice_item__product__name", "sale_invoice_item__product__e_name"]
    filterset_class = SaleReturnInvoiceItemFilter

    def get_queryset(self):
        user = self.request.user
        queryset = SaleReturnInvoiceItem.objects.select_related("sale_invoice_item", "invoice").all()

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(invoice__user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(invoice__user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(invoice__user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset


class SaleReturnInvoiceItemCreateAPIView(CreateAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = SaleReturnInvoiceItemCreateSerializer
    queryset = SaleReturnInvoiceItem.objects.all()


class SaleReturnInvoiceItemUpdateAPIView(UpdateAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]
    serializer_class = SaleReturnInvoiceItemUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = SaleReturnInvoiceItem.objects.select_related("sale_invoice_item", "invoice").exclude(
            invoice__status=SaleReturnInvoiceStatusChoice.CLOSED
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(invoice__user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(invoice__user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(invoice__user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset


class SaleReturnInvoiceItemDestroyAPIView(DestroyAPIView):
    permission_classes = [SalesRoleAuthentication | ManagerRoleAuthentication | AreaManagerRoleAuthentication]

    def get_queryset(self):
        user = self.request.user
        queryset = SaleReturnInvoiceItem.objects.select_related("invoice", "sale_invoice_item").exclude(
            invoice__status=SaleReturnInvoiceStatusChoice.CLOSED
        )

        if user.is_superuser:
            return queryset

        match user.role:
            case Role.SALES:
                queryset = queryset.filter(invoice__user__profile__sales=user)
            case Role.AREA_MANAGER:
                queryset = queryset.filter(invoice__user__profile__area_manager=user)
            case Role.MANAGER:
                queryset = queryset.filter(invoice__user__profile__manager=user)
            case _r:
                queryset = queryset.none()

        return queryset

    def perform_destroy(self, instance):
        with transaction.atomic():
            delete_sale_return_invoice_item(instance)
