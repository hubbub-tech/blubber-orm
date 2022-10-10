import os
import unittest

import blubber_orm._conn as Blubber
import blubber_orm._base as Models

TABLE_NAME = os.getenv("TEST_TABLE_NAME")
TABLE_PRIMARIES = ["id"]


class FakeModels(Models):
    """A fake table to test Blubber's Models Class."""

    table_name = TABLE_NAME
    table_primaries = TABLE_PRIMARIES
    table_attributes = None

    def __init__(self, attrs):
        self.id = attrs["id"]
        self.name = attrs["name"]



class TestModels(unittest.TestCase):

    def test_insert(self):
        # Test data insertion works and handles errors as expected

        # If it fails, it will fail silently and return 'None'
        fake_model = FakeModels.insert({"id": 1, "name": "Pennywise the Dancing Clown"})
        self.assertTrue(isinstance(fake_model, FakeModels))



    def test_get(self):
        #Test that function throws error at non-attributes or non-specific keys

        pkeys_of_correct_type = {"id": 1}

        with self.assertRaises(AssertionError):
            pkeys_of_incorrect_type = 1
            fake_model = FakeModels.get(pkeys_of_incorrect_type)

        fake_model = FakeModels.get(pkeys_of_correct_type)
        self.assertTrue(isinstance(fake_model, FakeModels))

        pkeys_does_not_exist = {"id": -1}
        fake_model = FakeModels.get(pkeys_does_not_exist)
        self.assertTrue(fake_model is None)


    def test_set(self):
        #Test data updates and handles errors if there is an non-attribute key 'test'

        pkeys_of_correct_type = {"id": 1}

        self.test_get()
        fake_model = FakeModels.get(pkeys_of_correct_type)
        self.assertTrue(isinstance(fake_model, FakeModels))

        with self.assertRaises(AssertionError):
            pkeys_of_incorrect_type = 1
            FakeModels.set(pkeys_of_incorrect_type, {"name": "Ronald McDonald"})


        FakeModels.set(pkeys_of_correct_type, {"name": "Ronald McDonald Jr."})
        fake_model = FakeModels.get(pkeys_of_correct_type)

        self.assertTrue(fake_model.name == "Ronald McDonald Jr.")


    def test_delete(self):
        # Delete a data row then check to make sure it's deleted by calling it back
        pkeys = {"id": 1}

        self.test_get()
        fake_model = FakeModels.get(pkeys)
        self.assertTrue(isinstance(fake_model, FakeModels))

        FakeModels.delete(pkeys)

        fake_model = FakeModels.get(pkeys)
        self.assertTrue(fake_model is None)

        FakeModels.insert({"id": 1, "name": "Pennywise the Dancing Clown"})


    def test_filter(self):
        #Test filter does not accept non-attributes. test it always returns type list

        keys_do_exist = {"id": 1}

        fake_models = FakeModels.filter(keys_do_exist)
        self.assertTrue(isinstance(fake_models, list))

        keys_do_not_exist = {"name": "The Joker"}
        fake_models = FakeModels.filter(keys_do_not_exist)
        self.assertTrue(isinstance(fake_models, list))
        self.assertTrue(fake_models == [])


if __name__ == '__main__':

    with Blubber.conn.cursor() as cursor:
        cursor.execute(f"""
            CREATE TABLE {TABLE_NAME} (
                id int,
                name text,
                PRIMARY KEY (id)
            );
        """)

    unittest.main()

    with Blubber.conn.cursor() as cursor:
        cursor.execute(f"DROP TABLE {TABLE_NAME};")
