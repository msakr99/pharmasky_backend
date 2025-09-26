from django.db import models

from inventory.choices import InventoryTypeChoice


class Inventory(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(choices=InventoryTypeChoice.choices)
    total_items = models.PositiveIntegerField()
    total_quantity = models.PositiveIntegerField()
    total_purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventories"
        indexes = [models.Index(fields=["type"])]

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    inventory = models.ForeignKey(
        Inventory, on_delete=models.CASCADE, related_name="items", related_query_name="items"
    )
    product = models.ForeignKey(
        "market.Product",
        on_delete=models.PROTECT,
        related_name="inventory_items",
        related_query_name="inventory_items",
    )
    purchase_invoice_item = models.OneToOneField(
        "invoices.PurchaseInvoiceItem",
        on_delete=models.SET_NULL,
        related_name="inventory_item",
        related_query_name="inventory_item",
        null=True,
        blank=True,
    )
    product_expiry_date = models.DateField(null=True, blank=True)
    operating_number = models.CharField(max_length=255, default="", blank=True)
    purchase_discount_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_discount_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    remaining_quantity = models.PositiveIntegerField()
    purchase_sub_total = models.DecimalField(max_digits=10, decimal_places=2)
    selling_sub_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Inventory item"
        verbose_name_plural = "Inventory items"

    def __str__(self):
        return f"{self.inventory} - {self.product}"
