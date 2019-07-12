# -*- coding: utf-8 -*-
"""
!/usr/bin/python3
@CreateDate   : 2019-07-12
@Author      : jet
@Filename : common_mock_server.py
@Software : pycharm
"""
import sys
import json
import os.path
from flask import Flask, request
from utility.Logger import handler
from views.demo_views_json_datas import demo_views_json_datas

instance_path = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, root_path=instance_path)
app.logger.addHandler(handler)
app.debug = True

app.register_blueprint(demo_views_json_datas, url_prefix='/demo_views_json_datas')


def config_app(app):
    app.logger.info('Setting up application...')
    app.config.from_mapping(HOST='0.0.0.0')
#     for handler in logger.handlers:
#         app.logger.addHandler(handler)

    @app.before_request
    def before_request():
        app.logger.info(
            'request url is {0}; method is {1}; remote_addr is {2}'.format(
                request.url,
                request.method,
                request.remote_addr))
        app.logger.info('request data is {0}'.format(request.data))

    @app.after_request
    def after_request(response):
        app.logger.info('response_status is {0}'.format(response._status))
        if hasattr(response, 'data'):
            data = response.data
            if isinstance(data, dict):
                response.data = json.dumps(data)
            elif not data:
                response.data = "{}"
        else:
            response.data = "{}"
        app.logger.info('response data is {0}'.format(response.data))
        return response


def dispatch_handlers(app):

    @app.errorhandler(403)
    def permission_error(error):
        return json.dumps({'error': str(error), 'errorCode': 403})

    @app.errorhandler(404)
    def page_not_found(error):
        return json.dumps({'error': str(error), 'errorCode': 404})

    @app.errorhandler(500)
    def page_error(error):
        return json.dumps({'error': str(error), 'errorCode': 500})


config_app(app)
dispatch_handlers(app)


@app.route('/test')
def test():
    return json.dumps({'recode': 0, 'message': 'success'}), 200


if __name__ == '__main__':
    port = ""
    if len(sys.argv) > 1:
        port = sys.argv[1]
    if not port:
        port = 5000
    app.run(host='0.0.0.0', port=port)
