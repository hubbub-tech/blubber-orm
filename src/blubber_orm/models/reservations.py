from ._conn import sql_to_dictionary
from ._base import Models

from blubber_orm.wrappers import LinkedList

class ReservationModelDecorator:
    """
    A decorator on Models which provides access to the user linked by the foreign
    keys for `reservations`.
    """

    @property
    def reservation(self):
        assert self.__dict__.get("res_date_start") is not None

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
        """A history of changes to the reservation primary keys."""

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

    @classmethod
    def swap(cls, hist_pkeys, new_pkeys):
        assert isinstance(hist_pkeys, dict)
        assert isinstance(new_pkeys, dict)

        assert cls.verify_attributes(hist_pkeys)
        assert cls.verify_attributes(new_pkeys)

        hist_reservation = Reservations.get(hist_pkeys)
        assert hist_reservation.is_calendared == True

        new_reservation_dict = {
            "date_started": new_pkeys["date_started"],
            "date_ended": new_pkeys["date_ended"],
            "renter_id": new_pkeys["renter_id"],
            "item_id": new_pkeys["item_id"],
            "is_calendared": new_pkeys["is_calendared"],
            "is_extended": new_pkeys["is_extended"],
            "is_in_cart": new_pkeys["is_in_cart"],
            "charge": new_pkeys["charge"],
            "deposit": new_pkeys["deposit"],
            "tax": new_pkeys["tax"],
            "dt_created": new_pkeys["dt_created"],
            "is_valid": new_pkeys["is_valid"],
            "hist_item_id": new_pkeys["item_id"],
            "hist_renter_id": new_pkeys["renter_id"],
            "hist_date_end": new_pkeys["date_ended"],
            "hist_date_start": new_pkeys["date_started"]
        }
        Reservations.set(hist_pkeys, {"is_calendared": False}) # @warning: concurrency? maybe lock?
        new_reservation = Reservations.insert(new_reservation_dict)

        if hist_reservation.is_extended: table = "extensions"
        else: table = "orders"

        SQL = f"""
            UPDATE {table}
            SET item_id = %s, renter_id = %s, res_date_start = %s, res_date_end = %s
            WHERE item_id = %s AND renter_id = %s AND res_date_start = %s AND res_date_end = %s
        """
        data = (
            new_reservation.item_id,
            new_reservation.renter_id,
            new_reservation.date_started,
            new_reservation.date_ended,
            hist_reservation.item_id,
            hist_reservation.renter_id,
            hist_reservation.date_started,
            hist_reservation.date_ended,
        )

        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    def print_total(self):
        """This is how much user must pay = charge + deposit + tax"""
        return f"${round(self._charge + self._deposit + self._tax, 2)}"

    def print_deposit(self): return f"${round(self._deposit, 2)}"
    def print_charge(self): return f"${round(self._charge, 2)}"
    def print_tax(self): return f"${round(self._tax, 2)}"
    def length(self): return (self.date_ended - self.date_started).days
