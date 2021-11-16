from ._conn import sql_to_dictionary
from ._base import Models

class AddressModelDecorator:
    """
    A decorator on Models which provides access to the user linked by the foreign
    keys for `addresses`.
    """

    @property
    def address(self):
        assert self.__dict__.get("address_num") is not None

        address_keys = {
            "num": self.address_num,
            "street": self.address_street,
            "apt": self.address_apt,
            "zip": self.address_zip
        }
        return Addresses.get(address_keys)

class Addresses(Models):
    table_name = "addresses"
    table_primaries = ["num", "street", "apt", "zip"]

    def __init__(self, db_data):
        self.num = db_data["num"]
        self.street = db_data["street"]
        self.apt = db_data["apt"]
        self.city = db_data["city"]
        self.state = db_data["state"]
        self.zip = db_data["zip"]

    def display(self):
        return f"{self.num} {self.street}, {self.city}, {self.state} {self.zip}"

    def region(self):
        return f"{self.city}, {self.state}"
