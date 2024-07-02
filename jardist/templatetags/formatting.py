from django import template
from datetime import timedelta
import locale

register = template.Library()

@register.filter
def currency(value):
    try:
        locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'id_ID.utf8')
        except locale.Error:
            pass
    formatted_value = locale.currency(value, grouping=True, symbol='')
    return "Rp. " + formatted_value

@register.filter
def add_days(value, arg):
    return value + timedelta(days=arg)

@register.filter
def replace(value, args):
    original, new = args.split(',')
    return value.replace(original, new)