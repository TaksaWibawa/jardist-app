import math

def clean_decimal_field(value):
    print(type(value), value)
    if value in [None, ''] or (isinstance(value, float) and math.isnan(value)):
        print('None')
        return 0.0
    elif isinstance(value, str):
        return float(value.replace(',', ''))
    else:
        return float(value)