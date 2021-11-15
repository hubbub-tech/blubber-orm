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
        self.chosen_time = db_data["chosen_time"]
        self.renter_id = db_data["renter_id"] #the renter id is stored then searched in users
        self.courier_id = db_data["courier_id"]
        #address
        self._address_num = db_data["address_num"]
        self._address_street = db_data["address_street"]
        self._address_apt = db_data["address_apt"]
        self._address_zip = db_data["address_zip"]

    @property
    def renter(self):
        return Users.get(self.renter_id)

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

    @property
    def is_completed(self):
        SQL = """
            SELECT dt_completed FROM order_pickups
                WHERE pickup_date = %s
                AND renter_id = %s
                AND dt_sched = %s;"""
        data = (self.pickup_date, self.renter_id, self.dt_scheduled)

        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()
        return None not in results

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

    @property
    def is_completed(self):
        SQL = """
            SELECT dt_completed FROM order_dropoffs
                WHERE dropoff_date = %s
                AND renter_id = %s
                AND dt_sched = %s;"""
        data = (self.dropoff_date, self.renter_id, self.dt_scheduled)

        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()
        return None not in results

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
