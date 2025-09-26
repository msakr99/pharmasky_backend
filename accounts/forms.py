from typing import Any
from django.contrib.auth.forms import AuthenticationForm as _AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import (
    BaseUserCreationForm as _BaseUserCreationForm,
    UserChangeForm as _UserChangeForm,
)
from phonenumber_field.formfields import PhoneNumberField
from django import forms
from accounts.choices import Role


class BaseUserCreationForm(_BaseUserCreationForm):
    username = PhoneNumberField()
    role = forms.ChoiceField(choices=Role.choices)
    name = forms.CharField(max_length=200)


class UserChangeForm(_UserChangeForm):
    username = PhoneNumberField()


class AuthenticationForm(_AuthenticationForm):
    def __init__(self, request: Any = ..., *args: Any, **kwargs: Any) -> None:
        super().__init__(request, *args, **kwargs)

        fields = self.fields
        fields["username"].label = "Mobile number"

        for visible in self.visible_fields():
            visible.field.widget.attrs["placeholder"] = visible.field.label
            visible.field.widget.attrs["class"] = "form-control"
            if visible.errors:
                visible.field.widget.attrs["class"] = "form-control is-invalid"
