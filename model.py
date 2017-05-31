"""Models and database functions for elevation data"""

from flask_sqlalchemy import SQLAlchemy
import numpy as np
from data import bay_data, BAY


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

        return "<tile_id=%s covers location: N=%s E=%s S=%s W=%s>" % (self.tile_id,
                                                                      self.top_bound,
                                                                      self.right_bound,
                                                                      self.bottom_bound,
                                                                      self.left_bound)

    @classmethod
    def load_tiles(cls, raw_data, incr, steps_x, steps_y, base_lat, base_lng, end_lat, end_lng):
        """create tiles and load into database, calls function to load points per tile"""

        lng_step = (end_lng - base_lng) / steps_x
        lat_step = (end_lat - base_lat) / steps_y
        for i in range(0, steps_y, incr):
            # splitting array into rows then unpacking
            top_bound, bottom_bound, row = cls.get_rows(raw_data, i, steps_y, incr, base_lat, lat_step)
            for j in range(0, steps_x, incr):
                # splitting rows into tiles then unpacking
                left_bound, right_bound, tile_array = cls.get_tiles(row, j, steps_x, incr, base_lng, lng_step)
                # instantiating a single tile object
                tile = cls(left_bound=left_bound, right_bound=right_bound, top_bound=top_bound, bottom_bound=bottom_bound)
                # commiting session to db, important before calling load_points
                db.session.add(tile)
                db.session.commit()
                Point.load_points(tile_array, top_bound, left_bound, tile.tile_id, lat_step, lng_step)

    @staticmethod
    def get_rows(raw_data, position, steps, increment, base_lat, lat_step):
        """splitting total array into rows and returns top and bottom bounds"""

        if (position + increment) <= steps:
            row = raw_data[position: position + increment]
            top_bound = base_lat + (position * lat_step)
            bottom_bound = top_bound + (increment * lat_step)
        else:
            # for the last row, increment won't necessarily go into steps evenly
            row = raw_data[position: steps]
            top_bound = base_lat + (position * lat_step)
            bottom_bound = top_bound + ((steps - position) * lat_step)
        # print (top_bound, bottom_bound)
        return (top_bound, bottom_bound, row)

    @staticmethod
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
        return (left_bound, right_bound, tile)


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

    @classmethod
    def load_points(cls, tile_array, top_bound, left_bound, tile_id, lat_step, lng_step):
        """finding highest elevation points per tile and loading into database"""

        latitude, longitude, elevation = cls.local_max(tile_array, top_bound, left_bound, lat_step, lng_step)
        # instantiating a single point for each tile, highest elevation point
        point = cls(tile_id=tile_id, latitude=latitude, longitude=longitude, elevation=elevation)
        # commiting session to db
        db.session.add(point)
        db.session.commit()

    @staticmethod
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

    @staticmethod
    def local_extrema(tile_arr, base_lat, base_lng, lat_step, lng_step):
        """finds peaks within tile and returns indices"""

        pass


class User(db.Model):
    """User of website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=True, default=None)
    email = db.Column(db.String(64), nullable=False, default=None)
    password = db.Column(db.String(64), nullable=False, default=None)

    s = db.relationship('Search', backref='u', order_by=user_id)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s password=%s>" % (self.user_id,
                                                           self.email,
                                                           self.password)

    @classmethod
    def check_user(cls, email, password, nickname=None):
        """checks if user is in databse"""

        result = cls.query.filter_by(email=email).one()
        if result:
            if result.password == password:
                return {"id": result.user_id,
                        "message": "You're now logged in! Congrats!"}
            else:
                return {"message": "That was the wrong password please try again"}
        else:
            user_id = cls.new_user(email, password, nickname)
            return {"id": user_id,
                    "message": "You're now registered! I've also logged you in :)"}

    @classmethod
    def new_user(cls, email, password, nickname=None):
        """new user registration"""

        if nickname:
            user = cls(email=email, password=password, name=nickname)
        else:
            user = cls(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return user.user_id


class Search(db.Model):
    """Searches that user has performed."""

    __tablename__ = "searches"

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.address_id'))
    search_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    end_point = db.Column(db.Integer, db.ForeignKey('points.point_id'))
    travel_time = db.Column(db.Integer, nullable=True)
    min_ele = db.Column(db.Integer)
    max_time = db.Column(db.Integer)
    travel_mode = db.Column(db.String(64))

    a = db.relationship('Address', backref='s', order_by=address_id)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s address_id=%s search_id=%s end_point=%s \n\
                travel_time=%s min_ele=%s max_time=%s travel_mode=%s>" % (self.user_id,
                                                                          self.address_id,
                                                                          self.search_id,
                                                                          self.end_point,
                                                                          self.travel_time,
                                                                          self.min_ele,
                                                                          self.max_time,
                                                                          self.travel_mode)

    @classmethod
    def tile_query(cls, lat, lng, user_id, min_height, max_time, travel_mode, elevation):
        """looking for high elevation just within a tile"""

        if not (South_B < lat < North_B) and not (West_B < lng < East_B):
            return None
        address_id = Address.check_address(cls, lat, lng, ele, name=None)
        search = cls(user_id=user_id, address_id=address_id, )
        point_objects = Tile.query.filter(Tile.bottom_bound < lat, Tile.top_bound > lat,
                                          Tile.left_bound < lng, Tile.right_bound > lng).one().p
        point_list = []
        for point in point_objects:
            tup = (point.tile_id, point.latitude, point.longitude, point.elevation)
            point_list.append(tup)
        return point_list


    def nearby_tiles_query(lat, lng, count=1):
        """looking for high elevation in nearby tiles"""

        if not (South_B < lat < North_B) and not (West_B < lng < East_B):
            return "Not in Bounds!"
        radius = ((East_B - West_B) / steps_x) * incr / 2
        radiate_bounds(count, radius)
        point_list = []
        for tile in tile_objects:
            points = tile.p
            for point in points:
                tup = (point.tile_id, point.latitude, point.longitude, point.elevation)
                point_list.append(tup)
        return point_list

    def radiate_bounds(count, radius):
        """calculate reach for tiles query"""

        tile_list = []
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
        tile_objects = Tile.query.filter(Tile.bottom_bound < top_reach, Tile.top_bound > bottom_reach,
                                         Tile.left_bound < right_reach, Tile.right_bound > left_reach).all()
        return tile_objects


class Address(db.Model):
    """Addresses that have been searched."""

    __tablename__ = "addresses"

    address_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=True, default=None)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    elevation = db.Column(db.Float)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Address address_id=%s name=%s latitude=%s longitude=%s elevation=%s>" % (self.address_id,
                                                                                          self.name,
                                                                                          self.latitude,
                                                                                          self.longitude,
                                                                                          self.elevation)

    @classmethod
    def check_address(cls, lat, lng, ele, name=None):
        """checks if an address is in the database, if not, calls instantiation"""

        place = db.session.query(cls).filter(cls.latitude == lat, cls.longitude == lng).one()
        if place:
            return place.address_id
        else:
            new = cls.new_address(lat, lng, ele, name)
            return new

    @classmethod
    def new_address(cls, lat, lng, ele, name=None):
        """adds an address to the database"""

        if name:
            new = cls(latitude=lat, longitude=lng, elevation=ele, name=name)
        else:
            new = cls(latitude=lat, longitude=lng, elevation=ele)
        db.session.add(new)
        db.session.commit()
        return new.address_id


def connect_to_db(app, db_url='postgresql:///newvp'):
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
    db.create_all()
    print "tables created"
    # Calling main load function with variables in correct order, be careful of order
    Tile.load_tiles(bay_data, BAY['incr'], BAY['steps_x'], BAY['steps_y'], BAY['N'], BAY['W'], BAY['S'], BAY['E'])
