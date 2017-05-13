from data import arr
# from model import connect_to_db, db
# from server import app
# from model import Tile
# from model import Point
prac = arr[0:20, 0:20]

West_B = -123.0005555556
East_B = -121.9994444445
North_B = 38.00055555556
South_B = 36.99944444444
steps = 10812
h_step = (East_B - West_B) / steps
v_step = (North_B - South_B) / steps
incr = 100
h_incr = incr * h_step
v_incr = incr * v_step

def tileit(incr, steps):
    """making larger tiles in incr size over steps#"""

    for 

# how I would populate it if I wanted every point
# creating nested for loop that iterates over 2D array
# keeps track of the indices as well

for x, row in enumerate(prac):
    lng = West_B - (x * h_step)
    for y, elv in enumerate(row):
        lat = North_B - (x * v_step)
        print lat, lng, elv
        # point = Point(latitude=lat, longitude=lng, elevation=elv)
# how do I alter it to add tiles?




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
