import unittest
from model import Tile, Point
import numpy as np


class MyRowsUnitTests(unittest.TestCase):
    """Data processing python functions, making rows"""

    @staticmethod
    def numpy_it(y, x):
        """getting a numpy array of y, x dimensions"""

        numpy_thing = np.arange(0, (x * y))
        numpy_thing.shape = (y, x)
        return numpy_thing

    def test_get_rows_square_top(self):
        """testing making rows from square, top"""

        y_dimension = 9
        test_array = self.numpy_it(y_dimension, y_dimension)
        increment = 3
        position = 0
        base = 0
        step = 1
        self.assertEqual(Tile.get_rows(test_array, position, y_dimension, increment, base, step)[2].tolist(),
                         [[0,  1,  2,  3,  4,  5,  6,  7,  8],
                          [9, 10, 11, 12, 13, 14, 15, 16, 17],
                          [18, 19, 20, 21, 22, 23, 24, 25, 26]])
        self.assertEqual((Tile.get_rows(test_array, position, y_dimension, increment, base, step)[0],
                          Tile.get_rows(test_array, position, y_dimension, increment, base, step)[1]),
                         (0, 3))

    def test_get_rows_square_bottom(self):
        """testing making rows from square, bottom"""

        y_dimension = 9
        test_array = self.numpy_it(y_dimension, y_dimension)
        increment = 3
        position = y_dimension - increment
        base = 0
        step = 1
        self.assertEqual(Tile.get_rows(test_array, position, y_dimension, increment, base, step)[2].tolist(),
                         [[54, 55, 56, 57, 58, 59, 60, 61, 62],
                          [63, 64, 65, 66, 67, 68, 69, 70, 71],
                          [72, 73, 74, 75, 76, 77, 78, 79, 80]])
        self.assertEqual((Tile.get_rows(test_array, position, y_dimension, increment, base, step)[0],
                          Tile.get_rows(test_array, position, y_dimension, increment, base, step)[1]),
                         (6, 9))

    def test_get_rows_asym_top(self):
        """testing making rows unevenly, normal"""

        x_dimension = 5
        y_dimension = 7
        test_array = self.numpy_it(y_dimension, x_dimension)
        increment = 2
        position = 0
        base = 0
        step = 1
        self.assertEqual(Tile.get_rows(test_array, position, y_dimension, increment, base, step)[2].tolist(),
                         [[0, 1, 2, 3, 4],
                          [5, 6, 7, 8, 9]])
        self.assertEqual((Tile.get_rows(test_array, position, y_dimension, increment, base, step)[0],
                          Tile.get_rows(test_array, position, y_dimension, increment, base, step)[1]),
                         (0, 2))

    def test_get_rows_asym_bottom(self):
        """testing making rows unevenly, edge"""

        x_dimension = 5
        y_dimension = 7
        test_array = self.numpy_it(y_dimension, x_dimension)
        increment = 2
        position = y_dimension - (y_dimension % increment)
        base = 0
        step = 1
        self.assertEqual(Tile.get_rows(test_array, position, y_dimension, increment, base, step)[2].tolist(),
                         [[30, 31, 32, 33, 34]])
        self.assertEqual((Tile.get_rows(test_array, position, y_dimension, increment, base, step)[0],
                          Tile.get_rows(test_array, position, y_dimension, increment, base, step)[1]),
                         (6, 8))


class MyTilesUnitTests(unittest.TestCase):
    """Data processing python functions, making tiles"""

    @staticmethod
    def numpy_row_it(position, y, x):
        """getting a numpy array of y, x dimensions"""

        start = position * x
        numpy_thing = np.arange(start, (start + (x * y)))
        numpy_thing.shape = (y, x)
        return numpy_thing

    def test_get_tiles_square_top(self):
        """testing making rows from square, top"""

        x_dimension = 9
        increment = 3
        position = 0
        base = 0
        step = 1
        test_array = self.numpy_row_it(position, increment, x_dimension)
        self.assertEqual(Tile.get_tiles(test_array, position, x_dimension, increment, base, step)[2].tolist(),
                         [[0,  1,  2],
                          [9, 10, 11],
                          [18, 19, 20]])
        self.assertEqual((Tile.get_tiles(test_array, position, x_dimension, increment, base, step)[0],
                          Tile.get_tiles(test_array, position, x_dimension, increment, base, step)[1]),
                         (0, 3))

    def test_get_tiles_square_bottom(self):
        """testing making rows from square, bottom"""

        x_dimension = 9
        increment = 3
        position = x_dimension - increment
        base = 0
        step = 1
        test_array = self.numpy_row_it(position, increment, x_dimension)
        self.assertEqual(Tile.get_tiles(test_array, position, x_dimension, increment, base, step)[2].tolist(),
                         [[60, 61, 62],
                          [69, 70, 71],
                          [78, 79, 80]])
        self.assertEqual((Tile.get_tiles(test_array, position, x_dimension, increment, base, step)[0],
                          Tile.get_tiles(test_array, position, x_dimension, increment, base, step)[1]),
                         (6, 9))

    def test_get_tiles_asym_top(self):
        """testing making rows unevenly, normal"""

        x_dimension = 5
        increment = 2
        position = 0
        base = 0
        step = 1
        test_array = self.numpy_row_it(position, increment, x_dimension)
        self.assertEqual(Tile.get_tiles(test_array, position, x_dimension, increment, base, step)[2].tolist(),
                         [[0, 1],
                          [5, 6]])
        self.assertEqual((Tile.get_tiles(test_array, position, x_dimension, increment, base, step)[0],
                          Tile.get_tiles(test_array, position, x_dimension, increment, base, step)[1]),
                         (0, 2))

    def test_get_tiles_asym_bottom(self):
        """testing making rows unevenly, edge"""

        x_dimension = 5
        increment = 2
        position = x_dimension - (x_dimension % increment)
        base = 0
        step = 1
        # this function call is different because I am testing the uneven edge | uneven edge
        test_array = self.numpy_row_it(position, 1, x_dimension)
        self.assertEqual(Tile.get_tiles(test_array, position, x_dimension, increment, base, step)[2].tolist(),
                         [[24]])
        self.assertEqual((Tile.get_tiles(test_array, position, x_dimension, increment, base, step)[0],
                          Tile.get_tiles(test_array, position, x_dimension, increment, base, step)[1]),
                         (4, 5))


class MyMaxUnitTests(unittest.TestCase):
    """unit tests on maxima finding functions"""

    @staticmethod
    def numpy_tile_it(x):
        """getting a numpy array of y, x dimensions"""

        numpy_thing = np.arange(0, (x ** 2))
        numpy_thing.shape = (x, x)
        return numpy_thing

    def test_get_local_max(self):
        """function should return single point per tile)"""

        test_array = self.numpy_tile_it(4)
        self.assertEqual(Point.local_max(test_array, 0, 0, 1, 1), (4, 4, 15.0))


if __name__ == "__main__":
    unittest.main()
