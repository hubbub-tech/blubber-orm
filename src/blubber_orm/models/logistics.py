import pytz
from datetime import datetime

from ._conn import sql_to_dictionary
from ._base import Models

from .addresses import AddressModelDecorator
from .users import Users
from .orders import Orders

class Logistics(Models, AddressModelDecorator):
    table_name = "logistics"
    table_primaries = ["dt_sched", "renter_id"]

    def __init__(self, db_data):
        self.dt_sched = db_data["dt_sched"]
        self.notes = db_data["notes"]
        self.referral = db_data["referral"]
        self.timeslots = db_data["timeslots"].split(",")
        self.chosen_time = db_data["chosen_time"]
        self.renter_id = db_data["renter_id"]
        self.courier_id = db_data["courier_id"]
        #address
        self.address_num = db_data["address_num"]
        self.address_street = db_data["address_street"]
        self.address_apt = db_data["address_apt"]
        self.address_zip = db_data["address_zip"]

    @property
    def renter(self):
        return Users.get({"id": self.renter_id})

class Pickups(Models):
    table_name = "pickups"
    table_primaries = ["pickup_date", "dt_sched", "renter_id"]

    def __init__(self, db_data):
        self.pickup_date = db_data["pickup_date"]
        self.renter_id = db_data["renter_id"]
        self.dt_sched = db_data["dt_sched"]

    @property
    def logistics(self):
        keys = {"dt_sched": self.dt_sched, "renter_id": self.renter_id}
        return Logistics.get(keys)


    @property
    def is_completed(self):
        SQL = """
            SELECT dt_completed FROM order_pickups
                WHERE pickup_date = %s
                AND renter_id = %s
                AND dt_sched = %s;"""
        data = (self.pickup_date, self.renter_id, self.dt_sched)

        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()
        assert results is not None
        for result in results:
            dt_completed, = result
            if dt_completed is None: return False
        return True


    @classmethod
    def by_order(cls, order):
        SQL = "SELECT pickup_date, dt_sched, renter_id FROM order_pickups WHERE order_id = %s;"
        data = (order.id, )
        Models.database.cursor.execute(SQL, data)
        result = Models.database.cursor.fetchone()

        if result is None: return None

        pickup_keys = sql_to_dictionary(Models.database.cursor, result)
        pickup = Pickups.get(pickup_keys)
        return pickup

    def schedule_orders(self, orders):
        assert isinstance(orders, list)

        SQL = """
            INSERT INTO order_pickups (order_id, pickup_date, renter_id, dt_sched)
            VALUES (%s, %s, %s, %s);
            """

        SQL_order_update = "UPDATE orders SET is_pickup_sched = %s WHERE id = %s;"
        for order in orders:
            data = (order.id, self.pickup_date, self.renter_id, self.dt_sched)
            Models.database.cursor.execute(SQL, data)
            Models.database.connection.commit()

            data = (True, order.id)
            Models.database.cursor.execute(SQL_order_update, data)
            Models.database.connection.commit()

    def cancel(self, order):
        SQL = "DELETE FROM order_pickups WHERE order_id = %s;" # Note: no quotes
        data = (order.id, )
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        SQL = "SELECT * FROM order_pickups WHERE pickup_date = %s AND dt_sched = %s AND renter_id = %s;"
        data = (self.pickup_date, self.dt_sched, self.renter_id)
        Models.database.cursor.execute(SQL, data)

        if Models.database.cursor.fetchone() is None:
            Logistics.delete({"dt_sched": self.dt_sched, "renter_id": self.renter_id})

        SQL = "UPDATE orders SET is_pickup_sched = %s WHERE id = %s;"
        data = (False, order.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

class Dropoffs(Models):
    table_name = "dropoffs"
    table_primaries = ["dropoff_date", "dt_sched", "renter_id"]

    def __init__(self, db_data):
        self.dropoff_date = db_data["dropoff_date"]
        self.dt_sched = db_data["dt_sched"]
        self.renter_id = db_data["renter_id"]

    @property
    def logistics(self):
        keys = {"dt_sched": self.dt_sched, "renter_id": self.renter_id}
        return Logistics.get(keys)

    @property
    def is_completed(self):
        SQL = """
            SELECT dt_completed FROM order_dropoffs
                WHERE dropoff_date = %s
                AND renter_id = %s
                AND dt_sched = %s;"""
        data = (self.dropoff_date, self.renter_id, self.dt_sched)

        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()
        assert results is not None
        for result in results:
            dt_completed, = result
            if dt_completed is None: return False
        return True

    @classmethod
    def by_order(cls, order):
        SQL = "SELECT dropoff_date, dt_sched, renter_id FROM order_dropoffs WHERE order_id = %s;" # Note: no quotes
        data = (order.id, )
        Models.database.cursor.execute(SQL, data)
        result = Models.database.cursor.fetchone()

        if result is None: return None

        dropoff_keys = sql_to_dictionary(Models.database.cursor, result)
        dropoff = Dropoffs.get(dropoff_keys)
        return dropoff

    def schedule_orders(self, orders):
        assert isinstance(orders, list)

        SQL = """
            INSERT INTO order_dropoffs (order_id, dropoff_date, renter_id, dt_sched)
            VALUES (%s, %s, %s, %s);
            """

        SQL_order_update = "UPDATE orders SET is_dropoff_sched = %s WHERE id = %s;"
        for order in orders:
            data = (order.id, self.dropoff_date, self.renter_id, self.dt_sched)
            Models.database.cursor.execute(SQL, data)
            Models.database.connection.commit()

            data = (True, order.id)
            Models.database.cursor.execute(SQL_order_update, data)
            Models.database.connection.commit()

    def cancel(self, order):
        SQL = "DELETE FROM order_dropoffs WHERE order_id = %s;" # Note: no quotes
        data = (order.id, )
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        SQL = "SELECT * FROM order_dropoffs WHERE dropoff_date = %s AND dt_sched = %s AND renter_id = %s;"
        data = (self.dropoff_date, self.dt_sched, self.renter_id)
        Models.database.cursor.execute(SQL, data)

        if Models.database.cursor.fetchone() is None:
            Logistics.delete({"dt_sched": self.dt_sched, "renter_id": self.renter_id})

        SQL = "UPDATE orders SET is_dropoff_sched = %s WHERE id = %s;"
        data = (False, order.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()
