from django_filters import filters
from django.db.models import Q
from rest_framework.fields import CharField
from rest_framework.filters import SearchFilter
from django.utils.text import smart_split, unescape_string_literal


def search_smart_split(search_terms):
    split_terms = []
    for term in smart_split(search_terms):
        term = term.strip(",")
        if term.startswith(('"', "'")) and term[0] == term[-1]:
            split_terms.append(unescape_string_literal(term))
        else:
            for sub_term in term.split(","):
                if sub_term:
                    split_terms.append(sub_term)
    return split_terms


class CustomSearchFilter(SearchFilter):
    def get_search_terms(self, request):
        value = request.query_params.get(self.search_param, "")
        if not value:
            return []
        field = CharField(trim_whitespace=False, allow_blank=True)
        cleaned_value = field.run_validation(value)
        # Split the search term into individual words for better search
        return [term.strip() for term in cleaned_value.split() if term.strip()]


class ListIDFilter(filters.Filter):
    null_value = "_n"
    EMPTY_VALUES = ([], (), {}, "", None)

    def filter(self, qs, value):
        if value in self.EMPTY_VALUES:
            return qs

        self.lookup_expr = "in"
        values: list = value.split(",")
        modified_values = []
        use_null = False

        for val in values:
            if val == self.null_value:
                use_null = True
                continue

            try:
                int(val)
                modified_values.append(val)
            except Exception:
                continue

        if self.distinct:
            qs = qs.distinct()

        if use_null:
            qs = self.get_method(qs)(
                Q(
                    **{
                        "%s__%s" % (self.field_name, self.lookup_expr): modified_values,
                    }
                )
                | Q(**{"%s__%s" % (self.field_name, "isnull"): True})
            )
        else:
            qs = self.get_method(qs)(**{"%s__%s" % (self.field_name, self.lookup_expr): modified_values})
        return qs


class ListBooleanFilter(filters.CharFilter):
    false_value = "false"
    true_value = "true"
    null_value = "_n"
    EMPTY_VALUES = ([], (), {}, "", None)

    def filter(self, qs, value):
        if value in self.EMPTY_VALUES:
            return qs

        values = value.split(",")
        modified_values = []
        use_true = False
        use_false = False
        use_null = False

        for val in values:
            if val == self.true_value and True not in modified_values:
                use_true = True
            elif val == self.false_value and False not in modified_values:
                use_false = True
            elif val == self.null_value:
                use_null = True

        use_all = use_true and use_false and use_null
        use_all_value = use_true and use_false
        use_one_value = use_true or use_false or use_null

        if use_all:
            qs = self.get_method(qs)(
                Q(**{self.field_name: True})
                | Q(**{self.field_name: False})
                | Q(**{"%s__%s" % (self.field_name, "isnull"): True})
            )

        elif use_all_value:
            qs = self.get_method(qs)(Q(**{self.field_name: True}) | Q(**{self.field_name: False}))

        elif use_one_value:
            if use_true:
                qs = self.get_method(qs)(Q(**{self.field_name: True}))

            elif use_false:
                qs = self.get_method(qs)(Q(**{self.field_name: False}))

            elif use_null:
                qs = self.get_method(qs)(Q(**{"%s__%s" % (self.field_name, "isnull"): True}))

        return qs.distinct() if self.distinct else qs


class ListCharFilter(filters.CharFilter):
    empty_value = "_e"
    null_value = "_n"
    EMPTY_VALUES = ([], (), {}, "", None)

    def filter(self, qs, value):
        if value in self.EMPTY_VALUES:
            return qs

        self.lookup_expr = "in"
        values = value.split(",")
        modified_values = []
        use_null = False

        for val in values:
            if val == self.empty_value:
                val = ""
            if val == self.null_value:
                use_null = True
                continue

            modified_values.append(val)

        if use_null:
            qs = self.get_method(qs)(
                Q(
                    **{
                        "%s__%s" % (self.field_name, self.lookup_expr): modified_values,
                    }
                )
                | Q(**{"%s__%s" % (self.field_name, "isnull"): True})
            )
        else:
            qs = self.get_method(qs)(**{"%s__%s" % (self.field_name, self.lookup_expr): modified_values})
        return qs.distinct() if self.distinct else qs
