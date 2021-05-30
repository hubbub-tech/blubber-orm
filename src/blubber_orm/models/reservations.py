from .db import sql_to_dictionary
from .base import Models

class ReservationModelDecorator:
    """
    A decorator on Models which provides access to the user linked by the foreign
    keys for `reservations`.
    """

    _reservation = None

    @property
    def reservation(self):
        model_class = type(self)
        if "_res_date_start" in model_class.__dict__.keys(): #in reality it needs the other res keys too
            if self._reservation is None:
                reservation_keys = {
                    "date_started": self._res_date_start,
                    "date_ended": self._res_date_end,
                    "renter_id": self._res_renter_id,
                    "item_id": self._res_item_id}
                self._reservation = Reservations.get(reservation_keys)
            return self._reservation
        else:
            raise Exception("This class cannot inherit from the reservation decorator. No res keys provided.")

    @property
    def renter_id(self):
        return self._res_renter_id

    @property
    def item_id(self):
        return self._res_item_id

    @property
    def res_date_start(self):
        return self._res_date_start

    @property
    def res_date_end(self):
        return self._res_date_end

class Reservations(Models):
    table_name = "reservations"
    table_primaries = ["date_started", "date_ended", "item_id", "renter_id"]

    def __init__(self, db_data):
        #attributes
        self.date_started = db_data["date_started"]
        self.date_ended = db_data["date_ended"]
        self.is_calendared = db_data["is_calendared"]
        self.is_extended = db_data["is_extended"]
        self.is_in_cart = db_data["is_in_cart"]
        self._charge = db_data["charge"]
        self._deposit = db_data["deposit"]
        self.item_id = db_data["item_id"]
        self.renter_id = db_data["renter_id"]
        self.dt_created = db_data["dt_created"]

    def print_total(self):
        """This is how much user must pay = charge + deposit"""
        return self._charge + self._deposit

    def print_deposit(self):
        return f"${self._deposit:,.2f}"

    def print_charge(self):
        return f"${self._charge:,.2f}"

    def length(self):
        return (self.date_started - self.date_ended).days

    def refresh(self):
        reservation_keys = {
            "date_started": self.date_started,
            "date_ended": self.date_ended,
            "renter_id": self.renter_id,
            "item_id": self.item_id}
        self = Reservations.get(reservation_keys)

    @classmethod
    def set(cls, reservation_keys, changes):
        targets = [f"{target} = %s" for target in changes.keys()]
        targets_str = ", ".join(targets)
        SQL = """
            UPDATE reservations SET {targets_str}
                WHERE date_started = %s
                AND date_ended = %s
                AND renter_id = %s
                AND item_id = %s;""" # Note: no quotes
        updates = [value for value in changes.values()]
        keys = [
            reservation_keys['date_started'],
            reservation_keys['date_ended'],
            reservation_keys['renter_id'],
            reservation_keys['item_id']]
        data = tuple(updates + keys)
        cls.database.cursor.execute(SQL, data)
        cls.database.connection.commit()

    @classmethod
    def get(cls, reservation_keys):
        SQL = """
            SELECT * FROM reservations
                WHERE date_started = %s
                AND date_ended = %s
                AND renter_id = %s
                AND item_id = %s;""" # Note: no quotes
        data = (
            reservation_keys['date_started'],
            reservation_keys['date_ended'],
            reservation_keys['renter_id'],
            reservation_keys['item_id'])
        cls.database.cursor.execute(SQL, data)
        db_reservation = sql_to_dictionary(cls.database.cursor, cls.database.cursor.fetchone())
        return Reservations(db_obj)

    @classmethod
    def delete(cls, reservation_keys):
        SQL = """
            DELETE * FROM reservations
                WHERE date_started = %s
                AND date_ended = %s
                AND renter_id = %s
                AND item_id = %s;""" # Note: no quotes
        data = (
            reservation_keys['date_started'],
            reservation_keys['date_ended'],
            reservation_keys['renter_id'],
            reservation_keys['item_id'])
        cls.database.cursor.execute(SQL, data)
        cls.database.connection.commit()
