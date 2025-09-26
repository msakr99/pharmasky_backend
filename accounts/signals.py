from django.apps import apps
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

get_model = apps.get_model
