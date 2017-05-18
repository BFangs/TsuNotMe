from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request,
                   flash, session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from model import Tile, Point, connect_to_db, db
import os
API_KEY = os.environ['googlekey']

app = Flask(__name__)
app.secret_key = "BOO"
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def home():
    """Homepage."""

    return render_template("homepage.html", API_KEY=API_KEY)

@app.route('/start')
def pick_location():
    """not sure if this needs a route yet"""
    pass


if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug
    connect_to_db(app)
    DebugToolbarExtension(app)
    app.run(port=5000, host='0.0.0.0')
