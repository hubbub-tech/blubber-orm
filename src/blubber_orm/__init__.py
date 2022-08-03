import os
from .models import Models

#WARNING: these functions will edit whichever DB is linked in the environment...

def get_blubber():
    """
    Get an instance of the database connection for custom uses.

    This is an object which contains the database connection, `.connection`.
    For the driver cursor, use connection.conn.cursor() which returns a `Cursor` instance.
    """
    from .models._conn import Blubber
    return Blubber.get_instance()
