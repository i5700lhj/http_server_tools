# -*- coding: utf-8 -*-
"""
!/usr/bin/python3
@CreateDate   : 2019-06-19
@Author      : jet
@Filename : simple_server_wsgi_get.py
@Software : pycharm
"""

from wsgiref.simple_server import make_server
from html import escape
from urllib.parse import parse_qs

# html中form的method是get，action是当前页面
html = """
<html>
<body>
   <form method="get" action="">
        <p>
           Age: <input type="text" name="age" value="%(age)s">
        </p>
        <p>
            Hobbies:
            <input
                name="hobbies" type="checkbox" value="software"
                %(checked-software)s
            > Software
            <input
                name="hobbies" type="checkbox" value="tunning"
                %(checked-tunning)s
            > Auto Tunning
        </p>
        <p>
            <input type="submit" value="Submit">
        </p>
    </form>
    <p>
        Age: %(age)s<br>
        Hobbies: %(hobbies)s
    </p>
</body>
</html>
"""


def application(environ, start_response):

    d = {}

    if 'GET' == environ['REQUEST_METHOD']:   # 处理GET请求
        # 解析QUERY_STRING，将URL中带有格式的输入参数转换为字典类型
        # 例如：'age=11&hobbies=tunning'  会转换为 {'age': ['11'], 'hobbies':
        # ['tunning']}
        d = parse_qs(environ['QUERY_STRING'])
    elif 'POST' == environ['REQUEST_METHOD']: # 处理POST请求
        # CONTENT_LENGTH 可能为空，或者没有
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0
        request_body = environ['wsgi.input'].read(request_body_size)
        d = parse_qs(str(request_body, encoding="utf-8"))

    age = d.get('age', [''])[0]  # 返回age对应的值
    hobbies = d.get('hobbies', [])  # 以list形式返回所有的hobbies

    # 防止脚本注入
    age = escape(age)
    hobbies = [escape(hobby) for hobby in hobbies]

    response_body = html % {
        'checked-software': ('', 'checked')['software' in hobbies],
        'checked-tunning': ('', 'checked')['tunning' in hobbies],
        'age': age or 'Empty',
        'hobbies': ', '.join(hobbies or ['No Hobbies?'])
    }

    status = '200 OK'

    # 这次的content type是text/html
    response_headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(response_body)))
    ]

    start_response(status, response_headers)
    return [response_body.encode("utf-8")]


httpd = make_server('localhost', 8051, application)

# 能够一直处理请求
httpd.serve_forever()

print('end')
