from data import bay_data, BAY
from model import connect_to_db, db
from server import app
from model import Tile
from model import Point

if __name__ == "__main__":
    connect_to_db(app)
    # In case tables haven't been created, create them
    connect_to_db(app)
    print "Connected to DB."
    db.create_all()
    print "tables created"
    # Calling main load function with variables in correct order, be careful of order
    Tile.load_tiles(bay_data, BAY['incr'], BAY['steps_x'], BAY['steps_y'], BAY['N'], BAY['W'], BAY['S'], BAY['E'])
    print "tiles loaded"
