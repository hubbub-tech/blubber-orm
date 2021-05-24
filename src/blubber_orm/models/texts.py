from .db import sql_to_dictionary
from .base import Models
from .items import ItemModelDecorator
from .users import UserModelDecorator

class Reviews(Models, UserModelDecorator, ItemModelDecorator):
    table_name = "reviews"
    table_primaries = ["id"]

    def __init__(self, db_data):
        #attributes
        self.id = db_data["id"]
        self.body = db_data["body"]
        self.dt_created = db_data["dt_created"]
        self.rating = db_data["rating"]
        self.item_id = db_data["item_id"]
        self.user_id = db_data["author_id"]

    @classmethod
    def by_author(cls, user):
        #get all items in this general location
        SQL = "SELECT * FROM reviews WHERE author_id = %s;" # Note: no quotes
        data = (user.id, )
        cls.database.cursor.execute(SQL, data)
        reviews = []
        for query in cls.database.cursor.fetchall():
            db_review = sql_to_dictionary(cls.database.cursor, query)
            reviews.append(cls(db_review))
        return reviews

    @classmethod
    def by_item(cls, item):
        #get all items in this general location
        SQL = "SELECT * FROM reviews WHERE item_id = %s;" # Note: no quotes
        data = (item.id, )
        cls.database.cursor.execute(SQL, data)
        reviews = []
        for query in cls.database.cursor.fetchall():
            db_review = sql_to_dictionary(cls.database.cursor, query)
            reviews.append(cls(db_review))
        return reviews

class Testimonials(Models, UserModelDecorator):
    table_name = "testimonials"
    table_primaries = ["date_created", "user_id"]

    def __init__(self, db_data):
        self.date_created = db_data["date_created"]
        self.description = db_data["description"]
        self.user_id = db_data["user_id"]

    @classmethod
    def get(cls, testimonial_keys):
        SQL = "SELECT * FROM testimonials WHERE date_created = %s AND user_id = %s;" # Note: no quotes
        data = (testimonial_keys["date_created"], testimonial_keys["user_id"])
        cls.database.cursor.execute(SQL, data)
        db_obj = sql_to_dictionary(cls.database.cursor, cls.database.cursor.fetchone())
        return cls(db_obj)

    @classmethod
    def set(cls):
        raise Exception("Testimonials are not editable. Make a new one instead.")

    @classmethod
    def delete(cls, testimonial_keys):
        SQL = "DELETE * FROM testimonials WHERE date_created = %s AND user_id = %s;" # Note: no quotes
        data = (testimonial_keys["date_created"], testimonial_keys["user_id"])
        cls.database.cursor.execute(SQL, data)
        cls.database.connection.commit()

    def refresh(self):
        testimonial_keys = {
            "date_created": self.date_created,
            "user_id": self.user_id}
        self = Testimonials.get(testimonial_keys)

class Tags(Models):
    table_name = "tags"
    table_primaries = ["tag_name"]

    def __init__(self, db_data):
        self.name = db_data["tag_name"]

    @classmethod
    def by_item(cls, item):
        SQL = "SELECT * FROM tagging WHERE item_id = %s;"
        data = (item.id, )
        cls.database.cursor.execute(SQL, data)
        tags = []
        for query in cls.database.cursor.fetchall():
            db_tag_by_item = sql_to_dictionary(cls.database.cursor, query)
            tags.append(Tags.get(db_tag_by_item["tag_name"]))
        return tags

    @classmethod
    def get(cls, tag_name):
        SQL = "SELECT * FROM tags WHERE tag_name = %s;" # Note: no quotes
        data = (testimonial_keys["tag_name"])
        cls.database.cursor.execute(SQL, data)
        db_obj = sql_to_dictionary(cls.database.cursor, cls.database.cursor.fetchone())
        return cls(db_obj)

    @classmethod
    def set(cls):
        raise Exception("Tags are not editable. Make a new one instead.")

    @classmethod
    def delete(cls, name):
        SQL = "DELETE * FROM tags WHERE tag_name = %s;" # Note: no quotes
        data = (name, )
        cls.database.cursor.execute(SQL, data)
        cls.database.connection.commit()

    def refresh(self):
        self = Tags.get(self.name)
