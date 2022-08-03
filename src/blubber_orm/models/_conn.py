import os
import logging
from psycopg2 import connect
from uritools import urisplit


class Blubber:
    """A class to store a connection to the Postgres database using psycopg2."""

    _instance = None
    _debug = None
    conn = None

    def __init__(self):
        if Blubber._instance:
            #TODO: log that this problem happened
            raise Exception("Database instance should only be created once.")
        else:
            Blubber._debug = Blubber.get_debug()
            Blubber.conn = Blubber.open_conn()
            Blubber._instance = self
            if Blubber._debug:
                logging.info("Database connection: ", Blubber.conn)

    @staticmethod
    def get_instance():
        if Blubber._instance is None:
            Blubber()
        return Blubber._instance

    @staticmethod
    def get_debug():
        _debug = os.environ.get("BLUBBER_DEBUG", None)
        if _debug == "1":
            return True
        elif _debug == "0":
            return False
        elif _debug is None:
            print("BLUBBER_DEBUG config not found. Defaulting to False.")
            return False
        else:
            raise Exception("ExportError: BLUBBER_DEBUG config must be either 0 or 1.")


    @staticmethod
    def format_to_dict(cursor, result):
        to_dictionary = {}
        for index, attr in enumerate(cursor.description):
            to_dictionary[attr.name] = result[index]
        return to_dictionary

    @staticmethod
    def parse_uri(database_uri):
        not_postgres_error = "This URI is not for a PostgreSQL database."
        assert("postgres://" in database_uri or "postgresql://" in database_uri), not_postgres_error
        uri_credentials = urisplit(database_uri)
        user, password = uri_credentials.userinfo.split(':')
        parsed_credentials = {
            "dbname": uri_credentials.path.replace("/", ""),
            "user": user,
            "password": password,
            "host": uri_credentials.host,
            "port": uri_credentials.port
        }
        return parsed_credentials


    #returns a database connection by reading the uri from the environment
    @classmethod
    def open_conn(cls, debug=None):
        conn = None
        try:
            #build exception for when URI cannot be found in environment
            database_uri = os.environ.get("DATABASE_URL", "Connection Failed.")
            credentials = Blubber.parse_uri(database_uri)
        except AssertionError as not_postgres_error:
            print(not_postgres_error)
        else:
            # establish connection
            try:
                conn = connect(
                    dbname=credentials["dbname"],
                    user=credentials["user"],
                    password=credentials["password"],
                    host=credentials["host"],
                    port=credentials["port"]
                )
            except Exception as connection_error:
                #TODO: log error to file with traceback
                print(connection_error)
        finally:
            return conn


    #we need to close the db and the connect established in 'open_conn'
    @classmethod
    def close_conn(cls):
        if cls.conn:
            cls.conn.close()
            cls.conn = None
