from django.db import models
from django.contrib.contenttypes.models import ContentType
from finance.choices import AccountTransactionTypeChoice
from invoices.abstract_models import AbstractInvoiceItemModel
from invoices.choices import (
    PurchaseInvoiceItemStatusChoice,
    PurchaseInvoiceStatusChoice,
    PurchaseReturnInvoiceStatusChoice,
    SaleInvoiceItemStatusChoice,
    SaleInvoiceStatusChoice,
    SaleReturnInvoiceStatusChoice,
)
from invoices.managers import (
    PurchaseInvoiceDeletedItemManager,
    PurchaseInvoiceItemManager,
    SaleInvoiceDeletedItemManager,
)


class PurchaseInvoice(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="purchase_invoices",
        related_query_name="purchase_invoices",
    )
    supplier_invoice_number = models.CharField(max_length=255, blank=True, default="")
    items_count = models.PositiveIntegerField()
    total_quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        choices=PurchaseInvoiceStatusChoice.choices,
        default=PurchaseInvoiceStatusChoice.PLACED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.pk}"

    @property
    def transaction_data(self):
        from finance.models import Account
        account, _ = Account.objects.get_or_create(user=self.user)
        return {
            "account": account,
            "type": AccountTransactionTypeChoice.PURCHASE_INVOICE,
            "amount": self.total_price,
            "content_type": ContentType.objects.get_for_model(self),
            "object_id": self.pk,
            "at": self.created_at,
        }


class PurchaseInvoiceItem(AbstractInvoiceItemModel):
    invoice = models.ForeignKey(
        PurchaseInvoice,
        on_delete=models.CASCADE,
        related_name="items",
        related_query_name="items",
    )
    product = models.ForeignKey(
        "market.Product",
        on_delete=models.PROTECT,
        related_name="purchase_invoice_items",
        related_query_name="purchase_invoice_items",
    )
    offer = models.ForeignKey(
        "offers.Offer",
        on_delete=models.SET_NULL,
        related_name="purchase_invoice_items",
        related_query_name="purchase_invoice_items",
        null=True,
        blank=True,
    )
    status = models.CharField(
        choices=PurchaseInvoiceItemStatusChoice.choices,
        default=PurchaseInvoiceItemStatusChoice.PLACED,
    )
    sale_invoice_item = models.OneToOneField(
        "SaleInvoiceItem",
        on_delete=models.SET_NULL,
        related_name="purchase_invoice_item",
        related_query_name="purchase_invoice_item",
        null=True,
        blank=True,
    )

    objects = PurchaseInvoiceItemManager()

    def __str__(self):
        return f"Invoice {self.invoice.pk} - Item {self.product}"


class PurchaseInvoiceDeletedItem(AbstractInvoiceItemModel):
    invoice = models.ForeignKey(
        PurchaseInvoice,
        on_delete=models.CASCADE,
        related_name="deleted_items",
        related_query_name="deleted_items",
    )
    product = models.ForeignKey(
        "market.Product",
        on_delete=models.PROTECT,
        related_name="purchase_invoice_deleted_items",
        related_query_name="purchase_invoice_deleted_items",
    )
    offer = models.ForeignKey(
        "offers.Offer",
        on_delete=models.SET_NULL,
        related_name="purchase_invoice_deleted_items",
        related_query_name="purchase_invoice_deleted_items",
        null=True,
        blank=True,
    )
    status = models.CharField(
        choices=PurchaseInvoiceItemStatusChoice.choices,
        default=PurchaseInvoiceItemStatusChoice.PLACED,
    )
    sale_invoice_item = models.OneToOneField(
        "SaleInvoiceItem",
        on_delete=models.SET_NULL,
        related_name="purchase_invoice_deleted_items",
        related_query_name="purchase_invoice_deleted_items",
        null=True,
        blank=True,
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = PurchaseInvoiceDeletedItemManager()

    def __str__(self):
        return f"{self.invoice} - Item {self.product}"


class PurchaseReturnInvoice(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="purchase_return_invoices",
        related_query_name="purchase_return_invoices",
    )
    items_count = models.PositiveIntegerField()
    total_quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        choices=PurchaseReturnInvoiceStatusChoice.choices,
        default=PurchaseReturnInvoiceStatusChoice.PLACED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase Return Invoice {self.pk}"

    @property
    def transaction_data(self):
        from finance.models import Account
        account, _ = Account.objects.get_or_create(user=self.user)
        return {
            "account": account,
            "type": AccountTransactionTypeChoice.PURCHASE_RETURN,
            "amount": self.total_price,
            "content_type": ContentType.objects.get_for_model(self),
            "object_id": self.pk,
            "at": self.created_at,
        }


class PurchaseReturnInvoiceItem(models.Model):
    invoice = models.ForeignKey(
        PurchaseReturnInvoice,
        on_delete=models.CASCADE,
        related_name="items",
        related_query_name="items",
    )
    purchase_invoice_item = models.ForeignKey(
        PurchaseInvoiceItem,
        on_delete=models.PROTECT,
        related_name="purchase_return_invoice_items",
        related_query_name="purchase_return_invoice_items",
    )
    quantity = models.PositiveIntegerField()
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.invoice} - Item {self.purchase_invoice_item.product}"


class SaleInvoice(models.Model):
    seller = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="sold_invoices",
        related_query_name="sold_invoices",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="sale_invoices",
        related_query_name="sale_invoices",
    )
    items_count = models.PositiveIntegerField()
    total_quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        choices=SaleInvoiceStatusChoice.choices,
        default=SaleInvoiceStatusChoice.PLACED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.pk}"

    class Meta:
        indexes = [
            models.Index(fields=["seller"]),
            models.Index(fields=["user"]),
            models.Index(fields=["user", "seller"]),
        ]

    @property
    def transaction_data(self):
        from finance.models import Account
        account, _ = Account.objects.get_or_create(user=self.user)
        return {
            "account": account,
            "type": AccountTransactionTypeChoice.SALE_INVOICE,
            "amount": self.total_price,
            "content_type": ContentType.objects.get_for_model(self),
            "object_id": self.pk,
            "at": self.created_at,
        }


class SaleInvoiceItem(AbstractInvoiceItemModel):
    invoice = models.ForeignKey(
        SaleInvoice,
        on_delete=models.CASCADE,
        related_name="items",
        related_query_name="items",
    )
    product = models.ForeignKey(
        "market.Product",
        on_delete=models.PROTECT,
        related_name="sale_invoice_items",
        related_query_name="sale_invoice_items",
    )
    offer = models.ForeignKey(
        "offers.Offer",
        on_delete=models.SET_NULL,
        related_name="sale_invoice_items",
        related_query_name="sale_invoice_items",
        null=True,
        blank=True,
    )
    status = models.CharField(
        choices=SaleInvoiceItemStatusChoice.choices,
        default=SaleInvoiceItemStatusChoice.PLACED,
    )

    def __str__(self):
        return f"{self.invoice} - Item {self.product}"


class SaleInvoiceDeletedItem(AbstractInvoiceItemModel):
    invoice = models.ForeignKey(
        SaleInvoice,
        on_delete=models.CASCADE,
        related_name="deleted_items",
        related_query_name="deleted_items",
    )
    product = models.ForeignKey(
        "market.Product",
        on_delete=models.PROTECT,
        related_name="sale_invoice_deleted_items",
        related_query_name="sale_invoice_deleted_items",
    )
    offer = models.ForeignKey(
        "offers.Offer",
        on_delete=models.SET_NULL,
        related_name="sale_invoice_deleted_items",
        related_query_name="sale_invoice_deleted_items",
        null=True,
        blank=True,
    )
    status = models.CharField(
        choices=SaleInvoiceItemStatusChoice.choices,
        default=SaleInvoiceItemStatusChoice.PLACED,
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = SaleInvoiceDeletedItemManager()

    def __str__(self):
        return f"{self.invoice} - Item {self.product}"


class SaleReturnInvoice(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="sale_return_invoices",
        related_query_name="sale_return_invoices",
    )
    items_count = models.PositiveIntegerField()
    total_quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        choices=SaleReturnInvoiceStatusChoice.choices,
        default=SaleReturnInvoiceStatusChoice.PLACED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale Return Invoice {self.pk}"

    @property
    def transaction_data(self):
        from finance.models import Account
        account, _ = Account.objects.get_or_create(user=self.user)
        return {
            "account": account,
            "type": AccountTransactionTypeChoice.SALE_RETURN,
            "amount": self.total_price,
            "content_type": ContentType.objects.get_for_model(self),
            "object_id": self.pk,
            "at": self.created_at,
        }


class SaleReturnInvoiceItem(models.Model):
    invoice = models.ForeignKey(
        SaleReturnInvoice,
        on_delete=models.CASCADE,
        related_name="items",
        related_query_name="items",
    )
    sale_invoice_item = models.ForeignKey(
        SaleInvoiceItem,
        on_delete=models.PROTECT,
        related_name="sale_return_invoice_items",
        related_query_name="sale_return_invoice_items",
    )
    quantity = models.PositiveIntegerField()
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.invoice} - Item {self.sale_invoice_item.product}"
