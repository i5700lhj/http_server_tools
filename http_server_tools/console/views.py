# -*- coding: utf-8 -*-
"""console views."""
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, logout_user, current_user

from http_server_tools.utils import flash_errors
from http_server_tools.extensions import login_manager

blueprint = Blueprint(
    "console",
    __name__,
    url_prefix="/console",
    static_folder="../static")


@blueprint.route("/")
@login_required
def home():
    """console home page"""
    return render_template("console/home.html")
