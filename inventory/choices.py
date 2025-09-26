from django.db import models


class InventoryTypeChoice(models.TextChoices):
    MAIN = "main", "Main"
    SECONDARY = "secondary", "Secondary"
