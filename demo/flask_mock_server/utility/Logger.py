#coding=utf-8

import os
import logging.handlers


def get_handler():
    basePath = os.path.join(os.path.dirname(__file__), 'log')
    if not os.path.exists(basePath):
        os.mkdir(basePath)
    logFile = os.path.join(basePath, 'mock_server.log')
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fhandler = logging.handlers.RotatingFileHandler(logFile, maxBytes=10*1024*1024, backupCount=50, encoding='utf-8')
    fhandler.setFormatter(formatter)
    fhandler.setLevel(logging.DEBUG)


    return fhandler

handler = get_handler()