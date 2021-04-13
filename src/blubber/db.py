import os
import psycopg2 #source docs: https://www.psycopg.org/docs/usage.html
from uritools import urisplit

def sql_to_dictionary(cursor, sql_query):
    to_dictionary = {}
    for attr_index, attribute in enumerate(cursor.description):
        to_dictionary[attribute.name] = sql_query[attr_index]
    return to_dictionary

#simple singleton design pattern
class DatabaseConnection:
    _instance = None
    cursor = None
    connection = None

    def __init__(self):
        if DatabaseConnection._instance:
            raise Exception("This class is a singleton!")
        else:
            DatabaseConnection.cursor, DatabaseConnection.connection = DatabaseConnection.get_db()
            DatabaseConnection._instance = self

    @staticmethod
    def get_instance():
        if DatabaseConnection._instance is None:
            DatabaseConnection()
        return DatabaseConnection._instance

    #returns a database connection by reading the uri from the environment
    @staticmethod
    def get_db():
        try:
            #build exception for when URI cannot be found in environment
            credentials = urisplit(os.environ['DATABASE_URI'])
        except:
            print("Can't find URI in environment. Make sure its named 'DATABASE_URI'.")
            return None, None
        if credentials.scheme == "postgres":
            dbname = credentials.path.replace("/", "")
            user, password = credentials.userinfo.split(':')
            try:
                # establish connection
                conn = psycopg2.connect(
                    dbname=dbname,
                    user=user,
                    password=password,
                    host=credentials.host,
                    port=credentials.port
                )
                #call the 'cursor' to make edits/db calls
                cur = conn.cursor()
                return cur, conn
            except:
                print("Error, failed to establish connection with the database.")
                return None, None
        else:
            print("Error, Not a postgres database.")
            return None, None

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
