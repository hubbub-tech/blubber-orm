#import pytest
import unittest
import src.blubber_orm.db as db

class TestGlobalFunctions(unittest.TestCase):

    def test_sql_to_dictionary(self):
        #TODO: im not sure how to test this, but should always return type dict
        #where key=db_column_name and value=db_corresponding_value
        pass

    def test_parse_uri(self):
        #TODO: should always correctly parse database uri, given conventional
        #formatting, and should throw correct error if not.
        pass

class TestDatabaseConnection(unittest.TestCase):

    def test_singleton_before_connection(self):
        #TODO: test that no instance exists and that the class contains:
        #_instance, cursor, connection
        pass

    def test_singleton_after_connection(self):
        #TODO: test that instance exists and that the class cannot be
        #initialized again. cursor and connection should also exist
        pass

    def test_get_instance(self):
        #TODO: should return object of type 'DatabaseConnection' containing not NULL
        #_instance, cursor, connection
        pass

    def test_get_db(self):
        #TODO: given valid credentials, should return a tuple of
        #cursor in position 0 and connection in position 1
        pass

    def test_close_db(self):
        #TODO: should delete the singleton. singleton should be able to re-init after
        #maybe also find a way to see if the database connection is actually closed
        pass

    def test_db_connection():
        #connection_uri = "postgresql://adekunlebalogun:none@localhost:5432/adekunlebalogun"
        #db_instance = DatabaseConnection.get_instance()
        #print("Connection", db_instance)
        pass

if __name__ == '__main__':
    unittest.main()
