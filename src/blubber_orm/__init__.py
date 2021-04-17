import os
from models import (
    Users, Profiles, Carts, Addresses, Items, Details, Calendars, Reservations,
    Orders, Extensions, Pickups, Dropoffs, Tags, Reviews, Testimonials
)
from queries import *

from db import parse_uri, DatabaseConnection

connection_uri = "postgresql://adekunlebalogun:none@localhost:5432/adekunlebalogun"
#print(connection_uri)

db_instance = DatabaseConnection.get_instance()
print(db_instance)
