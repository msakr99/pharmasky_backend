from django.urls import path
from market import views, filter_views
from django.conf import settings
from django.http import HttpResponse
import pandas as pd
import io


def download_sample_file():
    """Generate and return a sample Excel file for upload with flexible matching examples"""
    # Create sample data with examples showing flexibility
    sample_data = {
        'product_name': [
            'باراسيتامول 500 مجم',
            'أموكسيسيلين 250 مجم',
            'إيبوبروفين 400 مجم',
            'أوميبرازول 20 مجم',
            'فيتامين د3 1000 وحدة',
            'باراسيتامول 500 مج',  # مثال على اسم غير مكتمل
            'أموكسيسيلين 250',     # مثال على اسم مختصر
        ],
        'code': [
            1001,
            1002,
            1003,
            1004,
            1005,
            1006,
            1007
        ],
        'product_id': [
            1,
            2,
            3,
            4,
            5,
            1,  # نفس منتج باراسيتامول
            2   # نفس منتج أموكسيسيلين
        ],
        'notes': [
            'مسكن للآلام',
            'مضاد حيوي',
            'مضاد للالتهاب',
            'مثبط مضخة البروتون',
            'مكمل غذائي',
            'مسكن للآلام (اسم غير مكتمل)',
            'مضاد حيوي (اسم مختصر)'
        ],
        'price': [
            15.50,
            25.00,
            18.75,
            35.00,
            45.00,
            15.45,  # سعر مختلف قليلاً (0.05 فرق)
            25.05   # سعر مختلف قليلاً (0.05 فرق)
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Store Product Codes', index=False)
    
    output.seek(0)
    
    # Create HTTP response
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="sample_store_product_codes.xlsx"'
    
    return response

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
    
    # Store Product Code Upload API URLs
    path(
        "store-product-code-uploads/",
        views.StoreProductCodeUploadListAPIView.as_view(),
        name="store-product-code-uploads-list",
    ),
    path(
        "store-product-code-uploads/create/",
        views.StoreProductCodeUploadCreateAPIView.as_view(),
        name="store-product-code-uploads-create",
    ),
    path(
        "store-product-code-uploads/bulk/",
        views.BulkStoreProductCodeUploadCreateAPIView.as_view(),
        name="store-product-code-uploads-bulk",
    ),
    path(
        "store-product-code-uploads/<int:pk>/",
        views.StoreProductCodeUploadRetrieveAPIView.as_view(),
        name="store-product-code-uploads-detail",
    ),
    path(
        "store-product-code-uploads/<int:pk>/progress/",
        views.StoreProductCodeUploadProgressAPIView.as_view(),
        name="store-product-code-uploads-progress",
    ),
    path(
        "store-product-code-uploads/<int:pk>/retry/",
        views.StoreProductCodeUploadRetryAPIView.as_view(),
        name="store-product-code-uploads-retry",
    ),
    path(
        "store-product-code-uploads/statistics/",
        views.StoreProductCodeUploadStatisticsAPIView.as_view(),
        name="store-product-code-uploads-statistics",
    ),
    path(
        "stores/",
        views.StoreListAPIView.as_view(),
        name="stores-list",
    ),
    path(
        "upload/sample/",
        lambda request: download_sample_file(),
        name="download_sample",
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
