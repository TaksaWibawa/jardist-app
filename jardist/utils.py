import math

def clean_decimal_field(value):
    if value in [None, ''] or (isinstance(value, float) and math.isnan(value)):
        return 0.0
    elif isinstance(value, str):
        return float(value.replace(',', ''))
    else:
        return float(value)