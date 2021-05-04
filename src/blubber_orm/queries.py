from .db import DatabaseConnection
from .models import Users

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

def make_renter(user):
    #ASSERT user is not already in the renters table
    assert (type(user) == Users), "TypeError, must be of type user."
    database = DatabaseConnection.get_instance()
    SQL = f"INSERT INTO renters (renter_id) VALUES (%s);"
    data = (user.id, )
    database.cursor.execute(SQL, data)
    database.connection.commit()

def make_lister(user):
    #ASSERT user is not already in the listers table
    assert (type(user) == Users), "TypeError, must be of type user."
    database = DatabaseConnection.get_instance()
    SQL = f"INSERT INTO listers (lister_id) VALUES (%s);"
    data = (user.id, )
    database.cursor.execute(SQL, data)
    database.connection.commit()

def search_renter(user):
    SQL = f"SELECT * FROM renters WHERE renter_id = %s;" # Note: no quotes
    data = (user.id, )
    database.cursor.execute(SQL, data)
    if database.cursor.fetchone():
        return True
    else:
        return False

def search_lister(user):
    SQL = f"SELECT * FROM listers WHERE lister_id = %s;" # Note: no quotes
    data = (user.id, )
    database.cursor.execute(SQL, data)
    if database.cursor.fetchone():
        return True
    else:
        return False

#TODO
def mark_dropoff_as_completed(order):
    #ASSERT object is type order
    #Check to make sure there is a complete dropoff row
    #Check to see if order and dropoff are associated in order_dropoffs
    #Change dropoff dt_completed to current time
    pass

def mark_pickup_as_completed(order):
    #ASSERT object is type order
    #Check to make sure there is a complete pickup row
    #Check to see if order and pickup are associated in order_pickups
    #Change pickup dt_completed to current time
    pass
