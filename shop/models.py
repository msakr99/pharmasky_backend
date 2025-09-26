from django.db import models


class Cart(models.Model):
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="cart",
        related_query_name="cart",
    )
    items_count = models.PositiveIntegerField(default=0)
    total_quantity = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        indexes = [models.Index(fields=["user"])]

    def __str__(self) -> str:
        return f"{self.user}'s Cart"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        related_query_name="items",
    )
    offer = models.ForeignKey(
        "offers.Offer",
        on_delete=models.SET_NULL,
        related_name="cart_items",
        related_query_name="cart_items",
        null=True,
        blank=True,
    )
    product = models.ForeignKey(
        "market.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
        related_query_name="cart_items",
    )
    quantity = models.PositiveIntegerField()
    discount_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total = models.DecimalField(max_digits=8, decimal_places=2)
    sold_out = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["cart"]),
            models.Index(fields=["offer"]),
            models.Index(fields=["product", "quantity"]),
            models.Index(fields=["offer", "product", "quantity"]),
        ]

    def __str__(self) -> str:
        return f"{self.cart} | {self.product}"
