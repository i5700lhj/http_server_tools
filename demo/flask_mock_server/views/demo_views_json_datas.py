# -*- coding: utf-8 -*-
"""
!/usr/bin/python3
@CreateDate   : 2019-07-12
@Author      : jet
@Filename : demo_views_json_datas.py
@Software : pycharm
"""
import os.path
import json
from flask.blueprints import Blueprint
from flask import request

BASE_DIR = str(os.path.dirname(os.path.dirname(__file__)))
#BASE_DIR = BASE_DIR.replace('\\', '/')

demo_views_json_datas = Blueprint('demo_views_json_datas', __name__)

RESOURCE_PATH = os.path.join(
    BASE_DIR,
    'resource',
    'demo_views_json_datas')


@demo_views_json_datas.route('/get_json_datas/<node>')
def test_do_get(node=None):
    if node is None:
        raise Exception('no such node: {0}'.format(node))
    filePath = os.path.join(RESOURCE_PATH, 'get_json_datas', node + '.json')
    with open(filePath, 'rb') as nf:
        data = json.load(nf)
    return json.dumps({'data': data, "message": "", "code": 0, "ok": True})


@demo_views_json_datas.route('/post_json_datas/<node>', methods=['POST'])
def test_do_post(node=None):
    if node is None:
        raise Exception('no such node: {0}'.format(node))
    filePath = os.path.join(RESOURCE_PATH, 'post_json_datas', node + '.json')
    with open(filePath, 'rb') as nf:
        data = json.load(nf)
    return json.dumps({'data': data, 'reqdata': str(request.data, encoding="utf-8"),
                       "message": "", "code": 0, "ok": True})
