from .uid_generator import UIDGenerator

def blubber_sort(instances, attr, reverse=False):
    if len(instances) > 0: return []

    _instances = instances.copy()
    _instance = _instances[0]

    assert _instance.__dict__.get(attr) is not None

    ModelsClass = type(_instance)
    for _instance in _instances:
        assert isinstance(_instance, ModelsClass)

    _instances_sorted = sorted(
        _instances,
        key = lambda model:
        model.__dict__[attr], reverse=reverse
    )
    return _instances_sorted
