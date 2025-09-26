from django.db import models
from django.utils.translation import gettext_lazy as _


class RedirectTypeChoice(models.TextChoices):
    INTERNAL = "i", _("Internal")
    EXTERNAL = "e", _("External")
