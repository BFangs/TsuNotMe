from data import bay_data, get_rows, get_tiles, local_max
from data import West_B, East_B, North_B, South_B
from data import steps_x, steps_y, incr
from model import connect_to_db, db
from server import app
from model import Tile
from model import Point








if __name__ == "__main__":
    connect_to_db(app)
    # In case tables haven't been created, create them
    db.create_all()
    # Calling main load function with variables in correct order, be careful of order
    load_tiles(bay_data, incr, steps_x, steps_y, North_B, West_B, South_B, East_B)
