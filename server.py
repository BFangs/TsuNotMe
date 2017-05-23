from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request,
                   flash, session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from model import Tile, Point, connect_to_db, db
from data import tile_query
import numpy as np

import os
API_KEY = os.environ['googlekey']

app = Flask(__name__)
app.secret_key = "BOO"
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def home():
    """Homepage."""

    return render_template("homepage.html", API_KEY=API_KEY)

@app.route('/start.json')
def get_points():
    """ajax call querying location"""

    latitude = float(request.args.get("latitude"))
    longitude = float(request.args.get("longitude"))
    point_list = tile_query(latitude, longitude)
    # need to change this when I change algorithm to query multiple points
    top_point = point_list[0]
    answer = {"tile_id": top_point[0],
              "latitude": top_point[1],
              "longitude": top_point[2],
              "elevation": top_point[3]}
    return jsonify(answer)


if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug
    connect_to_db(app)
    DebugToolbarExtension(app)
    app.run(port=5000, host='0.0.0.0')
