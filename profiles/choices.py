from django.db import models


class UserProfileCategoryChoice(models.TextChoices):
    NONE = "none", "Unassigned"
    A = "a", "A"
    B = "b", "B"
    C = "c", "C"
    D = "d", "D"
