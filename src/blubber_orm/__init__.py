import os

from .db import DatabaseConnection
from .db import parse_uri

from .models import Addresses
from .models import Users
from .models import Profiles
from .models import Carts
from .models import Items
from .models import Details
from .models import Calendars
from .models import Reservations
from .models import Orders
from .models import Extensions
from .models import Pickups
from .models import Dropoffs
from .models import Tags
from .models import Reviews
from .models import Testimonials

#WARNING: these functions will edit whichever DB is linked in the environment...
from .queries import _create_database, _destroy_database
