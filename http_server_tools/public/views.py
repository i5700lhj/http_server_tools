# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, login_user, logout_user

from http_server_tools.extensions import login_manager
from http_server_tools.public.forms import LoginForm
from http_server_tools.user.forms import RegisterForm
from http_server_tools.user.models import User
from http_server_tools.utils import flash_errors

blueprint = Blueprint("public", __name__, static_folder="../static")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route("/", methods=["GET", "POST"])
def home():
    """Home page."""
    form = LoginForm(request.form)
    current_app.logger.info("Hello from the home page!")
    return render_template("public/home.html", form=form)


@blueprint.route("/login/", methods=["GET", "POST"])
def login():
    """login page."""
    form = LoginForm(request.form)
    current_app.logger.info(
        "call login request method:%s, username :%s ." %
        (request.method, form.data['username']))
    # Handle logging in
    if request.method == "POST":
        if form.validate_on_submit():
            current_app.logger.info(
                "login success. login user info:%s" %
                form.user)
            login_user(form.user)
            flash(
                "Logged in success ! Welcome %s !" %
                form.user.username, "success")
            redirect_url = request.args.get("next") or url_for("tools.cards")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/login.html", form=form)


@blueprint.route("/logout/")
@login_required
def logout():
    """Logout."""
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("public.login"))


@blueprint.route("/register/", methods=["GET", "POST"])
def register():
    """Register new user."""
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        User.create(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            active=True,
        )
        flash("Thank you for registering. You can now log in.", "success")
        return redirect(url_for("public.home"))
    else:
        flash_errors(form)
    return render_template("public/register.html", form=form)


@blueprint.route("/about/")
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)


@blueprint.route("/egg/")
@login_required
def egg():
    """egg page."""
    return render_template("public/egg.html")


@blueprint.route("/demo-jquery-jbox")
def demo():
    """demo-jquery-jbox"""
    return render_template("demo/demo-jquery-jbox.html")
