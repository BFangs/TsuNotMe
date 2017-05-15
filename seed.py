from data import arr
# from model import connect_to_db, db
# from server import app
# from model import Tile
# from model import Point
import numpy as np
prac = arr[0:6, 0:3]
#longitude
West_B = -123.0005555556
East_B = -121.9994444445
#latitude
North_B = 38.00055555556
South_B = 36.99944444444
steps = 10812
h_step = (East_B - West_B) / steps
v_step = (South_B - North_B) / steps
incr = 100
h_incr = incr * h_step
v_incr = incr * v_step

def tileit(incr, steps):
    """making larger tiles in incr size over steps#"""

    pass

# how I would populate it if I wanted every point
# creating nested for loop that iterates over 2D array
# keeps track of the indices as well

for y, row in enumerate(prac):
    lat = North_B + (y * v_step)
    for x, elv in enumerate(row):
        lng = West_B + (x * h_step)
        print lng, lat, elv
print prac

# how do I alter it to add tiles?


def localMax(tile_arr, base_lat, base_lng):
    """finds highest elevation point and returns indices"""

    side_y, side_x = tile_arr.shape
    max_index = np.argmax(tile_arr)
    y = max_index // side_x
    x = max_index % side_x
    elevation = tile_arr[y, x]
    latitude = ((y+1) * v_step) + base_lat
    longitude = ((x+1) * h_step) + base_lng
    point = Point(latitude=latitude, longitude=longitude, elevation=elevation)



# def load_tiles():
#     """create tiles and load into database"""

#     print "tiles"
#     Tile.query.delete()

#     db.session.commit()


# def load_points():
#     """finding highest elevation points per tile and loading into database"""

#     print "points"
#     Point.query.delete()

#     db.session.commit()

# if __name__ == "__main__":
#     connect_to_db(app)

#     # In case tables haven't been created, create them
#     db.create_all()

#     # Import different types of data
#     load_tiles()
