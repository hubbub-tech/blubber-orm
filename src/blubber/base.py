from blubber.db import get_db, close_db, sql_to_dictionary

class Models:
    table_name = None
    _cur, _conn = get_db() #inefficient that this needs to load for every Models instance and insecure that it stays open

    def __init__(self):
        self.table_columns = self._get_columns()

    @classmethod
    def insert(cls, attributes):
        attributes_str = ", ".join(attributes.keys())
        values = ["%s" for attribute in attributes.values()]
        values_str = ", ".join(values)
        SQL = f"INSERT INTO {cls.table_name} ({attributes_str}) VALUES ({values_str});"
        data = tuple(attributes.values())
        cls._cur.execute(SQL, data)
        cls._conn.commit()

    @classmethod
    def get(cls, id):
        SQL = f"SELECT * FROM {cls.table_name} WHERE id = %s;" # Note: no quotes
        data = (id, )
        cls._cur.execute(SQL, data)
        db_obj = sql_to_dictionary(cls._cur, cls._cur.fetchone())
        return cls(db_obj)

    @classmethod
    def set(cls, id, attributes):
        conditions = [f"{attributes} = %s" for attributes in attributes.keys()]
        conditions_str = " AND ".join(conditions)
        updates = [parameters for parameters in attributes.values()]
        SQL = f"UPDATE {cls.table_name} SET {conditions_str} WHERE id = %s;" # Note: no quotes
        data = tuple(updates + [id])
        cls._cur.execute(SQL, data)
        cls._conn.commit()

    @classmethod
    def filter(cls, filters):
        conditions = [f"{filter} = %s" for filter in filters.keys()]
        conditions_str = " AND ".join(conditions)
        SQL = f"SELECT * FROM {cls.table_name} WHERE {conditions_str};" # Note: no quotes
        data = tuple([parameters for parameters in filters.values()])
        cls._cur.execute(SQL, data)
        obj_list = []
        for query in cls._cur.fetchall():
            db_obj = sql_to_dictionary(cls._cur, query)
            obj_list.append(cls(db_obj))
        return obj_list # query here

    @classmethod
    def delete(cls, id):
        SQL = f"DELETE * FROM {cls.table_name} WHERE id = %s;" # Note: no quotes
        data = (id, )
        cls._cur.execute(SQL, data)
        cls._conn.commit()

    @classmethod
    def is_indexed(cls, query_column_names):
        return set(query_column_names).issubset(cls.table_columns)

    def _get_columns(self):
        self._cur.execute(f"SELECT * FROM {self.table_name} LIMIT 0")
        columns = [attribute.name for attribute in self._cur.description]
        return columns

    def refresh(self):
        cls = type(self)
        self = cls.get(self.id)

    def __repr__(self):
        model = self.table_name.capitalize()
        return f"<type: {model}>"
