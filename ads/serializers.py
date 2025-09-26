from ads.models import Advertisment
from core.serializers.abstract_serializers import BaseModelSerializer
from rest_framework import serializers


class AdvertismentReadSerializer(BaseModelSerializer):
    content_type = serializers.CharField(source="content_type.model", read_only=True)

    class Meta:
        model = Advertisment
        fields = ["id", "image", "redirect_type", "content_type", "object_id", "external_url"]
