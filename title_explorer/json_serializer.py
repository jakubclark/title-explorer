import json
from datetime import date


def json_serializer(o):
    if isinstance(o, date):
        return o.__str__()


def dumps(obj):
    res = json.dumps(obj, indent=2, default=json_serializer)
    return res
