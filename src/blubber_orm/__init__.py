import os

from .models._conn import parse_uri
from .models import Models

#WARNING: these functions will edit whichever DB is linked in the environment...

def get_db():
    """
    Get an instance of the database connection for custom uses.

    This is an object which contains the database connection, `.connection`, and
    a cursor for executing SQL queries, `.cursor`.
    """
    from .models._conn import DatabaseConnection
    return DatabaseConnection.get_instance()
