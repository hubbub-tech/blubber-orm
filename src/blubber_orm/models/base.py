import json
from datetime import datetime, date
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

    table_name => must be defined in every child class to tell what table the
    model reflects. This is a class-level attribute not changed between instances.

    tables_columns => defined on the first call of _get_columns and is a class-level
    attribute and not changed between instances.

    table_primaries => defines the primary key(s) of the modeled table. Class-level
    attribute.

    database => stored database connection and cursor for SQL scripts.
    """

    table_name = None
    table_columns = None
    table_primaries = None
    database = DatabaseConnection.get_instance()

    @classmethod
    @abstractmethod
    def insert(cls, attributes):
        """
        Insert a new row of data into the table connected to the child model.
        This daata is accepted as a dictionary with the column name as dictionary
        key and the value in the dictionary value.

        This function is defined in Models base class and inherited across models.py.
        There shouldn't be any reason to add/remove functionality from the Models
        definition.
        """

    @classmethod
    @abstractmethod
    def get(cls, id):
        """
        Get a row of data from the table connected to the child model by the
        primary key(s). The default is to take one primary key called `id`.
        When a table has multiple primary keys or a primary key not named `id`,
        this function should be redefined to accept a dictionary of keys.
        """

    @classmethod
    @abstractmethod
    def get_all(cls):
        """
        Get all rows from this table.
        """

    @classmethod
    @abstractmethod
    def set(cls, id, attributes):
        """
        Edit data in a particular row by passing its primary key(s) and the changes
        in a dictionary. If the item has multiple primary keys, again, redefine
        the function to take a dictionary of keys instead.
        """

    @classmethod
    @abstractmethod
    def filter(cls, filters):
        """
        Pass the filter(s) in a dictionary where the keys are the columns on which
        to filter and the values are the requirements for those columns. Should
        not be redefined after inheriting Models.
        """

    @classmethod
    @abstractmethod
    def _get_columns(cls):
        """
        An internal function which calls the columns for the table linked to the
        model.
        """

    @abstractmethod
    def refresh(self):
        """
        After an object has been updates, refresh allows you to quickly refresh
        the instance with the updates.
        """

class Models(AbstractModels):
    """
    All Models of Hubbub database tables should inherit this Models base class.

    NOTE: if you try to define this class, IT WILL NOT WORK. It must be inherited,
    with the child class providing all of the specifics which connect the Model to
    the database table.
    """

    @classmethod
    def insert(cls, attributes):
        debug = Models.database._debug

        attributes_str = ", ".join(attributes.keys())
        placeholders = ["%s" for attribute in attributes.values()]
        placeholders_str = ", ".join(placeholders)
        primaries_str = ", ".join(cls.table_primaries)
        SQL = f"INSERT INTO {cls.table_name} ({attributes_str}) VALUES ({placeholders_str}) RETURNING {primaries_str};"
        data = tuple(attributes.values())
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        if debug:
            print("SQL command: ", SQL)
            print("Data: ", data)
            print("Database cursor: ", Models.database.cursor)

        result = Models.database.cursor.fetchone()
        primary_key = sql_to_dictionary(Models.database.cursor, result)
        if len(primary_key.keys()) == 1:
            primary_key, = primary_key.values()
        new_entry = cls.get(primary_key)
        return new_entry

    @classmethod
    def get(cls, id):
        debug = Models.database._debug

        obj = None
        SQL = f"SELECT * FROM {cls.table_name} WHERE id = %s;" # Note: no quotes
        data = (id, )
        Models.database.cursor.execute(SQL, data)

        if debug:
            print("SQL command: ", SQL)
            print("Data: ", data)
            print("Database cursor: ", Models.database.cursor)
        result = Models.database.cursor.fetchone()
        if result:
            db_obj = sql_to_dictionary(Models.database.cursor, result)
            obj = cls(db_obj)
        return obj

    @classmethod
    def get_all(cls):
        debug = Models.database._debug

        SQL = f"SELECT * FROM {cls.table_name};" # Note: no quotes
        Models.database.cursor.execute(SQL)

        if debug:
            print("SQL command: ", SQL)
            print("Database cursor (fetch sample): ", Models.database.cursor)

        obj_list = []
        results = Models.database.cursor.fetchall()
        for query in results:
            db_obj = sql_to_dictionary(Models.database.cursor, query)
            obj_list.append(cls(db_obj))
        return obj_list

    @classmethod
    def set(cls, id, attributes):
        debug = Models.database._debug

        conditions = [f"{attributes} = %s" for attributes in attributes.keys()]
        conditions_str = ", ".join(conditions)
        updates = [parameters for parameters in attributes.values()]
        SQL = f"UPDATE {cls.table_name} SET {conditions_str} WHERE id = %s;" # Note: no quotes
        data = tuple(updates + [id])
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        if debug:
            print("SQL command: ", SQL)
            print("Data: ", data)

    @classmethod
    def filter(cls, filters):
        debug = Models.database._debug

        conditions = [f"{filter} = %s" for filter in filters.keys()]
        conditions_str = " AND ".join(conditions)
        SQL = f"SELECT * FROM {cls.table_name} WHERE {conditions_str};" # Note: no quotes
        data = tuple([parameters for parameters in filters.values()])
        Models.database.cursor.execute(SQL, data)

        if debug:
            print("SQL command: ", SQL)
            print("Data: ", data)
            print("Database cursor (fetch sample): ", Models.database.cursor)

        obj_list = []
        results = Models.database.cursor.fetchall()
        for query in results:
            db_obj = sql_to_dictionary(Models.database.cursor, query)
            obj_list.append(cls(db_obj))
        return obj_list # query here

    @classmethod
    def like(cls, attribute, key):
        debug = Models.database._debug

        SQL = f"SELECT * FROM {cls.table_name} WHERE {attribute} ILIKE %s;"
        data = (key,)
        Models.database.cursor.execute(SQL, data)

        if debug:
            print("SQL command: ", SQL)
            print("Data: ", data)
            print("Database cursor (fetch sample): ", Models.database.cursor)

        obj_list = []
        results = Models.database.cursor.fetchall()
        for query in results:
            db_obj = sql_to_dictionary(Models.database.cursor, query)
            obj_list.append(cls(db_obj))
        return obj_list

    @classmethod
    def delete(cls, id):
        debug = Models.database._debug

        SQL = f"DELETE FROM {cls.table_name} WHERE id = %s;" # Note: no quotes
        data = (id, )
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        if debug:
            print("SQL command: ", SQL)
            print("Data: ", data)

    #returns the element that was not in the table columns so you can fix
    @classmethod
    def check_columns(cls, query_column_names):
        """
        A controlled check to see if the list of queried columns (passed in), is
        actually a subset of the columns defined in the table.

        If not, then return False and print the name of the first entry to fail
        the check.
        """
        debug = Models.database._debug
        _query_column_names = query_column_names
        _comparison_column_name = _query_column_names.pop(0)
        if set([_comparison_column_name]).issubset(cls._get_columns()):
            if len(_query_column_names) > 0:
                return cls.check_columns(_query_column_names)
            else:
                return True
        else:
            #TODO: make an exception that logs to error file
            if debug:
                print(f"[{cls.table_name}.check_columns()] NotTableColumnError, value: ", _comparison_column_name)
            return False

    @classmethod
    def _get_columns(cls):
        debug = Models.database._debug

        if cls.table_columns is None:
            Models.database.cursor.execute(f"SELECT * FROM {cls.table_name} LIMIT 0")
            columns = [attribute.name for attribute in Models.database.cursor.description]
            cls.table_columns = columns

            if debug:
                print("Column names initialized as: ", cls.table_columns)
        return cls.table_columns

    def to_dict(self, serializable=True):
        _self_dict = self.__dict__
        if serializable:
            _serializable_dict = {}
            for key, value in _self_dict.items():
                if key[0] == "_":
                    key = key[1:]
                if isinstance(value, datetime):
                    _serializable_dict[key] = value.strftime("%Y-%m-%d %H:%M:%S.%f")
                elif isinstance(value, date):
                    _serializable_dict[key] = value.strftime("%Y-%m-%d")
                else:
                    _serializable_dict[key] = value
            _self_dict = _serializable_dict
        return _self_dict

    @classmethod
    def does_row_exist(cls, details, table=None):
        debug = Models.database._debug

        conditions = [f"{detail} = %s" for detail in details.keys()]
        conditions_str = " AND ".join(conditions)
        if table is None:
            table = cls.table_name
        SQL = f"SELECT * FROM {table} WHERE {conditions_str};"
        data = tuple([detail for detail in details.values()])
        Models.database.cursor.execute(SQL, data)

        if debug:
            print("SQL command: ", SQL)
            print("Data: ", data)
            print("Database cursor (fetch sample): ", Models.database.cursor)

        return Models.database.cursor.fetchone() is not None

    def __repr__(self):
        model = self.table_name.capitalize()
        return f"<type: {model}>"

    def __eq__(self, other) :
        return self.__dict__ == other.__dict__
