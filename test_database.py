from model import db, connect_to_db
from seed import load_tiles, load_points
from data import get_rows, get_tiles, local_max, how_many_dupe_tiles, which_tiles_duped
from server import app
import numpy as np
import unittest


class MyTileTableTests(unittest.TestCase):
    """check if overall dimensions and such are correct"""

    def test_for_duplicates(self):
        """are there duplicate tiles?"""

        self.assertEqual(how_many_dupe_tiles, "Seems fine")


class FlaskTestsDatabase(TestCase):
    """Flask tests that use the database."""

    @staticmethod
    def numpy_it(y, x):
        """getting a numpy array of y, x dimensions"""

        numpy_thing = np.arange(0,(x * y))
        numpy_thing.shape = (y, x)
        return numpy_thing

    def setUp(self):
        """Stuff to do before every test."""

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        load_tiles(numpy_it(100, 100), 30, 100, 100, 0, 0, -100, 100)

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_for_duplicates(self):
        """are there duplicate tiles?"""

        self.assertEqual(how_many_dupe_tiles(), "Seems fine")

    def test_how_many_duplicates(self):
        """which are duplicate tiles?"""

        self.assertEqual(which_tiles_duped(), None)
