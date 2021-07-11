from .db import sql_to_dictionary
from .base import Models
from .users import Users # for order.lister
from .reservations import Reservations, ReservationModelDecorator

class OrderModelDecorator:
    """
    A decorator on Models which provides access to the order linked by the foreign
    key `order_id`.
    """

    @property
    def order(self):
        model_class = type(self)
        if "order_id" in model_class.__dict__.keys():
            return Orders.get(self.order_id)
        else:
            raise Exception("This class cannot inherit from the order decorator. No order_id attribute.")

class Orders(Models, ReservationModelDecorator):
    table_name = "orders"
    table_primaries = ["id"]

    _ext_date_start = None
    _ext_date_end = None

    _res_date_start = None
    _res_date_end = None
    _res_renter_id = None
    _res_item_id = None

    def __init__(self, db_data):
        #attributes
        self.id = db_data["id"] #primary key
        self.date_placed = db_data["date_placed"]
        self.is_online_pay = db_data["is_online_pay"]
        self._is_dropoff_scheduled = db_data["is_dropoff_sched"]
        self._is_pickup_scheduled = db_data["is_pickup_sched"]
        self._lister_id = db_data["lister_id"]
        #reservation
        self._res_date_start = db_data["res_date_start"]
        self._res_date_end = db_data["res_date_end"]
        self._res_renter_id = db_data["renter_id"]
        self._res_item_id = db_data["item_id"]

    @property
    def ext_date_start(self):
        """Get the true end date for the order, extensions considered."""
        extensions = self.extensions
        if extensions:
            extensions.sort(key = lambda ext: ext._res_date_end)
            self._ext_date_start = extensions[-1]._res_date_start
        else:
            self._ext_date_start = self._res_date_start
        return self._ext_date_start

    @property
    def ext_date_end(self):
        """Get the true end date for the order, extensions considered."""
        extensions = self.extensions
        if extensions:
            extensions.sort(key = lambda ext: ext._res_date_end)
            self._ext_date_end = extensions[-1]._res_date_end
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
        SQL = "UPDATE orders SET is_dropoff_sched = %s WHERE id = %s;" # Note: no quotes
        data = (is_dropoff_scheduled, self.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()
        self._is_dropoff_scheduled = is_dropoff_scheduled

    @property
    def is_pickup_scheduled(self):
        return self._is_pickup_scheduled

    @is_pickup_scheduled.setter
    def is_pickup_scheduled(self, is_pickup_scheduled):
        SQL = "UPDATE orders SET is_pickup_sched = %s WHERE id = %s;" # Note: no quotes
        data = (is_pickup_scheduled, self.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()
        self._is_pickup_scheduled = is_pickup_scheduled

    @property
    def extensions(self):
        return Extensions.filter({"order_id": self.id})

    @property
    def lister(self):
        return Users.get(self._lister_id)

    @classmethod
    def by_pickup(cls, pickup):
        order = None
        SQL = "SELECT order_id FROM order_pickups WHERE pickup_date = %s AND dt_sched = %s AND renter_id = %s;" # Note: no quotes
        data = (pickup.pickup_date, pickup.dt_scheduled, pickup.renter_id)
        Models.database.cursor.execute(SQL, data)
        results = [id for id in Models.database.cursor.fetchall()]
        orders = []
        for order_id in results:
            orders.append(Orders.get(order_id))
        return orders

    @classmethod
    def by_dropoff(cls, dropoff):
        order = None
        SQL = "SELECT order_id FROM order_dropoffs WHERE dropoff_date = %s AND dt_sched = %s AND renter_id = %s;" # Note: no quotes
        data = (dropoff.dropoff_date, dropoff.dt_scheduled, dropoff.renter_id)
        Models.database.cursor.execute(SQL, data)
        results = [id for id in Models.database.cursor.fetchall()]
        orders = []
        for order_id in results:
            orders.append(Orders.get(order_id))
        return orders

    def refresh(self):
        self = Orders.get(self.id)

class Extensions(Models, OrderModelDecorator, ReservationModelDecorator):

    table_name = "extensions"
    table_primaries = ["order_id", "res_date_end"]

    _res_date_start = None
    _res_date_end = None
    _res_renter_id = None
    _res_item_id = None
    order_id = None

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
        ext = None
        SQL = "SELECT * FROM extensions WHERE order_id = %s AND res_date_end = %s;" # Note: no quotes
        data = (extension_keys['order_id'], extension_keys['res_date_end'])
        Models.database.cursor.execute(SQL, data)
        result = Models.database.cursor.fetchone()
        if result:
            db_ext = sql_to_dictionary(Models.database.cursor, result)
            ext = Extensions(db_ext)
        return ext

    @classmethod
    def set(cls):
        raise Exception("Extensions are not directly editable. Edit its reservation or order instead.")

    @classmethod
    def delete(cls, extension_keys):
        SQL = "DELETE FROM extensions WHERE order_id = %s AND res_date_end = %s;"
        data = (extension_keys['order_id'], extension_keys['res_date_end'])
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    def refresh(self):
        extension_keys = {
            "order_id": self.order_id,
            "res_date_end": self._res_date_end}
        self = Extensions.get(extension_keys)
