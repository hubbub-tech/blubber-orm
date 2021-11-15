from .db import sql_to_dictionary
from .base import Models

from utils.structs import LinkedList

class ReservationModelDecorator:
    """
    A decorator on Models which provides access to the user linked by the foreign
    keys for `reservations`.
    """

    @property
    def reservation(self):
        "Check to see if ModelClass is compatible with reservation decorator"

        ModelClass = type(self)
        assert ModelClass.__dict__.get("res_date_start")

        reservation_keys = {
            "date_started": self.res_date_start,
            "date_ended": self.res_date_end,
            "renter_id": self.renter_id,
            "item_id": self.item_id}
        return Reservations.get(reservation_keys)

class Reservations(Models):
    table_name = "reservations"
    table_primaries = ["date_started", "date_ended", "item_id", "renter_id"]

    _history = None

    def __init__(self, db_data):
        #attributes
        self.dt_created = db_data["dt_created"]
        self.date_started = db_data["date_started"]
        self.date_ended = db_data["date_ended"]
        self.is_calendared = db_data["is_calendared"]
        self.is_extended = db_data["is_extended"]
        self.is_in_cart = db_data["is_in_cart"]
        self._charge = db_data["charge"]
        self._deposit = db_data["deposit"]
        self._tax = db_data["tax"]
        self.item_id = db_data["item_id"]
        self.renter_id = db_data["renter_id"]

        # change history
        self.hist_item_id = db_data["hist_item_id"]
        self.hist_renter_id = db_data["hist_renter_id"]
        self.hist_date_start = db_data["hist_date_start"]
        self.hist_date_end = db_data["hist_date_end"]

    # reservation history linked list in development
    @property
    def history(self):
        if self._history is None and self.hist_item_id:
            self._history = LinkedList()
            hist_reservation = Reservations.get({
                "item_id": self.hist_item_id,
                "renter_id": self.hist_renter_id,
                "date_started": self.hist_date_start,
                "date_ended": self.hist_date_end
            })
            while hist_reservation:
                self._history.put({
                    "item_id": self.hist_item_id,
                    "renter_id": self.hist_renter_id,
                    "date_started": self.hist_date_start,
                    "date_ended": self.hist_date_end
                }, hist_reservation)
                if hist_reservation.hist_item_id:
                    hist_reservation = Reservations.get({
                        "item_id": next_reservation.hist_item_id,
                        "renter_id": next_reservation.hist_renter_id,
                        "date_started": next_reservation.hist_date_start,
                        "date_ended": next_reservation.hist_date_end
                    })
                else: break
        return self._history

    def print_total(self):
        """This is how much user must pay = charge + deposit + tax"""
        return f"${round(self._charge + self._deposit + self._tax, 2)}"

    def print_deposit(self):
        return f"${round(self._deposit, 2)}"

    def print_charge(self):
        return f"${round(self._charge, 2)}"

    def print_tax(self):
        return f"${round(self._tax, 2)}"

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
        SQL = f"""
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
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    @classmethod
    def get(cls, reservation_keys):
        res = None
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
        Models.database.cursor.execute(SQL, data)
        result = Models.database.cursor.fetchone()
        if result:
            db_reservation = sql_to_dictionary(Models.database.cursor, result)
            res = Reservations(db_reservation)
        return res

    @classmethod
    def delete(cls, reservation_keys):
        SQL = """
            DELETE FROM reservations
                WHERE date_started = %s
                AND date_ended = %s
                AND renter_id = %s
                AND item_id = %s;""" # Note: no quotes
        data = (
            reservation_keys['date_started'],
            reservation_keys['date_ended'],
            reservation_keys['renter_id'],
            reservation_keys['item_id'])
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()
