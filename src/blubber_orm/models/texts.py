from ._conn import sql_to_dictionary
from ._base import Models

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
        SQL = "SELECT * FROM reviews WHERE author_id = %s;"
        data = (user.id, )
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()

        reviews = []
        for result in results:
            review_dict = sql_to_dictionary(Models.database.cursor, result)
            review = Reviews(review_dict)
            reviews.append(review)
        return reviews


    @classmethod
    def by_item(cls, item):
        SQL = "SELECT * FROM reviews WHERE item_id = %s;"
        data = (item.id, )
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()

        reviews = []
        for result in results:
            review_dict = sql_to_dictionary(Models.database.cursor, result)
            review = Reviews(review_dict)
            reviews.append(review)
        return reviews


class Issues(Models, UserModelDecorator):
    table_name = "issues"
    table_primaries = ["id"]

    def __init__(self, db_data):
        self.id = db_data["id"]
        self.link = db_data["link"]
        self.complaint = db_data["complaint"]
        self.resolution = db_data["resolution"]
        self.is_resolved = db_data["is_resolved"]
        self.dt_created = db_data["dt_created"]
        self.user_id = db_data["user_id"]

    def close(self, comments=None):
        SQL = "UPDATE issues SET is_resolved = %s, resolution = %s WHERE id = %s;" # Note: no quotes
        data = (True, comments, self.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        self.resolution = comments
        self.is_resolved = True

    def open(self):
        SQL = "UPDATE issues SET is_resolved = %s WHERE id = %s;" # Note: no quotes
        data = (False, self.id)
        Models.database.cursor.execute(SQL, data)
        Models.database.connection.commit()

        self.is_resolved = False

class Testimonials(Models, UserModelDecorator):
    table_name = "testimonials"
    table_primaries = ["date_created", "user_id"]

    def __init__(self, db_data):
        self.date_created = db_data["date_created"]
        self.description = db_data["description"]
        self.user_id = db_data["user_id"]

    @classmethod
    def set(cls):
        raise Exception("Testimonials are not editable. Make a new one instead.")

class Tags(Models):
    table_name = "tags"
    table_primaries = ["tag_name"]

    def __init__(self, db_data):
        self.name = db_data["tag_name"]

    @classmethod
    def by_item(cls, item):
        SQL = "SELECT tag_name FROM tagging WHERE item_id = %s;"
        data = (item.id, )
        Models.database.cursor.execute(SQL, data)
        results = Models.database.cursor.fetchall()

        tags = []
        for result in results:
            tag_name, = result
            tag = Tags({"tag_name": tag_name})
            tags.append(tag)
        return tags

    @classmethod
    def set(cls):
        raise Exception("Tags are not editable. Make a new one instead.")
