from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_groups')
def has_groups(user, group_names):
    group_list = group_names.split(',')
    groups = Group.objects.filter(name__in=group_list)
    return user.groups.filter(id__in=groups).exists()