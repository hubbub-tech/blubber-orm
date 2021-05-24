from .db import sql_to_dictionary
from .base import Models

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
        SQL = """
            SELECT * FROM addresses
                WHERE num = %s AND street = %s AND apt = %s AND zip = %s;""" # Note: no quotes
        data = (
            address_keys['num'],
            address_keys['street'],
            address_keys['apt'],
            address_keys['zip'])
        cls.database.cursor.execute(SQL, data)
        db_address = sql_to_dictionary(cls.database.cursor, cls.database.cursor.fetchone())
        return Addresses(db_address) # query here

    #TODO: Addresses shouldnt change once created
    @classmethod
    def set(cls, address_keys, changes):
        targets = [f"{target} = %s" for target in changes.keys()]
        targets_str = ", ".join(targets)
        SQL = f"""
            UPDATE addresses SET {targets_str}
                WHERE num = %s AND street = %s AND apt = %s AND zip = %s;""" # Note: no quotes
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
        SQL = """
            DELETE * FROM addresses
                WHERE num = %s AND street = %s AND apt = %s AND zip = %s;""" # Note: no quotes
        data = (
            address_keys['num'],
            address_keys['street'],
            address_keys['apt'],
            address_keys['zip'])
        cls.database.cursor.execute(SQL, data)
        cls.database.connection.commit()

    def display(self):
        return f"{self.num} {self.street}, {self.city}, {self.state} {self.zip_code}"

    def region(self):
        return f"{self.city}, {self.state}"

    def refresh(self):
        address_keys = {
            "num": self.num,
            "street": self.street,
            "apt": self.apt,
            "zip": self.zip_code}
        self = Addresses.get(address_keys)
