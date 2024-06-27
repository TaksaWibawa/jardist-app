from django import template
from datetime import timedelta
import locale

register = template.Library()

@register.filter
def currency(value):
    locale.setlocale(locale.LC_ALL, 'id_ID.utf8')
    formatted_value = locale.currency(value, grouping=True, symbol='')
    return "Rp. " + formatted_value

@register.filter
def add_days(value, arg):
    return value + timedelta(days=arg)