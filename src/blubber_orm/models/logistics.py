import pytz
from datetime import datetime

from .db import sql_to_dictionary
from .base import Models
from .addresses import AddressModelDecorator
from .users import Users
from .orders import Orders

class Logistics(Models, AddressModelDecorator):
    table_name = "logistics"
    from .db import sql_to_dictionary

    table_primaries = ["dt_sched", "renter_id"]

    _address_num = None
    _address_street = None
    _address_apt = None
    _address_zip = None

    def __init__(self, db_data):
        #attributes
        self.dt_scheduled = db_data["dt_sched"]
        self.notes = db_data["notes"]
        self.referral = db_data["referral"]
        self.timeslots = db_data["timeslots"].split(",")
        self.renter_id = db_data["renter_id"] #the renter id is stored then searched in users
        self.chosen_time = db_data["chosen_time"]
        #address
        self._address_num = db_data["address_num"]
        self._address_street = db_data["address_street"]
        self._address_apt = db_data["address_apt"]
        self._address_zip = db_data["address_zip"]

    @property
    def renter(self):
        return Users.get(self.renter_id)

    @classmethod
    def get(cls, logistics_keys):
        logistics = None
        SQL = "SELECT * FROM logistics WHERE dt_sched = %s AND renter_id = %s;" # Note: no quotes
        data = (logistics_keys["dt_sched"], logistics_keys["renter_id"])
        Models.database.cursor.execute(SQL, data)
        result = Models.database.cursor.fetchone()
        if result:
            db_logistics = sql_to_dictionary(Models.database.cursor, result)
            logistics = Logistics(db_logistics)
        return logistics

    @classmethod
    def set(cls, logistics_keys, changes):
        targets = [f"{target} = %s" for target in changes.keys()]
        targets_str = ", ".join(targets)
        SQL = f"UPDATE logistics SET {targets_str} WHERE dt_sched = %s AND renter_id = %s;" # Note: no quotes
        updates = [value for value in changes.values()]
        keys = [logistics_keys['dt_sched'], logistics_keys['renter_id']]
        data = tuple(updates + keys)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    @classmethod
    def delete(cls, logistics_keys):
        SQL = "DELETE FROM logistics WHERE dt_sched = %s AND renter_id = %s;" # Note: no quotes
        data = (logistics_keys['dt_sched'], logistics_keys['renter_id'])
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    def refresh(self):
        logistics_keys = {
            "dt_sched": self.dt_scheduled,
            "renter_id": self.renter_id}
        self = Logistics.get(logistics_keys)

class Pickups(Models):
    table_name = "pickups"
    table_primaries = ["pickup_date", "dt_sched", "renter_id"]

    def __init__(self, db_data):
        self.pickup_date = db_data["pickup_date"]
        self.dt_scheduled = db_data["dt_sched"]
        self.renter_id = db_data["renter_id"]

    @property
    def logistics(self):
        keys = {"dt_sched": self.dt_scheduled, "renter_id": self.renter_id}
        return Logistics.get(keys)

    @classmethod
    def by_order(cls, order):
        pickup = None
        SQL = "SELECT pickup_date, dt_sched, renter_id FROM order_pickups WHERE order_id = %s;" # Note: no quotes
        data = (order.id, )
        Models.database.cursor.execute(SQL, data)
        result = Models.database.cursor.fetchone()
        if result:
            db_pickup = sql_to_dictionary(Models.database.cursor, result)
            pickup = Pickups.get(db_pickup)
        return pickup

    @classmethod
    def mark_as_collected(order):
        #ASSERT object is type order
        #Check to make sure there is a complete pickup row
        #Check to see if order and pickup are associated in order_pickups
        pickup = Pickups.by_order(order)
        if pickup:
            #Change pickup dt_completed to current time
            SQL = "UPDATE order_pickups SET dt_completed = %s WHERE order_id = %s;" # Note: no quotes
            data = (datetime.now(tz=pytz.UTC), order.id)
            Models.database.cursor.execute(SQL, data)
            Models.database.connection.commit()
        else:
            raise Exception(f"No pickup object is associated with <Order {order.id}>.")

    @classmethod
    def get(cls, pickup_keys):
        pickup = None
        SQL = "SELECT * FROM pickups WHERE pickup_date = %s AND dt_sched = %s AND renter_id = %s;" # Note: no quotes
        data = (pickup_keys["pickup_date"], pickup_keys["dt_sched"], pickup_keys["renter_id"])
        Models.database.cursor.execute(SQL, data)
        result = Models.database.cursor.fetchone()
        if result:
            db_pickup = sql_to_dictionary(Models.database.cursor, result)
            pickup = Pickups(db_pickup)
        return pickup

    @classmethod
    def set(cls, pickup_keys, changes):
        targets = [f"{target} = %s" for target in changes.keys()]
        targets_str = ", ".join(targets)
        SQL = f"UPDATE pickups SET {targets_str} WHERE pickup_date = %s AND dt_sched = %s AND renter_id = %s;" # Note: no quotes
        updates = [value for value in changes.values()]
        keys = [pickup_keys['pickup_date'], pickup_keys['dt_sched'], pickup_keys['renter_id']]
        data = tuple(updates + keys)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    @classmethod
    def delete(cls, pickup_keys):
        SQL = "DELETE FROM pickups WHERE pickup_date = %s AND dt_sched = %s AND renter_id = %s;" # Note: no quotes
        data = (pickup_keys["pickup_date"], pickup_keys["dt_sched"], pickup_keys["renter_id"])
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    def schedule_orders(self, orders):
        #ASSERT takes a list
        SQL = """
            INSERT INTO order_pickups (order_id, pickup_date, renter_id, dt_sched)
            VALUES (%s, %s, %s, %s);"""
        for order in orders:
            data = (order.id, self.pickup_date, self.renter_id, self.dt_scheduled)
            Models.database.cursor.execute(SQL, data)
            Models.database.connection.commit()
            order.is_pickup_scheduled = True

    def cancel(self, order):
        SQL = "DELETE FROM order_pickups WHERE order_id = %s;" # Note: no quotes
        data = (order.id, )
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        SQL = "SELECT * FROM order_pickups WHERE pickup_date = %s AND dt_sched = %s AND renter_id = %s;"
        data = (self.pickup_date, self.dt_scheduled, self.renter_id)
        Models.database.cursor.execute(SQL, data)
        if Models.database.cursor.fetchone() is None:
            Logistics.delete({"dt_sched": self.dt_scheduled, "renter_id": self.renter_id})
        order.is_pickup_scheduled = False

    def refresh(self):
        pickup_keys = {
            "pickup_date": self.pickup_date,
            "dt_sched": self.dt_scheduled,
            "renter_id": self.renter_id}
        self = Pickups.get(pickup_keys)

class Dropoffs(Models):
    table_name = "dropoffs"
    table_primaries = ["dropoff_date", "dt_sched", "renter_id"]

    def __init__(self, db_data):
        self.dropoff_date = db_data["dropoff_date"]
        self.dt_scheduled = db_data["dt_sched"]
        self.renter_id = db_data["renter_id"]

    @property
    def logistics(self):
        keys = {"dt_sched": self.dt_scheduled, "renter_id": self.renter_id}
        return Logistics.get(keys)

    @classmethod
    def by_order(cls, order):
        dropoff = None
        SQL = "SELECT dropoff_date, dt_sched, renter_id FROM order_dropoffs WHERE order_id = %s;" # Note: no quotes
        data = (order.id, )
        Models.database.cursor.execute(SQL, data)
        result = Models.database.cursor.fetchone()
        if result:
            db_dropoff = sql_to_dictionary(Models.database.cursor, result)
            dropoff = Dropoffs.get(db_dropoff)
        return dropoff

    @classmethod
    def mark_as_delivered(order):
        #ASSERT object is type order
        #Check to make sure there is a complete dropoff row
        #Check to see if order and dropoff are associated in order_dropoffs
        dropoff = Dropoffs.by_order(order)
        if dropoff:
            #Change dropoff dt_completed to current time
            SQL = "UPDATE order_dropoffs SET dt_completed = %s WHERE order_id = %s;" # Note: no quotes
            data = (datetime.now(tz=pytz.UTC), order.id)
            Models.database.cursor.execute(SQL, data)
            Models.database.connection.commit()
        else:
            raise Exception(f"No dropoff object is associated with <Order {order.id}>.")

    @classmethod
    def get(cls, dropoff_keys):
        dropoff = None
        SQL = "SELECT * FROM dropoffs WHERE dropoff_date = %s AND dt_sched = %s AND renter_id = %s;" # Note: no quotes
        data = (dropoff_keys["dropoff_date"], dropoff_keys["dt_sched"], dropoff_keys["renter_id"])
        Models.database.cursor.execute(SQL, data)
        result = Models.database.cursor.fetchone()
        if result:
            db_dropoff = sql_to_dictionary(Models.database.cursor, result)
            dropoff = Dropoffs(db_dropoff)
        return dropoff

    @classmethod
    def set(cls, dropoff_keys, changes):
        targets = [f"{target} = %s" for target in changes.keys()]
        targets_str = ", ".join(targets)
        SQL = f"UPDATE dropoffs SET {targets_str} WHERE dropoff_date = %s AND dt_sched = %s AND renter_id = %s;" # Note: no quotes
        updates = [value for value in changes.values()]
        keys = [dropoff_keys['dropoff_date'], dropoff_keys['dt_sched'], dropoff_keys['renter_id']]
        data = tuple(updates + keys)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    @classmethod
    def delete(cls, dropoff_keys):
        SQL = f"DELETE FROM dropoffs WHERE dropoff_date = %s AND dt_sched = %s AND renter_id = %s;" # Note: no quotes
        data = (dropoff_keys["dropoff_date"], dropoff_keys["dt_sched"], dropoff_keys["renter_id"])
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    def schedule_orders(self, orders):
        #ASSERT takes a list
        SQL = """
            INSERT INTO order_dropoffs (order_id, dropoff_date, renter_id, dt_sched)
            VALUES (%s, %s, %s, %s);"""
        for order in orders:
            data = (order.id, self.dropoff_date, self.renter_id, self.dt_scheduled)
            Models.database.cursor.execute(SQL, data)
            Models.database.connection.commit()
            order.is_dropoff_scheduled = True

    def cancel(self, order):
        SQL = "DELETE FROM order_dropoffs WHERE order_id = %s;" # Note: no quotes
        data = (order.id, )
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        SQL = "SELECT * FROM order_dropoffs WHERE dropoff_date = %s AND dt_sched = %s AND renter_id = %s;"
        data = (self.dropoff_date, self.dt_scheduled, self.renter_id)
        Models.database.cursor.execute(SQL, data)
        if Models.database.cursor.fetchone() is None:
            Logistics.delete({"dt_sched": self.dt_scheduled, "renter_id": self.renter_id})
        order.is_dropoff_scheduled = False

    def refresh(self):
        dropoff_keys = {
            "dropoff_date": self.dropoff_date,
            "dt_sched": self.dt_scheduled,
            "renter_id": self.renter_id}
        self = Dropoffs.get(dropoff_keys)
