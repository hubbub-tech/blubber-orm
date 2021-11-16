import calendar as calpy
from datetime import datetime, date, timedelta

from ._conn import sql_to_dictionary
from ._base import Models

from .addresses import AddressModelDecorator
from .reservations import Reservations #for calendars

class ItemModelDecorator:
    """
    A decorator on Models which provides access to the item linked by the foreign
    key `item_id`.
    """

    @property
    def item(self):
        assert self.__dict__.get("item_id") is not None
        return Items.get({"id": self.item_id})

class Items(Models, AddressModelDecorator):
    table_name = "items"
    table_primaries = ["id"]

    def __init__(self, db_data):
        #attributes
        self.id = db_data["id"]
        self.name = db_data["name"]
        self.dt_created = db_data["dt_created"]

        self.price = db_data["price"]
        self.is_available = db_data["is_available"]
        self.is_featured = db_data["is_featured"]

        self.is_locked = db_data["is_locked"]
        self.is_routed = db_data["is_routed"]
        self.last_locked = db_data["last_locked"]
        self.lister_id = db_data["lister_id"]
        #address
        self.address_num = db_data["address_num"]
        self.address_street = db_data["address_street"]
        self.address_apt = db_data["address_apt"]
        self.address_zip = db_data["address_zip"]

    @property
    def details(self):
        return Details.get({"id": self.id})

    @property
    def calendar(self):
        return Calendars.get({"id": self.id})

    @classmethod
    def by_address(cls, address):
        SQL = """
            SELECT * FROM items
                WHERE address_num = %s
                AND address_street = %s
                AND address_apt = %s
                AND address_zip = %s;"""
        data = (address.num, address.street, address.apt, address.zip)
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()

        items = []
        for result in results:
            item_dict = sql_to_dictionary(Models.database.cursor, result)
            item = Items(item_dict)
            items.append(item)
        return items

    @classmethod
    def by_zip(cls, zip):
        SQL = "SELECT * FROM items WHERE address_zip = %s;"
        data = (zip, )
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()

        items = []
        for result in results:
            item_dict = sql_to_dictionary(Models.database.cursor, result)
            item = Items(item_dict)
            items.append(item)
        return items

    @classmethod
    def by_lister(cls, user):
        SQL = "SELECT * FROM items WHERE lister_id = %s;" # Note: no quotes
        data = (user.id, )
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()

        items = []
        for result in results:
            item_dict = sql_to_dictionary(Models.database.cursor, result)
            item = Items(item_dict)
            items.append(item)
        return items

    @classmethod
    def by_tag(cls, tag):
        SQL = "SELECT item_id FROM tagging WHERE tag_name = %s;"
        data = (tag.name, )
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall() # [(item_id,),...]
        results = results.copy() # shallow copy is needed to preserve the cursor

        items = []
        for result in results:
            item_id, = result
            item = Items.get({"id": item_id})
            items.append(item)
        return items

    def lock(self, user):
        SQL = "UPDATE items SET is_locked = %s, last_locked = %s WHERE id = %s;" # Note: no quotes
        data = (True, user.id, self.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        self.is_locked = True
        self.last_locked = user.id

    def unlock(self):
        SQL = "UPDATE items SET is_locked = %s, is_routed = %s, last_locked = %s WHERE id = %s;"
        data = (False, False, None, self.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        self.is_locked = False
        self.is_routed = False
        self.last_locked = None

    def add_tag(self, tag):
        SQL = "INSERT INTO tagging (item_id, tag_name) VALUES (%s, %s);"
        data = (self.id, tag.name)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    def remove_tag(self, tag):
        SQL = "DELETE FROM tagging WHERE item_id = %s AND tag_name = %s;"
        data = (self.id, tag.name)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    def print_price(self): return f"${round(self.price, 2)}"

class Details(Models, ItemModelDecorator):
    table_name = "details"
    table_primaries = ["id"]

    def __init__(self, db_data):
        self.item_id = db_data["id"]
        self.description = db_data["description"]
        self._condition = db_data["condition"]
        self._weight = db_data["weight"]
        self._volume = db_data["volume"]

    @property
    def condition(self):
        condition_key = {3: 'Very Good', 2: 'Good', 1: 'Acceptable'}
        if self._condition in range(1, 4):
            return condition_key[self._condition]
        else:
            return "Like New"

    @property
    def weight(self):
        weight_key = {3: 'Heavy', 2: 'Medium', 1: 'Light'}
        if self._weight in range(1, 4):
            return weight_key[self._weight]
        else:
            return "Very Heavy"

    @property
    def volume(self):
        volume_key = {3: "Large", 2: 'Medium', 1: 'Small'}
        if self._volume in range(1, 4):
            return volume_key[self._volume]
        else:
            return "Very Large"

    def abbreviate(self, max_chars=127):
        abbreviation = ''
        if len(self.description) <= max_chars: abbreviation = self.description
        else: abbreviation = self.description[:max_chars] + "..."
        return abbreviation

class Calendars(Models, ItemModelDecorator):
    table_name = "calendars"
    table_primaries = ["id"]

    def __init__(self, db_data):
        self.item_id = db_data["id"]
        self.date_started = db_data["date_started"]
        self.date_ended = db_data["date_ended"]

    @property
    def reservations(self):
        filters = {"item_id": self.item_id, "is_calendared": True}
        return Reservations.filter(filters)

    def size(self): return len(self.reservations)

    #for remove() and add(), you need to pass the specific res, bc no way to tell otherwise
    def remove(self, reservation):
        SQL = """
            UPDATE reservations SET is_calendared = %s
                WHERE item_id = %s AND renter_id = %s AND date_started = %s AND date_ended = %s;"""
        data = (
            False,
            reservation.item_id,
            reservation.renter_id,
            reservation.date_started,
            reservation.date_ended
        )
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    def add(self, reservation):
        SQL = """
            UPDATE reservations SET is_in_cart = %s, is_calendared = %s
                WHERE item_id = %s AND renter_id = %s AND date_started = %s AND date_ended = %s;"""
        data = (
            False,
            True,
            reservation.item_id,
            reservation.renter_id,
            reservation.date_started,
            reservation.date_ended
        )
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    #determining if an item is available day-by-day
    def check_availability(self, comparison_date=date.today()):
        if self.size() > 0:
            for res in self.reservations:
                if res.date_started <= comparison_date and res.date_ended >= comparison_date:
                    return False
        return True

    #proposing the next available rental period
    def next_availability(self):
        closest_operating_date = date.today() + timedelta(days=2)
        bookings = self.reservations
        bookings.sort(key = lambda res: res.date_ended)
        if self.size() == 0:
            if closest_operating_date > self.date_started:
                return [closest_operating_date, self.date_ended]
            else:
                return [self.date_started, self.date_ended]
        for i in range(self.size()):
            if i + 1 < self.size():
                if bookings[i].date_ended < bookings[i + 1].date_started:
                    if closest_operating_date < bookings[i].date_ended:
                        return [bookings[i].date_ended, bookings[i + 1].date_started] # Original
                    elif closest_operating_date < bookings[i + 1].date_started:
                        return [closest_operating_date, bookings[i + 1].date_started]
            elif bookings[0].date_started > closest_operating_date:
                if closest_operating_date >= self.date_started:
                    return [closest_operating_date, bookings[0].date_started]
                elif bookings[0].date_started > self.date_started:
                    return [self.date_started, bookings[0].date_started]
                else:
                    return [bookings[i].date_ended, self.date_ended]
            elif closest_operating_date < self.date_ended:
                if closest_operating_date > bookings[i].date_ended:
                    return [closest_operating_date, self.date_ended]
                else:
                    return [bookings[i].date_ended, self.date_ended]
            else:
                return [closest_operating_date, closest_operating_date]

    #returns true if a reservation if valid, returns false if not, returns none if expired item
    def scheduler(self, new_res, bookings=None):
        if bookings is None:
            bookings = self.reservations
            bookings.sort(key = lambda res: res.date_ended)
        _bookings = bookings.copy()
        if len(_bookings) > 0:
            comparison_res = _bookings.pop(0)
            if comparison_res.date_ended <= new_res.date_started:
                return self.scheduler(new_res, _bookings)
            elif comparison_res.date_started >= new_res.date_ended:
                return self.scheduler(new_res, _bookings)
            else:
                return False
        elif date.today() < self.date_ended:
            return True
        else:
            return None

    def get_booked_days(self, month, stripped=True):
        if stripped:
            booked_days = []
            for res in self.reservations:
                booked_day = res.date_stated
                while booked_day.strftime("%m") == month:
                    booked_days.append(booked_day.strftime("%-d"))
                    booked_day += timedelta(days=1)
            return booked_days
        else:
            year = date.today().strftime("%Y")
            month = date.today().strftime("%-m")
            first_day_of_week, days_in_month = calpy.monthrange(int(year), int(month))
            _booked_days = item.calendar.get_booked_days(month)
            days_in_month_list = [str(day) for day in range(1, days_in_month + 1)]

            booked_days_unstripped = []
            for day in days_in_month_list:
                if day in _booked_days:
                    booked_days_unstripped.append((day, True))
                else:
                    booked_days_unstripped.append((day, False))
            return booked_days_unstripped
