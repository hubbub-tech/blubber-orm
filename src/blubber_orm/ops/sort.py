import pytz
from datetime import datetime

def sort_by_attribute(blubber_list, attribute, reverse=False):
    _blubber_list = [obj for obj in blubber_list]
    assert len(_blubber_list) > 0, "SortError: Your list must be getter than zero to sort."
    if attribute in _blubber_list[0].__dict__.keys():
        uniform_model_type = type(_blubber_list[0])
        for blubber_object in _blubber_list:
            if uniform_model_type != type(blubber_object):
                raise Exception("Your list must be of a uniform type.")
        _blubber_list.sort(key = lambda _object: _object.__dict__[attribute], reverse=reverse)
        return _blubber_list
    else:
        #TODO: also consider the case where an attribute is failed but it's protected
        raise Exception("The attribute you passed does not belong to this model.")

def sort_tags_by_usage(tags, reverse=False):
    # NOTE: maybe iterate through the tags to count the associated items
    return tags
