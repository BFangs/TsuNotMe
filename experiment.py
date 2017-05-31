from flask_sqlalchemy import SQLAlchemy
from data import BAY

# connecting to the PostgreSQL database through flask_sqlalchemy
# helper library

db = SQLAlchemy()


class Thing(db.Model):
    """high elevation points within tiles"""

    __tablename__ = "things"

    point_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    elevation = db.Column(db.Float)

    def __repr__(self):
        """Provide helpful information when printed"""

        return "<Point is: point_id=%s latitude=%s longitude=%s elevation=%s>" % (self.point_id,
                                                                                  self.latitude,
                                                                                  self.longitude,
                                                                                  self.elevation)


def all_points(raw_data, steps_x=BAY['steps_x'], steps_y=BAY['steps_y'], base_lat=BAY['N'], base_lng=BAY['W'], end_lat=BAY['S'], end_lng=BAY['E']):
    """loads all points into database"""

    lng_step = (end_lng - base_lng) / steps_x
    lat_step = (end_lat - base_lat) / steps_y
    for y, row in enumerate(raw_data):
        lat = base_lat + (y * lat_step)
        for x, column in enumerate(row):
            lng = base_lng + (x * lng_step)
            elevation = raw_data[y, x]
            thing = Thing(latitude=lat, longitude=lng, elevation=float(elevation))
            db.session.add(thing)
            db.session.commit()


def range_query(lat, lng, count=1):
    """find all points within range"""

    if not (South_B < lat < North_B) and not (West_B < lng < East_B):
        return "Not in Bounds!"
    radius = ((East_B - West_B) / steps_x) * 50 / 2
    print radius
    counter = count
    reach = radius * counter
    top_reach = lat + reach
    if top_reach > North_B:
        top_reach = North_B
    bottom_reach = lat - reach
    if bottom_reach < South_B:
        bottom_reach = South_B
    left_reach = lng - reach
    if left_reach < West_B:
        left_reach = West_B
    right_reach = lng + reach
    if right_reach > East_B:
        right_reach = East_B
    print top_reach, bottom_reach, left_reach, right_reach
    things = Thing.query.filter(Thing.latitude < top_reach,
                                bottom_reach < Thing.latitude,
                                left_reach < Thing.longitude,
                                Thing.longitude < right_reach).all()

    return things


def connect_to_db(app, db_url='postgresql:///allpoints'):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    #when running module interactively will allow working with database directly

    from server import app
    connect_to_db(app)
    print "Connected to DB."
