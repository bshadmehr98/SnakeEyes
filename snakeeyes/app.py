from flask import Flask
from snakeeyes.extentions import db, api

from snakeeyes.blueprints.users import users  # noqa
from snakeeyes.blueprints.general import general  # noqa
from snakeeyes.blueprints.calendar import calendar  # noqa
from snakeeyes.blueprints import dashboard  # noqa
import os
from .signals import register_signals


def create_app(settings_override=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object("config.settings")
    my_instance_location = os.path.join(os.getcwd(), "instance")
    app.config.from_pyfile(f"{my_instance_location}/settings.py", silent=False)

    if settings_override is not None:
        app.config.update(settings_override)

    extentions(app)
    register_signals([])

    return app


def extentions(app):
    db.init_app(app)
    api.init_app(app)
    return None
