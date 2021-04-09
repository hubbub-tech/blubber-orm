import os
import psycopg2 #source docs: https://www.psycopg.org/docs/usage.html
from uritools import urisplit

#returns a database connection by reading the uri from the environment
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
def close_db(cur=None, conn=None):
    if cur:
        cur.close()
    if conn:
        conn.close()

def sql_to_dictionary(cursor, sql_query):
    to_dictionary = {}
    for attr_index, attribute in enumerate(cursor.description):
        to_dictionary[attribute.name] = sql_query[attr_index]
    return to_dictionary
