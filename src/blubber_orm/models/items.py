import calendar as calpy
from datetime import datetime, date, timedelta

from .db import sql_to_dictionary
from .base import Models
from .addresses import AddressModelDecorator
from .reservations import Reservations #for calendars

class ItemModelDecorator:
    """
    A decorator on Models which provides access to the item linked by the foreign
    key `item_id`.
    """

    item_id = None

    @property
    def item(self):
        model_class = type(self)
        if "item_id" in model_class.__dict__.keys():
            return Items.get(self.item_id)
        else:
            raise Exception("This class cannot inherit from the item decorator. No item_id attribute.")

class Items(Models, AddressModelDecorator):
    table_name = "items"
    table_primaries = ["id"]

    _address_num = None
    _address_street = None
    _address_apt = None
    _address_zip = None

    def __init__(self, db_data):
        #attributes
        self.id = db_data["id"]
        self.name = db_data["name"]
        self._price = db_data["price"]
        self._price_per_day = self._price / 10.00 #TODO
        self._price_per_week = self._price / 5.00 #TODO
        self._price_per_month = self._price / 2.00 #TODO
        self._is_available = db_data["is_available"]
        self._is_featured = db_data["is_featured"]
        self.dt_created = db_data["dt_created"]
        self.is_locked = db_data["is_locked"]
        self._is_routed = db_data["is_routed"]
        self.last_locked = db_data["last_locked"]
        self.lister_id = db_data["lister_id"]
        #address
        self._address_num = db_data["address_num"]
        self._address_street = db_data["address_street"]
        self._address_apt = db_data["address_apt"]
        self._address_zip = db_data["address_zip"]

    @property
    def is_available(self):
        return self._is_available

    @is_available.setter
    def is_available(self, is_available):
        SQL = "UPDATE items SET is_available = %s WHERE id = %s;" # Note: no quotes
        data = (is_available, self.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()
        self._is_available = is_available

    @property
    def is_routed(self):
        return self._is_routed

    @is_routed.setter
    def is_routed(self, is_routed):
        SQL = "UPDATE items SET is_routed = %s WHERE id = %s;" # Note: no quotes
        data = (is_routed, self.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()
        self._is_routed = is_routed

    @property
    def is_featured(self):
        return self._is_featured

    @is_featured.setter
    def is_featured(self, is_featured):
        SQL = "UPDATE items SET is_featured = %s WHERE id = %s;" # Note: no quotes
        data = (is_featured, self.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()
        self._is_featured = is_featured

    @property
    def price(self):
        return self._price

    @property
    def details(self):
        return Details.get(self.id)

    @property
    def calendar(self):
        return Calendars.get(self.id)

    @classmethod
    def by_address(cls, address):
        #get all items at this address
        SQL = """
            SELECT * FROM items
                WHERE address_num = %s
                AND address_street = %s
                AND address_apt = %s
                AND address_zip = %s;""" # Note: no quotes
        data = (address.num, address.street, address.apt, address.zip_code)
        Models.database.cursor.execute(SQL, data)
        items = []
        results = Models.database.cursor.fetchall()
        for query in results:
            db_item = sql_to_dictionary(Models.database.cursor, query)
            items.append(Items(db_item))
        return items

    @classmethod
    def by_zip(cls, zip_code):
        #get all items in this general location
        SQL = "SELECT * FROM items WHERE address_zip = %s;" # Note: no quotes
        data = (zip_code, )
        Models.database.cursor.execute(SQL, data)
        items = []
        results = Models.database.cursor.fetchall()
        for query in results:
            db_item = sql_to_dictionary(Models.database.cursor, query)
            items.append(Items(db_item))
        return items

    @classmethod
    def by_lister(cls, lister):
        #get all items in this lister
        SQL = "SELECT * FROM items WHERE lister_id = %s;" # Note: no quotes
        data = (lister.id, )
        Models.database.cursor.execute(SQL, data)
        items = []
        results = Models.database.cursor.fetchall()
        for query in results:
            db_item = sql_to_dictionary(Models.database.cursor, query)
            items.append(Items(db_item))
        return items

    @classmethod
    def by_tag(cls, tag):
        SQL = "SELECT * FROM tagging WHERE tag_name = %s;"
        data = (tag.name, )
        Models.database.cursor.execute(SQL, data)
        items = []
        db_items = []
        results = Models.database.cursor.fetchall()
        for query in results:
            db_item_by_tag = sql_to_dictionary(Models.database.cursor, query)
            db_items.append(db_item_by_tag)

        for db_item_by_tag in db_items:
            items.append(Items.get(db_item_by_tag["item_id"]))
        return items

    def retail(self):
        return f"${self._price:,.2f}"

    def lock(self, user):
        SQL = "UPDATE items SET is_locked = %s, last_locked = %s WHERE id = %s;" # Note: no quotes
        data = (True, user.id, self.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()
        self.refresh()

    def unlock(self):
        SQL = "UPDATE items SET is_locked = %s, last_locked = %s, is_routed = %s WHERE id = %s;" # Note: no quotes
        data = (False, None, False, self.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()
        self.refresh()

    def add_tag(self, tag):
        SQL = "INSERT INTO tagging (item_id, tag_name) VALUES (%s, %s);" #does this return a tuple or single value?
        data = (self.id, tag.name) #sensitive to tuple order
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    def remove_tag(self, tag):
        SQL = "DELETE FROM tagging WHERE item_id = %s AND tag_name = %s;" #does this return a tuple or single value?
        data = (self.id, tag.name) #sensitive to tuple order
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    def refresh(self):
        self = Items.get(self.id)

class Details(Models, ItemModelDecorator):
    table_name = "details"
    table_primaries = ["id"]

    item_id = None

    def __init__(self, db_data):
        #attributes
        self.item_id = db_data["id"]
        self.description = db_data["description"]
        self._condition = db_data["condition"] #int
        self._weight = db_data["weight"] #int
        self._volume = db_data["volume"] #int

    @property
    def condition(self):
        condition_key = {3: 'Very Good', 2: 'Good', 1: 'Acceptible'}
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

    #RENAME: abbreviation?
    def abbreviate(self, max_chars=127):
        abbreviation = ''
        if len(self.description) > max_chars:
            abbreviation = self.description[:max_chars] + "..."
        else:
            abbreviation = self.description
        return abbreviation

    def refresh(self):
        self = Details.get(self.item_id)

class Calendars(Models, ItemModelDecorator):
    table_name = "calendars"
    table_primaries = ["id"]

    _reservations = None
    item_id = None

    def __init__(self, db_data):
        self.item_id = db_data["id"]
        self.date_started = db_data["date_started"]
        self.date_ended = db_data["date_ended"]

    @property
    def reservations(self):
        filters = {"item_id": self.item_id, "is_calendared": True}
        return Reservations.filter(filters)

    def size(self):
        return len(self.reservations)

    #for remove() and add(), you need to pass the specific res, bc no way to tell otherwise
    def remove(self, reservation):
        SQL = """
            UPDATE reservations SET is_calendared = %s
                WHERE item_id = %s AND renter_id = %s AND date_started = %s AND date_ended = %s;"""
        data = (False,
            reservation.item_id,
            reservation.renter_id,
            reservation.date_started,
            reservation.date_ended)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        #resetting self.contents
        self._reservations = None

    def add(self, reservation):
        SQL = """
            UPDATE reservations SET is_in_cart = %s, is_calendared = %s
                WHERE item_id = %s AND renter_id = %s AND date_started = %s AND date_ended = %s;"""
        data = (False, True,
            reservation.item_id,
            reservation.renter_id,
            reservation.date_started,
            reservation.date_ended)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        #resetting self.contents
        self._reservations = None

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
                    return [bookings[i].date_ended, bookings[i + 1].date_started]
            elif bookings[0].date_started > closest_operating_date:
                if closest_operating_date >= self.date_started:
                    return [closest_operating_date, bookings[0].date_started]
                elif bookings[0].date_started > self.date_started:
                    return [self.date_started, bookings[0].date_started]
                else:
                    return [bookings[i].date_ended, self.date_ended]
            else:
                return [bookings[i].date_ended, self.date_ended]

    #schedules a reservation if valid, returns false if not, returns none if expired item
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

    def refresh(self):
        self = Calendars.get(self.item_id)
