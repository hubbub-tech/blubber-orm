#import pytest
import unittest
import src.blubber_orm.base as base

class TestAbstractModels(unittest.TestCase):

    def test_abstract_attributes(self):
        #TODO: test that table_name and database exist in namespace
        pass

    def test_database_connection(self):
        #TODO: get the class AbstractModels and make sure database is of type
        #DatabaseConnection.
        pass

    def test_abstract_methods(self):
        #TODO: try to instantiate the class, it should fail.
        #Try to run functions, should similarly fail.
        pass

class TestModels(unittest.TestCase):

    def prepare_for_tests(self):
        #TODO: create a new table for test attributes? or create a test db?
        pass

    def test_abstract_inheritance(self):
        #TODO: test Models is of type AbstractModels. then make sure that all
        #the methods defined in AbstractModels have been defined in Models. also
        pass

    def test_insert(self):
        #TODO: test data insertion works and handles errors as expected
        #also rotate through table names to see if any of them fail
        pass

    def test_set(self):
        #TODO: test data updates and handles errors if there is an non-attribute key 'test'
        #also rotate through table names to see if any of them fail
        pass

    def test_get(self):
        #TODO: test that function throws error at non-attributes or non-specific keys
        #with appropriate errors. also rotate through table names to see if any of them fail
        pass

    def test_delete(self):
        #TODO: delete a data row then check to make sure it's deleted by calling it back
        #also rotate through table names to see if any of them fail
        pass

    def test_filter(self):
        #TODO: test filter does not accept non-attributes. test it always returns type list
        #also rotate through table names to see if any of them fail
        pass

    def test_get_columns(self):
        #TODO: test to be sure get_columns gets the correct columns for all the
        #models, this is important to verification at every other class method
        #also rotate through table names to see if any of them fail
        pass

    def test_refresh(self):
        #TODO: create two instances of a model class with the same data
        #then make a change to one and refresh it
        #assert that the two instances are different
        #also rotate through table names to see if any of them fail
        pass

if __name__ == '__main__':
    unittest.main()
