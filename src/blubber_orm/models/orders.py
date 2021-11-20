import pytz
from datetime import datetime, date, timedelta

from ._conn import sql_to_dictionary
from ._base import Models

from .users import Users # for order.lister
from .reservations import Reservations, ReservationModelDecorator

class OrderModelDecorator:
    """
    A decorator on Models which provides access to the order linked by the foreign
    key `order_id`.
    """

    @property
    def order(self):
        assert self.__dict__.get("order_id") is not None
        return Orders.get({"id": self.order_id})

class Orders(Models, ReservationModelDecorator):
    table_name = "orders"
    table_primaries = ["id"]

    _ext_date_start = None
    _ext_date_end = None

    def __init__(self, db_data):
        #attributes
        self.id = db_data["id"] #primary key
        self.date_placed = db_data["date_placed"]
        self.is_online_pay = db_data["is_online_pay"]
        self.is_dropoff_sched = db_data["is_dropoff_sched"]
        self.is_pickup_sched = db_data["is_pickup_sched"]
        self.lister_id = db_data["lister_id"]
        self.is_cancelled = db_data["is_cancelled"]
        #reservation
        self.res_date_start = db_data["res_date_start"]
        self.res_date_end = db_data["res_date_end"]
        self.renter_id = db_data["renter_id"]
        self.item_id = db_data["item_id"]

    @property
    def ext_date_start(self):
        """Get the true end date for the order, extensions considered."""

        extensions = self.extensions
        if extensions:
            extensions.sort(key = lambda ext: ext.res_date_end)
            self._ext_date_start = extensions[-1].res_date_start
        else: self._ext_date_start = self.res_date_start
        return self._ext_date_start

    @property
    def ext_date_end(self):
        """Get the true end date for the order, extensions considered."""

        extensions = self.extensions
        if extensions:
            extensions.sort(key = lambda ext: ext.res_date_end)
            self._ext_date_end = extensions[-1].res_date_end
        else: self._ext_date_end = self.res_date_end
        return self._ext_date_end


    @property
    def extensions(self):
        return Extensions.filter({"order_id": self.id})

    @property
    def dt_dropoff_completed(self):
        SQL = "SELECT dt_completed FROM order_dropoffs WHERE order_id = %s;"
        data = (self.id,)
        Models.database.cursor.execute(SQL, data)
        dt_completed = Models.database.cursor.fetchone()
        if dt_completed: return dt_completed[0]
        else: return None

    @property
    def dt_pickup_completed(self):
        SQL = "SELECT dt_completed FROM order_pickups WHERE order_id = %s;"
        data = (self.id,)
        Models.database.cursor.execute(SQL, data)
        dt_completed = Models.database.cursor.fetchone()
        if dt_completed: return dt_completed[0]
        else: return None

    def complete_dropoff(self, dt_completed=None):
        SQL1 = "SELECT dropoff_date, dt_sched, renter_id FROM order_dropoffs WHERE order_id = %s;"
        data1 = (self.id,)
        Models.database.cursor.execute(SQL1, data1)
        result = Models.database.cursor.fetchone()

        assert result is not None, "This order-dropoff relationship does not exist."
        if dt_completed is None: dt_completed = datetime.now(tz=pytz.UTC)
        SQL2 = "UPDATE order_dropoffs SET dt_completed = %s WHERE order_id = %s;"
        data2 = (dt_completed, self.id)
        Models.database.cursor.execute(SQL2, data2)
        Models.database.connection.commit()

    def complete_pickup(self, dt_completed=None):
        SQL1 = "SELECT pickup_date, dt_sched, renter_id FROM order_pickups WHERE order_id = %s;"
        data1 = (self.id, )
        Models.database.cursor.execute(SQL1, data1)
        result = Models.database.cursor.fetchone()

        assert result is not None, "This order-dropoff relationship does not exist."
        if dt_completed is None: dt_completed = datetime.now(tz=pytz.UTC)
        SQL2 = "UPDATE order_pickups SET dt_completed = %s WHERE order_id = %s;"
        data2 = (dt_completed, self.id)
        Models.database.cursor.execute(SQL2, data2)
        Models.database.connection.commit()

    @classmethod
    def by_pickup(cls, pickup):
        SQL = "SELECT order_id FROM order_pickups WHERE pickup_date = %s AND dt_sched = %s AND renter_id = %s;"
        data = (pickup.pickup_date, pickup.dt_sched, pickup.renter_id)
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()
        ids = results.copy()

        orders = []
        for order_id in ids:
            order = Orders.get({"id": order_id})
            orders.append(order)
        return orders

    @classmethod
    def by_dropoff(cls, dropoff):
        SQL = "SELECT order_id FROM order_dropoffs WHERE dropoff_date = %s AND dt_sched = %s AND renter_id = %s;"
        data = (dropoff.dropoff_date, dropoff.dt_sched, dropoff.renter_id)
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()
        ids = results.copy()

        orders = []
        for order_id in ids:
            order = Orders.get({"id": order_id})
            orders.append(order)
        return orders

class Extensions(Models, OrderModelDecorator, ReservationModelDecorator):

    table_name = "extensions"
    table_primaries = ["order_id", "res_date_end"]

    def __init__(self, db_data):
        #order
        self.order_id = db_data["order_id"]
        #reservation
        self.res_date_start = db_data["res_date_start"]
        self.res_date_end = db_data["res_date_end"]
        self.renter_id = db_data["renter_id"]
        self.item_id = db_data["item_id"]

    @classmethod
    def set(cls, extension_keys, changes):
        raise Exception("Extensions are not directly editable. Edit reservations or orders instead.")
