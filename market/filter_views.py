from django.utils.translation import gettext_lazy as _
from accounts.permissions import *
from core.views.abstract_api_views import BooleanFilterAPIView, CharFilterAPIView, IDFilterAPIView
from market.filters import ProductFilter, ProductCodeFilter
from market.models import Product, ProductCode


class ProductCompanyFilterAPIView(IDFilterAPIView):
    permission_classes = [
        SalesRoleAuthentication | DataEntryRoleAuthentication | PharmacyRoleAuthentication | ManagerRoleAuthentication
    ]
    filterset_class = ProductFilter
    text_field = "company__name"
    id_field = "company__id"

    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset


class ProductCategoryFilterAPIView(IDFilterAPIView):
    permission_classes = [
        SalesRoleAuthentication | DataEntryRoleAuthentication | PharmacyRoleAuthentication | ManagerRoleAuthentication
    ]
    filterset_class = ProductFilter
    text_field = "category__name"
    id_field = "category__id"

    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset


class ProductLetterFilterAPIView(CharFilterAPIView):
    permission_classes = [
        SalesRoleAuthentication | DataEntryRoleAuthentication | PharmacyRoleAuthentication | ManagerRoleAuthentication
    ]
    filterset_class = ProductFilter
    text_field = "letter"

    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset


class ProductShapeFilterAPIView(CharFilterAPIView):
    permission_classes = [
        SalesRoleAuthentication | DataEntryRoleAuthentication | PharmacyRoleAuthentication | ManagerRoleAuthentication
    ]
    filterset_class = ProductFilter
    text_field = "shape"

    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset
