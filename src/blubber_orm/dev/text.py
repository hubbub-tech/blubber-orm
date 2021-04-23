import random
import pytz
from datetime import datetime, date
from .tools import date_range_generator

firstnames = ["Andy", "Bob", "Cornelious", "Dee", "Eugene", "Flan", "Gary", "Hammy", "Ignatious",
    "Johnny", "Kakarot", "Larry", "Missy", "Naruto", "Octavious", "Pennelope", "Q", "Ron",
    "Spongebob", "Teper", "Uranus", "Vicky", "Wande", "X", "Yergen", "Zsar"]

lastnames = ["Sout", "Burt", "Coppercorn", "Day", "Krabs", "Ders", "Squarepants", "String",
    "Test", "Doe", "Frost", "Goku", "Lobster", "Eliot", "Uzimaki", "Cesar", "Vodka",
    "Tee", "Stoppable", "Cubetrousers", "Ture", "Yams", "Roberts", "Pectashun"]

streets = ["Second","Third","First","Fourth","Park","Fifth","Main","Sixth","Oak","Seventh",
    "Pine","Maple","Cedar","Eighth","Elm","View","Washington","Ninth","Lake","Hill"]

street_suffixes = ["Street", "Road", "Avenue", "Way", "Lane"]

items = ["TV", "Meaty Claws", "Clarinet", "Squeaky Boots", "One Rock", "Pineapple",
    "Computer", "Lasso", "1000lbs Weights", "Pom-Poms", "iClicker"]

def generate_identity():
    firstname = random.choice(firstnames)
    lastname = random.choice(lastnames)
    name = f"{firstname},{lastname}"
    email = f"fake_{firstname.lower()[0]}-{lastname.lower()}@gmail.com"
    payment = f"@{firstname[0]}-{lastname}-1"
    phone = f"732{random.randint(100, 999)}{random.randint(100, 999)}0"
    bio = "I love Hubbub!"
    return {
        "firstname": firstname,
        "lastname": lastname,
        "name": name,
        "email": email,
        "dt_joined": datetime.now(tz=pytz.UTC),
        "dt_last_active": datetime.now(tz=pytz.UTC),
        "is_blocked": False,
        "payment": payment,
        "phone": phone,
        "bio": bio,
        "has_pic": False,
        "total":0}

def generate_address():
    num = random.randint(1, 99)
    street = random.choice(streets)
    street_suffix = random.choice(street_suffixes)
    apt = ""
    city = "New York"
    state = "NY"
    zip = f"100{random.randint(10, 99)}"
    return {
        "num": num,
        "street": street + " " + street_suffix,
        "apt": apt,
        "city": city,
        "state": state,
        "zip": zip}

def generate_item():
    item_name = random.choice(items)
    start_date, end_date = date_range_generator(max=date(2025, 12, 31))
    item_data = {
        "lister_id" : None,
        "name" : item_name,
        "price" : random.randint(100, 400) + .99,
        "is_available": True,
        "is_featured": False,
        "dt_created": datetime.now(tz=pytz.UTC),
        "is_locked": False,
        "last_locked": None,
        "is_routed": False,
        "date_started" : start_date,
        "date_ended" : end_date,
        "description" : "This is just for lols.",
        "condition" : random.randint(1, 3),
        "volume" : random.randint(1, 3),
        "weight" : random.randint(1, 3)}
    return item_data
