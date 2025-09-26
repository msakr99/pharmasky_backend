from django.db import models


class AbstractInvoiceItemModel(models.Model):
    product_expiry_date = models.DateField(null=True, blank=True)
    operating_number = models.CharField(max_length=255, default="", blank=True)
    purchase_discount_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_discount_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    remaining_quantity = models.PositiveIntegerField()
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        abstract = True
