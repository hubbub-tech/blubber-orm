from abc import ABC, abstractmethod
from .db import DatabaseConnection, sql_to_dictionary

class AbstractModels(ABC):
    """
    AbstractModels defines the basic functions that each of the Models should
    come with: CREATE (insert), READ (get, filter), UPDATE (set), and DESTROY
    (delete).

    Some other default attributes are `table_name` and `database`. These do
    not correspond to columns from the Hubbub database, but rather are functional.
    these attributes are different between child classes but NOT between
    instances of that class. They are meant to power psycopg2 queries.

    """

    table_name = None
    table_columns = None
    table_primaries = None
    database = DatabaseConnection.get_instance()

    @classmethod
    @abstractmethod
    def insert(cls, attributes):
        pass

    @classmethod
    @abstractmethod
    def get(cls, id):
        pass

    @classmethod
    @abstractmethod
    def set(cls, id, attributes):
        pass

    @classmethod
    @abstractmethod
    def filter(cls, filters):
        pass

    @classmethod
    @abstractmethod
    def _get_columns(cls):
        pass

    @abstractmethod
    def refresh(self):
        pass

class Models(AbstractModels):

    @classmethod
    def insert(cls, attributes):
        attributes_str = ", ".join(attributes.keys())
        placeholders = ["%s" for attribute in attributes.values()]
        placeholders_str = ", ".join(placeholders)
        primaries_str = ", ".join(cls.table_primaries)
        SQL = f"INSERT INTO {cls.table_name} ({attributes_str}) VALUES ({placeholders_str}) RETURNING {primaries_str};"
        data = tuple(attributes.values())
        cls.database.cursor.execute(SQL, data)
        cls.database.connection.commit()

        primary_key = sql_to_dictionary(cls.database.cursor, cls.database.cursor.fetchone())
        if len(primary_key.keys()) == 1:
            primary_key, = primary_key.values()
        new_entry = cls.get(primary_key)
        return new_entry

    @classmethod
    def get(cls, id):
        SQL = f"SELECT * FROM {cls.table_name} WHERE id = %s;" # Note: no quotes
        data = (id, )
        cls.database.cursor.execute(SQL, data)
        db_obj = sql_to_dictionary(cls.database.cursor, cls.database.cursor.fetchone())
        return cls(db_obj)

    @classmethod
    def set(cls, id, attributes):
        conditions = [f"{attributes} = %s" for attributes in attributes.keys()]
        conditions_str = ", ".join(conditions)
        updates = [parameters for parameters in attributes.values()]
        SQL = f"UPDATE {cls.table_name} SET {conditions_str} WHERE id = %s;" # Note: no quotes
        data = tuple(updates + [id])
        cls.database.cursor.execute(SQL, data)
        cls.database.connection.commit()

    @classmethod
    def filter(cls, filters):
        conditions = [f"{filter} = %s" for filter in filters.keys()]
        conditions_str = " AND ".join(conditions)
        SQL = f"SELECT * FROM {cls.table_name} WHERE {conditions_str};" # Note: no quotes
        data = tuple([parameters for parameters in filters.values()])
        cls.database.cursor.execute(SQL, data)
        obj_list = []
        for query in cls.database.cursor.fetchall():
            db_obj = sql_to_dictionary(cls.database.cursor, query)
            obj_list.append(cls(db_obj))
        return obj_list # query here

    @classmethod
    def delete(cls, id):
        SQL = f"DELETE * FROM {cls.table_name} WHERE id = %s;" # Note: no quotes
        data = (id, )
        cls.database.cursor.execute(SQL, data)
        cls.database.connection.commit()

    #returns the element that was not in the table columns so you can fix
    @classmethod
    def check_columns(cls, query_column_names):
        _query_column_names = query_column_names
        _comparison_column_name = _query_column_names.pop(0)
        if set([_comparison_column_name]).issubset(cls._get_columns()):
            if len(_query_column_names) > 0:
                return cls.check_columns(_query_column_names)
            else:
                return True
        else:
            #TODO: make an exception that logs to error file
            print("This element was not in column names: ", _comparison_column_name)
            return False

    @classmethod
    def _get_columns(cls):
        if not cls.table_columns:
            cls.database.cursor.execute(f"SELECT * FROM {cls.table_name} LIMIT 0")
            columns = [attribute.name for attribute in cls.database.cursor.description]
            cls.table_columns = columns
        return cls.table_columns

    def refresh(self):
        cls = type(self)
        self = cls.get(self.id)

    def __repr__(self):
        model = self.table_name.capitalize()
        return f"<type: {model}>"
