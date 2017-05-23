from data import bay_data, get_rows, get_tiles, local_max
from data import West_B, East_B, North_B, South_B
from data import steps_x, steps_y, incr
from model import connect_to_db, db
from server import app
from model import Tile
from model import Point
import numpy as np


def load_tiles(raw_data, incr, steps_x, steps_y, base_lat, base_lng, end_lat, end_lng):
    """create tiles and load into database, calls function to load points per tile"""

    lng_step = (East_B - West_B) / steps_x
    lat_step = (South_B - North_B) / steps_y
    for i in range(0, steps_y, incr):
        # splitting array into rows then unpacking
        top_bound, bottom_bound, row = get_rows(raw_data, i, steps_y, incr, base_lat, lat_step)
        for j in range(0, steps_x, incr):
            # splitting rows into tiles then unpacking
            left_bound, right_bound, tile_array = get_tiles(row, j, steps_x, incr, base_lng, lng_step)
            # instantiating a single tile object
            tile = Tile(left_bound=left_bound, right_bound=right_bound, top_bound=top_bound, bottom_bound=bottom_bound)
            # commiting session to db, important before calling load_points
            db.session.add(tile)
            db.session.commit()
            load_points(tile_array, top_bound, left_bound, tile.tile_id, lat_step, lng_step)


def load_points(tile_array, top_bound, left_bound, tile_id, lat_step, lng_step):
    """finding highest elevation points per tile and loading into database"""

    latitude, longitude, elevation = local_max(tile_array, top_bound, left_bound, lat_step, lng_step)
    # instantiating a single point for each tile, highest elevation point
    point = Point(tile_id=tile_id, latitude=latitude, longitude=longitude, elevation=elevation)
    # commiting session to db
    db.session.add(point)
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    # In case tables haven't been created, create them
    db.create_all()
    # Calling main load function with variables in correct order, be careful of order
    load_tiles(bay_data, incr, steps_x, steps_y, North_B, West_B, South_B, East_B)
