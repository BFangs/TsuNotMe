"""Models definitions and database functions for elevation data, users, search history"""

from flask_sqlalchemy import SQLAlchemy
import numpy as np
# necessary constants for many function calculations
from data import BAY


# connecting to the PostgreSQL database through flask_sqlalchemy helper library
db = SQLAlchemy()


class Tile(db.Model):
    """my geospatial data will be broken down into tiles by area"""

    __tablename__ = "tiles"

    tile_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    left_bound = db.Column(db.Float)
    right_bound = db.Column(db.Float)
    top_bound = db.Column(db.Float)
    bottom_bound = db.Column(db.Float)

    p = db.relationship('Point', backref='t', order_by='Point.elevation')

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

    def __repr__(self):
        """Provide helpful information when printed"""

        return "<Point is in: tile_id=%s latitude=%s longitude=%s elevation=%s>" % (self.tile_id,
                                                                                    self.latitude,
                                                                                    self.longitude,
                                                                                    self.elevation)

    @classmethod
    def load_points(cls, tile_array, top_bound, left_bound, tile_id, lat_step, lng_step):
        """finding highest elevation points per tile and loading into database"""

        # latitude, longitude, elevation = cls.local_max(tile_array, top_bound, left_bound, lat_step, lng_step)
        # instantiating a single point for each tile, highest elevation point, commmented out and tabled
        peaks = cls.local_extrema(tile_array)
        ave = np.mean(tile_array)
        if peaks:
            whys, exes = peaks
            for i in xrange(len(whys)):
                elevation = float(tile_array[whys[i], exes[i]])
                if elevation > 25 and elevation > ave:
                    latitude, longitude = cls.explicify_data(whys[i], exes[i], top_bound, left_bound, lat_step, lng_step)
                    point = cls(tile_id=tile_id, latitude=latitude, longitude=longitude, elevation=elevation)
                    db.session.add(point)
        else:
            latitude, longitude, elevation = cls.local_max(tile_array, top_bound, left_bound, lat_step, lng_step)
            if elevation > 25:
                point = cls(tile_id=tile_id, latitude=latitude, longitude=longitude, elevation=elevation)
                db.session.add(point)
        # commit placed purposefully to keep from commiting after every point, really slows down loading
        db.session.commit()

    @staticmethod
    def local_max(tile_arr, base_lat, base_lng, lat_step, lng_step):
        """finds highest elevation point and returns indices"""

        # finds the index of the highest data point in array
        max_index = np.argmax(tile_arr)
        # index was returned in flattened form, need to find 2D index
        # extracts the dimensions of the array given
        side_y, side_x = tile_arr.shape
        y = max_index // side_x
        x = max_index % side_x
        # selecting elevation from index
        # converting to python float is important for compatibility to psql
        elevation = float(tile_arr[y, x])
        latitude, longitude = Point.explicify_data(y, x, base_lat, base_lng, lat_step, lng_step)
        return (latitude, longitude, elevation)

    @staticmethod
    def explicify_data(y, x, base_lat, base_lng, lat_step, lng_step):
        """takes indices and bounding coordinates and returns lat, lng"""

        latitude = ((y+1) * lat_step) + base_lat
        longitude = ((x+1) * lng_step) + base_lng
        return (latitude, longitude)

    @staticmethod
    def local_extrema(tile, order=1, mode='clip'):
        """finds peaks within tile and returns indices, based on np.argrelmax"""

        side_y = tile.shape[0]
        side_x = tile.shape[1]
        yloci = np.arange(0, side_y)
        xloci = np.arange(0, side_x)
        results = np.ones(tile.shape, dtype=bool)
        y_index = tile.take(yloci, axis=0, mode=mode)
        x_index = tile.take(xloci, axis=1, mode=mode)

        for shift in xrange(1, order + 1):
            plus = tile.take(yloci + shift, axis=0, mode=mode)
            minus = tile.take(yloci - shift, axis=0, mode=mode)
            results &= np.greater(y_index, plus)
            results &= np.greater(y_index, minus)
        for shift in xrange(1, order + 1):
            plus = tile.take(xloci + shift, axis=1, mode=mode)
            minus = tile.take(xloci - shift, axis=1, mode=mode)
            results &= np.greater(x_index, plus)
            results &= np.greater(x_index, minus)
        if(~results.any()):
            return []
        whys, exes = map(lambda x: x.tolist(), np.where(results))
        return (whys, exes)


class User(db.Model):
    """User of website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=True, default=None)
    email = db.Column(db.String(64), nullable=False, default=None)
    password = db.Column(db.String(64), nullable=False, default=None)

    s = db.relationship('Search', backref='u', order_by='Search.address_id')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s password=%s>" % (self.user_id,
                                                           self.email,
                                                           self.password)

    @classmethod
    def check_user(cls, email):
        """checks if user is in databse"""
        try:
            result = cls.query.filter_by(email=email).one()
            return result
        except:
            return None

    @classmethod
    def new_user(cls, email, password, nickname=None):
        """new user registration"""
        if nickname:
            user = cls(email=email, password=password, name=nickname)
        else:
            user = cls(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return {"id": user.user_id, "message": "You're now registered! I've also logged you in!"}

    @classmethod
    def change_password(cls, user_id, password):
        person = cls.query.filter(cls.user_id == user_id).one()
        person.password = password
        db.session.commit()
        return "You updated your password!"

    @classmethod
    def get_history(cls, user_id):
        """getting search history for an user"""

        person = cls.query.filter(cls.user_id == user_id).one()
        history = person.s
        return history


class Search(db.Model):
    """Searches that user has performed."""

    __tablename__ = "searches"

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.address_id'))
    search_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    end_point = db.Column(db.Integer, db.ForeignKey('points.point_id'))
    travel_time = db.Column(db.Integer, nullable=True)
    travel_distance = db.Column(db.Integer)
    min_ele = db.Column(db.Integer)
    max_time = db.Column(db.Integer)
    travel_mode = db.Column(db.String(64))

    p = db.relationship('Point', backref='s', order_by='Point.latitude')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s address_id=%s search_id=%s end_point=%s \n\
                travel_time/distance=%s,%s min_ele=%s max_time=%s travel_mode=%s>" % (self.user_id,
                                                                                      self.address_id,
                                                                                      self.search_id,
                                                                                      self.end_point,
                                                                                      self.travel_time,
                                                                                      self.travel_distance,
                                                                                      self.min_ele,
                                                                                      self.max_time,
                                                                                      self.travel_mode)

    @classmethod
    def new_search(cls, lat, lng, user_id, min_height, max_time, travel_mode, elevation):
        """looking for high elevation just within a tile"""

        if not (BAY['S'] < lat < BAY['N']) and not (BAY['W'] < lng < BAY['E']):
            return {"message": "Not in Bounds"}
        address_id = Address.check_address(lat, lng, elevation)
        search = cls(user_id=user_id, address_id=address_id, max_time=max_time, min_ele=min_height,
                     travel_mode=travel_mode)
        db.session.add(search)
        db.session.flush()
        if elevation < search.min_ele:
            threshold = search.min_ele
        else:
            threshold = elevation
        if threshold >= 500:
            points = search.high_threshold_query(threshold)
            print "high"
        else:
            radius = search.calc_radius(max_time, travel_mode)
            print radius
            points = search.nearby_tiles_query(lat, lng, radius, threshold)
            print "nearby"
        distance, top_point = search.get_closest(points, lat, lng)
        search.end_point = top_point.point_id
        print search.p
        db.session.commit()
        response = {"point": search.p, "id": search.search_id}
        return response

    @classmethod
    def add_travel_data(cls, search_id, duration, distance):
        """looking up search_id to update entry with duration info from google directions"""

        search = cls.query.filter(cls.search_id == search_id).one()
        # duration is in seconds, change to minutes
        # pretty sure distance is in meters. pretty sure....
        length = int(distance)
        time = int(duration) / 60
        search.travel_time = time
        search.travel_distance = length
        db.session.commit()
        return "You updated your search!"  # % (search.u.name) need to handle when no user logged in

    @classmethod
    def delete_entry(cls, search_id):
        """deleting entry using search_id"""

        # haven't decided whether I want to store error data into search table instead
        pass

    def calc_radius(self, max_time, travel_mode):
        """calculating what increment to pass into radiating query, speed is in ft/min"""

        typical_speed = {"WALKING": 440,
                         "DRIVING": 2500,
                         "BICYCLING": 750,
                         "TRANSIT": 1000}
        max_distance = max_time * typical_speed[travel_mode]
        # increment distance is first in feet, allows it to radiate out 6 times before running out of time
        increment_distance = max_distance / 6
        # translating to steps, data isn't continuous each step is around 30 ft
        increment_steps = increment_distance / 30
        # translating to lat/lng increments which will be used in the future for reasonable euclidian estimates
        radius = ((BAY['E'] - BAY['W']) / BAY['steps_x']) * increment_steps
        return radius

    @staticmethod
    def get_meters(distance):
        """turns elevation in feet into meters for storage"""

        return distance * 0.305

    @staticmethod
    def get_feet(distance):
        """turns elevation and travel into feet for display"""

        return distance * 3.28084

    def nearby_tiles_query(self, lat, lng, radius, threshold, count=1):
        """looking for high elevation in nearby tiles"""

        point_list = []
        counter = count
        tile_memo = set()
        while not point_list:
            reach = radius * counter
            top_reach = lat + reach
            if top_reach > BAY['N']:
                top_reach = BAY['N']
            bottom_reach = lat - reach
            if bottom_reach < BAY['S']:
                bottom_reach = BAY['S']
            left_reach = lng - reach
            if left_reach < BAY['W']:
                left_reach = BAY['W']
            right_reach = lng + reach
            if right_reach > BAY['E']:
                right_reach = BAY['E']
            # this type of query was noticeably slow. functional. but slow.
            # tile_objects = Tile.query.filter(Tile.bottom_bound < top_reach, Tile.top_bound > bottom_reach,
            #                                  Tile.left_bound < right_reach, Tile.right_bound > left_reach).all()
            # print "num tiles"
            # print len(tile_objects)
            # tiles = [x for x in tile_objects if x not in tile_memo]
            # for tile in tiles:
            #     tile_memo.add(tile)
            #     points = tile.p
            #     for point in points:
            #         if point.elevation > threshold:
            #             point_list.append(point)
            tile_objects = db.session.query(Tile.tile_id, Point).filter(Tile.bottom_bound < top_reach, Tile.top_bound > bottom_reach,
                                                                        Tile.left_bound < right_reach, Tile.right_bound > left_reach,
                                                                        Point.elevation > threshold).join(Point).all()
            print len(tile_objects)
            for tile, point in tile_objects:
                # if point.elevation > threshold:
                if tile not in tile_memo:
                    point_list.append(point)
                tile_memo.add(tile)
            counter += 1
        return point_list

    def high_threshold_query(self, threshold):
        """looking for points from points table over threshold"""

        point_list = Point.query.filter(Point.elevation > threshold).all()
        return point_list

    @staticmethod
    def get_closest(points, lat, lng):
        """takes a list of points, calculates euclidean distance and returns the closest point object"""

        distances = []
        print "getting closest!"
        for point in points:
            # errors happened with difference math syntax, unsure why, don't change unless to import math sqrt
            distance = (((point.latitude - lat) ** 2) + ((point.longitude - lng) ** 2)) ** (0.5)
            distances.append((distance, point))
        distances.sort(key=lambda x: x[0])
        return distances[0]


class Address(db.Model):
    """Addresses that have been searched."""

    __tablename__ = "addresses"

    address_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=True, default=None)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    elevation = db.Column(db.Float)

    s = db.relationship('Search', backref='a', order_by='Search.address_id')

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

        try:
            place = db.session.query(cls).filter(cls.latitude == lat, cls.longitude == lng).one()
            return place.address_id
        except:
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


def connect_to_db(app, db_url='postgresql:///expand'):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # when running module interactively will allow working with database directly
    from server import app
    connect_to_db(app)
    print "Connected to DB."
