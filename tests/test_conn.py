import unittest
from blubber_orm._conn import Blubber


class TestBlubber(unittest.TestCase):

    def test_format_to_dict(self):
        # TODO: im not sure how to test this, but should always return type dict
        # where key=db_column_name and value=db_corresponding_value
        pass

    def test_parse_uri(self):
        # TODO: should always correctly parse database uri, given conventional
        # formatting, and should throw correct error if not.
        pass


    def test_singleton_before_connection(self):
        # Test that no instance exists and that the class contains:
        self.assertEqual(Blubber._instance, None)


    def test_singleton_after_connection(self):
        # Test that instance exists and that the class cannot be
        test_conn = Blubber.get_instance()

        # NOTE: Eventually, create a specific error type to watch for...
        with self.assertRaises(Exception):
            test_another_conn = Blubber()

        # NOTE: Might need to write a way for these two to be compared...
        test_another_conn = Blubber.get_instance()
        self.assertEqual(test_conn, test_another_conn)


    def test_get_instance(self):
        # Should return object of type 'Blubber' containing not NULL

        test_blubber = Blubber.get_instance()
        self.assertTrue(isinstance(test_blubber, Blubber))


    def test_open_conn(self):
        # Sould return a connection object, defined by psycopg2

        test_blubber = Blubber.get_instance()
        test_conn = test_blubber.conn

        # 1. Test the connections ability to execute query.
        with test_conn.cursor() as cursor:
            cursor.execute("CREATE TABLE test_connections;")
            cursor.execute("DROP TABLE test_connections;")
            test_conn.commit()

        # TODO: 2. import Connection Class from psycopg2 and test that test_conn is an isntance of it


    def test_close_conn(self):
        # Should not delete the singleton. Should only NULL the .conn attribute.

        test_blubber = Blubber.get_instance()
        self.assertFalse(test_blubber.conn is None)

        test_blubber.close_conn() # should test_blubber

        self.assertTrue(test_blubber.conn is None)
        self.test_singleton_after_connection()


if __name__ == '__main__':
    unittest.main()
