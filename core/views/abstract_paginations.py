from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_query_param = "p"
    page_size_query_param = "ps"
    max_page_size = 50
    total_page_sizes = None

    def paginate_queryset(self, queryset, request, view=None):
        self.total_page_sizes = queryset.count()
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("current_page_number", self.page.number),
                    ("page_size", self.page.paginator.per_page),
                    ("links", {"next": self.get_next_link(), "previous": self.get_previous_link()}),
                    ("results", data),
                ]
            )
        )


class LargePageNumberPagination(CustomPageNumberPagination):
    page_size = 100
