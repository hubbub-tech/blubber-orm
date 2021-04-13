from abc import ABC, abstractmethod
from blubber.db import DatabaseConnection, sql_to_dictionary

class AbstractModels(ABC):
    table_name = None
    database = DatabaseConnection.get_instance()

    def __init__(self):
        self.table_columns = self._get_columns()
        self._cur = self.database.cursor
        self._conn = self.database.connection

    @classmethod
    @abstractmethod
    def insert(cls, attributes):
        pass

    @classmethod
    @abstractmethod
    def get(cls, id):
        pass

    @classmethod
    @abstractmethod
    def set(cls, id, attributes):
        pass

    @classmethod
    @abstractmethod
    def filter(cls, filters):
        pass

    @abstractmethod
    def _get_columns(self):
        pass

    @abstractmethod
    def refresh(self):
        pass

class Models(AbstractModels):

    @classmethod
    def insert(cls, attributes):
        attributes_str = ", ".join(attributes.keys())
        values = ["%s" for attribute in attributes.values()]
        values_str = ", ".join(values)
        SQL = f"INSERT INTO {cls.table_name} ({attributes_str}) VALUES ({values_str});"
        data = tuple(attributes.values())
        cls._cur.execute(SQL, data)
        cls._conn.commit()

    @classmethod
    def get(cls, id):
        SQL = f"SELECT * FROM {cls.table_name} WHERE id = %s;" # Note: no quotes
        data = (id, )
        cls._cur.execute(SQL, data)
        db_obj = sql_to_dictionary(cls._cur, cls._cur.fetchone())
        return cls(db_obj)

    @classmethod
    def set(cls, id, attributes):
        conditions = [f"{attributes} = %s" for attributes in attributes.keys()]
        conditions_str = " AND ".join(conditions)
        updates = [parameters for parameters in attributes.values()]
        SQL = f"UPDATE {cls.table_name} SET {conditions_str} WHERE id = %s;" # Note: no quotes
        data = tuple(updates + [id])
        cls._cur.execute(SQL, data)
        cls._conn.commit()

    @classmethod
    def filter(cls, filters):
        conditions = [f"{filter} = %s" for filter in filters.keys()]
        conditions_str = " AND ".join(conditions)
        SQL = f"SELECT * FROM {cls.table_name} WHERE {conditions_str};" # Note: no quotes
        data = tuple([parameters for parameters in filters.values()])
        cls._cur.execute(SQL, data)
        obj_list = []
        for query in cls._cur.fetchall():
            db_obj = sql_to_dictionary(cls._cur, query)
            obj_list.append(cls(db_obj))
        return obj_list # query here

    @classmethod
    def delete(cls, id):
        SQL = f"DELETE * FROM {cls.table_name} WHERE id = %s;" # Note: no quotes
        data = (id, )
        cls._cur.execute(SQL, data)
        cls._conn.commit()

    @classmethod
    def is_indexed(cls, query_column_names):
        return set(query_column_names).issubset(cls.table_columns)

    def _get_columns(self):
        self._cur.execute(f"SELECT * FROM {self.table_name} LIMIT 0")
        columns = [attribute.name for attribute in self._cur.description]
        return columns

    def refresh(self):
        cls = type(self)
        self = cls.get(self.id)

    def __repr__(self):
        model = self.table_name.capitalize()
        return f"<type: {model}>"

class ItemModelDecorator:
    self._item = None

    @property
    def item(self):
        model_class = type(self)
        if "item_id" in model_class.__dict__.keys():
            if self._item:
                return self._item
            return Items.get(self.item_id)
        else:
            raise Exception("This class cannot inherit from the item decorator. No item_id attribute.")

class UserModelDecorator:
    self._user = None

    @property
    def user(self):
        model_class = type(self)
        if "user_id" in model_class.__dict__.keys():
            if self._user:
                return self._user
            return Users.get(self.user_id)
        else:
            raise Exception("This class cannot inherit from the user decorator. No user_id attribute.")

class AddressModels(Models):

    def __init__(self, db_data):
        super(AddressModels, self).__init__()
        self.num = db_data["address_num"]
        self.street = db_data["address_street"]
        self.apt = db_data["address_apt"]
        self.zip = db_data["address_zip"]
        address_keys = {
            "num": self.num,
            "street": self.street,
            "apt": self.apt,
            "zip": self.zip}
        self.address = Addresses.get(address_keys)

class ReservationModels(Models, ItemModelDecorator):

    def __init__(self, db_data):
        super(ReservationModels, self).__init__()
        self.date_started = db_data["res_date_start"]
        self.date_ended = db_data["res_date_end"]
        self.renter_id = db_data["renter_id"]
        self.item_id = db_data["item_id"]
        reservation_keys = {
            "date_started": self.date_started,
            "date_ended": self.date_ended,
            "renter_id": self.renter_id,
            "item_id": self.item_id}
        self.reservation = Reservations.get(reservation_keys)

    def renter(self):
        return Users.get(self.renter_id) #the renter id is stored then searched in users

    def price(self):
        return f"${self.reservation.charge:,.2f}"
