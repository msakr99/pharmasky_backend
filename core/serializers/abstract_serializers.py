from rest_framework import serializers
from urllib.parse import urlencode
from accounts.models import Pharmacy, User
from core.validators import file_validators
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from phonenumber_field.serializerfields import PhoneNumberField
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
import pandas as pd

from core.views.mixins import RoleViewMixin


class BaseSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)
        exclude = kwargs.pop("exclude", None)
        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        context = kwargs.get("context", None)
        if context:
            self.request = context.get("request", None)

        assert not (fields is not None and exclude is not None), "Only one of 'field' or 'exclude' should be passed."

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        elif exclude is not None:
            for field_name in exclude:
                self.fields.pop(field_name, None)


class BaseModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)
        exclude = kwargs.pop("exclude", None)
        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        context = kwargs.get("context", None)
        if context:
            self.request = context.get("request", None)

        assert not (fields is not None and exclude is not None), "Only one of 'field' or 'exclude' should be passed."

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        elif exclude is not None:
            for field_name in exclude:
                self.fields.pop(field_name, None)

    # def get_fields(self):
    #     fields = super().get_fields()

    #     for field_name in fields:
    #         field = fields[field_name]
    #         if isinstance(field, CustomPrimaryKeyRelatedField):
    #             assert hasattr(
    #                 self, f"get_{field_name}_queryset"
    #             ), f"""
    #             get_{field_name}_queryset is missing in {self.__class__.__name__} field {field_name}
    #             """
    #             field.queryset = getattr(self, f"get_{field_name}_queryset")()

    #         elif isinstance(field, serializers.ListField):
    #             if isinstance(field.child, CustomPrimaryKeyRelatedField):
    #                 assert hasattr(
    #                     self, f"get_{field_name}_children_queryset"
    #                 ), f"""
    #                 get_{field_name}_children_queryset is missing in {self.__class__.__name__} field {field_name}
    #                 """
    #                 field.child.queryset = getattr(
    #                     self, f"get_{field_name}_children_queryset"
    #                 )()

    #     return fields


class UserRolePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField, RoleViewMixin):
    def __init__(self, roles=None, filter_role_use_pk=None, additional_role_filter=None, **kwargs):
        self.role_filter = roles
        self.filter_role_use_pk = filter_role_use_pk
        self.additional_role_filter = additional_role_filter
        super().__init__(**kwargs)

    def _get_user(self) -> User:
        try:
            request = getattr(self.parent, "request")
            return request.user
        except Exception as e:
            raise e

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.role_filter is not None:
            queryset = self.filter_role(queryset)
        return queryset


class BaseUserCreateSerializer(BaseModelSerializer):
    username = PhoneNumberField(
        region="EG",
        validators=[
            UniqueValidator(
                queryset=get_user_model().objects.all(),
                message=_("Phone number already exists."),
            ),
        ],
    )
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs.get("password", None)
        confirm_password = attrs.pop("confirm_password", None)

        if password != confirm_password:
            raise ValidationError({"confirm_password": _("Passwords does not match.")})

        validate_password(password)
        attrs["is_active"] = False
        return super().validate(attrs)

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance: Pharmacy = super().create(validated_data)
        instance.set_password(password)
        instance.save()
        return instance


class BaseUploaderSerializer(serializers.Serializer):
    file = serializers.FileField(
        validators=[
            file_validators.EXCEL_VALIDATOR,
            file_validators.validate_excel_extension,
        ]
    )
    required_columns = []
    additional_values = []

    def validate_file(self, value):
        # Read the file into a Pandas DataFrame
        dataset = pd.read_excel(value)

        FILE_COLUMNS = [col.lower().strip() for col in dataset.columns]

        columns_not_found = []
        for required_column in self.required_columns:
            if required_column not in FILE_COLUMNS:
                columns_not_found.append(required_column)

        if columns_not_found:
            raise ValidationError(
                _(
                    "Could not find [{columns_not_found_str}] in columns, please make sure the files contains the required columns."
                ).format(columns_not_found_str=", ".join(columns_not_found))
            )

        return value

    def _validate_column_value(self, column_name, row_value, line_number):
        try:
            fn = getattr(self, "validate_column_{}".format(column_name))

            if fn is None:
                return None, False

            _v = fn(row_value, line_number)
            return _v, False

        except ValidationError as err:
            return err.detail, True

    def _get_column_value(self, additional_value, row_values, validated_row_values, line_number):
        try:
            fn = getattr(self, "get_value_{}".format(additional_value), None)

            if fn is None:
                return None, False

            _v = fn(row_values, validated_row_values, line_number)
            return _v, False

        except ValidationError as err:
            return err.detail, True

    def validate_file_data(self, file):
        dataset = pd.read_excel(file)

        errs = []
        data = []

        for index, row in dataset.iterrows():
            row_errs = {}
            obj = {}
            line_number = index + 1

            row_values = {}
            validated_row_values = {}

            for column_name in self.required_columns:
                row_value = row.get(column_name, None)

                if pd.isna(row_value):
                    row_value = None

                _v, _e = self._validate_column_value(column_name, row_value, line_number)

                if _e:
                    row_errs[column_name] = _v
                else:
                    row_values[column_name] = row_value
                    validated_row_values[column_name] = _v
                    obj[column_name] = _v

            if row_errs:
                errs.append(row_errs)
                continue

            for additional_value in self.additional_values:
                _v, _e = self._get_column_value(additional_value, row_values, validated_row_values, line_number)
                if _e:
                    row_errs[additional_value] = _v
                else:
                    obj[additional_value] = _v

            if row_errs:
                errs.append(row_errs)
                continue

            data.append(obj)

        if errs:
            raise ValidationError({"file": errs})

        return {"data": data}

    def validate(self, attrs):
        file = attrs.get("file")
        attrs.update(self.validate_file_data(file))
        return super().validate(attrs)


class QueryParameterHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    def __init__(self, view_name=None, query_param=None, additional_query_params=None, **kwargs):
        self.qp = query_param
        self.additional_query_params = additional_query_params

        if self.additional_query_params is not None:
            assert type(self.additional_query_params) == dict, "additional query params should be of type dict."

        super().__init__(view_name, **kwargs)

    def get_url(self, obj, view_name, request, format):
        lookup_field_value = getattr(obj, self.lookup_field, None)
        query_params = {self.qp: lookup_field_value}

        if self.additional_query_params is not None:
            query_params.update(self.additional_query_params)

        result = "{}?{}".format(
            self.reverse(view_name, kwargs={}, request=request, format=format),
            urlencode(query_params),
        )
        return result


class ExtendedPhoneNumberField(PhoneNumberField):
    FORMATS = ["E", "INT", "RFC"]

    def __init__(self, *args, region=None, format="INT", **kwargs):
        assert format in self.FORMATS, """Phone number format is not allowed"""
        self.format = format
        super().__init__(*args, region=region, **kwargs)

    def to_representation(self, value):
        match self.format:
            case "E":
                value = value.as_e164
            case "INT":
                value = value.as_international
            case "RFC":
                value = value.as_rfc3966

        return str(value)


class IDFilterSerializer(serializers.Serializer):
    filter_id = serializers.CharField()
    filter_text = serializers.CharField()


class CharFilterSerializer(serializers.Serializer):
    filter_value = serializers.CharField()
    filter_text = serializers.CharField()


class BooleanFilterSerializer(serializers.Serializer):
    filter_value = serializers.CharField()
    filter_text = serializers.CharField()


class DateTimeRangeFilterSerializer(serializers.Serializer):
    filter_min_date_time = serializers.DateTimeField()
    filter_max_date_time = serializers.DateTimeField()


class TextChoiceSerializer(serializers.Serializer):
    label = serializers.CharField(read_only=True)
    value = serializers.CharField(read_only=True)
