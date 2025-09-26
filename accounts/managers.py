from typing import Any
from django.contrib.auth.models import UserManager as _UserManager
from django.db import models
from django.apps import apps

get_model = apps.get_model


class UserManager(_UserManager):
    base_role = None

    def get_queryset(self) -> models.QuerySet:
        return (
            super()
            .get_queryset()
            .select_related("profile")
            .filter(models.Q(role=self.model.base_role) | models.Q(is_superuser=True))
        )


class UserQuerySet(models.QuerySet):
    def create(self, **kwargs: Any) -> Any:
        base_role = getattr(self.model, "base_role", None)

        assert (
            base_role is not None
        ), """
        Base Role is not assigned for model
        """
        kwargs.update({"role": base_role})
        return super().create(**kwargs)


class PharmacyQuerySet(UserQuerySet):
    pass


class PharmacyManager(UserManager):
    pass


class SalesQuerySet(UserQuerySet):
    pass


class SalesManager(UserManager):
    pass


class DeliveryQuerySet(UserQuerySet):
    pass


class DeliveryManager(UserManager):
    pass


class DataEntryQuerySet(UserQuerySet):
    pass


class DataEntryManager(UserManager):
    pass


class StoreQuerySet(UserQuerySet):
    pass


class StoreManager(UserManager):
    pass


class AreaManagerQuerySet(UserQuerySet):
    pass


class AreaManagerManager(UserManager):
    pass


class ManagerQuerySet(UserQuerySet):
    pass


class ManagerManager(UserManager):
    pass


class PharmacyProfileQuerySet(models.QuerySet):
    pass


class PharmacyProfileManager(models.Manager):
    pass
