from django import template
from datetime import datetime
from num2words import num2words as _num2words

register = template.Library()


@register.filter
def date(value, format="%Y-%m-%d %H:%M"):
    if not value:
        return value

    date = datetime.fromisoformat(value)
    return datetime.strftime(date, format)


@register.filter
def num2words(value, to="currency", lang="ar", currency="EGP") -> str:
    if not value:
        return value
    try:
        float(value)
    except ValueError:
        return value
    else:
        text = _num2words(value, lang=lang, to=to, currency=currency)
        return text
