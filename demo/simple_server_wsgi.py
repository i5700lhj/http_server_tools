# -*- coding: utf-8 -*-
"""
!/usr/bin/python3
@CreateDate   : 2019-06-19
@Author      : jet
@Filename : wsgi_server_simple.py
@Software : pycharm
"""

# 导入python内置的WSGI server
from wsgiref.simple_server import make_server


def application(environ, start_response):
    # 打印环境变量字典参数
    print(environ)    # 查看环境变量字典参数
    # 一个包含 http 状态码和描述的字符串, 比如 '200 OK'
    status = '200 OK'
    # 一个包含http头的元组列表
    headers = [('Content-Type', 'text/html; charset=utf8')]

    # 取出 QUERY_STRING 字符串，通常为 key=value 格式键值对
    query_string = environ['QUERY_STRING']

    # 设置默认的返回值，注意返回的 bytes 编码要符合你指定的返回头
    rb = [b"<h1>Hello, World!</h1>"]

    # 当用户访问 http://localhost:8888/?name=XXX 的时候， 在网页上输出 “Hello XXX”
    if '' != query_string:
        # 取出 value
        q_value = query_string.split("=")[1]
        # 设置返回值
        _rb = "<h1>Hello, {}!</h1>".format(q_value)
        rb = [_rb.encode('utf-8')]

    start_response(status, headers)
    return rb


if __name__ == '__main__':
    httpd = make_server('127.0.0.1', 8888, application)
    httpd.serve_forever()
