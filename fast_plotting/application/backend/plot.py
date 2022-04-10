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
        self.names = None

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
    WRAPPER.names = None


def plot(selected_sources):
    # returns the JSONs
    data_wrappers = [load_source_from_config(WRAPPER.config, s, True) for s in selected_sources]

    df = combine_data_wrappers_df(*data_wrappers)

    fig = px.bar(df, x="x", y="y", color="tag", barmode="overlay")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def get_sources_for_html():
    return [(s[0], s[2]) for s in WRAPPER.sources] if WRAPPER.sources else None

@BLUEPRINT.route('/do', methods=('GET', 'POST'))
def do():


    if request.method == 'POST':
        if request.form["btn"] == "Add":
            add_source(request)

        if request.form["btn"] == "Load":
            BACKEND_LOGGER.info("LOAD")
            load_from_source()

        if request.form["btn"] == "Remove":
            BACKEND_LOGGER.info("Remove sources")
            remove_sources()

        return redirect(url_for("plot.do"))

    return render_template('plot/do.html', plots_list=WRAPPER.names, sources=get_sources_for_html())

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


@BLUEPRINT.route("/modal")
def modal():
    return render_template("plot/plot_configure.html")


@BLUEPRINT.route("/defineplots/front")
def defineplots_front():
    return render_template("plot/define_plots.html", plots_list=WRAPPER.names, sources=get_sources_for_html())


@BLUEPRINT.route("/defineplots/add", methods=('GET', 'POST'))
def define_plots():

    if request.method == 'POST':
        BACKEND_LOGGER.info("ADD PLOT")
        name = request.form.get('plot_name')
        if not WRAPPER.names:
            WRAPPER.names = []
        WRAPPER.names.append(name)
        print(name)



    return render_template("plot/plots_list.html", plots_list=WRAPPER.names, sources=get_sources_for_html())


@BLUEPRINT.route("/defineplots/remove", methods=('GET', 'POST'))
def remove_plot():

    to_be_removed = request.args.get("name")
    print(to_be_removed)
    if to_be_removed and WRAPPER.names and to_be_removed in WRAPPER.names:
        del WRAPPER.names[WRAPPER.names.index(to_be_removed)]
        print("removed")
    return redirect(url_for("plot.do"))


@BLUEPRINT.route("/defineplots/configure")
def defineplots_configure():
    source_identifiers = None

    print("I am here", WRAPPER.config)

    if WRAPPER.config:
        full_source_names = {s[1]: i for i, s in enumerate(WRAPPER.sources)}
        identifiers = [[] for _ in full_source_names]
        for batch in WRAPPER.config.get_sources():
            ind = full_source_names[batch["filepath"]]
            identifiers[ind].append(batch["identifier"])

        source_identifiers = [(s[0], i) for s, i in zip(WRAPPER.sources, identifiers)]
    return render_template("plot/configure_plots.html", plots_list=WRAPPER.names, sources=get_sources_for_html(), source_identifiers=source_identifiers)


@BLUEPRINT.route("/defineplots/configure/add", methods=('GET', 'POST'))
def defineplots_configure_add():
    if request.method == 'POST':
        BACKEND_LOGGER.info("CONFIGURED PLOT")
        to_be_configured = request.form.getlist("top5")
        print(to_be_configured)
    return redirect(url_for("plot.do"))


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
