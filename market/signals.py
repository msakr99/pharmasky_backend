from django.apps import apps
from django.db.models.signals import pre_save
from django.dispatch import receiver
from market.models import Product

get_model = apps.get_model


@receiver(pre_save, sender=Product)
def product_pre_save(sender, instance, *args, **kwargs):
    instance.letter = f"{instance.e_name[:1]}".upper()
