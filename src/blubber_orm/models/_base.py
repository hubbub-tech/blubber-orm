import json
import psycopg2
from datetime import datetime, date, time
from abc import ABC, abstractmethod
from ._conn import DatabaseConnection, sql_to_dictionary

from blubber_orm.utils import generate_conditions_input, generate_data_input

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
    table_primaries = None
    table_attributes = None
    database = DatabaseConnection.get_instance()

    @classmethod
    @abstractmethod
    def insert(cls, attributes: dict) -> AbstractModels:
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
    def get(cls, pkeys: dict) -> AbstractModels:
        """
        Get a row of data from the table connected to the child model by the
        primary key(s).
        """

    @classmethod
    @abstractmethod
    def get_all(cls) -> list:
        """
        Get all rows from this table.
        """

    @classmethod
    @abstractmethod
    def set(cls, pkeys: dict, attributes: dict):
        """
        Edit data in a particular row by passing its primary key(s) and the changes
        in a dictionary.
        """

    @classmethod
    @abstractmethod
    def filter(cls, filters: dict) -> list:
        """
        Pass the filter(s) in a dictionary where the keys are the columns on which
        to filter and the values are the requirements for those columns. Should
        not be redefined after inheriting Models.
        """

    @classmethod
    @abstractmethod
    def _get_attributes(cls) -> list:
        """
        An internal function which calls the columns for the table linked to the
        model.
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
        is_debugging = Models.database._debug

        keys = ", ".join(attributes.keys())
        values = ", ".join(["%s"] * len(attributes))
        pkey = ", ".join(cls.table_primaries)

        SQL = f"INSERT INTO {cls.table_name} ({keys}) VALUES ({values}) RETURNING {pkey};"
        data = tuple(attributes.values())

        # @notice: skips incrementer to next available pkey if current pkey is occupied
        if cls.table_name in ["users", "items", "orders", "reviews", "issues"]:
            while True:
                try:
                    Models.database.cursor.execute(SQL, data)
                    if is_debugging: print("Attempting: ", SQL, data)
                    break
                except psycopg2.errors.InFailedSqlTransaction as e:
                    Models.database.connection.rollback()
                    continue
                except psycopg2.errors.UniqueViolation as e:
                    print(e)
                    continue
                except Exception as e:
                    print(e)
        else:
            Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()
        result = Models.database.cursor.fetchone()

        if is_debugging: print("SQL command: ", SQL)
        pkey_returned = sql_to_dictionary(Models.database.cursor, result)

        _instance = cls.get(pkey_returned)
        return _instance

    @classmethod
    def get(cls, pkeys):
        assert isinstance(pkeys, dict)
        is_debugging = Models.database._debug

        conds = generate_conditions_input(cls.table_primaries, pkeys)
        data = generate_data_input(cls.table_primaries, pkeys)

        SQL = f"SELECT * FROM {cls.table_name} WHERE {conds};"

        Models.database.cursor.execute(SQL, data)
        result = Models.database.cursor.fetchone()

        if is_debugging: print("SQL command: ", SQL)
        if result is None: return None

        _instance_dict = sql_to_dictionary(Models.database.cursor, result)
        _instance = cls(_instance_dict)
        return _instance

    @classmethod
    def set(cls, pkeys, changes):
        assert isinstance(pkeys, dict)
        is_debugging = Models.database._debug

        set_data = tuple(changes.values())
        set_conds = ", ".join([f"{key} = %s" for key in changes.keys()])

        where_data = generate_data_input(cls.table_primaries, pkeys)
        where_conds = generate_conditions_input(cls.table_primaries, pkeys)

        SQL = f"UPDATE {cls.table_name} SET {set_conds} WHERE {where_conds};"
        data = set_data + where_data

        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        if is_debugging: print("SQL command: ", SQL)

    @classmethod
    def delete(cls, pkeys):
        is_debugging = Models.database._debug

        conds = generate_conditions_input(cls.table_primaries, pkeys)
        data = generate_data_input(cls.table_primaries, pkeys)

        SQL = f"DELETE FROM {cls.table_name} WHERE {conds};" # Note: no quotes

        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        if is_debugging: print("SQL command: ", SQL, data)

    @classmethod
    def get_all(cls):
        is_debugging = Models.database._debug

        SQL = f"SELECT * FROM {cls.table_name};"

        Models.database.cursor.execute(SQL)
        results = Models.database.cursor.fetchall()

        if is_debugging: print("SQL command: ", SQL)

        _instances = []
        for result in results:
            _instance_dict = sql_to_dictionary(Models.database.cursor, result)
            _instance = cls(_instance_dict)
            _instances.append(_instance)
        return _instances

    @classmethod
    def filter(cls, filters):
        filter_keys = [key for key in filters.keys()]

        assert isinstance(filters, dict)
        assert cls.verify_attributes(filter_keys)
        is_debugging = Models.database._debug

        data = tuple(filters.values())
        conds = " AND ".join([f"{key} = %s" for key in filters.keys()])

        SQL = f"SELECT * FROM {cls.table_name} WHERE {conds};"
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()

        if is_debugging: print("SQL command: ", SQL)

        _instances = []
        for result in results:
            _instance_dict = sql_to_dictionary(Models.database.cursor, result)
            _instance = cls(_instance_dict)
            _instances.append(_instance)
        return _instances

    # @notice: operates like Models.filter() but promises to only return 1 result
    @classmethod
    def unique(cls, filters):
        filter_keys = [key for key in filters.keys()]

        assert isinstance(filters, dict)
        assert cls.verify_attributes(filter_keys)
        is_debugging = Models.database._debug

        data = tuple(filters.values())
        conds = " AND ".join([f"{key} = %s" for key in filters.keys()])
        SQL = f"SELECT * FROM {cls.table_name} WHERE {conds};"
        Models.database.cursor.execute(SQL, data)
        result = Models.database.cursor.fetchall()

        if is_debugging: print("SQL command: ", SQL)
        if len(result) == 0: return None

        assert len(result) == 1, "The set of filters applied are not unique to one row."

        result, = result
        _instance_dict = sql_to_dictionary(Models.database.cursor, result)
        _instance = cls(_instance_dict)
        return _instance

    @classmethod
    def like(cls, condition, value):
        assert cls.verify_attributes([condition])
        is_debugging = Models.database._debug

        SQL = f"SELECT * FROM {cls.table_name} WHERE {condition} ILIKE %s;"
        data = (value,)
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()

        if is_debugging: print("SQL command: ", SQL)

        _instances = []
        for result in results:
            _instance_dict = sql_to_dictionary(Models.database.cursor, result)
            _instance = cls(_instance_dict)
            _instances.append(_instance)
        return _instances

    @classmethod
    def verify_attributes(cls, query_attributes: list) -> bool:
        """
        A controlled check to see if the list of query_attributes (input), is
        actually a subset of the columns defined in the table.

        If not, then return False and print the name of the first entry to fail
        the check.
        """
        is_debugging = Models.database._debug
        _query_attributes = query_attributes.copy()
        _attribute = _query_attributes.pop(0)
        attribute = set([_attribute])
        table_attributes = cls._get_attributes()
        if attribute.issubset(table_attributes):
            if len(_query_attributes) == 0: return True
            else: return cls.verify_attributes(_query_attributes)

        raise Excetion(f"NotTableAttributeError, {_attribute} is not an attribute of {cls.table_name}.")

    @classmethod
    def _get_attributes(cls):
        is_debugging = Models.database._debug

        if cls.table_attributes is None:
            SQL = f"SELECT * FROM {cls.table_name} LIMIT 0"
            Models.database.cursor.execute(SQL)
            cls.table_attributes = [attr.name for attr in Models.database.cursor.description]

            if is_debugging: print("Table aattributes are initialized as: ", cls.table_attributes)
        return cls.table_attributes

    @classmethod
    def does_row_exist(cls, attributes):
        attr_keys = [key for key in attributes.keys()]

        assert isinstance(attributes, dict)
        assert cls.verify_attributes(attr_keys)
        is_debugging = Models.database._debug

        conds = generate_conditions_input(attributes.keys(), attributes)
        data = tuple(attributes.values())

        SQL = f"SELECT * FROM {cls.table_name} WHERE {conds};"
        Models.database.cursor.execute(SQL, data)

        if is_debugging: print("SQL command: ", SQL)
        return Models.database.cursor.fetchone() is not None

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
                elif isinstance(value, time):
                    _serializable_dict[key] = value.strftime("%H:%M")
                elif key not in ["password", "session"]:
                    _serializable_dict[key] = value
            _self_dict = _serializable_dict
        return _self_dict

    def __repr__(self): return f"<Blubber object: {self.table_name}>"
    def __eq__(self, other) : return self.__dict__ == other.__dict__
