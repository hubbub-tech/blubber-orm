import pytz
from datetime import datetime

from .models.db import DatabaseConnection

def _create_database():
    try:
        database = DatabaseConnection.get_instance()
        database.cursor.execute(open("dev/create.sql", "r").read())
    except FileNotFoundError as no_create_sql_present:
        print(no_create_sql_present)
    else:
        print("Successfully created Hubbub database.")

def _destroy_database():
    try:
        database = DatabaseConnection.get_instance()
        database.cursor.execute(open("dev/destroy.sql", "r").read())
    except FileNotFoundError as no_create_sql_present:
        print(no_create_sql_present)
    else:
        print("Successfully destroyed Hubbub database.")
