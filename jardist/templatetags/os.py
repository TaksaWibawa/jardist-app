from django import template
import os

register = template.Library()

@register.filter
def basename(value):
    return os.path.basename(value)

@register.filter
def zip_lists(a, b):
    return zip(a, b)