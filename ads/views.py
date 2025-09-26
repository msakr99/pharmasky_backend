from rest_framework.generics import ListAPIView

from ads.models import Advertisment
from ads.serializers import AdvertismentReadSerializer


class AdvertismentListAPIView(ListAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = AdvertismentReadSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Advertisment.objects.all()
        return queryset
