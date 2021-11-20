from ._conn import sql_to_dictionary
from ._base import Models

from .orders import OrderModelDecorator

class Charges(Models, OrderModelDecorator):
    table_name = "charges"
    table_primaries = ["id"]

    def __init__(self, db_data):
        self.id = db_data["id"]
        self.notes = db_data["notes"]
        self.amount = db_data["amount"]
        self.processor_id = db_data["processor_id"]
        self.dt_created = db_data["dt_created"]

        self.order_id = db_data["order_id"]
        self.payee_id = db_data["payee_id"]
        self.payer_id = db_data["payer_id"]
        self.issue_id = db_data["issue_id"]
