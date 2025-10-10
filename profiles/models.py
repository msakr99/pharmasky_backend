from decimal import Decimal
from django.db import models

from profiles.choices import UserProfileCategoryChoice


class Area(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.name}"


class Country(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self) -> str:
        return f"{self.name}"


class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities", related_query_name="cities")
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Cities"

    def __str__(self) -> str:
        return f"{self.country} | {self.name}"


class PaymentPeriod(models.Model):
    def __str__(self) -> str:
        return f"{self.name}"

    name = models.CharField(max_length=255)
    period_in_days = models.PositiveIntegerField()
    addition_percentage = models.DecimalField(max_digits=4, decimal_places=2, blank=True)


class UserProfile(models.Model):
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="profile",
        related_query_name="profile",
    )
    data_entry = models.ForeignKey(
        "accounts.DataEntry",
        on_delete=models.SET_NULL,
        related_name="assigned_profiles_data_entry",
        related_query_name="assigned_profiles_data_entry",
        null=True,
        blank=True,
    )
    sales = models.ForeignKey(
        "accounts.Sales",
        on_delete=models.SET_NULL,
        related_name="assigned_profiles_sales",
        related_query_name="assigned_profiles_sales",
        null=True,
        blank=True,
    )
    manager = models.ForeignKey(
        "accounts.Manager",
        on_delete=models.SET_NULL,
        related_name="assigned_profiles_manager",
        related_query_name="assigned_profiles_manager",
        null=True,
        blank=True,
    )
    area_manager = models.ForeignKey(
        "accounts.AreaManager",
        on_delete=models.SET_NULL,
        related_name="assigned_profiles_area_manager",
        related_query_name="assigned_profiles_area_manager",
        null=True,
        blank=True,
    )
    delivery = models.ForeignKey(
        "accounts.Delivery",
        on_delete=models.SET_NULL,
        related_name="assigned_profiles_delivery",
        related_query_name="assigned_profiles_delivery",
        null=True,
        blank=True,
    )
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, related_name="profiles", related_query_name="profiles", blank=True, null=True
    )
    category = models.CharField(choices=UserProfileCategoryChoice.choices, default=UserProfileCategoryChoice.NONE)
    license = models.ImageField(null=True, blank=True)
    address = models.TextField(max_length=200, blank=True, default="")
    remarks = models.TextField(default="", blank=True)
    latest_invoice_date = models.DateTimeField(null=True, blank=True)
    payment_period = models.ForeignKey(
        PaymentPeriod,
        on_delete=models.SET_NULL,
        related_name="profiles",
        related_query_name="profiles",
        null=True,
        blank=True,
    )
    profit_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("1.50"))
    order_by_phone = models.BooleanField(default=False)
    company = models.BooleanField(default=False)
    key_person = models.CharField(max_length=255, blank=True, default="")
    key_person_phone = models.CharField(max_length=255, blank=True, default="")
    
    # Late payment penalty and early payment cashback
    late_payment_penalty_percentage = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=Decimal("0.20"),
        help_text="Daily penalty percentage for late payments (default 0.20%)"
    )
    early_payment_cashback_percentage = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=Decimal("0.10"),
        help_text="Daily cashback percentage for early payments (default 0.10%)"
    )

    def __str__(self):
        return f"{self.user}'s Profile"


class Complaint(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="user_complaints",
        related_query_name="user_complaints",
    )
    subject = models.CharField(max_length=255)
    body = models.TextField(max_length=400)
    mark_as_solved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} | {self.subject}"

    class Meta:
        indexes = [models.Index(fields=["user"])]
