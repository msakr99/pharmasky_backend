from django.urls import path
from market import views, filter_views
from django.conf import settings

app_name = "market"

urlpatterns = [
    path(
        "companies/list",
        views.CompanyListAPIView.as_view(),
        name="companies-list-view",
    ),
    path(
        "categories/list",
        views.CategoryListAPIView.as_view(),
        name="categories-list-view",
    ),
    path(
        "products/",
        views.ProductListAPIView.as_view(),
        name="products-list-view",
    ),
    path(
        "products/create/",
        views.ProductCreateAPIView.as_view(),
        name="products-create-view",
    ),
    path(
        "products/<int:pk>/",
        views.ProductRetrieveAPIView.as_view(),
        name="products-object-view",
    ),
    path(
        "products/<int:pk>/change/",
        views.ProductUpdateAPIView.as_view(),
        name="products-update-view",
    ),
    path(
        "products/object/<int:pk>/product-alternatives/list",
        views.ProductAlternativeListAPIView.as_view(),
        name="product-alternatives-list-view",
    ),
    path(
        "products/object/<int:pk>/product-instances/list",
        views.ProductInstanceListAPIView.as_view(),
        name="product-instances-list-view",
    ),
    path(
        "product-codes/",
        views.ProductCodeListAPIView.as_view(),
        name="product-codes-list-view",
    ),
    path(
        "user/product-wishlist/",
        views.UserPharmacyProductWishListListAPIView.as_view(),
        name="user-product-wishlist-list-view",
    ),
    path(
        "user/product-wishlist/create/",
        views.UserPharmacyProductWishListCreateAPIView.as_view(),
        name="user-product-wishlist-create-view",
    ),
]


filter_urls = [
    path(
        "filters/products/company",
        filter_views.ProductCompanyFilterAPIView.as_view(),
        name="product-filter-by-company-list-view",
    ),
    path(
        "filters/products/category",
        filter_views.ProductCategoryFilterAPIView.as_view(),
        name="product-filter-by-category-list-view",
    ),
    path(
        "filters/products/letter",
        filter_views.ProductLetterFilterAPIView.as_view(),
        name="product-filter-by-letter-list-view",
    ),
    path(
        "filters/products/shape",
        filter_views.ProductShapeFilterAPIView.as_view(),
        name="product-filter-by-shape-list-view",
    ),
]


urlpatterns += filter_urls


if settings.DEBUG:
    urlpatterns += [path("template/test", views.TemplateTest.as_view(), name="test-template")]
