# -*- coding: utf-8 -*-
"""
!/usr/bin/python3
@CreateDate   : 2019-07-22
@Author      : jet
@Filename : mongodb.py
@Software : pycharm
"""

import io
import os
import sys
from pymongo import MongoClient, errors
import configparser as cparser
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_dir = str(os.path.dirname(os.path.dirname(__file__)))
base_dir = base_dir.replace('\\', '/')
file_path = base_dir + "/generate/db_config.ini"

mongocf = cparser.ConfigParser()

mongocf.read(file_path)
host = mongocf.get("ip_list", "host1")
port = mongocf.get("mongo_config", "port")
dbname = mongocf.get("mongo_config", "db_name")


class MongodbClient(object):

    def __init__(self, timeout=300):
        try:
            self.client = MongoClient('mongodb://%s:%s' % (host, port))
        except Exception as connection_error:
            print(connection_error)
        self.xl_db = self.client[dbname]
        self.timeout = timeout

    # 批量创建集合，写入模板数据
    def batch_collection_insert(
            self, api_db_name, collection_names, api_template):
        db = self.client[api_db_name]
        for i in range(len(collection_names)):
            cn = db[collection_names[i]]
            cn.save(api_template)

    # 在指定的集合中插入多条记录
    def collection_insert_many(
            self, db_name, collection_name, list_of_records):
        db = self.client[db_name]
        collection = db[collection_name]
        collection.insert_many(list_of_records)


class MongodbOpt(object):
    def __init__(self, dbname, timeout=300):
        try:
            self.client = MongoClient('mongodb://%s:%s' % (host, port))
        except Exception as connection_error:
            print(connection_error)
        self.db = self.client[dbname]
        self.timeout = timeout

    # 通过key/value获取一个集合数据
    def get_one_data(self, collection_name, key, value):
        collection = self.db[collection_name]
        return collection.find_one({key: value})

    # 通过指定集合的caseName获取接口数据
    def get_case_data(self, collection_name, case_name):
        collection = self.db[collection_name]
        return collection.find_one({"caseName": case_name})

    # 通过指定集合的caseName获取接口发送参数数据
    def get_case_req(self, collection_name, case_name):
        collection = self.db[collection_name]
        return collection.find_one({"caseName": case_name})["req"]

    # 通过指定集合的caseName获取接口返回期望值数据
    def get_case_resp(self, collection_name, case_name):
        collection = self.db[collection_name]
        return collection.find_one({"caseName": case_name})["resp"]

    # 通过指定集合的caseName、接口数据字段，获取接口发送及返回的详细数据
    def get_case_api_data(self, collection_name, case_name, api_data_key):
        collection = self.db[collection_name]
        try:
            return collection.find_one({"caseName": case_name})[api_data_key]
        except Exception as e:
            print("api_data_key: %s not found" % e)


if __name__ == '__main__':
    mongodb = MongodbClient()
