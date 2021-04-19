import os
import psycopg2 #source docs: https://www.psycopg.org/docs/usage.html
from uritools import urisplit

#postgres app commands: https://kb.objectrocket.com/postgresql/how-to-run-an-sql-file-in-postgres-846
#postgres app website: https://postgresapp.com/documentation/cli-tools.html

def sql_to_dictionary(cursor, sql_query):
    to_dictionary = {}
    for attr_index, attribute in enumerate(cursor.description):
        to_dictionary[attribute.name] = sql_query[attr_index]
    return to_dictionary

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

#simple singleton design pattern
class DatabaseConnection:
    _instance = None
    cursor = None
    connection = None

    def __init__(self):
        if DatabaseConnection._instance:
            #TODO: log that this problem happened
            raise Exception("Database instance should only be created once.")
        else:
            print("getting db")
            DatabaseConnection.cursor, DatabaseConnection.connection = DatabaseConnection.get_db()
            DatabaseConnection._instance = self
            print("got it", DatabaseConnection.cursor, DatabaseConnection.connection)

    @staticmethod
    def get_instance():
        if DatabaseConnection._instance is None:
            DatabaseConnection()
        return DatabaseConnection._instance

    #returns a database connection by reading the uri from the environment
    @staticmethod
    def get_db():
        conn = None
        cur = None
        print("starting")
        try:
            #build exception for when URI cannot be found in environment
            database_uri = "postgresql://adekunlebalogun:none@localhost:5432/adekunlebalogun"
            credentials = parse_uri(database_uri)
        except AssertionError as not_postgres_error:
            #TODO: log error to file with traceback
            print(not_postgres_error)
        else:
            # establish connection
            try:
                conn = psycopg2.connect(
                    dbname=credentials["dbname"],
                    user=credentials["user"],
                    password=credentials["password"],
                    host=credentials["host"],
                    port=credentials["port"]
                )
            except Exception as connection_error:
                #TODO: log error to file with traceback
                print(connection_error)
            else:
                #call the 'cursor' to make edits/db calls
                cur = conn.cursor()
        finally:
            return cur, conn

    #we need to close the db and the connect established in 'get_db'
    @classmethod
    def close_db(cls):
        if cls.cursor:
            cls.cursor.close()
            cls.cursor = None
        if cls.connection:
            cls.connection.close()
            cls.connection = None
        cls._instance = None