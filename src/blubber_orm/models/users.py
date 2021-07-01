from .db import sql_to_dictionary
from .base import Models
from .addresses import AddressModelDecorator
from .items import Items #for carts

class UserModelDecorator:
    """
    A decorator on Models which provides access to the user linked by the foreign
    key `user_id`.
    """

    @property
    def user(self):
        model_class = type(self)
        if "user_id" in model_class.__dict__.keys():
            return Users.get(self.user_id)
        else:
            raise Exception("This class cannot inherit from the user decorator. No user_id attribute.")

class Users(Models, AddressModelDecorator):
    table_name = "users"
    table_primaries = ["id"]

    _address_num = None
    _address_street = None
    _address_apt = None
    _address_zip = None

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
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()
        self._email = email

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, hashed_password):
        SQL = "UPDATE users SET password = %s WHERE id = %s;" # Note: no quotes
        data = (hashed_password, self.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()
        self._password = hashed_password

    @property
    def payment(self):
        return self._payment

    @payment.setter
    def payment(self, email):
        SQL = "UPDATE users SET payment = %s WHERE id = %s;" # Note: no quotes
        data = (payment, self.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()
        self._payment = payment

    @property
    def dt_last_active(self):
        return self._dt_last_active

    @dt_last_active.setter
    def dt_last_active(self, dt_last_active):
        SQL = "UPDATE users SET dt_last_active = %s WHERE id = %s;" # Note: no quotes
        data = (dt_last_active, self.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()
        self._dt_last_active = dt_last_active

    @property
    def is_blocked(self):
        return self._is_blocked

    @is_blocked.setter
    def is_blocked(self, is_blocked):
        SQL = "UPDATE users SET is_blocked = %s WHERE id = %s;" # Note: no quotes
        data = (is_blocked, self.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()
        self._is_blocked = is_blocked

    @property
    def cart(self):
        return Carts.get(self.id)

    @property
    def profile(self):
        return Profiles.get(self.id)

    @property
    def name(self):
        first, last = self._name.split(",")
        return f"{first} {last}"

    def make_username(self):
        first, last = self._name.split(",")
        return f"{first[:4]}{last[:4]}.{self.id}"

    @classmethod
    def get_all_listers(cls):
        SQL = "SELECT * FROM listers;"
        Models.database.cursor.execute(SQL)

        listers = []
        db_lister_ids = []
        results = Models.database.cursor.fetchall()
        for query in results:
            db_lister = sql_to_dictionary(Models.database.cursor, query)
            db_lister_ids.append(db_lister)

        for db_lister in db_lister_ids:
            lister = Users.get(db_lister["id"])
            listers.append(lister)
        return listers

    @classmethod
    def get_all_renters(cls):
        SQL = "SELECT * FROM renters;"
        Models.database.cursor.execute(SQL)

        renters = []
        db_renter_ids = []
        results = Models.database.cursor.fetchall()
        for query in results:
            db_renter = sql_to_dictionary(Models.database.cursor, query)
            db_renter_ids.append(db_renter)

        for db_renter in db_renter_ids:
            renter = Users.get(db_renter["id"])
            renters.append(renter)
        return renters

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
        Models.database.cursor.execute(SQL, data)
        users = []
        results = Models.database.cursor.fetchall()
        for query in results:
            db_user = sql_to_dictionary(Models.database.cursor, query)
            users.append(Users(db_user))
        return users

    @classmethod
    def by_zip(cls, zip_code):
        #get all items in this general location
        SQL = "SELECT * FROM users WHERE address_zip = %s;" # Note: no quotes
        data = (zip_code, )
        Models.database.cursor.execute(SQL, data)
        users = []
        results = Models.database.cursor.fetchall()
        for query in results:
            db_user = sql_to_dictionary(Models.database.cursor, query)
            users.append(Users(db_user))
        return users

    @classmethod
    def search_renter(cls, user):
        SQL = "SELECT * FROM renters WHERE renter_id = %s;" # Note: no quotes
        data = (user.id, )
        Models.database.cursor.execute(SQL, data)
        return Models.database.cursor.fetchone() is not None

    @classmethod
    def search_lister(cls, user):
        SQL = "SELECT * FROM listers WHERE lister_id = %s;" # Note: no quotes
        data = (user.id, )
        Models.database.cursor.execute(SQL, data)
        return Models.database.cursor.fetchone() is not None

    def make_renter(self):
        #ASSERT user is not already in the renters table
        if Users.search_renter(self) == False:
            SQL = "INSERT INTO renters (renter_id) VALUES (%s);"
            data = (self.id, )
            Models.database.cursor.execute(SQL, data)
            Models.database.connection.commit()

    def make_lister(self):
        #ASSERT user is not already in the listers table
        if Users.search_lister(self) == False:
            SQL = "INSERT INTO listers (lister_id) VALUES (%s);"
            data = (self.id, )
            Models.database.cursor.execute(SQL, data)
            Models.database.connection.commit()

#No setter-getter because this class is not important
class Profiles(Models, UserModelDecorator):

    table_name = "profiles"
    table_primaries = ["id"]

    user_id = None

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
    user_id = None

    def __init__(self, db_data):
        #attributes
        self.user_id = db_data["id"]
        self._total = db_data["total"]
        self._total_deposit = db_data["total_deposit"]
        self._total_tax = db_data["total_tax"]

    @classmethod
    def by_item(cls, item):
        SQL = "SELECT cart_id FROM shopping WHERE item_id = %s;" #does this return a tuple or single value?
        data = (item.id, )
        Models.database.cursor.execute(SQL, data)
        carts = []
        db_cart_ids = [id for id in Models.database.cursor.fetchall()]
        for id in db_cart_ids:
            carts.append(Carts.get(id))
        return carts

    def print_total(self):
        return f"${round(self._total, 2):,.2f}"

    def size(self):
        return len(self.contents)

    @property
    def contents(self):
        SQL = "SELECT item_id FROM shopping WHERE cart_id = %s;" #does this return a tuple or single value?
        data = (self.user_id, )
        Models.database.cursor.execute(SQL, data)
        items = []
        db_item_ids = [id for id in Models.database.cursor.fetchall()]
        for id in db_item_ids:
            items.append(Items.get(id))
        return items

    #for remove() and add(), you need to pass the specific res, bc no way to tell otherwise
    def remove(self, reservation):
        #ASSERT reservation.item_id is associated with cart_id
        SQL = "DELETE FROM shopping WHERE cart_id = %s AND item_id = %s;" #does this return a tuple or single value?
        data = (self.user_id, reservation.item_id)
        Models.database.cursor.execute(SQL, data)

        self._total -= reservation._charge
        self._total_deposit -= reservation._deposit
        self._total_tax -= reservation._tax

        SQL = "UPDATE carts SET total = %s, total_deposit = %s, total_tax = %s WHERE id = %s;"
        data = (self._total, self._total_deposit, self._total_tax, self.user_id)
        Models.database.cursor.execute(SQL, data)

        SQL = """
            UPDATE reservations SET is_in_cart = %s
                WHERE item_id = %s AND renter_id = %s AND date_started = %s AND date_ended = %s;"""
        data = (False,
            reservation.item_id,
            reservation.renter_id,
            reservation.date_started,
            reservation.date_ended)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        #resetting self.contents
        self._contents = None

    def add(self, reservation):
        #ASSERT reservation.item_id is NOT associated with cart_id
        SQL = "INSERT INTO shopping (cart_id, item_id) VALUES (%s, %s);" #does this return a tuple or single value?
        data = (self.user_id, reservation.item_id) #sensitive to tuple order
        Models.database.cursor.execute(SQL, data)

        self._total += reservation._charge
        self._total_deposit += reservation._deposit
        self._total_tax += reservation._tax

        SQL = "UPDATE carts SET total = %s, total_deposit = %s, total_tax = %s WHERE id = %s;"
        data = (self._total, self._total_deposit, self._total_tax, self.user_id)
        Models.database.cursor.execute(SQL, data)

        SQL = """
            UPDATE reservations SET is_in_cart = %s
                WHERE item_id = %s AND renter_id = %s AND date_started = %s AND date_ended = %s;"""
        data = (True,
            reservation.item_id,
            reservation.renter_id,
            reservation.date_started,
            reservation.date_ended)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        #resetting self.contents
        self._contents = None

    def remove_without_reservation(self, item):
        """This is a non-commital add to cart where the user doesn't have to reserve immediately."""
        #ASSERT reservation.item_id is NOT associated with cart_id
        SQL = "DELETE FROM shopping WHERE cart_id = %s AND item_id = %s;" #does this return a tuple or single value?
        data = (self.user_id, item.id) #sensitive to tuple order
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    #NOTE to add a reservation to this later, "remove_without_reservation()" then re-add with "add()"
    def add_without_reservation(self, item):
        """This resolves the non-commital 'add to cart' where the user didn't reserve."""
        #ASSERT reservation.item_id is NOT associated with cart_id
        SQL = "INSERT INTO shopping (cart_id, item_id) VALUES (%s, %s);" #does this return a tuple or single value?
        data = (self.user_id, item.id) #sensitive to tuple order
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    def contains(self, item):
        """Check if the cart contains this item."""
        return Carts.does_row_exist({
                "cart_id": self.user_id,
                "item_id": item.id
            }, table="shopping")

    def get_reserved_contents(self):
        SQL = """
            SELECT item_id FROM reservations
                WHERE is_in_cart = %s AND renter_id = %s AND is_calendared = %s;""" #does this return a tuple or single value?
        data = (True, self.user_id, False)
        Models.database.cursor.execute(SQL, data)
        items = []
        db_item_ids = [id for id in Models.database.cursor.fetchall()]
        for id in db_item_ids:
            items.append(Items.get(id))
        return items

    def refresh(self):
        self = Carts.get(self.user_id)
