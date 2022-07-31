def format_query_statement(required_keys: list, unverified_data: dict) -> str:
    statement = []
    for rkey in required_keys:
        assert unverified_data.get(rkey) is not None, "Query not specific enough for Models.get()."
        statement.append(f"{rkey} = %s")

    statement = " AND ".join(statement)
    return statement


def format_query_data(required_keys: list, unverified_data: dict) -> tuple:
    data = []
    for rkey in required_keys:
        assert unverified_data.get(rkey) is not None, "Query not specific enough for Models.get()."
        data.append(unverified_data[rkey])

    data = tuple(data)
    return data
