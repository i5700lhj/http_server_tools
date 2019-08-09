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


from http_server_tools.user.forms import ChangePwdForm
from http_server_tools.user.models import User
from http_server_tools.utils import flash_errors

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


@blueprint.route("/users/", methods=["GET", "POST"])
@login_required
def users():
    """console users page."""
    l_users = []
    # s_users = ""
    # 使用get_by_id类函数据逐个获取users表中数据
    # ss = User.get_by_id(1)
    # 使用query_all类函数，直接获取users表中所有数据
    rows = User.query_all("select * from users")
    current_app.logger.info("users() User.query_all() return: %s", rows)
    # 使用for方法将获取到的行数据赋值给一个列表变量
    for row in rows:
        current_app.logger.debug("users table row: %s", row)
        l_users.append(row)
        # s_users = s_users + ":" + str(row)
    current_app.logger.info("l_users: %s", l_users)
    # current_app.logger.info("s_users: %s", s_users)
    return render_template("console/users.html",
                           l_users=l_users, num=len(l_users))


@blueprint.route("/users/manger", methods=["GET", "POST"])
@login_required
def users_manage():
    """console users manger page."""
    form = ChangePwdForm(request.form)
    current_app.logger.info("users_manage() request.method: %s", request.method)
    # 处理表单请求
    if request.method == 'POST':
        current_app.logger.info("users_manage() request.form: %s", request.form)
        return redirect(url_for('console.users_manage'))
    # 获取数据库中users表数据并展示
    l_users = []
    # s_users = ""
    # 使用get_by_id类函数据逐个获取users表中数据
    # ss = User.get_by_id(1)
    # 使用query_all类函数，直接获取users表中所有数据
    rows = User.query_all("select * from users")
    current_app.logger.info("users_manage() User.query_all() return: %s", rows)
    # 使用for方法将获取到的行数据赋值给一个列表变量
    for row in rows:
        current_app.logger.debug("users table row: %s", row)
        l_users.append(row)
        # s_users = s_users + ":" + str(row)
    current_app.logger.info("users_manage() l_users: %s", l_users)
    # current_app.logger.info("s_users: %s", s_users)
    return render_template("console/users_manage.html",
                           l_users=l_users, num=len(l_users), form=form)
