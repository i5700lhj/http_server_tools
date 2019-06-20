# -*- coding: utf-8 -*-
"""
!/usr/bin/python3
@CreateDate   : 2019-06-19
@Author      : jet
@Filename : werkzenug_server_simple.py
@Software : pycharm
"""

from wsgiref.simple_server import make_server
from werkzeug.wrappers import Request, Response


@Request.application
def application(request):
    name = request.args.get('name', 'PyCon')
    return Response(['<h1>hello {name}</h1>'.format(name=name)])


if __name__ == '__main__':
    httpd = make_server('127.0.0.1', 8889, application)
    httpd.serve_forever()
