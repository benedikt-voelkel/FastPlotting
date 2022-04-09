import functools
from os.path import join
from time import time

import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, escape
)
from flask import current_app

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import plotly.express as px
import plotly

# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField
# from wtforms.validators import DataRequired

from fast_plotting.logger import get_logger
from fast_plotting.config import read_config, configure_from_sources
from fast_plotting.registry import load_source_from_config
from fast_plotting.data.data import combine_data_wrappers_df

BACKEND_LOGGER = get_logger("Backend")

BLUEPRINT = Blueprint('plot', __name__, url_prefix='/plot')

class Wrapper:
    def __init__(self):
        self.config = None
        self.sources = []
        self.plotter = None

WRAPPER = Wrapper()

def save_file(file, path):
    prefix = int(time())
    filename_raw = secure_filename(file.filename)
    filename_prefixed = f"{prefix}_{filename_raw}"
    full_name = join(path, filename_prefixed)
    file.save(full_name)
    return filename_raw, full_name


def add_source(request):
    source = request.files['source']
    label = request.form["label"]

    if not source or not label:
        BACKEND_LOGGER.warning("Label or source missing")
        return False

    if not source.filename:
        return False

    label = escape(label)
    filename_raw, filename_prefixed = save_file(source, current_app.config["UPLOAD_FOLDER"])
    WRAPPER.sources.append((filename_raw, filename_prefixed, label))
    return True


def load_from_source():
    if WRAPPER.config:
        WRAPPER.config = None
    WRAPPER.config = configure_from_sources([s[1] for s in WRAPPER.sources], [s[2] for s in WRAPPER.sources])


def remove_sources():
    WRAPPER.config = None
    WRAPPER.sources = []


def plot(selected_sources):
    # returns the JSONs
    data_wrappers = [load_source_from_config(WRAPPER.config, s, True) for s in selected_sources]

    df = combine_data_wrappers_df(*data_wrappers)

    fig = px.bar(df, x="x", y="y", color="tag", barmode="overlay")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@BLUEPRINT.route('/do', methods=('GET', 'POST'))
def do():
    if WRAPPER.sources:
        if not hasattr(g, "sources"):
            g.sources = {"paths": [(s[0], s[2]) for s in WRAPPER.sources]}
        else:
            last_source = WRAPPER.sources[-1]
            g.sources["paths"].append((last_source[0], last_source[2]))
    if WRAPPER.config:
        full_source_names = {s[1]: i for i, s in enumerate(WRAPPER.sources)}
        identifiers = [[] for _ in full_source_names]
        for batch in WRAPPER.config.get_sources():
            ind = full_source_names[batch["filepath"]]
            identifiers[ind].append(batch["identifier"])
        # re-arrange so that we can make a nice column
        max_length = max(len(ident) for ident in identifiers)
        # for ident in identifiers:
        #     ident.extend([""] * (max_length - len(ident)))
        identifiers_tuples = []
        for ident in zip(*identifiers):
            identifiers_tuples.append([i for i in ident])
        g.source_identifiers = {"source_paths": [(s[0], i) for s, i in zip(WRAPPER.sources, identifiers)]}
        g.width = 100 / len(identifiers)
    if request.method == 'POST':
        if request.form["btn"] == "Add":
            add_source(request)

        if request.form["btn"] == "Load":
            BACKEND_LOGGER.info("LOAD")
            load_from_source()

        if request.form["btn"] == "Remove":
            BACKEND_LOGGER.info("Remove sources")
            remove_sources()
            if hasattr(g, "sources"):
                del g.sources
            if hasattr(g, "source_identifiers"):
                del g.source_identifiers

        # if request.form["btn"] == "Plot":
        #     return redirect(url_for("plot.plots"))

        return redirect(url_for("plot.do"))

    return render_template('plot/do.html')

@BLUEPRINT.route('/plots', methods=('GET', 'POST'))
def plots():
    plots = []
    if request.method == 'POST':
        BACKEND_LOGGER.info("PLOT")
        selected = request.form.getlist('top5')
        print(selected)
        plots.append(plot(selected))
        print(plots)

    #plots = plots[0] if plots else
    return render_template('plot/plots.html', plotsJSON=plots[0] if plots else [])


#
# @BLUEPRINT.route('/login', methods=('GET', 'POST'))
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         BACKEND_LOGGER.info("Logging in")
#         error = "weird username" if username == "bene" else None
#         user = {"id": "1"}
#
#         if error is None:
#             session.clear()
#             session['user_id'] = user['id']
#             return redirect(url_for('index'))
#
#     return render_template('auth/login.html')
#
# @BLUEPRINT.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')
#
#     if user_id is None:
#         g.user = None
#     else:
#         g.user = {"username": "other"}
#
# def login_required(view):
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return redirect(url_for('auth.login'))
#
#         return view(**kwargs)
#
#     return wrapped_view
