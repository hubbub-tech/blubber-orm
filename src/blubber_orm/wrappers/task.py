from datetime import date, datetime, time

from blubber_orm.models._base import Models
from blubber_orm.models import Users, Orders, Dropoffs, Pickups, Logistics

class TaskWrapper:

    def __init__(self, task=None):
        # if isinstance(task, dict): pass # TODO: load a dictionary into TaskWrapper
        if isinstance(task, Dropoffs):
            self.type = "dropoff"
            self.task_date = task.dropoff_date

            self.logistics = task.logistics
            self.address = task.logistics.address


        elif isinstance(task, Pickups):
            self.type = "pickup"
            self.task_date = task.pickup_date

            self.logistics = task.logistics
            self.address = task.logistics.address

        elif isinstance(task, Logistics):
            self.type = "logistics"
            self.task_date = None

            self.logistics = task
            self.address = task.address

        else: raise Exception("Passed input is not of the required type.")

        self.renter_id = task.renter_id
        self.dt_sched = task.dt_sched

        self._is_completed = None


    @property
    def orders(self):
        if  self.type == "dropoff":
            SQL = "SELECT order_id FROM order_dropoffs WHERE dropoff_date = %s AND dt_sched = %s AND renter_id = %s;"
        elif self.type == "pickup":
            SQL = "SELECT order_id FROM order_pickups WHERE pickup_date = %s AND dt_sched = %s AND renter_id = %s;"
        else:
            raise Exception(f"Sorry, there is an issue with the type: {self.type}")

        data = (self.task_date, self.dt_sched, self.renter_id)
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()
        ids = results.copy()

        orders = []
        for order_id in ids:
            order = Orders.get({"id": order_id})
            orders.append(order)

        return orders

    @property
    def is_completed(self):
        if self.type == "dropoff"
            for order in self.orders:
                if order.dt_dropoff_completed == None: return False
        elif self.type == "pickup"
            for order in self.orders:
                if order.dt_pickup_completed == None: return False
        else: raise Exception(f"Sorry, there is an issue with the type: {self.type}")
        return True

    def to_dict(self, serializable=True):
        _self_dict = self.__dict__
        if serializable:
            _serializable_dict = {}
            for key, value in _self_dict.items():
                if key[0] == "_":
                    key = key[1:]
                if isinstance(value, datetime):
                    _serializable_dict[key] = value.strftime("%Y-%m-%d %H:%M:%S.%f")
                elif isinstance(value, date):
                    _serializable_dict[key] = value.strftime("%Y-%m-%d")
                elif isinstance(value, time):
                    _serializable_dict[key] = value.strftime("%H:%M")
                elif isinstance(value, Models):
                    continue
                elif key not in ["password", "session"]:
                    _serializable_dict[key] = value
            _self_dict = _serializable_dict
        return _self_dict

    def __repr__(self): return f"<Blubber wrapper object: TaskWrapper>"
    def __eq__(self, other) : return self.__dict__ == other.__dict__
