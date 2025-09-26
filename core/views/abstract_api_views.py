from rest_framework.generics import GenericAPIView
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework import status
from django.db import models
from django.db.models import Q, Value, F, Case, When, Min, Max
from django.db.models.functions import Coalesce, Cast
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from core.serializers.abstract_serializers import (
    BooleanFilterSerializer,
    CharFilterSerializer,
    DateTimeRangeFilterSerializer,
    IDFilterSerializer,
    TextChoiceSerializer,
)
from django.shortcuts import get_object_or_404
from drf_excel.mixins import XLSXFileMixin
from core.views.mixins import PDFFileMixin


class BulkUpdateAPIView(GenericAPIView):
    def perform_update(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.get_response(serializer.data)

    def get_response(self, data):
        return Response(data)

    def put(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, data=request.data, many=True)
        return self.perform_update(serializer)


class IDFilterAPIView(GenericAPIView):
    serializer_class = IDFilterSerializer
    text_field = ""
    id_field = "id"

    def get_filter_queryset(self):
        searchParam = self.request.query_params.get("s")
        queryset = self.get_queryset()

        if searchParam:
            queryset = queryset.filter(Q(**{f"{self.text_field}__icontains": searchParam}))
        else:
            queryset = queryset

        EMPTY = force_str(_("Empty"))

        if hasattr(self, "filter_role"):
            queryset = getattr(self, "filter_role")(queryset)

        queryset = (
            self.filter_queryset(queryset)
            .annotate(
                filter_id=Coalesce(
                    Cast(F(self.id_field), output_field=models.CharField()),
                    Value("_n"),
                    output_field=models.CharField(),
                ),
                filter_text=Coalesce(
                    Cast(F(self.text_field), output_field=models.CharField()),
                    Value(EMPTY),
                    output_field=models.CharField(),
                ),
            )
            .order_by("filter_text")
            .distinct("filter_text", "filter_id")
            .values("filter_id", "filter_text")
        )

        return queryset

    def get(self, request):
        queryset = self.get_filter_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class IDFilterAPIView(GenericAPIView):
    serializer_class = IDFilterSerializer
    text_field = ""
    id_field = "id"

    def get_filter_queryset(self):
        searchParam = self.request.query_params.get("s")
        queryset = self.get_queryset()

        if searchParam:
            queryset = queryset.filter(Q(**{f"{self.text_field}__icontains": searchParam}))
        else:
            queryset = queryset

        EMPTY = force_str(_("Empty"))

        if hasattr(self, "filter_role"):
            queryset = getattr(self, "filter_role")(queryset)

        queryset = (
            self.filter_queryset(queryset)
            .annotate(
                filter_id=Coalesce(
                    Cast(F(self.id_field), output_field=models.CharField()),
                    Value("_n"),
                    output_field=models.CharField(),
                ),
                filter_text=Coalesce(
                    Cast(F(self.text_field), output_field=models.CharField()),
                    Value(EMPTY),
                    output_field=models.CharField(),
                ),
            )
            .order_by("filter_text")
            .distinct("filter_text", "filter_id")
            .values("filter_id", "filter_text")
        )

        return queryset

    def get(self, request):
        queryset = self.get_filter_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CharFilterAPIView(GenericAPIView):
    serializer_class = CharFilterSerializer
    text_field = ""

    def get_filter_queryset(self):
        searchParam = self.request.query_params.get("s")
        queryset = self.get_queryset()

        if searchParam:
            queryset = queryset.filter(Q(**{f"{self.text_field}__icontains": searchParam}))
        else:
            queryset = queryset

        EMPTY = force_str(_("Empty"))
        queryset = (
            self.filter_queryset(queryset)
            .annotate(init_filter_text=F(self.text_field))
            .annotate(
                filter_value=Case(
                    When(init_filter_text="", then=Value("_e")),
                    When(init_filter_text__isnull=True, then=Value("_n")),
                    default=F("init_filter_text"),
                    output_field=models.CharField(),
                ),
                filter_text=Case(
                    When(
                        Q(init_filter_text="") | Q(init_filter_text__isnull=True),
                        then=Value(EMPTY),
                    ),
                    default=F("init_filter_text"),
                    output_field=models.CharField(),
                ),
            )
            .values("filter_text", "filter_value")
            .order_by("filter_text")
            .distinct("filter_text", "filter_value")
        )

        return queryset

    def get(self, request):
        queryset = self.get_filter_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BooleanFilterAPIView(GenericAPIView):
    serializer_class = BooleanFilterSerializer
    boolean_field = ""
    true_value = _("True")
    false_value = _("False")
    null_value = _("N/A")

    def get_filter_queryset(self):
        queryset = self.get_queryset()

        queryset = (
            self.filter_queryset(queryset)
            .annotate(init_filter_value=F(self.boolean_field))
            .annotate(
                filter_value=Case(
                    When(Q(init_filter_value=True), then=Value("true")),
                    When(Q(init_filter_value=False), then=Value("false")),
                    When(
                        Q(init_filter_value__isnull=True),
                        then=Value("_n"),
                    ),
                    output_field=models.CharField(),
                )
            )
            .annotate(
                filter_text=Case(
                    When(
                        Q(init_filter_value=True),
                        then=Value(force_str(self.true_value)),
                    ),
                    When(
                        Q(init_filter_value=False),
                        then=Value(force_str(self.false_value)),
                    ),
                    When(
                        Q(init_filter_value__isnull=True),
                        then=Value(force_str(self.null_value)),
                    ),
                    output_field=models.CharField(),
                )
            )
            .order_by("filter_text", "filter_value")
            .distinct("filter_text", "filter_value")
            .values("filter_text", "filter_value")
        )
        return queryset

    def get(self, request):
        queryset = self.get_filter_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TextChoiceFilterAPIView(GenericAPIView):
    serializer_class = CharFilterSerializer
    field_name: str = ""
    text_choice_class = None

    def get_choices_dict(self) -> dict:
        choices_dict = dict()
        for value, text in self.text_choice_class.choices:
            if value == "":
                value = "_e"
            choices_dict[value] = text

        choices_dict["_n"] = _("N/A")
        return choices_dict

    def get_filter_queryset(self):
        choices = self.get_choices_dict()

        queryset: models.QuerySet = (
            self.filter_queryset(self.get_queryset())
            .order_by(self.field_name)
            .values_list(self.field_name, flat=True)
            .distinct(self.field_name)
        )

        lst = []

        for value in queryset:
            if value == "":
                value = "_e"

            if value is None:
                value = "_n"

            visible_name = choices.get(value, "N/A")
            obj = {"filter_value": value, "filter_text": visible_name}
            lst.append(obj)

        return lst

    def get(self, request):
        queryset = self.get_filter_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DateTimeRangeFilterAPIView(GenericAPIView):
    serializer_class = DateTimeRangeFilterSerializer
    date_time_field = ""

    def _get_queryset(self):
        qs = self.get_queryset()

        queryset = qs.aggregate(
            filter_min_date_time=Min(self.date_time_field),
            filter_max_date_time=Max(self.date_time_field),
        )
        return queryset

    def get(self, request):
        queryset = self.filter_queryset(self._get_queryset())
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TextChoiceListAPIView(GenericAPIView):
    serializer_class = TextChoiceSerializer
    choices_class = None

    def get_queryset(self):
        choices = [{"label": choice[1], "value": choice[0]} for choice in self.choices_class.choices]
        return choices

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
