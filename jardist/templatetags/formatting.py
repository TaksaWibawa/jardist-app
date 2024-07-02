from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def currency(value):
    value_str = "{:.2f}".format(value)
    whole, fraction = value_str.split('.')
    whole_with_separator = ".".join([whole[max(i-3, 0):i] for i in range(len(whole), 0, -3)][::-1])
    
    formatted_value = whole_with_separator + ',' + fraction
    return "Rp " + formatted_value

@register.filter
def add_days(value, arg):
    return value + timedelta(days=arg)

@register.filter
def replace(value, args):
    original, new = args.split(',')
    return value.replace(original, new)