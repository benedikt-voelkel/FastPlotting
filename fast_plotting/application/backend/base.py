import os
from os.path import realpath, dirname, join, exists
from os import makedirs

from flask import Flask

from fast_plotting.application.backend.plot import BLUEPRINT

UPLOAD_FOLDER = '/tmp/fast_plotting/uploads/'

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, template_folder=join(dirname(realpath(__file__)), "..", "templates"), static_folder=join(dirname(realpath(__file__)), "..", "static"))
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def hello():
        return 'Hello, World, sup!'

    app.register_blueprint(BLUEPRINT)

    if not exists(UPLOAD_FOLDER):
        makedirs(UPLOAD_FOLDER)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    return app
