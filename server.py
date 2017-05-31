from jinja2 import StrictUndefined
from flask import (Flask, session, render_template, request, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, User, Search

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
    elevation = float(request.args.get("elevation"))
    min_height = request.args.get("min_height")
    max_time = request.args.get("max_time")
    travel_mode = request.args.get("travel_mode")
    user_id = session.get('user_id', 'nemo')
    point_list = Search.tile_query(latitude, longitude, user_id, min_height, max_time, travel_mode, elevation)
    answer = {}
    for point, i in enumerate(point_list):
        answer[i] = {"tile_id": point[0],
                     "latitude": point[1],
                     "longitude": point[2],
                     "elevation": point[3]}
    return jsonify(answer)


@app.route('/login.json', methods=['POST'])
def login_user():
    """ajax call querying registration then administering login"""

    email = request.form.get('email')
    password = request.form.get('password')
    nickname = request.form.get('nickname')
    response = {}
    check = User.check_user(email, password, nickname)
    if check["user_id"]:
        session["user_id"] = check["user_id"]
        response["success"] = True
    response["message"] = check["message"]
    return jsonify(response)


@app.route('/loggout.json')
def loggout_user():
    """ajax call for loggout"""

    response = {}
    del session["user_id"]
    response["message"] = "You're now logged out"
    return jsonify(response)


if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug
    connect_to_db(app)
    DebugToolbarExtension(app)
    app.run(port=5000, host='0.0.0.0')
