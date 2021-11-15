from .db import sql_to_dictionary
from .base import Models

class AddressModelDecorator:
    """
    A decorator on Models which provides access to the user linked by the foreign
    keys for `addresses`.
    """

    @property
    def address(self):
        model_class = type(self)
        if "_address_num" in model_class.__dict__.keys(): #in reality it needs the other address keys too
            address_keys = {
                "num": self._address_num,
                "street": self._address_street,
                "apt": self._address_apt,
                "zip": self._address_zip}
            return Addresses.get(address_keys)
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

    def display(self):
        return f"{self.num} {self.street}, {self.city}, {self.state} {self.zip_code}"

    def region(self):
        return f"{self.city}, {self.state}"
