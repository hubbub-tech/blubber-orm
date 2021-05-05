import pytz
from datetime import datetime

from .db import DatabaseConnection
from .models import Users, Orders

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
    database = DatabaseConnection.get_instance()
    SQL = f"SELECT * FROM renters WHERE renter_id = %s;" # Note: no quotes
    data = (user.id, )
    database.cursor.execute(SQL, data)
    if database.cursor.fetchone():
        return True
    else:
        return False

def search_lister(user):
    database = DatabaseConnection.get_instance()
    SQL = f"SELECT * FROM listers WHERE lister_id = %s;" # Note: no quotes
    data = (user.id, )
    database.cursor.execute(SQL, data)
    if database.cursor.fetchone():
        return True
    else:
        return False

#TODO
def mark_dropoff_as_completed(order):
    database = DatabaseConnection.get_instance()
    #ASSERT object is type order
    assert (type(order) == Orders), "TypeError, must be of type order."
    #Check to make sure there is a complete dropoff row
    #Check to see if order and dropoff are associated in order_dropoffs
    dropoff = order.get_dropoff()
    if dropoff:
        #Change dropoff dt_completed to current time
        SQL = f"UPDATE order_dropoffs SET dt_completed = %s WHERE order_id = %s;" # Note: no quotes
        data = (datetime.now(tz=pytz.UTC), order.id)
        database.cursor.execute(SQL, data)
        database.connection.commit()
    else:
        raise Exception(f"No dropoff object is associated with <Order {order.id}>.")

def mark_pickup_as_completed(order):
    database = DatabaseConnection.get_instance()
    #ASSERT object is type order
    assert (type(order) == Orders), "TypeError, must be of type order."
    #Check to make sure there is a complete pickup row
    #Check to see if order and pickup are associated in order_pickups
    dropoff = order.get_dropoff()
    if dropoff:
        #Change pickup dt_completed to current time
        SQL = f"UPDATE order_pickups SET dt_completed = %s WHERE order_id = %s;" # Note: no quotes
        data = (datetime.now(tz=pytz.UTC), order.id)
        database.cursor.execute(SQL, data)
        database.connection.commit()
    else:
        raise Exception(f"No pickup object is associated with <Order {order.id}>.")
