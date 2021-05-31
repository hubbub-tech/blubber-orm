from .db import sql_to_dictionary
from .base import Models
from .users import Users
from .reservations import Reservations, ReservationModelDecorator

class OrderModelDecorator:
    """
    A decorator on Models which provides access to the order linked by the foreign
    key `order_id`.
    """

    _order = None

    @property
    def order(self):
        model_class = type(self)
        if "order_id" in model_class.__dict__.keys():
            if self._order is None:
                self._order = Orders.get(self.order_id)
            return self._order
        else:
            raise Exception("This class cannot inherit from the order decorator. No order_id attribute.")

class Orders(Models, ReservationModelDecorator):
    table_name = "orders"
    table_primaries = ["id"]

    _extensions = None
    _ext_date_end = None
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
        self._res_date_start = db_data["res_date_start"]
        self._res_date_end = db_data["res_date_end"]
        self._res_renter_id = db_data["renter_id"]
        self._res_item_id = db_data["item_id"]

    @property
    def ext_date_end(self):
        extensions = self.extensions
        if extensions:
            extensions.sort(key = lambda ext: ext.res_date_end)
            self._ext_date_end = extensions[-1].res_date_end
        else:
            self._ext_date_end = self._res_date_end
        return self._ext_date_end

    @property
    def lister_id(self):
        return self._lister_id

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
        if self._extensions is None:
            extensions = Extensions.filter({"order_id": self.id})
            self._extensions = extensions
        return self._extensions

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
    def by_dropoff(cls, dropoff):
        SQL = "SELECT order_id FROM order_dropoffs WHERE dropoff_date = %s, dt_sched = %s, renter_id = %s;" # Note: no quotes
        data = (dropoff.date_dropoff, dropoff._dt_sched, dropoff._renter_id)
        cls.database.cursor.execute(SQL, data)
        db_obj = sql_to_dictionary(cls.database.cursor, cls.database.cursor.fetchone()) #NOTE is this just {"order_id": order_id}?
        order = Orders.get(db_obj["order_id"])
        return order

    def early_return(self, early_return_reservation):
        #NOTE: the order also should not have extensions attached to it
        return_err = "Early returns must be earlier than the current return date."
        assert early_return_reservation.date_ended < self.res_date_end, return_err

        item_err = "The reservation is not tied to the same object."
        assert early_return_reservation.item_id == self.item_id, item_err

        renter_err = "The reservation is not tied to the same renter."
        assert early_return_reservation.renter_id == self.renter_id, renter_err

        SQL = """UPDATE orders
            SET is_pickup_scheduled = %s, res_date_start = %s, res_date_end = %s,
            WHERE id = %s;"""
        data = (
            False,
            early_return_reservation.date_started,
            early_return_reservation.date_ended,
            self.id
        )
        self.database.cursor.execute(SQL, data)
        self.database.connection.commit()

class Extensions(Models, OrderModelDecorator, ReservationModelDecorator):
    table_name = "extensions"
    table_primaries = ["order_id", "res_date_end"]

    def __init__(self, db_data):
        #order
        self.order_id = db_data["order_id"]
        #reservation
        self._res_date_start = db_data["res_date_start"]
        self._res_date_end = db_data["res_date_end"]
        self._res_renter_id = db_data["renter_id"]
        self._res_item_id = db_data["item_id"]

    @classmethod
    def get(cls, extension_keys):
        SQL = "SELECT * FROM extensions WHERE order_id = %s AND res_date_end = %s;" # Note: no quotes
        data = (extension_keys['order_id'], extension_keys['res_date_end'])
        cls.database.cursor.execute(SQL, data)
        db_obj = sql_to_dictionary(cls.database.cursor, cls.database.cursor.fetchone())
        return Extensions(db_obj)

    @classmethod
    def set(cls):
        raise Exception("Extensions are not directly editable. Edit its reservation or order instead.")

    @classmethod
    def delete(cls, extension_keys):
        SQL = "DELETE * FROM extensions WHERE order_id = %s AND res_date_end = %s;"
        data = (extension_keys['order_id'], extension_keys['res_date_end'])
        cls.database.cursor.execute(SQL, data)
        cls.database.connection.commit()

    def refresh(self):
        extension_keys = {
            "order_id": self.order_id,
            "res_date_end": self._res_date_end}
        self = Extensions.get(extension_keys)
