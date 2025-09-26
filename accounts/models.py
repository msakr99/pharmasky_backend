from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from accounts import managers
from django.utils.translation import gettext_lazy as _
from accounts.choices import Role


class Area(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"{self.name}"


class User(AbstractUser):
    base_role = Role.ADMIN

    role = models.CharField(max_length=20, choices=Role.choices)
    username = PhoneNumberField(blank=True, unique=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=200)
    e_name = models.CharField(max_length=50, blank=True, default="")

    USERNAME_FIELD = "username"
    unique_together = ("username",)

    def __str__(self) -> str:
        return f"{self.name}"


class Pharmacy(User):
    base_role = Role.PHARMACY
    objects = managers.PharmacyManager.from_queryset(managers.PharmacyQuerySet)()

    class Meta:
        proxy = True
        verbose_name_plural = _("Pharmacies")


class Delivery(User):
    base_role = Role.DELIVERY
    objects = managers.DeliveryManager.from_queryset(managers.DeliveryQuerySet)()

    class Meta:
        proxy = True
        verbose_name_plural = _("Deliveries")


class Sales(User):
    base_role = Role.SALES
    objects = managers.SalesManager.from_queryset(managers.SalesQuerySet)()

    class Meta:
        proxy = True
        verbose_name_plural = _("Sales")


class Store(User):
    base_role = Role.STORE
    objects = managers.StoreManager.from_queryset(managers.StoreQuerySet)()

    class Meta:
        proxy = True


class AreaManager(User):
    base_role = Role.AREA_MANAGER
    objects = managers.AreaManagerManager.from_queryset(managers.AreaManagerQuerySet)()

    class Meta:
        proxy = True


class Manager(User):
    base_role = Role.MANAGER
    objects = managers.ManagerManager.from_queryset(managers.ManagerQuerySet)()

    class Meta:
        proxy = True


class DataEntry(User):
    base_role = Role.DATA_ENTRY
    objects = managers.DataEntryManager.from_queryset(managers.DataEntryQuerySet)()

    class Meta:
        proxy = True


class ReturnPolicy(models.Model):
    point = models.CharField(max_length=300)


class PrivacyPolicy(models.Model):
    point = models.CharField(max_length=300)


class PublicRules(models.Model):
    point = models.CharField(max_length=300)


class OurServices(models.Model):
    point = models.CharField(max_length=300)
