from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def row_color(end_date, status):
    today = datetime.today().date()
    if status.lower() == 'selesai':
        return 'table-success'
    elif end_date < today:
        return 'table-danger'
    elif today + timedelta(days=7) >= end_date:
        return 'table-warning'
    else:
        return 'table-primary'