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
    min_height = int(request.args.get("min_height"))
    max_time = int(request.args.get("max_time"))
    travel_mode = request.args.get("travel_mode")
    user_id = session.get('user_id', None)
    print latitude, longitude, elevation, min_height, max_time, travel_mode, user_id
    result = Search.new_search(latitude, longitude, user_id, min_height, max_time, travel_mode, elevation)
    point = result["point"]
    if elevation > min_height:
        message = "You're already at a safe location! If you want to climb even higher follow the route"
    else:
        message = "Hurry to safety! tik tok tik tok..."
    answer = {"point_elevation": int(point.elevation),
              "latitude": point.latitude,
              "longitude": point.longitude,
              "elevation": int(elevation),
              "travel_mode": travel_mode,
              "max_time": max_time,
              "message": message,
              "search_id": result["id"]}
    print answer
    return jsonify(answer)


@app.route('/search_history.json')
def get_history():
    """ajax call querying search history for person"""

    response = {'history': []}
    try:
        user_id = session["user_id"]
    except:
        user_id = 1
    history = User.get_history(user_id)
    for search in history:
        thing = {"start_lat": search.a.latitude,
                 "start_lng": search.a.longitude,
                 "start_ele": int(search.a.elevation),
                 "end_lat": search.p.latitude,
                 "end_lng": search.p.longitude,
                 "end_ele": int(search.p.elevation),
                 "min_ele": search.min_ele,
                 "max_time": search.max_time,
                 "travel_mode": search.travel_mode,
                 "search_id": search.search_id}
        response['history'].append(thing)
    return jsonify(response)


@app.route('/results.json', methods=['POST'])
def update_search_history():
    """ajax call updating search with distance and duration info"""

    duration = request.form.get('duration')
    distance = request.form.get('distance')
    search_id = request.form.get('search_id')
    success = Search.add_travel_data(search_id, duration, distance)
    answer = {"message": success}
    return jsonify(answer)


@app.route('/route_fail.json', methods=['POST'])
def delete_search():
    """ajax call deleting search when route fails to load from google"""

    search_id = request.form.get('search_id')
    message = Search.delete_entry(search_id)
    answer = {"message": message}
    return jsonify(answer)


@app.route('/login.json', methods=['POST'])
def login_user():
    """ajax call querying registration then administering login"""

    email = request.form.get('email')
    password = request.form.get('password')
    nickname = request.form.get('nickname')
    response = {}
    check = User.check_user(email, password, nickname)
    if check["id"]:
        session["user_id"] = check["id"]
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
