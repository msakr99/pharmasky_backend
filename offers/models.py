from decimal import Decimal
from django.db import models


class Offer(models.Model):
    product_code = models.ForeignKey(
        "market.StoreProductCode",
        on_delete=models.CASCADE,
        related_name="offers",
        related_query_name="offers",
        null=True,
        blank=True,
    )
    product = models.ForeignKey(
        "market.Product",
        on_delete=models.CASCADE,
        related_name="offers",
        related_query_name="offers",
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="offers",
        related_query_name="offers",
    )
    operating_number = models.CharField(max_length=255, default="", blank=True)
    available_amount = models.PositiveIntegerField()
    remaining_amount = models.PositiveIntegerField()
    max_amount_per_invoice = models.PositiveIntegerField(null=True, blank=True)
    product_expiry_date = models.DateField(null=True, blank=True)
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    purchase_discount_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_discount_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_max = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_code}"
