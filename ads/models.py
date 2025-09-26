from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from ads.choices import RedirectTypeChoice


class Advertisment(models.Model):
    image = models.ImageField(null=True)
    redirect_type = models.CharField(choices=RedirectTypeChoice.choices, default=RedirectTypeChoice.INTERNAL)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="advertisment",
        related_query_name="advertisment",
        null=True,
        blank=True,
    )
    object_id = models.PositiveBigIntegerField(null=True, blank=True)
    related_object = GenericForeignKey("content_type", "object_id")
    external_url = models.URLField(default="", blank=True)

    def __str__(self) -> str:
        return f"{self.get_redirect_type_display()} advertisment | {self.content_type} | {self.object_id}"
