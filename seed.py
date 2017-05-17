from data import arr
from model import connect_to_db, db
from server import app
from model import Tile
from model import Point
import numpy as np

#longitude (west is base)
West_B = -123.0005555556
East_B = -121.9994444445
#latitude (north is base)
North_B = 38.00055555556
South_B = 36.99944444444
steps = 10812
h_step = (East_B - West_B) / steps
v_step = (South_B - North_B) / steps
incr = 100


def load_tiles(incr_y, incr_x, steps_y, steps_x, base_lat, base_lng):
    """create tiles and load into database"""

    left_bound, right_bound, top_bound, bottom_bound, tiles = tile_it(incr_y,
                                                              incr_x,
                                                              steps_y,
                                                              steps_x,
                                                              base_lat,
                                                              base_lng)
    tile = Tile(left_bound=left_bound,
                right_bound=right_bound,
                top_bound=top_bound,
                bottom_bound=bottom_bound)
    db.session.add(tile)
    db.session.commit()
    load_points(tiles, top_bound, left_bound, tile.tile_id)


def load_points(tiles, top_bound, left_bound, tile_id):
    """finding highest elevation points per tile and loading into database"""

    latitude, longitude, elevation = local_max(tiles, top_bound, left_bound)
    # instantiating a single point for each tile, highest elevation point
    point = Point(tile_id=tile_id, latitude=latitude, longitude=longitude, elevation=elevation)
    # commiting session to db
    db.session.add(point)
    db.session.commit()


def tile_it(incr_y, incr_x, steps_y, steps_x, base_lat, base_lng):
    """making larger tiles in incr size over steps # """

    for i in range(0, steps_y, incr_y):
        if (i+incr_y) < steps_y:
            # splits array into rows
            rows = arr[i: i + incr_y - 1]
        else:
            # for the last row, incr won't necessarily go into steps evenly
            rows = arr[i:steps_y]
        #latitude bounds
        top_bound = base_lat + (i * v_step)
        bottom_bound = top_bound + (incr_y * v_step)
        for j in range(0, steps_x, incr_x):
            if (j+incr_x) < steps_x:
                tiles = rows[:, j: j + incr_x - 1]
            else:
                # for the last column, incr won't necessarily go into steps evenly
                tiles = rows[:, j: steps_x]
            #longitude bounds
            left_bound = base_lng + (j * h_step)
            right_bound = left_bound + (incr_x * h_step)
            return (left_bound, right_bound, top_bound, bottom_bound, tiles)


def local_max(tile_arr, base_lat, base_lng):
    """finds highest elevation point and returns indices"""

    # extracts the dimensions of the array given
    side_y, side_x = tile_arr.shape
    # finds the index of the highest data point in array
    max_index = np.argmax(tile_arr)
    # index was returned in flattened form, need to find 2D index
    y = max_index // side_x
    x = max_index % side_x
    # selecting elevation from index
    # converting to python float is important for compatibility to psql
    elevation = float(tile_arr[y, x])
    latitude = ((y+1) * v_step) + base_lat
    longitude = ((x+1) * h_step) + base_lng
    return (latitude, longitude, elevation)

# how I would populate it if I wanted every point
# creating nested for loop that iterates over 2D array
# keeps track of the indices as well

# for y, row in enumerate(prac):
#     lat = North_B + (y * v_step)
#     for x, elv in enumerate(row):
#         lng = West_B + (x * h_step)
#         print lng, lat, elv
# print prac

# how do I alter it to add tiles?

if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_tiles(incr, incr, steps, steps, North_B, West_B)
