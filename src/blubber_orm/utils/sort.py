import pytz
from datetime import datetime

def blubber_sort(instances, attr, reverse=False):
    assert len(instances) > 0

    _instances = instances.copy()
    _instance = _instances[0]

    assert _instance.__dict__.get(attr) is not None

    ModelsClass = type(_instance)
    for _instance in _instances:
        assert isinstance(_instance, ModelsClass)
    _instances.sort(key = lambda model: model.__dict__[attr], reverse=reverse)
    return _instances


def sort_tags_by_usage(tags, reverse=False): return tags
