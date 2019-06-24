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
from .api import TodoList, Todo, TaskList


def create_app(config_object="flask_server_user.settings"):
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    print(__name__.split(".")[0])
    app = Flask(__name__)
    app.config.from_object(config_object)
    api_demo(app)
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

    return api
