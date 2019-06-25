# -*- coding: utf-8 -*-
"""
!/usr/bin/python3
@CreateDate   : 2019-06-24
@Author      : jet
@Filename : app.py
@Software : pycharm

The app module, containing the app factory function.
"""

from flask import Flask
from flask_restful import Api

from flask_server_user.api import TodoList, Todo, TaskList
from flask_server_user import public, user
from flask_server_user.extensions import (
    # bcrypt,
    # cache,
    csrf_protect, #防跨站脚本攻击扩展功能
    # db,
    debug_toolbar,  #激活flask debug tool bar功能
    # login_manager,
    # migrate,
    # webpack,
)


def create_app(config_object="flask_server_user.settings"):
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    print(__name__.split(".")[0])
    app = Flask(__name__)
    app.config.from_object(config_object)
    api_demo(app)

    register_extensions(app)
    register_blueprints(app)
    # register_errorhandlers(app)
    # register_shellcontext(app)
    # register_commands(app)
    # configure_logger(app)

    return app


def api_demo(app):
    """create restful api"""
    api = Api(app)
    ##
    # Actually setup the Api resource routing here
    ##
    api.add_resource(TodoList, '/todos')
    api.add_resource(Todo, '/todos/<todo_id>')
    api.add_resource(TaskList, '/tasks')

    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(user.views.blueprint)
    return None

def register_extensions(app):
    """Register Flask extensions."""
    # bcrypt.init_app(app)
    # cache.init_app(app)
    # db.init_app(app)
    csrf_protect.init_app(app)
    # login_manager.init_app(app)
    debug_toolbar.init_app(app)
    # migrate.init_app(app, db)
    # webpack.init_app(app)
    return None
