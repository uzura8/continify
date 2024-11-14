import json
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def decimal_default(obj):
    if isinstance(obj, Decimal):
        if int(obj) == obj:
            return int(obj)
        return float(obj)
    raise TypeError
