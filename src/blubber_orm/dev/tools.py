import random
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
