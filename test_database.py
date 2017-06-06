from model import db, connect_to_db, Tile, Point
from seed import load_tiles
from server import app
import numpy as np
import unittest


class MyTileTableTests(unittest.TestCase):
    """check if overall dimensions and such are correct"""

    def test_for_duplicates(self):
        """are there duplicate tiles?"""

        self.assertEqual(self.how_many_dupe_tiles, "Seems fine")

    def test_how_many_duplicates(self):
        """which are duplicate tiles?"""

        self.assertEqual(self.which_tiles_duped, None)

    @staticmethod
    def how_many_dupe_tiles(database):
        """looking for duplicate tile bounds"""

        tile_list = []
        tile_objects = database.query.all()
        for tile in tile_objects:
            tile_list.append((tile.bottom_bound, tile.top_bound, tile.left_bound, tile.right_bound))
        tile_set = set(tile_list)
        print "list length: %s set length: %s" % (len(tile_list), len(tile_set))
        if len(tile_list) != len(tile_set):
            return "You've got duplicates!"
        else:
            return "Seems fine"

    @staticmethod
    def which_tiles_duped(database):
        """looking for tile objects with duplicate tile bounds"""

        tile_list = []
        tile_objects = database.query.all()
        for tile in tile_objects:
            tile_list.append((tile.bottom_bound, tile.top_bound, tile.left_bound, tile.right_bound))
        tiles_count = {}
        for tile in tile_list:
            if tiles_count.get(tile):
                return tile
            else:
                tiles_count[tile] = 1

    @staticmethod
    def is_total_area_correct():
        """calculate area of all tiles and add together, is it same as whole data set?"""

        pass


class FlaskTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    @staticmethod
    def numpy_it(y, x):
        """getting a numpy array of y, x dimensions"""

        numpy_thing = np.arange(0, (x * y))
        numpy_thing.shape = (y, x)
        return numpy_thing

    def setUp(self):
        """Stuff to do before every test."""

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        load_tiles(self.numpy_it(100, 100), 30, 100, 100, 0, 0, -100, 100)

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()
