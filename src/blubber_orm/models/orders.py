from .db import sql_to_dictionary
from .base import Models
from .users import Users
from .reservations import Reservations, ReservationModelDecorator

class Orders(Models, ReservationModelDecorator):
    table_name = "orders"
    table_primaries = ["id"]

    _extensions = None
    _lister = None

    def __init__(self, db_data):
        #attributes
        self.id = db_data["id"] #primary key
        self.date_placed = db_data["date_placed"]
        self.is_online_pay = db_data["is_online_pay"]
        self._is_dropoff_scheduled = db_data["is_dropoff_sched"]
        self._is_pickup_scheduled = db_data["is_pick_sched"]
        self._lister_id = db_data["lister_id"]
        #reservation
        self._res_date_started = db_data["res_date_start"]
        self._res_date_ended = db_data["res_date_end"]
        self._res_renter_id = db_data["renter_id"]
        self._res_item_id = db_data["item_id"]

    @property
    def is_dropoff_scheduled(self):
        return self._is_dropoff_scheduled

    @is_dropoff_scheduled.setter
    def is_dropoff_scheduled(self, is_dropoff_scheduled):
        SQL = "UPDATE orders SET is_dropoff_scheduled = %s WHERE id = %s;" # Note: no quotes
        data = (is_dropoff_scheduled, self.id)
        self.database.cursor.execute(SQL, data)
        self.database.connection.commit()
        self._is_dropoff_scheduled = is_dropoff_scheduled

    @property
    def is_pickup_scheduled(self):
        return self._is_pickup_scheduled

    @is_pickup_scheduled.setter
    def is_pickup_scheduled(self, is_pickup_scheduled):
        SQL = "UPDATE orders SET is_pickup_scheduled = %s WHERE id = %s;" # Note: no quotes
        data = (is_pickup_scheduled, self.id)
        self.database.cursor.execute(SQL, data)
        self.database.connection.commit()
        self._is_pickup_scheduled = is_pickup_scheduled

    @property
    def extensions(self):
        if self.reservation.is_extended:
            if self._extensions is None:
                filters = {"renter_id": self._res_renter_id, "item_id": self._res_item_id}
                extensions = Extensions.filter(filters)
                #TODO: sort extensions sequentially, most recent to oldest
                self._extensions = extensions
            return self._extensions
        return None

    @property
    def lister(self):
        if self._lister is None:
            self._lister = Users.get(self._lister_id)
        return self._lister

    @classmethod
    def by_pickup(cls, pickup):
        SQL = "SELECT order_id FROM order_pickups WHERE pickup_date = %s, dt_sched = %s, renter_id = %s;" # Note: no quotes
        data = (pickup.date_pickup, pickup._dt_sched, pickup._renter_id)
        cls.database.cursor.execute(SQL, data)
        db_obj = sql_to_dictionary(cls.database.cursor, cls.database.cursor.fetchone()) #NOTE is this just {"order_id": order_id}?
        order = Orders.get(db_obj["order_id"])
        return order

    @classmethod
    def by_dropoff(cls, pickup):
        SQL = "SELECT order_id FROM order_dropoffs WHERE dropoff_date = %s, dt_sched = %s, renter_id = %s;" # Note: no quotes
        data = (pickup.date_dropoff, pickup._dt_sched, pickup._renter_id)
        cls.database.cursor.execute(SQL, data)
        db_obj = sql_to_dictionary(cls.database.cursor, cls.database.cursor.fetchone()) #NOTE is this just {"order_id": order_id}?
        order = Orders.get(db_obj["order_id"])
        return order

class Extensions(Models, ReservationModelDecorator):
    table_name = "extensions"
    table_primaries = ["ext_charge", "ext_date_end", "renter_id"]

    def __init__(self, db_data):
        #attributes
        self.ext_charge = db_data["ext_charge"]
        self._deposit = db_data["deposit"]
        self.ext_date_end = db_data["ext_date_end"]
        #reservation
        self._res_date_started = db_data["res_date_start"]
        self._res_date_ended = db_data["res_date_end"]
        self._res_renter_id = db_data["renter_id"]
        self._res_item_id = db_data["item_id"]

    def price(self):
        return f"${self.ext_charge:,.2f}"

    def refresh(self):
        extension_keys = {
            "ext_charge": self.ext_charge,
            "ext_date_end": self.ext_date_end,
            "renter_id": self._res_renter_id}
        self = Extensions.get(extension_keys)

    @classmethod
    def set(cls, extension_keys, changes):
        targets = [f"{target} = %s" for target in changes.keys()]
        targets_str = ", ".join(targets)
        SQL = f"""
            UPDATE extensions SET {targets_str}
                WHERE ext_charge = %s AND ext_date_end = %s AND renter_id = %s;""" # Note: no quotes
        updates = [value for value in changes.values()]
        keys = [
            extension_keys['ext_charge'],
            extension_keys['ext_date_end'],
            extension_keys['renter_id']]
        data = tuple(updates + keys)
        cls.database.cursor.execute(SQL, data)
        cls.database.connection.commit()

    @classmethod
    def get(cls, extension_keys):
        SQL = """
            SELECT * FROM extensions
                WHERE ext_charge = %s AND ext_date_end = %s AND renter_id = %s;""" # Note: no quotes
        data = (
            extension_keys['ext_charge'],
            extension_keys['ext_date_end'],
            extension_keys['renter_id'])
        cls.database.cursor.execute(SQL, data)
        db_obj = sql_to_dictionary(cls.database.cursor, cls.database.cursor.fetchone())
        return cls(db_obj)

    @classmethod
    def delete(cls, extension_keys):
        SQL = """
            DELETE * FROM extensions
                WHERE ext_charge = %s AND ext_date_end = %s AND renter_id = %s;""" # Note: no quotes
        data = (
            extension_keys['ext_charge'],
            extension_keys['ext_date_end'],
            extension_keys['renter_id'])
        cls.database.cursor.execute(SQL, data)
        cls.database.connection.commit()
