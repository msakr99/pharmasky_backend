from django import forms


FORM_CONTROL_WIDGETS = (
    forms.TextInput,
    forms.URLInput,
    forms.Textarea,
    forms.Select,
    forms.NumberInput,
    forms.ModelChoiceField,
)

TABLE_VIEW_CONTROL_WIDGETS = (forms.Textarea,)


class BaseForm(forms.ModelForm):
    def __init__(self, fields=[], ex_fields=[], *args, **kwargs):
        self.context = kwargs.pop('context', None)
        super().__init__(*args, **kwargs)

        if fields:
            _fields = {}
            for field_name in self.fields.keys():
                if field_name in fields:
                    _fields[field_name] = self.fields[field_name]

            self.fields = _fields

        elif ex_fields:
            _fields = {}
            for field_name in self.fields.keys():
                if not field_name in ex_fields:
                    _fields[field_name] = self.fields[field_name]

            self.fields = _fields

        for visible in self.visible_fields():
            if isinstance(visible.field.widget, FORM_CONTROL_WIDGETS):
                visible.field.widget.attrs["placeholder"] = visible.field.label
                visible.field.widget.attrs["class"] = "form-control"
                if visible.errors:
                    visible.field.widget.attrs["class"] = "form-control is-invalid"
            elif isinstance(visible.field.widget, forms.CheckboxInput):
                visible.field.widget.attrs["class"] = "form-check-input"
                if visible.errors:
                    visible.field.widget.attrs["class"] = "form-check-input is-invalid"

            if isinstance(visible.field.widget, TABLE_VIEW_CONTROL_WIDGETS):
                visible.field.widget.attrs["data_view_type"] = "TABLE"
