from .db import sql_to_dictionary
from .base import Models
from .addresses import AddressModelDecorator
from .items import Items #for carts

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

class Users(Models, AddressModelDecorator):
    table_name = "users"
    table_primaries = ["id"]

    _cart = None
    _profile = None

    def __init__(self, db_data):
        #attributes
        self.id = db_data["id"] #primary key
        self._name = db_data["name"]
        self._email = db_data["email"]
        self._password = db_data["password"] #already hashed
        self._payment = db_data["payment"]
        self.dt_joined = db_data["dt_joined"]
        self._dt_last_active = db_data["dt_last_active"]
        self._is_blocked = db_data["is_blocked"]
        #address
        self._address_num = db_data["address_num"]
        self._address_street = db_data["address_street"]
        self._address_apt = db_data["address_apt"]
        self._address_zip = db_data["address_zip"]

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        SQL = "UPDATE users SET email = %s WHERE id = %s;" # Note: no quotes
        data = (email, self.id)
        self.database.cursor.execute(SQL, data)
        self.database.connection.commit()
        self._email = email

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, hashed_password):
        SQL = "UPDATE users SET password = %s WHERE id = %s;" # Note: no quotes
        data = (hashed_password, self.id)
        self.database.cursor.execute(SQL, data)
        self.database.connection.commit()
        self._password = hashed_password

    @property
    def payment(self):
        return self._payment

    @payment.setter
    def payment(self, email):
        SQL = "UPDATE users SET payment = %s WHERE id = %s;" # Note: no quotes
        data = (payment, self.id)
        self.database.cursor.execute(SQL, data)
        self.database.connection.commit()
        self._payment = payment

    @property
    def dt_last_active(self):
        return self._dt_last_active

    @dt_last_active.setter
    def dt_last_active(self, dt_last_active):
        SQL = "UPDATE users SET dt_last_active = %s WHERE id = %s;" # Note: no quotes
        data = (dt_last_active, self.id)
        self.database.cursor.execute(SQL, data)
        self.database.connection.commit()
        self._dt_last_active = dt_last_active

    @property
    def is_blocked(self):
        return self._is_blocked

    @is_blocked.setter
    def is_blocked(self, is_blocked):
        SQL = "UPDATE users SET is_blocked = %s WHERE id = %s;" # Note: no quotes
        data = (is_blocked, self.id)
        self.database.cursor.execute(SQL, data)
        self.database.connection.commit()
        self._is_blocked = is_blocked

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
        first, last = self._name.split(",")
        return f"{first} {last}"

    def make_username(self):
        first, last = self._name.split(",")
        return f"{first[:4]}{last[:4]}.{self.id}"

    @classmethod
    def get_by_username(cls, username):
        _, id = username.split(".")
        return Users.get(id)

    def refresh(self):
        self = Users.get(self.id)

    @classmethod
    def by_address(cls, address):
        #get all users at this address
        SQL = """
            SELECT * FROM users
                WHERE address_num = %s
                AND address_street = %s
                AND address_apt = %s
                AND address_zip = %s;""" # Note: no quotes
        data = (address.num, address.street, address.apt, address.zip_code)
        cls.database.cursor.execute(SQL, data)
        users = []
        for query in cls.database.cursor.fetchall():
            db_user = sql_to_dictionary(cls.database.cursor, query)
            users.append(cls(db_user))
        return users

    @classmethod
    def by_zip(cls, zip_code):
        #get all items in this general location
        SQL = "SELECT * FROM users WHERE address_zip = %s;" # Note: no quotes
        data = (zip_code, )
        cls.database.cursor.execute(SQL, data)
        users = []
        for query in cls.database.cursor.fetchall():
            db_user = sql_to_dictionary(cls.database.cursor, query)
            users.append(cls(db_user))
        return users

    @classmethod
    def search_renter(user):
        SQL = "SELECT * FROM renters WHERE renter_id = %s;" # Note: no quotes
        data = (user.id, )
        cls.database.cursor.execute(SQL, data)
        if cls.database.cursor.fetchone():
            return True
        else:
            return False

    @classmethod
    def search_lister(user):
        SQL = "SELECT * FROM listers WHERE lister_id = %s;" # Note: no quotes
        data = (user.id, )
        cls.database.cursor.execute(SQL, data)
        if cls.database.cursor.fetchone():
            return True
        else:
            return False

    def make_renter(self):
        #ASSERT user is not already in the renters table
        if Users.search_renter(self) == False:
            SQL = "INSERT INTO renters (renter_id) VALUES (%s);"
            data = (self.id, )
            Users.database.cursor.execute(SQL, data)
            Users.database.connection.commit()

    def make_lister(self):
        #ASSERT user is not already in the listers table
        if Users.search_lister(self) == False:
            SQL = "INSERT INTO listers (lister_id) VALUES (%s);"
            data = (self.id, )
            Users.database.cursor.execute(SQL, data)
            Users.database.connection.commit()

#No setter-getter because this class is not important
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

#NOTE: attributes total and total_deposit should NEVER have to be directly edited
class Carts(Models, UserModelDecorator):
    table_name = "carts"
    table_primaries = ["id"]

    _contents = None

    def __init__(self, db_data):
        #attributes
        self.user_id = db_data["id"]
        self._total = db_data["total"]
        self._total_deposit = db_data["total_deposit"]

    @classmethod
    def by_item(cls, item):
        SQL = "SELECT cart_id FROM shopping WHERE item_id = %s;" #does this return a tuple or single value?
        data = (item.id, )
        cls.database.cursor.execute(SQL, data)
        carts = []
        for id in cls.database.cursor.fetchall():
            carts.append(Carts.get(id))
        return carts

    def print_total(self):
        return f"${round(self._total, 2):,.2f}"

    def size(self):
        return len(self.contents)

    @property
    def contents(self):
        if self._contents is None:
            SQL = "SELECT item_id FROM shopping WHERE cart_id = %s;" #does this return a tuple or single value?
            data = (self.user_id, )
            self.database.cursor.execute(SQL, data)
            items = []
            for id in self.database.cursor.fetchall():
                items.append(Items.get(id))
            self._contents = items
        return self._contents

    #for remove() and add(), you need to pass the specific res, bc no way to tell otherwise
    def remove(self, reservation):
        #ASSERT reservation.item_id is associated with cart_id
        SQL = "DELETE * FROM shopping WHERE cart_id = %s AND item_id = %s;" #does this return a tuple or single value?
        data = (self.user_id, reservation.item_id)
        self.database.cursor.execute(SQL, data)
        self._total -= reservation._charge
        self._total_deposit -= reservation._deposit
        SQL = "UPDATE carts SET total = %s WHERE id = %s;"
        data = (self._total, self.user_id)
        self.database.cursor.execute(SQL, data)

        SQL = """
            UPDATE reservations SET is_in_cart = %s
                WHERE item_id = %s AND renter_id = %s AND date_started = %s AND date_ended = %s;"""
        data = (False,
            reservation.item_id,
            reservation.renter_id,
            reservation.date_started,
            reservation.date_ended)
        self.database.cursor.execute(SQL, data)
        self.database.connection.commit()

        #resetting self.contents
        self._contents = None

    def add(self, reservation):
        #ASSERT reservation.item_id is NOT associated with cart_id
        SQL = "INSERT INTO shopping (user_id, item_id) VALUES (%s, %s);" #does this return a tuple or single value?
        data = (self.user_id, reservation.item_id) #sensitive to tuple order
        self.database.cursor.execute(SQL, data)

        self._total += reservation._charge
        self._total_deposit += reservation._deposit

        SQL = "UPDATE carts SET total = %s WHERE id = %s;"
        data = (self._total, self.user_id)
        self.database.cursor.execute(SQL, data)

        SQL = """
            UPDATE reservations SET is_in_cart = %s
                WHERE item_id = %s AND renter_id = %s AND date_started = %s AND date_ended = %s;"""
        data = (True,
            reservation.item_id,
            reservation.renter_id,
            reservation.date_started,
            reservation.date_ended)
        self.database.cursor.execute(SQL, data)
        self.database.connection.commit()

        #resetting self.contents
        self._contents = None

    def remove_without_reservation(self, item):
        """This is a non-commital add to cart where the user doesn't have to reserve immediately."""
        #ASSERT reservation.item_id is NOT associated with cart_id
        SQL = "INSERT INTO shopping (user_id, item_id) VALUES (%s, %s);" #does this return a tuple or single value?
        data = (self.user_id, item.id) #sensitive to tuple order
        self.database.cursor.execute(SQL, data)
        self.database.connection.commit()

    #NOTE to add a reservation to this later, "remove_without_reservation()" then re-add with "add()"
    def add_without_reservation(self, item):
        """This resolves the non-commital 'add to cart' where the user didn't reserve."""
        #ASSERT reservation.item_id is NOT associated with cart_id
        SQL = "INSERT INTO shopping (user_id, item_id) VALUES (%s, %s);" #does this return a tuple or single value?
        data = (self.user_id, item.id) #sensitive to tuple order
        self.database.cursor.execute(SQL, data)
        self.database.connection.commit()

    def get_reserved_contents(self):
        SQL = """
            SELECT item_id FROM reservations
                WHERE is_in_cart = %s AND renter_id = %s AND is_calendared = %s;""" #does this return a tuple or single value?
        data = (True, self.user_id, False)
        self.database.cursor.execute(SQL, data)
        items = []
        for id in self.database.cursor.fetchall():
            items.append(Items.get(id))
        return items

    def refresh(self):
        self = Carts.get(self.user_id)
