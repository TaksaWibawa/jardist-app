from django import template
import locale

register = template.Library()

@register.filter
def currency(value):
    locale.setlocale(locale.LC_ALL, 'id_ID.utf8')
    formatted_value = locale.currency(value, grouping=True, symbol='')
    return "Rp. " + formatted_value