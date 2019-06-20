# -*- coding: utf-8 -*-
"""
!/usr/bin/python3
@CreateDate   : 2019-06-19
@Author      : jet
@Filename : routers_server_simple.py
@Software : pycharm
"""
import re
from wsgiref.simple_server import make_server
from werkzeug.wrappers import Request, Response


class NotFoundError(Exception):
    """ url pattern not found """
    pass


class Router:
    def __init__(self):
        self.routing_table = []    # 保存 url pattern 和 可调用对象

    def add_route(self, pattern, callback):
        self.routing_table.append((pattern, callback))

    def match(self, path):
        for (pattern, callback) in self.routing_table:
            m = re.match(pattern, path)
            if m:
                return (callback, m.groups())
        raise NotFoundError()


def hello(request, name):
    return Response("<h1>Hello, {name}</h1>".format(name=name))


def goodbye(request, name):
    return Response("<h1>Goodbye, {name}</h1>".format(name=name))


routers = Router()
routers.add_route(r'/hello/(.*)/$', hello)
routers.add_route(r'/goodbye/(.*)/$', goodbye)


def application(environ, start_response):
    try:
        request = Request(environ)
        callback, args = routers.match(request.path)
        response = callback(request, *args)
    except NotFoundError:
        response = Response("<h1>Not found</h1>", status=404)
    start_response(response.status, response.headers.to_list())
    return iter(response.response)


if __name__ == '__main__':
    httpd = make_server('127.0.0.1', 8880, application)
    httpd.serve_forever()
