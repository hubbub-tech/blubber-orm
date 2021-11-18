import random
import sqlite3
from datetime import datetime, date, timedelta

def date_range_generator(min=date.today(), max=date.max):
    time_between_dates = max - min
    days_between_dates = time_between_dates.days
    random_duration = random.randrange(days_between_dates)
    random_offset = random.randrange(days_between_dates)
    while random_duration + random_offset >= days_between_dates:
        random_duration = random.randrange(days_between_dates)
        random_offset = random.randrange(days_between_dates)
    random_start_date = min + timedelta(days=random_offset)
    random_end_date = random_start_date + timedelta(days=random_duration)
    return random_start_date, random_end_date

def get_test_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    db = sqlite3.connect(
        current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row

    return db


def close_test_db(e=None):
    """If this request connected to the database, close the
    connection.
    """


def init_test_db(app, sql_file):
    """Clear existing data and create new tables."""
    db = get_test_db()

    with app.open_resource(sql_file) as f:
        db.executescript(f.read().decode("utf8"))
