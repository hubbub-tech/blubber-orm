from ._conn import sql_to_dictionary
from ._base import Models

from .addresses import AddressModelDecorator
from .items import Items #for carts

class UserModelDecorator:
    """
    A decorator on Models which provides access to the user linked by the foreign
    key `user_id`.
    """

    @property
    def user(self):
        assert self.__dict__.get("user_id") is not None
        return Users.get({"id": self.user_id})

class Users(Models, AddressModelDecorator):
    table_name = "users"
    table_primaries = ["id"]

    def __init__(self, db_data):
        #attributes
        self.id = db_data["id"] #primary key
        self._name = db_data["name"]
        self.email = db_data["email"]
        self.password = db_data["password"] #already hashed
        self.dt_joined = db_data["dt_joined"]
        self.dt_last_active = db_data["dt_last_active"]
        self.is_blocked = db_data["is_blocked"]
        self.session = db_data["session"]

        # payment
        self.payment = db_data["payment"]
        self.privkey = db_data.get("privkey")
        self.pubkey = db_data.get("pubkey")

        # address
        self.address_line_1 = db_data["address_line_1"]
        self.address_line_2 = db_data["address_line_2"]
        self.address_zip = db_data["address_zip"]

    @property
    def cart(self):
        return Carts.get({"id": self.id})

    @property
    def profile(self):
        return Profiles.get({"id": self.id})

    @property
    def name(self):
        first, last = self._name.split(",")
        return f"{first} {last}"

    @property
    def username(self):
        first, last = self._name.split(",")
        return f"{first[:4]}{last[:4]}.{self.id}"

    @property
    def alias(self):
        user_name = self.name.title().split(" ")
        alias = f"{user_name[0]} {user_name[-1][0]}."
        return alias

    @classmethod
    def get_all(cls, role=None):
        if role is None: return super().get_all()

        valid_roles = ["payees", "payers", "couriers", "renters", "listers"]
        assert role in valid_roles

        SQL = f"SELECT * FROM {role};"
        Models.database.cursor.execute(SQL)
        results = Models.database.cursor.fetchall()
        results = results.copy()

        users = []
        for result in results:
            id, = result
            user = Users.get({"id": id})
            users.append(user)
        return users

    @classmethod
    def by_address(cls, address):
        SQL = """
            SELECT * FROM users
                WHERE address_line_1 = %s
                AND address_line_2 = %s
                AND address_zip = %s;"""
        data = (address.line_1, address.line_2, address.zip)
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()

        users = []
        for result in results:
            user_dict = sql_to_dictionary(Models.database.cursor, result)
            user = Users(user_dict)
            users.append(user)
        return users

    @classmethod
    def by_zip(cls, zip):
        SQL = "SELECT * FROM users WHERE address_zip = %s;"
        data = (zip, )
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()

        users = []
        for result in results:
            user_dict = sql_to_dictionary(Models.database.cursor, result)
            user = Users(user_dict)
            users.append(user)
        return users

    @property
    def roles(self):
        roles = []

        data = (self.id, )
        couriers_query = "SELECT * FROM couriers WHERE courier_id = %s;"

        renters_query = "SELECT * FROM renters WHERE renter_id = %s;"
        listers_query = "SELECT * FROM listers WHERE lister_id = %s;"

        payers_query = "SELECT * FROM payers WHERE payer_id = %s;"
        payees_query = "SELECT * FROM payees WHERE payee_id = %s;"

        Models.database.cursor.execute(couriers_query, data)
        if Models.database.cursor.fetchone(): roles.append("couriers")

        Models.database.cursor.execute(renters_query, data)
        if Models.database.cursor.fetchone(): roles.append("renters")

        Models.database.cursor.execute(listers_query, data)
        if Models.database.cursor.fetchone(): roles.append("listers")

        Models.database.cursor.execute(payers_query, data)
        if Models.database.cursor.fetchone(): roles.append("payers")

        Models.database.cursor.execute(payees_query, data)
        if Models.database.cursor.fetchone(): roles.append("payees")

        return roles


    def set_role(role):
        valid_roles = ["payees", "payers", "couriers", "renters", "listers"]

        assert role in valid_roles, "Please provide one of the valid roles: 'payees', 'payers', 'couriers', 'renters', 'listers'."

        if role in self.roles: return

        role_id = role[:-1] + "_id" # formatting the field name according to role
        SQL = f"INSERT INTO {role} ({role_id}) VALUES (%s);"

        data = (self.id, )
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    def make_courier(self):
        if self.is_courier == False:
            SQL = "INSERT INTO couriers (courier_id) VALUES (%s);" # Note: no quotes
            data = (self.id, )
            Models.database.cursor.execute(SQL, data)
            Models.database.connection.commit()



class Couriers(Models, UserModelDecorator):
    table_name = "couriers"
    table_primaries = ["courier_id"]

    def __init__(self, db_data):
        self.courier_id = db_data["courier_id"]
        self.session = dt_data["session"]
        self.is_admin = dt_data["is_admin"]

        self.user_id = db_data["courier_id"]


class Profiles(Models, UserModelDecorator):
    table_name = "profiles"
    table_primaries = ["id"]

    def __init__(self, db_data):
        self.user_id = db_data["id"]
        self.phone = db_data["phone"]
        self.has_pic = db_data["has_pic"]
        self.bio = db_data["bio"]


class Carts(Models, UserModelDecorator):
    table_name = "carts"
    table_primaries = ["id"]

    _contents = None

    def __init__(self, db_data):
        #attributes
        self.user_id = db_data["id"]
        self._total = db_data["total"]
        self._total_deposit = db_data["total_deposit"]
        self._total_tax = db_data["total_tax"]

    @classmethod
    def by_item(cls, item):
        SQL = "SELECT cart_id FROM shopping WHERE item_id = %s;"
        data = (item.id, )
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()
        results = results.copy()

        carts = []
        for result in results:
            cart_id, = result
            cart = Carts.get({"id": cart_id})
            carts.append(cart)
        return carts

    @classmethod
    def get_shoppers(cls):
        SQL = "SELECT cart_id FROM shopping;"
        Models.database.cursor.execute(SQL)
        results = Models.database.cursor.fetchall()
        results = results.copy()

        shoppers = []
        results = set(results)
        for result in results:
            id, = result
            shopper = Users.get({"id": id})
            shoppers.append(shopper)
        return shoppers

    def print_total(self): return f"${round(self._total, 2):,.2f}"
    def size(self): return len(self.contents)

    @property
    def contents(self):
        SQL = "SELECT item_id FROM shopping WHERE cart_id = %s;" #does this return a tuple or single value?
        data = (self.user_id, )
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()
        results = results.copy()

        items = []
        for result in results:
            id, = result
            item = Items.get({"id": id})
            items.append(item)
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
        data = (
            False,
            reservation.item_id,
            reservation.renter_id,
            reservation.date_started,
            reservation.date_ended
        )
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
        data = (
            True,
            reservation.item_id,
            reservation.renter_id,
            reservation.date_started,
            reservation.date_ended
        )
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        #resetting self.contents
        self._contents = None

    def remove_without_reservation(self, item):
        """This resolves the non-commital 'add to cart' where the user didn't reserve."""
        #ASSERT reservation.item_id is NOT associated with cart_id
        SQL = "DELETE FROM shopping WHERE cart_id = %s AND item_id = %s;" #does this return a tuple or single value?
        data = (self.user_id, item.id) #sensitive to tuple order
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    #NOTE to add a reservation to this later, "remove_without_reservation()" then re-add with "add()"
    def add_without_reservation(self, item):
        """This is a non-commital add to cart where the user doesn't have to reserve immediately."""
        #ASSERT reservation.item_id is NOT associated with cart_id
        SQL = "INSERT INTO shopping (cart_id, item_id) VALUES (%s, %s);" #does this return a tuple or single value?
        data = (self.user_id, item.id) #sensitive to tuple order
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

    def contains(self, item):
        """Check if the cart contains this item."""

        SQL = f"SELECT * FROM shopping WHERE cart_id = %s AND item_id = %s;"
        data = (self.user_id, item.id)

        Models.database.cursor.execute(SQL, data)
        result = Models.database.cursor.fetchone()

        return result is not None

    def get_reserved_contents(self):
        SQL = """
            SELECT item_id FROM reservations
                WHERE is_in_cart = %s AND renter_id = %s AND is_calendared = %s;""" #does this return a tuple or single value?
        data = (True, self.user_id, False)
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()
        results = results.copy()

        items = []
        for result in results:
            id, = result
            item = Items.get({"id": id})
            items.append(item)
        return items
