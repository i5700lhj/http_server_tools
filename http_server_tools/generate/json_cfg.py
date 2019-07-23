# -*- coding: utf-8 -*-
"""
!/usr/bin/python3
@CreateDate   : 2019-03-21
@Author      : jet
@Filename : json_cfg.py
@Software : pycharm
"""
import json
from http_server_tools.utils import Logger

LOG = Logger()


class JsonConfig(object):
    """
    json文件解析模块
    """

    def __init__(self):
        self.xl_logger = LOG.get_logger(
            "%s %s" %
            (__name__, self.__class__.__name__))
        self._lis_value = []

    def load_json_to_dict(self, file_path_name):
        """
        将json文件中的内容读取到一个字典变量
        :param file_path_name: json文件路径及文件名，字符串类型
        :return: json文件内容的字典类型数据
        """
        with open(file_path_name, 'r', encoding="utf-8") as load_f:
            load_dict = json.load(load_f)
        return load_dict

    def dump_dict_to_json(self, file_path_name, new_dict):
        """
        将一个字典内容数据，写入到json文件中
        :param file_path_name: json文件路径及文件名，字符串类型
        :param new_dict: 需要写入的字典类型数据
        :return:
        """
        with open(file_path_name, "w", encoding="utf-8") as dump_f:
            json.dump(new_dict, dump_f)
        return

    def get_json_file_value(self, json_file_path_name, key):
        """
        将指定JSON文件中内容取出转换为DICT，并解析取出指定key所对应的所有Value
        :param json_file_path_name: json文件路径及文件名（字符串类型）
        :param key: 需要查找内容对应的Key值（字符串类型）
        :return: 指定key所对应的所有Value（列表类型）
        """
        self._lis_value = []
        dict_data = self.load_json_to_dict(json_file_path_name)
        self.__get_from_json_ex(dict_data, key)
        return self._lis_value

    def __get_from_json_ex(self, data, name):
        """
        私有递归方法，找出data中所有对应name的值
        :param data: 传入一个字典类型数据
        :param name: 传入要查找的Key值（字符串类型）
        :return: 通过递归查找，返回指定key所对应的所有Value（列表类型）
        """
        self.xl_logger.debug("input data : %s" % data)
        self.xl_logger.debug("input name : %s" % name)
        if type(data).__name__ == 'dict':
            self.xl_logger.debug("parse dict...")
            if name in data.keys():
                self.xl_logger.debug("append value : %s" % data[name])
                self._lis_value.append(data[name])
            else:
                for key in data.keys():
                    # print 'ssss %s' % data
                    new_data = data[key]
                    if type(new_data).__name__ == 'dict':
                        self.xl_logger.debug("parse dict......")
                        # data = new_data[key]
                        # print ('data1 %s' % data)
                        self.__get_from_json_ex(new_data, name)
                    if type(new_data).__name__ == 'list':
                        self.xl_logger.debug("parse list......")
                        for i in range(len(new_data)):
                            temp_data = new_data[i]
                            self.__get_from_json_ex(temp_data, name)

        if type(data).__name__ == 'list':
            self.xl_logger.debug("parse list...")
            for i in range(len(data)):
                temp_data = data[i]
                # print ('temp_data %s' % temp_data)
                self.__get_from_json_ex(temp_data, name)
