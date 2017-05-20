from osgeo import gdal
import numpy as np
from model import Tile, Point
from model import connect_to_db, db

geo = gdal.Open('imgn38w123_13.img')
bay_data = geo.ReadAsArray()

#longitude (west is base)
West_B = -123.0005555556
East_B = -121.9994444445
#latitude (north is base)
North_B = 38.00055555556
South_B = 36.99944444444
steps_x = 10812
steps_y = 10812
incr = 100


def tile_query(lat, lng):
    """looking for high elevation just within a tile"""

    if not (South_B < lat < North_B) and not (West_B < lng < East_B):
        return None
    point_objects = Tile.query.filter(Tile.bottom_bound<lat, Tile.top_bound>lat,
                               Tile.left_bound<lng, Tile.right_bound>lng).one().p
    point_list = []
    for point in point_objects:
        tup = (point.tile_id, point.latitude, point.longitude, point.elevation)
        point_list.append(tup)
    return point_list


def get_rows(raw_data, position, steps, increment, base_lat, lat_step):
    """splitting total array into rows and returns top and bottom bounds"""

    if (position + increment) <= steps_y:
        row = raw_data[position: position + increment]
        top_bound = base_lat + (position * lat_step)
        bottom_bound = top_bound + (increment * lat_step)
    else:
        # for the last row, increment won't necessarily go into steps evenly
        row = raw_data[position: steps_y]
        top_bound = base_lat + (position * lat_step)
        bottom_bound = top_bound + ((steps_y-position) * lat_step)
    print row, top_bound, bottom_bound, position
    return (top_bound, bottom_bound, row)


def get_tiles(row, position, steps, increment, base_lng, lng_step):
    """splitting row into tiles and returns left and right bounds"""

    if (position + increment) <= steps:
        tile = row[:, position: position + increment]
        left_bound = base_lng + (position * lng_step)
        right_bound = left_bound + (increment * lng_step)
    else:
        # for the last column, increment won't necessarily go into steps evenly
        tile = row[:, position: steps]
        left_bound = base_lng + (position * lng_step)
        right_bound = left_bound + ((steps-position) * lng_step)
    print tile, left_bound, right_bound, position
    return (left_bound, right_bound, tile)


def local_max(tile_arr, base_lat, base_lng, lat_step, lng_step):
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
    latitude = ((y+1) * lat_step) + base_lat
    longitude = ((x+1) * lng_step) + base_lng
    return (latitude, longitude, elevation)


if __name__ == "__main__":
    #when running module interactively will allow working with database directly

    from server import app
    connect_to_db(app)
    print "Connected to DB."
