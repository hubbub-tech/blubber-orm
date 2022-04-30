from ._conn import sql_to_dictionary
from ._base import Models

class AddressModelDecorator:
    """
    A decorator on Models which provides access to the user linked by the foreign
    keys for `addresses`.
    """

    @property
    def address(self):
        assert self.__dict__.get("address_zip") is not None

        address_keys = {
            "line_1": self.address_line_1,
            "line_2": self.address_line_2,
            "zip": self.address_zip
        }
        return Addresses.get(address_keys)

class Addresses(Models):
    table_name = "addresses"
    table_primaries = ["line_1", "line_2", "zip"]

    def __init__(self, db_data):
        self.line_1 = db_data["line_1"]
        self.line_2 = db_data["line_2"]
        self.city = db_data["city"]
        self.state = db_data["state"]
        self.zip = db_data["zip"]

    def display(self):
        return f"{self.line_1} {self.line_2},{self.city} {self.state} {self.zip}"

    def region(self):
        return f"{self.city}, {self.state}"
