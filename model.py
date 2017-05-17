"""Models and database functions for elevation data"""

from flask_sqlalchemy import SQLAlchemy

# connecting to the PostgreSQL database through flask_sqlalchemy
# helper library

db = SQLAlchemy()

# Model definitions


class Tile(db.Model):
    """my geospatial data will be broken down into tiles by area"""

    __tablename__ = "tiles"

    tile_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    left_bound = db.Column(db.Float)
    right_bound = db.Column(db.Float)
    top_bound = db.Column(db.Float)
    bottom_bound = db.Column(db.Float)

    def __repr__(self):
        """Provide helpful information when printed"""

        return "<tile_id=%s covers location: N=%s E=%s S=%s W=%s" % (self.tile_id,
                                                                     self.top_bound,
                                                                     self.right_bound,
                                                                     self.bottom_bound,
                                                                     self.left_bound)


class Point(db.Model):
    """high elevation points within tiles"""

    __tablename__ = "points"

    point_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tile_id = db.Column(db.Integer, db.ForeignKey('tiles.tile_id'))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    elevation = db.Column(db.Float)

    t = db.relationship('Tile', backref='p', order_by=elevation)

    def __repr__(self):
        """Provide helpful information when printed"""

        return "<Point is in: tile_id=%s latitude=%s longitude=%s elevation=%s>" % (self.tile_id,
                                                                                   self.latitude,
                                                                                   self.longitude,
                                                                                   self.elevation)


def connect_to_db(app, db_url='postgresql:///mvp'):
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
