# -*- coding: utf-8 -*-
"""
!/usr/bin/python3
@CreateDate   : 2019-05-05
@Author      : jet
@Filename : assistScript.py
@Software : pycharm
Helper utilities and decorators.
"""


import os
import time
import logging

from flask import flash


class Logger(object):
    """
    useage:
    1.    logger.info("Input >>> pdict : {0} , rdict : {1}".format(pdict,rdict))
    2.    logger.info("\n".join(remainTextList))
    """

    def __init__(self):
        pass

    def get_logger(self, class_name=""):
        #bashPath = os.path.join(os.path.dirname(__file__), '../../../')
        bashPath = os.path.join(os.path.dirname(__file__), '../log')
        if not os.path.exists(bashPath):
            os.mkdir(bashPath)

        cur_time = "%s" % time.strftime(
            '%Y%m%d%H%M%S', time.localtime(time.time()))
        # 每隔一天创建一个新文件
        log_file_name = "dataProvider.%s.log" % cur_time[:-6]
        logFile = os.path.join(bashPath, log_file_name)

        my_logger = logging.getLogger(class_name)
        my_logger.setLevel(level=logging.DEBUG)
        handler = logging.FileHandler(logFile)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s - %(message)s')
        handler.setFormatter(formatter)

        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)

        my_logger.addHandler(handler)
        my_logger.addHandler(console)
        return my_logger


def flash_errors(form, category="warning"):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash("{0} - {1}".format(getattr(form, field).label.text, error), category)
