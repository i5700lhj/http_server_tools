# -*- coding: utf-8 -*-
"""
!/usr/bin/python3
@CreateDate   : 2019-06-24
@Author      : jet
@Filename : autoapp.py
@Software : pycharm

Create an application instance.
"""

from flask_server_user.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)  # port =5000
