import json
import logging
import psycopg2

from datetime import datetime, date, time
from abc import ABC, abstractmethod

from ._conn import Blubber
from ._utils import format_query_statement, format_query_data

logger = logging.getLogger('blubber-orm')
logger.addHandler(logging.NullHandler())

class AbstractModels(ABC):
    """
    AbstractModels defines the basic functions that each of the Models should
    come with: CREATE (insert), READ (get, get_many, get_all, unique, like, filter),
    UPDATE (set), and DESTROY (delete).

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

    db => Blubber instance which stores database connection and cursor for SQL scripts.
    """

    table_name = None
    table_primaries = None
    table_attributes = None
    sensitive_attributes = None

    db = Blubber.get_instance()

    @classmethod
    @abstractmethod
    def insert(cls, attributes: dict):
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
    def get(cls, pkeys: dict):
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
        debug_mode = Models.db._debug

        cols = ", ".join(attributes.keys())
        values = ", ".join(["%s"] * len(attributes))
        pkey = ", ".join(cls.table_primaries)

        SQL = f"""
            INSERT
            INTO {cls.table_name} ({cols})
            VALUES ({values})
            RETURNING {pkey};
            """

        data = tuple(attributes.values())

        with Models.db.conn.cursor() as cursor:

            try:
                cursor.execute(SQL, data)

            except psycopg2.errors.UniqueViolation as e:
                logger.error(e, exc_info=True)
                Models.db.conn.rollback()

                pkeys = {}
                for primary in cls.table_primaries:
                    attribute = attributes[primary]
                    pkeys[primary] = attribute

                return cls.get(pkeys)

            logger.debug(f"Query:\n\t{SQL}")

            Models.db.conn.commit()
            result = cursor.fetchone()

            logger.debug(f"Result:\n\t{result}")

            pkey = Blubber.format_to_dict(cursor, result)

        _instance = cls.get(pkey)
        return _instance


    @classmethod
    def get(cls, pkeys):
        assert isinstance(pkeys, dict)

        data = format_query_data(cls.table_primaries, pkeys)
        conds = format_query_statement(cls.table_primaries, pkeys)

        SQL = f"""
            SELECT *
            FROM {cls.table_name}
            WHERE {conds};
            """

        logger.debug(f"Query:\n\t{SQL}")

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            result = cursor.fetchone()

            logger.debug(f"Result:\n\t{result}")

            if result is None: return None

            _instance_dict = Blubber.format_to_dict(cursor, result)

        _instance = cls(_instance_dict)
        return _instance


    @classmethod
    def set(cls, pkeys, changes):
        assert isinstance(pkeys, dict)

        set_data = tuple(changes.values())
        set_conds = ", ".join([f"{col} = %s" for col in changes.keys()])

        where_data = format_query_data(cls.table_primaries, pkeys)
        where_conds = format_query_statement(cls.table_primaries, pkeys)

        SQL = f"""
            UPDATE {cls.table_name}
            SET {set_conds}
            WHERE {where_conds};
            """

        data = set_data + where_data

        logger.debug(f"Query:\n\t{SQL}")

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)

            Models.db.conn.commit()


    @classmethod
    def delete(cls, pkeys):

        data = format_query_data(cls.table_primaries, pkeys)
        conds = format_query_statement(cls.table_primaries, pkeys)

        SQL = f"""
            DELETE
            FROM {cls.table_name}
            WHERE {conds};
            """

        logger.debug(f"Query:\n\t{SQL}")

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)

            Models.db.conn.commit()


    @classmethod
    def get_all(cls):
        SQL = f"""
            SELECT *
            FROM {cls.table_name};
            """

        logger.debug(f"Query:\n\t{SQL}")

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL)
            results = cursor.fetchall()

            logger.debug(f"Result:\n\t{results}")

            _instances = []
            for result in results:
                _instance_dict = Blubber.format_to_dict(cursor, result)
                _instance = cls(_instance_dict)
                _instances.append(_instance)
        return _instances


    @classmethod
    def get_many(cls, limit):
        assert isinstance(limit, int), "Limit must be of type integer."

        SQL = f"""
            SELECT *
            FROM {cls.table_name}
            """

        logger.debug(f"Query:\n\t{SQL}")

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL)
            results = cursor.fetchmany(limit)

            logger.debug(f"Result:\n\t{results}")

            _instances = []
            for result in results:
                _instance_dict = Blubber.format_to_dict(cursor, result)
                _instance = cls(_instance_dict)
                _instances.append(_instance)
        return _instances


    @classmethod
    def filter(cls, filters):
        filter_keys = [key for key in filters.keys()]

        assert isinstance(filters, dict)
        assert cls.verify_attributes(filter_keys)

        data = tuple(filters.values())
        conds = " AND ".join([f"{key} = %s" for key in filters.keys()])

        SQL = f"""
            SELECT *
            FROM {cls.table_name}
            WHERE {conds};
            """

        logger.debug(f"Query:\n\t{SQL}")

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            results = cursor.fetchall()

            logger.debug(f"Result:\n\t{results}")

            _instances = []
            for result in results:
                _instance_dict = Blubber.format_to_dict(cursor, result)
                _instance = cls(_instance_dict)
                _instances.append(_instance)
        return _instances

    # @notice: operates like Models.filter() but promises to only return 1 result
    @classmethod
    def unique(cls, filters):
        filter_keys = [key for key in filters.keys()]

        assert isinstance(filters, dict)
        assert cls.verify_attributes(filter_keys)

        data = tuple(filters.values())
        conds = " AND ".join([f"{key} = %s" for key in filters.keys()])

        SQL = f"""
            SELECT *
            FROM {cls.table_name}
            WHERE {conds};
            """

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            result = cursor.fetchall()

            logger.debug(f"Result:\n\t{result}")

            if len(result) == 0: return None

            assert len(result) == 1, "The set of filters applied are not unique to one row."

            result, = result
            _instance_dict = Blubber.format_to_dict(cursor, result)
            _instance = cls(_instance_dict)
        return _instance


    @classmethod
    def like(cls, column, search, where="any", case_sensitive=False):
        assert cls.verify_attributes([column]), "Error: invalid column name."
        assert where in ["start", "any", "end"], "Error: invalid search location."

        if where == "start": search = f"{search}%"
        elif where == "any": search = f"%{search}%"
        elif where == "end": search = f"%{search}"

        if case_sensitive: like_command = 'LIKE'
        else: like_command = 'ILIKE'

        # FLAG: 'column' is directly formatted into the str... *ONLY* because of this check^
        # do *NOT* replicate this implementation...
        SQL = f"""
            SELECT *
            FROM {cls.table_name}
            WHERE {column}
            {like_command} %s
            ESCAPE '';
            """

        data = (search, )

        logger.debug(f"Query:\n\t{SQL}")

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            results = cursor.fetchall()

            logger.debug(f"Result:\n\t{results}")

            _instances = []
            for result in results:
                _instance_dict = Blubber.format_to_dict(cursor, result)
                _instance = cls(_instance_dict)
                _instances.append(_instance)
        return _instances


    @classmethod
    def verify_attributes(cls, query_attributes: list) -> bool:
        """
        A controlled check to see if the list of query_attributes (input), is
        actually a subset of the columns defined in the table.

        If not, then returns False and prints the name of the first entry to fail
        the check.
        """
        _query_attributes = query_attributes.copy()
        _attribute = _query_attributes.pop(0)

        attribute = set([_attribute])
        table_attributes = cls._get_attributes()
        if attribute.issubset(table_attributes):
            if len(_query_attributes) == 0: return True
            else: return cls.verify_attributes(_query_attributes)

        logger.error(f"NotTableAttributeError, {_attribute} is not an attribute of {cls.table_name}.")


    @classmethod
    def _get_attributes(cls):
        if cls.table_attributes is None:
            SQL = f"""
                SELECT *
                FROM {cls.table_name}
                LIMIT 0
                """

            with Models.db.conn.cursor() as cursor:
                cursor.execute(SQL)
                cls.table_attributes = [attr.name for attr in cursor.description]

            logger.debug(f"Table attributes are initialized as: {cls.table_attributes}")
        return cls.table_attributes


    @classmethod
    def does_row_exist(cls, attributes):
        attr_keys = [key for key in attributes.keys()]

        assert isinstance(attributes, dict)
        assert cls.verify_attributes(attr_keys)

        data = tuple(attributes.values())
        conds = format_query_statement(attributes.keys(), attributes)

        SQL = f"""
            SELECT *
            FROM {cls.table_name}
            WHERE {conds};
            """

        logger.debug(f"Query:\n\t{SQL}")

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            result = cursor.fetchone()

        return result is not None


    def to_dict(self, serializable=True):
        _self_dict = self.__dict__
        if serializable:
            _serializable_dict = {}
            for key, value in _self_dict.items():
                if key[0] == "_":
                    key = key[1:]
                if isinstance(value, datetime):
                    _serializable_dict[key] = datetime.timestamp(value)
                elif isinstance(value, date):
                    _serializable_dict[key] = datetime.timestamp(value)
                elif isinstance(value, time):
                    _serializable_dict[key] = value.strftime("%H:%M:%S.%f")
                elif key not in self.sensitive_attributes:
                    _serializable_dict[key] = value
            _self_dict = _serializable_dict
        return _self_dict


    def __repr__(self): return f"<Blubber Table: {self.table_name}>"
    def __eq__(self, other): return self.__dict__ == other.__dict__
