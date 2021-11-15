from .sort import sort_by_attribute, sort_tags_by_usage
from .structs import *

def generate_conditions_input(required_keys: list, unverified_data: dict) -> str:
    conditions = []
    for key in required_keys:
        assert unverified_data.get(key), "Query not specific enough for Models.get()."
        conditions.append(f"{key} = %s")

    conditions = " AND ".join(conditions) # transform from list to string
    return conditions

def generate_data_input(required_keys: list, unverified_data: dict) -> tuple:
    data = []
    for key in required_keys:
        assert unverified_data.get(key), "Query not specific enough for Models.get()."
        data.append(unverified_data[key])

    data = tuple(data) # transform from list to tuple
    return data
