from datetime import datetime, date, timedelta
import pytz

from blubber.db import sql_to_dictionary
from blubber.base import Models

class ItemModels(Models):
    #Cant reference in __init__() because infinite loop
    def item(self):
        return Items.get(self.item_id)

class UserModels(Models):
    #Cant reference in __init__() because infinite loop
    def user(self):
        return Users.get(self.user_id)

class AddressModels(Models):
    def __init__(self, db_data):
        self._num = db_data["address_num"]
        self._street = db_data["address_street"]
        self._apt = db_data["address_apt"]
        self._zip = db_data["address_zip"]
        address_keys = {
            "num": self._num,
            "street": self._street,
            "apt": self._apt,
            "zip": self._zip}
        self.address = Addresses.get(address_keys)

class ReservationModels(Models):
    def __init__(self, db_data):
        self._date_started = db_data["res_date_start"]
        self._date_ended = db_data["res_date_end"]
        self._renter_id = db_data["renter_id"]
        self._item_id = db_data["item_id"]
        reservation_keys = {
            "date_started": self._date_started,
            "date_ended": self._date_ended,
            "renter_id": self._renter_id,
            "item_id": self._item_id}
        self.reservation = Reservations.get(reservation_keys)

    def renter(self):
        return Users.get(self._renter_id) #the renter id is stored then searched in users

    def item(self):
        return Items.get(self._item_id)

    def price(self):
        return f"${self.reservation.charge:,.2f}"

class Addresses(Models):
    table_name = "addresses"

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
        cls._cur.execute(SQL, data)
        db_obj = sql_to_dictionary(cls._cur, cls._cur.fetchone())
        return cls(db_obj) # query here

    @classmethod
    def set(cls):
        pass

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
        cls._cur.execute(SQL, data)
        cls._conn.commit()

    @classmethod
    def local_users(cls, zip_code):
        #get all items in this general location
        SQL = f"SELECT * FROM users WHERE address_zip = %s;" # Note: no quotes
        data = (zip_code, )
        cls._cur.execute(SQL, data)
        users = []
        for query in cls._cur.fetchall():
            db_user = sql_to_dictionary(cls._cur, query)
            users.append(cls(db_user))
        return users

    @classmethod
    def local_items(cls, zip_code):
        #get all items in this general location
        SQL = f"SELECT * FROM items WHERE address_zip = %s;" # Note: no quotes
        data = (zip_code, )
        cls._cur.execute(SQL, data)
        items = []
        for query in cls._cur.fetchall():
            db_item = sql_to_dictionary(cls._cur, query)
            items.append(cls(db_item))
        return items

    def display(self):
        return f"{self.num} {self.street}, {self.city}, {self.state} {self.zip_code}"

    def region(self):
        return f"{self.city}, {self.state}"

    def occupants(self):
        #get all users at this address
        SQL = f"""
            SELECT * FROM users
                WHERE address_num = %s
                AND address_street = %s
                AND address_apt = %s
                AND address_zip = %s;""" # Note: no quotes
        data = (self.num, self.street, self.apt, self.zip_code)
        cls._cur.execute(SQL, data)
        occupants = []
        for query in cls._cur.fetchall():
            db_occupant = sql_to_dictionary(cls._cur, query)
            occupants.append(cls(db_occupant))
        return occupants

    def items(self):
        #get all items at this address
        SQL = f"""
            SELECT * FROM items
                WHERE address_num = %s
                AND address_street = %s
                AND address_apt = %s
                AND address_zip = %s;""" # Note: no quotes
        data = (self.num, self.street, self.apt, self.zip_code)
        cls._cur.execute(SQL, data)
        items = []
        for query in cls._cur.fetchall():
            db_item = sql_to_dictionary(cls._cur, query)
            items.append(cls(db_item))
        return items

    def refresh(self):
        address_keys = {
            "num": self.num,
            "street": self.street,
            "apt": self.apt,
            "zip": self.zip_code
        }
        self = Addresses.get(address_keys)

class Users(AddressModels):
    table_name = "users"

    def __init__(self, db_data):
        #Users inherits address creation from AddressModels
        super(Users, self).__init__(db_data)
        #attributes
        self.id = db_data["id"] #primary key
        self._name = db_data["name"]
        self.email = db_data["email"]
        self.password = db_data["password"] #already hashed
        self.payment = db_data["payment"]
        self.dt_joined = db_data["dt_joined"]
        self.dt_last_active = db_data["dt_last_active"]
        self.is_blocked = db_data["is_blocked"]
        #foreign keys
        self.cart = Carts.get(self.id)
        self.profile = Profiles.get(self.id)

    def name(self):
        return " ".join(self.name.split(",")).lower().title()

    def phone(self):
        return self.profile.phone

    def listings(self):
        credentials = {"lister_id": self.id}
        return Items.filter(credentials)

    def reviews(self):
        credentials = {"author_id": self.id}
        return Reviews.filter(credentials)

    def testimonials(self):
        credentials = {"user_id": self.id}
        return Testimonials.filter(credentials)

    def reservations(self):
        credentials = {"renter_id": self.id}
        return Reservations.filter(credentials)

    def refresh(self):
        self = Users.get(self.id)

class Profiles(UserModels):
    table_name = "profiles"

    def __init__(self, db_data):
        self.user_id = db_data["id"]
        self.phone = db_data["phone"]
        self.has_pic = db_data["has_pic"]
        self.bio = db_data["bio"]

    def refresh(self):
        self = Profiles.get(self.user_id)

class Carts(UserModels):
    table_name = "carts"

    def __init__(self, db_data):
        #attributes
        self.user_id = db_data["id"]
        self._total = db_data["total"]

    def total(self):
        return f"${self._total:,.2f}"

    def size(self):
        return len(self.contents())

    def contents(self):
        SQL = f"SELECT item_id FROM shopping WHERE cart_id = %s;" #does this return a tuple or single value?
        data = (self.user_id, )
        self._cur.execute(SQL, data)
        items = []
        for id in self._cur.fetchall():
            items.append(Items.get(id))
        return items

    #for remove() and add(), you need to pass the specific res, bc no way to tell otherwise
    def remove(self, reservation):
        SQL = f"DELETE * FROM shopping WHERE cart_id = %s AND item_id = %s;" #does this return a tuple or single value?
        data = (self.user_id, reservation.item_id)
        self._cur.execute(SQL, data)
        self._total -= reservation._charge
        SQL = f"UPDATE carts SET total = %s WHERE id = %s;"
        data = (self._total, self.user_id)
        self._cur.execute(SQL, data)
        self._conn.commit()

    def add(self, reservation):
        SQL = f"INSERT INTO shopping VALUES (%s, %s);" #does this return a tuple or single value?
        data = (self.user_id, reservation.item_id) #sensitive to tuple order
        self._cur.execute(SQL, data)
        self._total += reservation._charge
        SQL = f"UPDATE carts SET total = %s WHERE id = %s;"
        data = (self._total, self.user_id)
        self._cur.execute(SQL, data)
        self._conn.commit()

    def refresh(self):
        self = Carts.get(self.user_id)

class Items(AddressModels):
    table_name = "items"

    def __init__(self, db_data):
        #Users inherits address creation from AddressModels
        super(Items, self).__init__(db_data)
        #attributes
        self.id = db_data["id"]
        self.name = db_data["name"]
        self._price = db_data["price"]
        self._price_per_day = self.price / 10.00
        self.is_available = db_data["is_available"]
        self.is_featured = db_data["is_featured"]
        self.dt_created = db_data["dt_created"]
        self.is_locked = db_data["is_locked"]
        self.is_routed = db_data["is_routed"]
        self.last_locked = db_data["last_locked"]
        self._lister_id = db_data["lister_id"]
        self.details = Details.get(db_data["id"])
        self.calendar = Calendars.get(db_data["id"])

    def lister(self):
        return Users.get(self._lister_id)

    def retail(self):
        return f"${self._price:,.2f}"

    def price_per_day(self):
        return f"${self._price_per_day:,.2f}"

    def reviews(self):
        credentials = {"item_id": self.id}
        return Reviews.filter(credentials)

    def active_carts(self):
        SQL = f"SELECT cart_id FROM shopping WHERE item_id = %s;" #does this return a tuple or single value?
        data = (self.id, )
        self._cur.execute(SQL, data)
        carts = []
        for id in self._cur.fetchall():
            carts.append(Carts.get(id))
        return carts

    def lock(self, user):
        SQL = f"UPDATE items SET is_locked = %s AND last_locked = %s WHERE id = %s;" # Note: no quotes
        data = (True, user.id, self.id)
        cls._cur.execute(SQL, data)
        self = Items.get(self.id)

    def unlock(self):
        SQL = f"""UPDATE items
            SET is_locked = %s
                AND last_locked = %s
                AND is_routed = %s
                WHERE id = %s;""" # Note: no quotes
        data = (False, 0, False, self.id)
        cls._cur.execute(SQL, data)
        self = Items.get(self.id)

    #determining if an item is available day-by-day
    def check_availability(self, current_date=date.today()):
        if self.calendar.size() > 0:
            for res in self.calendar.reservations():
                if res.date_started <= current_date and res.date_ended >= current_date:
                    return False
        return True

    #proposing the next available rental period
    def next_availability(self):
        closest_operating_date = date.today() + timedelta(days=2)
        bookings = self.calendar.reservations()
        bookings.sort(key = lambda res: res.date_ended)
        if self.calendar.size() == 0:
            if closest_operating_date > self.calendar.date_started:
                return [closest_operating_date, self.calendar.date_ended]
            else:
                return [self.calendar.date_started, self.calendar.date_ended]
        for i in range(self.calendar.size()):
            if i + 1 < self.calendar.size():
                if bookings[i].date_ended < bookings[i + 1].date_started:
                    return [bookings[i].date_ended, bookings[i + 1].date_started]
            elif bookings[0].date_started > closest_operating_date:
                if closest_operating_date >= self.calendar.date_started:
                    return [closest_operating_date, bookings[0].date_started]
                elif bookings[0].date_started > self.calendar.date_started:
                    return [self.calendar.date_started, bookings[0].date_started]
                else:
                    return [bookings[i].date_ended, self.calendar.date_ended]
            else:
                return [bookings[i].date_ended, self.calendar.date_ended]

    def refresh(self):
        self = Items.get(self.id)

class Details(ItemModels):
    table_name = "details"

    def __init__(self, db_data):
        #attributes
        self.item_id = db_data["id"]
        self.description = db_data["description"]
        self._condition = db_data["condition"] #int
        self._weight = db_data["weight"] #int
        self._volume = db_data["volume"] #int
        #foreign_key

    def condition(self):
        condition_key = {3: 'Very Good', 2: 'Good', 1: 'Acceptible'}
        if self.condition in range(1, 4):
            return condition_key[self.condition]
        else:
            return "Like New"

    def weight(self):
        weight_key = {3: 'Heavy', 2: 'Medium', 1: 'Light'}
        if self.weight in range(1, 4):
            return weight_key[self.weight]
        else:
            return "Very Heavy"

    def volume(self):
        volume_key = {3: "Large", 2: 'Medium', 1: 'Small'}
        if self.volume in range(1, 4):
            return volume_key[self.volume]
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

class Calendars(ItemModels):
    table_name = "calendars"

    def __init__(self, db_data):
        self.item_id = db_data["id"]
        self.date_started = db_data["date_started"]
        self.date_ended = db_data["date_ended"]

    def reservations(self):
        credentials = {"item_id": self.item_id}
        return Reservations.filter(credentials)

    def size(self):
        return len(self.reservations())

    #schedules a reservation if valid, returns false if not, returns none if expired item
    def scheduler(self, new_res, bookings=None):
        if not bookings:
            bookings = self.reservations()
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
        bookings = self.reservations()
        for res in bookings:
            booked_day = res.date_stated
            while booked_day.strftime("%m") == month:
                booked_days.append(booked_day.strftime("%-d"))
                booked_day += timedelta(days=1)
        return booked_days

    def refresh(self):
        self = Calendars.get(self.item_id)

class Reservations(UserModels):
    table_name = "reservations"

    def __init__(self, db_data):
        #attributes
        self.date_started = db_data["date_started"]
        self.date_ended = db_data["date_ended"]
        self.is_calendared = db_data["is_calendared"]
        self.is_extended = db_data["is_extended"]
        self.is_expired = db_data["is_expired"]
        self._charge = db_data["charge"]
        self.item_id = db_data["item_id"]
        self.user_id = db_data["renter_id"]

    def item(self):
        return Items.get(self.item_id)

    def charge(self):
        return f"${self._charge:,.2f}"

    def length(self):
        return (self.date_started - self.date_ended).days

    @classmethod
    def set(cls, reservation_keys, changes):
        updates = [f"{changes} = %s" for changes in changes.keys()]
        updates_str = " AND ".join(conditions)
        updates = [change for change in changes.values()]
        SQL = f"""
            UPDATE reservations SET {updates_str}
                WHERE date_started = %s
                AND date_ended = %s
                AND renter_id = %s
                AND item_id = %s;""" # Note: no quotes
        keys = [
            reservation_keys['date_started'],
            reservation_keys['date_ended'],
            reservation_keys['renter_id'],
            reservation_keys['item_id']]
        data = tuple(updates + keys)
        cls._cur.execute(SQL, data)
        cls._conn.commit()

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
        cls._cur.execute(SQL, data)
        db_obj = sql_to_dictionary(cls._cur, cls._cur.fetchone())
        obj = cls(db_obj)
        return obj # query here

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
        cls._cur.execute(SQL, data)
        cls._conn.commit()

class Orders(ReservationModels):
    table_name = "orders"

    def __init__(self, db_data):
        super(Orders, self).__init__(db_data)
        #attributes
        self.id = db_data["id"] #primary key
        self.date_placed = db_data["date_placed"]
        self.is_online_pay = db_data["is_online_pay"]
        self.is_dropoff_scheduled = db_data["is_dropoff_sched"]
        self.is_pickup_scheduled = db_data["is_pick_sched"]
        self._lister_id = db_data["lister_id"]

    def get_pickup(self):
        if self.is_pickup_scheduled:
            SQL = f"SELECT pickup_date, dt_sched, renter_id FROM order_pickups WHERE order_id = %s;" # Note: no quotes
            data = (self.id, )
            self._cur.execute(SQL, data)
            db_obj = sql_to_dictionary(self._cur, self._cur.fetchone())
            return Pickups.get(db_obj)
        else:
            return None

    def get_dropoff(self):
        if self.is_dropoff_scheduled:
            SQL = f"SELECT dropoff_date, dt_sched, renter_id FROM order_dropoffs WHERE order_id = %s;" # Note: no quotes
            data = (self.id, )
            self._cur.execute(SQL, data)
            db_obj = sql_to_dictionary(self._cur, self._cur.fetchone())
            return Dropoffs.get(db_obj)
        else:
            return None

    def lister(self):
        return Users.get(self._lister_id) #the renter id is stored then searched in users

    # find a simpler way to see if an order is extended
    def is_extended(self):
        return self.reservation.is_extended

    def extensions(self):
        credentials = {
            "renter_id": self._renter_id,
            "item_id": self._item_id,
            }
        extensions = Extensions.filter(credentials)
        #TODO: sort extensions sequentially, most recent to oldest
        return extensions

    def identifier(self):
        return f"{self.renter.id}.{self.date.strftime("%Y.%m.%d")}"

class Extensions(ReservationModels):
    table_name = "extensions"

    def __init__(self, db_data):
        super(Extensions, self).__init__(db_data)
        #attributes
        self.ext_charge = db_data["ext_charge"]
        self.ext_date_end = db_data["ext_date_end"]

    def price(self):
        return f"${self.ext_charge:,.2f}"

class Logistics(AddressModels):
    table_name = "logistics"

    def __init__(self, db_data):
        super(Logistics, self).__init__(db_data)
        #attributes
        self.date_scheduled = db_data["dt_sched"]
        self.notes = db_data["notes"]
        self.referral = db_data["referral"]
        self._timeslots = db_data["timeslots"]
        self.renter_id = db_data["renter_id"] #the renter id is stored then searched in users

    def renter(self):
        return Users.get(self.renter_id)

    def timeslots(self):
        return self._timelots.split(",")

    @classmethod
    def get(cls, logistics_keys):
        SQL = f"SELECT * FROM logistics WHERE dt_sched = %s AND renter_id = %s;" # Note: no quotes
        data = (logistics_keys["dt_sched"], logistics_keys["renter_id"])
        cls._cur.execute(SQL, data)
        db_obj = sql_to_dictionary(cls._cur, cls._cur.fetchone())
        obj = cls(db_obj)
        return obj # query here

class Pickups(Models):
    table_name = "pickups"

    def __init__(self, db_data):
        self.date_pickup = db_data["pickup_date"]
        self._dt_sched = db_data["dt_sched"]
        self._renter_id = db_data["renter_id"]
        self.logistics = Logistics.get(db_data)

    def order(self):
        SQL = f"SELECT order_id FROM order_pickups WHERE pickup_date = %s, dt_sched = %s, renter_id = %s;" # Note: no quotes
        data = (self.date_pickup, self._dt_sched, self._renter_id)
        self._cur.execute(SQL, data)
        db_obj = sql_to_dictionary(self._cur, self._cur.fetchone())
        return Orders.get(db_obj["order_id"])

class Dropoffs(Models):
    table_name = "dropoffs"

    def __init__(self, db_data):
        self.date_dropoff = db_data["dropoff_date"]
        self._dt_sched = db_data["dt_sched"]
        self._renter_id = db_data["renter_id"]
        self.logistics = Logistics.get(db_data)

    def order(self):
        SQL = f"SELECT order_id FROM order_dropoffs WHERE dropoff_date = %s, dt_sched = %s, renter_id = %s;" # Note: no quotes
        data = (self.date_dropoff, self._dt_sched, self._renter_id)
        self._cur.execute(SQL, data)
        db_obj = sql_to_dictionary(self._cur, self._cur.fetchone())
        return Orders.get(db_obj["order_id"])

class Reviews(UserModels):
    table_name = "reviews"

    def __init__(self, db_data):
        #attributes
        self.id = db_data["id"]
        self.body = db_data["body"]
        self.dt_created = db_data["dt_created"]
        self.rating = db_data["rating"]
        self.item_id = db_data["item_id"]
        self.user_id = db_data["author_id"]

    def item(self):
        return Items.get(self.item_id)

class Testimonials(UserModels):
    table_name = "testimonials"

    def __init__(self, db_data):
        self.date_created = db_data["date_created"]
        self.description = db_data["description"]
        self.user_id = db_data["user_id"]

class Tags(Models):
    table_name = "tags"

    def __init__(self, db_data):
        self.name = db_data["tag_name"]
