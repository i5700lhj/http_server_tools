# -*- coding: utf-8 -*-
"""User views."""
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

from .forms import ChangePwdForm
from .models import User

from http_server_tools.utils import flash_errors
from http_server_tools.extensions import login_manager

blueprint = Blueprint(
    "user",
    __name__,
    url_prefix="/users",
    static_folder="../static")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route("/")
@login_required
def members():
    """List members."""
    return render_template("users/members.html")


@blueprint.route("/changePwd/", methods=["GET", "POST"])
@login_required
def change_pwd():
    """Change member password"""
    current_app.logger.info("change_pwd(). user: %s", current_user.username)
    form = ChangePwdForm(request.form)
    user = User.query.filter_by(username=current_user.username).first()
    if form.validate_on_submit():
        # User.exe("UPDATE users SET is_admin=1 WHERE id=1;")
        user.set_password(form.password.data)
        user.update({'password': user.password})
        logout_user()
        flash("Change password successfully! Please re-login!", "success")
        return redirect(url_for("public.login"))
    else:
        flash_errors(form)
    return render_template("users/change_pwd.html", form=form)
