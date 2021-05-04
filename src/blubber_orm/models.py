import pytz
from datetime import datetime, date, timedelta

from .db import sql_to_dictionary
from .base import Models

class ItemModelDecorator:
    """
    A decorator on Models which provides access to the item linked by the foreign
    key `item_id`.
    """

    _item = None

    @property
    def item(self):
        model_class = type(self)
        if "item_id" in model_class.__dict__.keys():
            if self._item is None:
                self._item = Items.get(self.item_id)
            return self._item
        else:
            raise Exception("This class cannot inherit from the item decorator. No item_id attribute.")

class UserModelDecorator:
    """
    A decorator on Models which provides access to the user linked by the foreign
    key `user_id`.
    """

    _user = None

    @property
    def user(self):
        model_class = type(self)
        if "user_id" in model_class.__dict__.keys():
            if self._user is None:
                self._user = Users.get(self.user_id)
            return self._user
        else:
            raise Exception("This class cannot inherit from the user decorator. No user_id attribute.")

class AddressModelDecorator:
    """
    A decorator on Models which provides access to the user linked by the foreign
    keys for `addresses`.
    """

    _address = None

    @property
    def address(self):
        model_class = type(self)
        if "_address_num" in model_class.__dict__.keys(): #in reality it needs the other address keys too
            if self._address is None:
                address_keys = {
                    "num": self._address_num,
                    "street": self._address_street,
                    "apt": self._address_apt,
                    "zip": self._address_zip}
                self._address = Addresses.get(address_keys)
            return self._address
        else:
            raise Exception("This class cannot inherit from the address decorator. No address keys provided.")

class ReservationModelDecorator:
    """
    A decorator on Models which provides access to the user linked by the foreign
    keys for `reservations`.
    """

    _reservation = None

    @property
    def reservation(self):
        model_class = type(self)
        if "_res_date_started" in model_class.__dict__.keys(): #in reality it needs the other res keys too
            if self._reservation is None:
                reservation_keys = {
                    "date_started": self._res_date_started,
                    "date_ended": self._res_date_ended,
                    "renter_id": self._res_renter_id,
                    "item_id": self._res_item_id}
                self._reservation = Reservations.get(reservation_keys)
            return self._reservation
        else:
            raise Exception("This class cannot inherit from the reservation decorator. No res keys provided.")

class Addresses(Models):
    table_name = "addresses"
    table_primaries = ["num", "street", "apt", "zip"]

    _occupants = None
    _items = None

    def __init__(self, db_data):
        self.num = db_data["num"]
        self.street = db_data["street"]
        self.apt = db_data["apt"]
        self.city = db_data["city"]
        self.state = db_data["state"]
        self.zip_code = db_data["zip"]

    @classmethod
    def get(cls, address_keys):
        SQL = f"""
            SELECT * FROM addresses
                WHERE num = %s AND street = %s AND apt = %s AND zip = %s;""" # Note: no quotes
        data = (
            address_keys['num'],
            address_keys['street'],
            address_keys['apt'],
            address_keys['zip'])
        cls.database.cursor.execute(SQL, data)
        db_address = sql_to_dictionary(cls.database.cursor, cls.database.cursor.fetchone())
        return cls(db_address) # query here

    @classmethod
    def set(cls, address_keys, changes):
        targets = [f"{target} = %s" for target in changes.keys()]
        targets_str = ", ".join(targets)
        SQL = f"""
            UPDATE addresses SET {targets_str}
                WHERE num = %s
                AND street = %s
                AND apt = %s
                AND zip = %s;""" # Note: no quotes
        updates = [value for value in changes.values()]
        keys = [
            address_keys['num'],
            address_keys['street'],
            address_keys['apt'],
            address_keys['zip']]
        data = tuple(updates + keys)
        cls.database.cursor.execute(SQL, data)
        cls.database.connection.commit()

    @classmethod
    def delete(cls, address_keys):
        SQL = f"""
            DELETE * FROM addresses
                WHERE num = %s AND street = %s AND apt = %s AND zip = %s;""" # Note: no quotes
        data = (
            address_keys['num'],
            address_keys['street'],
            address_keys['apt'],
            address_keys['zip'])
        cls.database.cursor.execute(SQL, data)
        cls.database.connection.commit()

    @classmethod
    def local_users(cls, zip_code):
        #get all items in this general location
        SQL = f"SELECT * FROM users WHERE address_zip = %s;" # Note: no quotes
        data = (zip_code, )
        cls.database.cursor.execute(SQL, data)
        users = []
        for query in cls.database.cursor.fetchall():
            db_user = sql_to_dictionary(cls.database.cursor, query)
            users.append(Users(db_user))
        return users

    @classmethod
    def local_items(cls, zip_code):
        #get all items in this general location
        SQL = f"SELECT * FROM items WHERE address_zip = %s;" # Note: no quotes
        data = (zip_code, )
        cls.database.cursor.execute(SQL, data)
        items = []
        for query in cls.database.cursor.fetchall():
            db_item = sql_to_dictionary(cls.database.cursor, query)
            items.append(Items(db_item))
        return items

    def display(self):
        return f"{self.num} {self.street}, {self.city}, {self.state} {self.zip_code}"

    def region(self):
        return f"{self.city}, {self.state}"

    @property
    def occupants(self):
        if not self._occupants:
            #get all users at this address
            SQL = f"""
                SELECT * FROM users
                    WHERE address_num = %s
                    AND address_street = %s
                    AND address_apt = %s
                    AND address_zip = %s;""" # Note: no quotes
            data = (self.num, self.street, self.apt, self.zip_code)
            self.database.cursor.execute(SQL, data)
            occupants = []
            for query in self.database.cursor.fetchall():
                db_occupant = sql_to_dictionary(self.database.cursor, query)
                occupants.append(Users(db_occupant))
            self._occupants = occupants
        return self._occupants

    @property
    def items(self):
        if not self._items:
            #get all items at this address
            SQL = f"""
                SELECT * FROM items
                    WHERE address_num = %s
                    AND address_street = %s
                    AND address_apt = %s
                    AND address_zip = %s;""" # Note: no quotes
            data = (self.num, self.street, self.apt, self.zip_code)
            self.database.cursor.execute(SQL, data)
            items = []
            for query in self.database.cursor.fetchall():
                db_item = sql_to_dictionary(self.database.cursor, query)
                items.append(Items(db_item))
            self._items = items
        return self._items

    def refresh(self):
        address_keys = {
            "num": self.num,
            "street": self.street,
            "apt": self.apt,
            "zip": self.zip_code}
        self = Addresses.get(address_keys)

class Users(Models, AddressModelDecorator):
    table_name = "users"
    table_primaries = ["id"]

    _listings = None
    _reviews = None
    _cart = None
    _profile = None
    _testimonials = None
    _reservations = None

    def __init__(self, db_data):
        #attributes
        self.id = db_data["id"] #primary key
        self._name = db_data["name"]
        self.email = db_data["email"]
        self.password = db_data["password"] #already hashed
        self.payment = db_data["payment"]
        self.dt_joined = db_data["dt_joined"]
        self.dt_last_active = db_data["dt_last_active"]
        self.is_blocked = db_data["is_blocked"]
        #address
        self._address_num = db_data["address_num"]
        self._address_street = db_data["address_street"]
        self._address_apt = db_data["address_apt"]
        self._address_zip = db_data["address_zip"]

    def phone(self):
        return self.profile.phone

    @property
    def cart(self):
        if self._cart is None:
            self._cart = Carts.get(self.id)
        return self._cart

    @property
    def profile(self):
        if self._profile is None:
            self._profile = Profiles.get(self.id)
        return self._profile

    @property
    def name(self):
        return " ".join(self._name.split(",")).lower().title()

    @property
    def listings(self):
        if self._listings is None:
            credentials = {"lister_id": self.id}
            self._listings = Items.filter(credentials)
        return self._listings

    @property
    def reviews(self):
        if self._reviews is None:
            credentials = {"author_id": self.id}
            self._reviews = Reviews.filter(credentials)
        return self._reviews

    @property
    def testimonials(self):
        if self._testimonials is None:
            credentials = {"user_id": self.id}
            self._testimonials = Testimonials.filter(credentials)
        return self._testimonials

    @property
    def reservations(self):
        if self._reservations is None:
            credentials = {"renter_id": self.id}
            self._reservations = Reservations.filter(credentials)
        return self._reservations

class Profiles(Models, UserModelDecorator):
    table_name = "profiles"
    table_primaries = ["id"]

    def __init__(self, db_data):
        self.user_id = db_data["id"]
        self.phone = db_data["phone"]
        self.has_pic = db_data["has_pic"]
        self.bio = db_data["bio"]

    def refresh(self):
        self = Profiles.get(self.user_id)

class Carts(Models, UserModelDecorator):
    table_name = "carts"
    table_primaries = ["id"]

    _contents = None

    def __init__(self, db_data):
        #attributes
        self.user_id = db_data["id"]
        self._total = db_data["total"]


    def print_total(self):
        return f"${round(self._total, 2):,.2f}"

    def size(self):
        return len(self.contents())

    @property
    def contents(self):
        if self._contents is None:
            SQL = f"SELECT item_id FROM shopping WHERE cart_id = %s;" #does this return a tuple or single value?
            data = (self.user_id, )
            self.database.cursor.execute(SQL, data)
            items = []
            for id in self.database.cursor.fetchall():
                items.append(Items.get(id))
            self._contents = items
        return self._contents

    #for remove() and add(), you need to pass the specific res, bc no way to tell otherwise
    def remove(self, reservation):
        SQL = f"DELETE * FROM shopping WHERE cart_id = %s AND item_id = %s;" #does this return a tuple or single value?
        data = (self.user_id, reservation.item_id)
        self.database.cursor.execute(SQL, data)
        self._total -= reservation._charge
        SQL = f"UPDATE carts SET total = %s WHERE id = %s;"
        data = (self._total, self.user_id)
        self.database.cursor.execute(SQL, data)
        self.database.connection.commit()

    def add(self, reservation):
        SQL = f"INSERT INTO shopping VALUES (%s, %s);" #does this return a tuple or single value?
        data = (self.user_id, reservation.item_id) #sensitive to tuple order
        self.database.cursor.execute(SQL, data)
        self._total += reservation._charge
        SQL = f"UPDATE carts SET total = %s WHERE id = %s;"
        data = (self._total, self.user_id)
        self.database.cursor.execute(SQL, data)
        self.database.connection.commit()

    def refresh(self):
        self = Carts.get(self.user_id)

class Items(Models, AddressModelDecorator):
    table_name = "items"
    table_primaries = ["id"]

    _lister = None
    _details = None
    _calendar = None
    _active_carts = None

    def __init__(self, db_data):
        #attributes
        self.id = db_data["id"]
        self.name = db_data["name"]
        self._price = db_data["price"]
        self._price_per_day = self._price / 10.00 #TODO
        self._price_per_week = self._price / 5.00 #TODO
        self._price_per_month = self._price / 2.00 #TODO
        self.is_available = db_data["is_available"]
        self.is_featured = db_data["is_featured"]
        self.dt_created = db_data["dt_created"]
        self.is_locked = db_data["is_locked"]
        self.is_routed = db_data["is_routed"]
        self.last_locked = db_data["last_locked"]
        self._lister_id = db_data["lister_id"]
        #address
        self._address_num = db_data["address_num"]
        self._address_street = db_data["address_street"]
        self._address_apt = db_data["address_apt"]
        self._address_zip = db_data["address_zip"]

    @property
    def details(self):
        if self._details is None:
            self._details = Details.get(self.id)
        return self._details

    @property
    def calendar(self):
        if self._calendar is None:
            self._calendar = Calendars.get(self.id)
        return self._calendar

    @property
    def lister(self):
        if self._lister is None:
            self._lister = Users.get(self._lister_id)
        return self._lister

    @property
    def reviews(self):
        if self._reviews is None:
            credentials = {"item_id": self.id}
            self._reviews = Reviews.filter(credentials)
        return self._reviews

    @property
    def active_carts(self):
        if self._active_carts is None:
            SQL = f"SELECT cart_id FROM shopping WHERE item_id = %s;" #does this return a tuple or single value?
            data = (self.id, )
            self.database.cursor.execute(SQL, data)
            carts = []
            for id in self.database.cursor.fetchall():
                carts.append(Carts.get(id))
            self._active_carts = carts
        return self._active_carts

    def retail(self):
        return f"${self._price:,.2f}"

    def lock(self, user):
        SQL = f"UPDATE items SET is_locked = %s, last_locked = %s WHERE id = %s;" # Note: no quotes
        data = (True, user.id, self.id)
        self.database.cursor.execute(SQL, data)
        self.database.connection.commit()
        self = Items.get(self.id)

    def unlock(self):
        SQL = f"""UPDATE items
            SET is_locked = %s,
                last_locked = %s,
                is_routed = %s
                WHERE id = %s;""" # Note: no quotes
        data = (False, 0, False, self.id)
        self.database.cursor.execute(SQL, data)
        self.database.connection.commit()
        self = Items.get(self.id)

class Details(Models, ItemModelDecorator):
    table_name = "details"
    table_primaries = ["id"]

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

    def abbreviate(self, max_chars=127):
        abbreviation = ''
        if len(self.description) > max_chars:
            for i in range(max_chars):
                abbreviation += self.description[i]
            abbreviation += "..."
        else:
            abbreviation = self.description
        return abbreviation

    def refresh(self):
        self = Details.get(self.item_id)

class Calendars(Models, ItemModelDecorator):
    table_name = "calendars"
    table_primaries = ["id"]

    _reservations = None

    def __init__(self, db_data):
        self.item_id = db_data["id"]
        self.date_started = db_data["date_started"]
        self.date_ended = db_data["date_ended"]

    @property
    def reservations(self):
        if self._reservations is None:
            filters = {
                "item_id": self.item_id,
                "is_calendared": True}
            self._reservations = Reservations.filter(filters)
        return self._reservations

    def size(self):
        return len(self.reservations)

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
        if not bookings:
            bookings = self.reservations
            bookings.sort(key = lambda res: res.date_ended)
        _bookings = [res for res in bookings]
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

    def get_booked_days(self, month):
        booked_days = []
        bookings = self.reservations
        for res in bookings:
            booked_day = res.date_stated
            while booked_day.strftime("%m") == month:
                booked_days.append(booked_day.strftime("%-d"))
                booked_day += timedelta(days=1)
        return booked_days

    def refresh(self):
        self = Calendars.get(self.item_id)

class Reservations(Models, UserModelDecorator, ItemModelDecorator):
    table_name = "reservations"
    table_primaries = ["date_started", "date_ended", "item_id", "renter_id"]

    def __init__(self, db_data):
        #attributes
        self.date_started = db_data["date_started"]
        self.date_ended = db_data["date_ended"]
        self.is_calendared = db_data["is_calendared"]
        self.is_extended = db_data["is_extended"]
        self._charge = db_data["charge"]
        self.item_id = db_data["item_id"]
        self.user_id = db_data["renter_id"]

    def charge(self):
        return f"${self._charge:,.2f}"

    def length(self):
        return (self.date_started - self.date_ended).days

    def reserve(self):
        if self.is_calendared == False:
            reservation_keys = {
                "date_started": self.date_started,
                "date_ended": self.date_ended,
                "renter_id": self.user_id,
                "item_id": self.item_id}
            changes = {"is_calendared": True}
            Reservations.set(reservation_keys, changes)
            self.refresh()

    def extend(self):
        if self.is_extended == False:
            reservation_keys = {
                "date_started": self.date_started,
                "date_ended": self.date_ended,
                "renter_id": self.user_id,
                "item_id": self.item_id}
            changes = {"is_extended": True}
            Reservations.set(reservation_keys, changes)
            self.refresh()

    def refresh(self):
        reservation_keys = {
            "date_started": self.date_started,
            "date_ended": self.date_ended,
            "renter_id": self.user_id,
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
        cls.database.cursor.execute(SQL, data)
        cls.database.connection.commit()

    @classmethod
    def get(cls, reservation_keys):
        SQL = f"""
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
        db_obj = sql_to_dictionary(cls.database.cursor, cls.database.cursor.fetchone())
        return cls(db_obj)

    @classmethod
    def delete(cls, reservation_keys):
        SQL = f"""
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

class Orders(Models, ReservationModelDecorator):
    table_name = "orders"
    table_primaries = ["id"]

    _extensions = None

    def __init__(self, db_data):
        #attributes
        self.id = db_data["id"] #primary key
        self.date_placed = db_data["date_placed"]
        self.is_online_pay = db_data["is_online_pay"]
        self.is_dropoff_scheduled = db_data["is_dropoff_sched"]
        self.is_pickup_scheduled = db_data["is_pick_sched"]
        self._lister_id = db_data["lister_id"]
        #reservation
        self._res_date_started = db_data["res_date_start"]
        self._res_date_ended = db_data["res_date_end"]
        self._res_renter_id = db_data["renter_id"]
        self._res_item_id = db_data["item_id"]

    @property
    def extensions(self):
        if self.reservation.is_extended:
            if self._extensions is None:
                credentials = {"renter_id": self._res_renter_id, "item_id": self._res_item_id}
                extensions = Extensions.filter(credentials)
                #TODO: sort extensions sequentially, most recent to oldest
                self._extensions = extensions
            return self._extensions
        return None

    def get_pickup(self):
        if self.is_pickup_scheduled:
            SQL = f"SELECT pickup_date, dt_sched, renter_id FROM order_pickups WHERE order_id = %s;" # Note: no quotes
            data = (self.id, )
            self.database.cursor.execute(SQL, data)
            db_obj = sql_to_dictionary(self.database.cursor, self.database.cursor.fetchone())
            return Pickups.get(db_obj)
        else:
            return None

    def get_dropoff(self):
        if self.is_dropoff_scheduled:
            SQL = f"SELECT dropoff_date, dt_sched, renter_id FROM order_dropoffs WHERE order_id = %s;" # Note: no quotes
            data = (self.id, )
            self.database.cursor.execute(SQL, data)
            db_obj = sql_to_dictionary(self.database.cursor, self.database.cursor.fetchone())
            return Dropoffs.get(db_obj)
        else:
            return None

    def lister(self):
        return Users.get(self._lister_id) #the renter id is stored then searched in users

    # find a simpler way to see if an order is extended
    def is_extended(self):
        return self.reservation.is_extended

    def identifier(self):
        renter = self.renter()
        return f"{renter.id}.{self.date_placed.strftime('%Y.%m.%d')}"

class Extensions(Models, ReservationModelDecorator):
    table_name = "extensions"
    table_primaries = ["ext_charge", "ext_date_end", "renter_id"]

    def __init__(self, db_data):
        #attributes
        self.ext_charge = db_data["ext_charge"]
        self.ext_date_end = db_data["ext_date_end"]
        #reservation
        self._res_date_started = db_data["res_date_start"]
        self._res_date_ended = db_data["res_date_end"]
        self._res_renter_id = db_data["renter_id"]
        self._res_item_id = db_data["item_id"]

    def price(self):
        return f"${self.ext_charge:,.2f}"

class Logistics(Models, AddressModelDecorator):
    table_name = "logistics"
    table_primaries = ["dt_sched", "renter_id"]

    def __init__(self, db_data):
        #attributes
        self.date_scheduled = db_data["dt_sched"]
        self.notes = db_data["notes"]
        self.referral = db_data["referral"]
        self.timeslots = db_data["timeslots"].split(",")
        self.renter_id = db_data["renter_id"] #the renter id is stored then searched in users
        #address
        self._address_num = db_data["address_num"]
        self._address_street = db_data["address_street"]
        self._address_apt = db_data["address_apt"]
        self._address_zip = db_data["address_zip"]

    def renter(self):
        return Users.get(self.renter_id)

    @classmethod
    def get(cls, logistics_keys):
        SQL = f"SELECT * FROM logistics WHERE dt_sched = %s AND renter_id = %s;" # Note: no quotes
        data = (logistics_keys["dt_sched"], logistics_keys["renter_id"])
        cls.database.cursor.execute(SQL, data)
        db_obj = sql_to_dictionary(cls.database.cursor, cls.database.cursor.fetchone())
        return cls(db_obj)

class Pickups(Models):
    table_name = "pickups"
    table_primaries = ["pickup_date", "dt_sched", "renter_id"]
    _order = None
    _logistics = None

    def __init__(self, db_data):
        self.date_pickup = db_data["pickup_date"]
        self._dt_sched = db_data["dt_sched"]
        self._renter_id = db_data["renter_id"]

    @property
    def logistics(self):
        if self._logistics is None:
            keys = {
                "dt_sched": self._dt_sched,
                "renter_id": self._renter_id}
            self._logistics = Logistics.get(keys)
        return self._logistics

    @property
    def order(self):
        if self._order is None:
            SQL = f"SELECT order_id FROM order_pickups WHERE pickup_date = %s, dt_sched = %s, renter_id = %s;" # Note: no quotes
            data = (self.date_pickup, self._dt_sched, self._renter_id)
            self.database.cursor.execute(SQL, data)
            db_obj = sql_to_dictionary(self.database.cursor, self.database.cursor.fetchone()) #NOTE is this just {"order_id": order_id}?
            self._order = Orders.get(db_obj["order_id"])
        return self._order

class Dropoffs(Models):
    table_name = "dropoffs"
    table_primaries = ["dropoff_date", "dt_sched", "renter_id"]

    _order = None
    _logistics = None

    def __init__(self, db_data):
        self.date_dropoff = db_data["dropoff_date"]
        self._dt_sched = db_data["dt_sched"]
        self._renter_id = db_data["renter_id"]

    @property
    def logistics(self):
        if self._logistics is None:
            keys = {
                "dt_sched": self._dt_sched,
                "renter_id": self._renter_id}
            self._logistics = Logistics.get(keys)
        return self._logistics

    @property
    def order(self):
        if self._order is None:
            SQL = f"SELECT order_id FROM order_dropoffs WHERE dropoff_date = %s, dt_sched = %s, renter_id = %s;" # Note: no quotes
            data = (self.date_dropoff, self._dt_sched, self._renter_id)
            self.database.cursor.execute(SQL, data)
            db_obj = sql_to_dictionary(self.database.cursor, self.database.cursor.fetchone()) #NOTE is this just {"order_id": order_id}?
            self._order = Orders.get(db_obj["order_id"])
        return self._order

class Reviews(Models, UserModelDecorator, ItemModelDecorator):
    table_name = "reviews"
    table_primaries = ["id"]

    def __init__(self, db_data):
        #attributes
        self.id = db_data["id"]
        self.body = db_data["body"]
        self.dt_created = db_data["dt_created"]
        self.rating = db_data["rating"]
        self.item_id = db_data["item_id"]
        self.user_id = db_data["author_id"]

class Testimonials(Models, UserModelDecorator):
    table_name = "testimonials"
    table_primaries = ["date_made", "user_id"]

    def __init__(self, db_data):
        self.date_made = db_data["date_made"]
        self.description = db_data["description"]
        self.user_id = db_data["user_id"]

    @classmethod
    def get(cls, testimonial_keys):
        SQL = f"SELECT * FROM testimonials WHERE date_made = %s AND user_id = %s;" # Note: no quotes
        data = (testimonial_keys["date_made"], testimonial_keys["user_id"])
        cls.database.cursor.execute(SQL, data)
        db_obj = sql_to_dictionary(cls.database.cursor, cls.database.cursor.fetchone())
        return cls(db_obj)

    @classmethod
    def set(cls):
        raise Exception("Testimonials are not editable. Make a new one instead.")

    @classmethod
    def delete(cls, testimonial_keys):
        SQL = f"DELETE * FROM {cls.table_name} WHERE date_made = %s AND user_id = %s;" # Note: no quotes
        data = (testimonial_keys["date_made"], testimonial_keys["user_id"])
        cls.database.cursor.execute(SQL, data)
        cls.database.connection.commit()

    def refresh(self):
        testimonial_keys = {
            "date_made": self.date_made,
            "user_id": self.user_id}
        self = Tags.get(testimonial_keys)

class Tags(Models):
    table_name = "tags"
    table_primaries = ["tag_name"]

    def __init__(self, db_data):
        self.name = db_data["tag_name"]

    @classmethod
    def items_by_tag(cls, tag_name):
        SQL = "SELECT * FROM tagging WHERE tag_name = %s;"
        data = (tag_name, )
        self.database.cursor.execute(SQL, data)
        items = []
        for query in cls.database.cursor.fetchall():
            db_item_to_tag = sql_to_dictionary(cls.database.cursor, query)
            items.append(Items(db_item_to_tag["item_id"]))
        return items

    @classmethod
    def get(cls, tag_name):
        SQL = f"SELECT * FROM tags WHERE tag_name = %s;" # Note: no quotes
        data = (testimonial_keys["tag_name"])
        cls.database.cursor.execute(SQL, data)
        db_obj = sql_to_dictionary(cls.database.cursor, cls.database.cursor.fetchone())
        return cls(db_obj)

    @classmethod
    def set(cls):
        raise Exception("Tags are not editable. Make a new one instead.")

    @classmethod
    def delete(cls, name):
        SQL = f"DELETE * FROM {cls.table_name} WHERE tag_name = %s;" # Note: no quotes
        data = (name, )
        cls.database.cursor.execute(SQL, data)
        cls.database.connection.commit()

    def refresh(self):
        self = Tags.get(self.name)
