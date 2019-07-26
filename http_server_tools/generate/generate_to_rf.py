# -*- coding: utf-8 -*-
"""
!/usr/bin/python3
@CreateDate   : 2019-07-22
@Author      : jet
@Filename : postman_to_rf.py
@Software : pycharm
"""

import os
import sys
import re
import shutil
import time
from http_server_tools.utils import Logger
from http_server_tools.generate.xls_cfg import XlsConfig
from http_server_tools.generate.json_cfg import JsonConfig
from http_server_tools.generate.set_data import InitJsonFile

LOG = Logger()
GENERATE_FILE_NAME_PRE = "Demo"


class GenerateRF(object):
    def __init__(self):
        self.xl_logger = LOG.get_logger(
            "%s %s" %
            (__name__, self.__class__.__name__))
        self.xl_xls = XlsConfig()
        self.xl_json = JsonConfig()
        self.xl_ijf = InitJsonFile()
        self._rf_kw_file_name = ""

    def __init_kw_robot_file(self, robot_file_path_name,
                             settings_template_file_path_name):
        """
        初始化创建RF脚关键字脚本文件，如果文件存在则备份此文件后，删除掉原文件重新创建
        :param robot_file_path_name:    RF文件名
        :param settings_template_file_path_name:  设置内容信息模板
        :return: NONE
        """
        if os.path.exists(robot_file_path_name):
            """
            shutil.copy(
                robot_file_path_name,
                "%s.%s.bak" %
                (robot_file_path_name,
                 time.strftime(
                     '%Y%m%d%H%M%S',
                     time.localtime(
                         time.time()))))
            """
            os.remove(robot_file_path_name)

        with open(settings_template_file_path_name, 'r', encoding="utf-8") as f:
            rs = f.read()

        with open(robot_file_path_name, 'a', encoding="utf-8") as f:
            f.write('*** Settings ***' + '\n')
            f.write(rs + '\n')
            f.write('\n')
            f.write('*** Keywords ***' + '\n')
            f.close()

    def generate_rf_kw_from_postman(
            self, postman_file_path_name, kw_template_file_path_name,
            settings_template_file_path_name, robot_file_path, kw_pre=GENERATE_FILE_NAME_PRE):
        """
        说明：解析指定目录下postman测试用例导出文件，生成API底层封装关键字ROBOT文件
        :param postman_file_path_name: 需要解析的postman脚本导出文件地址
        :param kw_template_file_path_name:  关键字内容模板文件地址
        :param settings_template_file_path_name:  需要生成的关键字文件，设置信息模板文件地址
        :param robot_file_path:  RF文件生成目录
        :param kw_pre: RF文件名及关键字名称前缀设置，用于区别不同业务及模块
        :return:   生成RF文件名称
        """
        # 定义一个MAP，解决postman脚本http type与RF脚本之间的对应关系
        _http_type_map = {
            "GET": "Get Request",
            "POST": "Post Request",
            "Get": "Get Request",
            "Post": "Post Request"}

        # 读取postman测试用例导出文件，获取脚本文件基本信息
        info_dict = self.xl_json.get_json_file_value(
            postman_file_path_name, "info")

        # 从postman测试用例导出文件中提取name值，做为RF关键字文件名的一部分
        _robot_file_name = "%s/%s_%s_kwRequests.robot" % (
            robot_file_path, kw_pre, info_dict[0]["name"])
        # 初始化RF关键字文件
        self.__init_kw_robot_file(
            _robot_file_name,
            settings_template_file_path_name)

        # 读取postman测试用例导出文件，获取接口信息数据集合
        items_list = self.xl_json.get_json_file_value(
            postman_file_path_name, "item")
        # 设置关键字临时文件，用于替换组装每个关键字
        temp_file_name = "%s.temp" % kw_template_file_path_name
        # 替换临关键字中内容
        for item_dict in items_list[0]:
            # 如果临时关键字文件已存在，则删除掉
            if os.path.exists(temp_file_name):
                os.remove(temp_file_name)
            # 重新拷贝一份临时关键字文件
            shutil.copy(
                kw_template_file_path_name, temp_file_name)
            # 替换#API_NAME#内容，如不指定前缀则默认前缀为 GENERATE_FILE_NAME_PRE
            self.replace_robot_template_value(
                temp_file_name, "#API_NAME#", "%s_%s" %
                (kw_pre, item_dict["name"]))
            # 替换#Documentation#内容
            self.replace_robot_template_value(
                temp_file_name, "#Documentation#", item_dict["request"]["description"])
            # 替换#headers#内容
            headers_list = item_dict["request"]["header"]
            _sep = "    "
            headers_str = self.__generate_str_headers(headers_list, _sep)
            self.replace_robot_template_value(
                temp_file_name, "#headers#", headers_str)
            # 替换#url#内容
            _url_str = ""
            url_list = item_dict["request"]["url"]["path"]
            if "GET" == item_dict["request"]["method"]:
                _url_str = "/%s?" % "/".join(url_list)
                self.replace_robot_template_value(
                    temp_file_name,
                    "#url#",
                    "%s${data}" %
                    _url_str)
            elif "POST" == item_dict["request"]["method"]:
                _url_str = "/%s" % "/".join(url_list)
                self.replace_robot_template_value(
                    temp_file_name,
                    "#url#",
                    "%s    data=${data}" %
                    _url_str)

            # 处理在url和headers中带有的变量参数，将这些变量参数替换到#args#
            url_str = "/%s?" % "/".join(url_list)
            header_keys = re.findall(
                r'\${(.+?)}', headers_str)  # 取出header中需要输入的变量
            url_keys = re.findall(r'\${(.+?)}', url_str)  # 取出URL中需要输入的变量
            i_args = ""
            # 收集headers中的变量
            if len(header_keys):
                for key in header_keys:
                    i_args = i_args + '    ${' + key + '}'
            # 收集url中的变量
            if len(url_keys):
                for key in url_keys:
                    i_args = i_args + '    ${' + key + '}'
            # 替换#args#内容
            self.replace_robot_template_value(temp_file_name, "#args#", i_args)

            # 替换#httpType#内容
            self.replace_robot_template_value(
                temp_file_name, "#httpType#", _http_type_map[item_dict["request"]["method"]])

            # 读取临时文件内容
            with open(temp_file_name, 'r', encoding="utf-8") as f:
                rk = f.read()
            # 将临时文件内容写入API底层封装关键字ROBOT文件
            with open(_robot_file_name, 'a', encoding="utf-8") as f:
                f.write(rk + '\n')
                f.write('\n')
                f.close()

        return _robot_file_name

    def __init_testcase_robot_file(
            self, robot_file_path_name, settings_template_file_path_name,
            variables_template_file_path_name, postman_item_name):
        """
        初始化创建RF脚关键字脚本文件，如果文件存在则备份此文件后，删除掉原文件重新创建
        :param robot_file_path_name:    RF文件名
        :param settings_template_file_path_name:  设置内容信息模板
        :param variables_template_file_path_name: 变量内容信息模板
        :param postman_item_name: postman导出脚本名称，用于生成RF关键字文件名称
        :return: NONE
        """
        if os.path.exists(robot_file_path_name):
            """
            shutil.copy(
                robot_file_path_name,
                "%s.%s.bak" %
                (robot_file_path_name,
                 time.strftime(
                     '%Y%m%d%H%M%S',
                     time.localtime(
                         time.time()))))
            """
            os.remove(robot_file_path_name)

        with open(settings_template_file_path_name, 'r', encoding="utf-8") as f:
            rs = f.read()
            f.close()

        with open(variables_template_file_path_name, 'r', encoding="utf-8") as f:
            rv = f.read()
            f.close()

        _rf_kw_file_name = "%s_%s_kwRequests.robot" % (GENERATE_FILE_NAME_PRE, postman_item_name)

        with open(robot_file_path_name, 'a', encoding="utf-8") as f:
            f.write('*** Settings ***' + '\n')
            f.write(rs + '\n')
            f.write("Resource          " + _rf_kw_file_name + '\n')
            f.write('\n')
            f.write('*** Variables ***' + '\n')
            f.write(rv + '\n')
            f.write('\n')
            f.write('*** Test Cases ***' + '\n')
            f.close()

    def generate_rf_case_from_postman(
            self, postman_file_path_name, testcase_template_file_path_name, settings_template_file_path_name,
            variables_template_file_path_name, robot_file_path, kw_pre=GENERATE_FILE_NAME_PRE):
        """
        说明：解析指定目录下postman测试用例导出文件，生成RF测试用例文件，用于验证自动生成的RF关键字
        :param postman_file_path_name: 需要解析的postman脚本导出文件地址
        :param testcase_template_file_path_name:  测试用例内容模板文件地址
        :param settings_template_file_path_name:  设置内容模板文件地址
        :param variables_template_file_path_name: 变量内容模板文件地址
        :param robot_file_path:  RF文件生成目录
        :param kw_pre: RF文件名及测试用例名称前缀设置，用于区别不同业务及模块
        :return:   返回生成测试用例RF脚本文件名称
        """
        # 读取postman测试用例导出文件，获取脚本文件基本信息
        info_dict = self.xl_json.get_json_file_value(
            postman_file_path_name, "info")

        # 从postman测试用例导出文件中提取name值，做为RF测试用例文件名的一部分
        _robot_file_name = "%s/%s_%s_InterfaceTestCaseDemo.robot" % (
            robot_file_path, kw_pre, info_dict[0]["name"])
        # 初始化RF测试用例文件
        self.__init_testcase_robot_file(
            _robot_file_name,
            settings_template_file_path_name,
            variables_template_file_path_name,
            info_dict[0]["name"])

        # 读取postman测试用例导出文件，获取接口信息数据集合
        items_list = self.xl_json.get_json_file_value(
            postman_file_path_name, "item")
        # 设置关键字临时文件，用于替换组装每个关键字
        temp_file_name = "%s.temp" % testcase_template_file_path_name
        # 替换临关键字中内容
        for item_dict in items_list[0]:
            # 如果临时关键字文件已存在，则删除掉
            if os.path.exists(temp_file_name):
                os.remove(temp_file_name)
            # 重新拷贝一份临时关键字文件
            shutil.copy(
                testcase_template_file_path_name, temp_file_name)
            # 替换#CASE_NAME#内容，如不指定前缀则默认前缀为"XL"
            self.replace_robot_template_value(
                temp_file_name, "#CASE_NAME#", "%s_%s" %
                (kw_pre, item_dict["name"]))

            # 替换#TAGS#内容，postman脚本中无对应项，设置为def_tag
            self.replace_robot_template_value(
                temp_file_name, "#TAGS#", "def_tag")

            # 替换#CASE_DATA#内容
            _case_data = self.__generate_str_request_data(item_dict["request"])
            self.replace_robot_template_value(
                temp_file_name, "#CASE_DATA#", _case_data)

            # 替换#EXP_CODE#内容
            if "event" in item_dict.keys():
                _exp_code, _exp_contain = self.__generate_str_case_expect(
                    item_dict["event"][0])
            else:
                _exp_code, _exp_contain = "200", ""
            self.replace_robot_template_value(
                temp_file_name, "#EXP_CODE#", _exp_code)

            # 替换#EXP_CONTAIN#内容
            self.replace_robot_template_value(
                temp_file_name, "#EXP_CONTAIN#", _exp_contain)

            # 替换#API_KW#内容，如不指定前缀则默认前缀为"XL"
            self.replace_robot_template_value(
                temp_file_name, "#API_KW#", "%s_%s" %
                (kw_pre, item_dict["name"]))

            # 读取临时文件内容
            with open(temp_file_name, 'r', encoding="utf-8") as f:
                rk = f.read()
            # 将临时文件内容写入API底层封装关键字ROBOT文件
            with open(_robot_file_name, 'a', encoding="utf-8") as f:
                f.write(rk + '\n')
                f.write('\n')
                f.close()
        return _robot_file_name

    def __generate_str_headers(self, headers_list, header_sep_str):
        """
        将postman导出文件中的Headers列表转换成RFKW文件需要用的Headers字符串
        :param headers_list: postman导出文件中的Headers列表变量
        :param header_sep_str: 转换后每个K,V之间的分隔符
        :return: RFKW文件需要用的Headers字符串
        """
        str_headers = ""
        for header_kv_dict in headers_list:
            str_headers = "%s=%s%s" % (
                header_kv_dict["key"], header_kv_dict["value"], header_sep_str) + str_headers
        return str_headers

    def __generate_str_request_data(self, postman_request_dict):
        """解析postman脚本，返回RF测试用例脚本需要的接口调用输入参数"""
        ret_request_data_str = ""
        if "GET" == postman_request_dict["method"]:
            ret_request_data_str = \
                postman_request_dict["url"]["raw"].split("?")[1]
        elif "POST" == postman_request_dict["method"]:
            req_list = postman_request_dict["body"][postman_request_dict["body"]["mode"]]
            _req_str = ""
            if "urlencoded" == postman_request_dict["body"]["mode"]:
                # 使用解析postman脚本header字段的方法，来解析请求消息体字段列表，将分隔符设置为"&"
                _req_str = self.__generate_str_headers(req_list, "&")
                # 去掉未尾的分隔符
                ret_request_data_str = _req_str[:-1]
            elif "raw" == postman_request_dict["body"]["mode"]:
                # 此时"req_list"类型为字符串
                if "str" == type(req_list).__name__:
                    _req_str = req_list
                    _req_str = _req_str.replace("\r\n  ", "")
                    ret_request_data_str = _req_str.replace("\r\n", "")
                else:
                    self.xl_logger.debug(
                        "req_list type is :%s" %
                        type(req_list).__name__)

        self.xl_logger.debug("return is :%s" % ret_request_data_str)
        return ret_request_data_str

    def __generate_str_case_expect(self, postman_event_dict):
        """解析postman脚本，返回RF测试用例需要的两个期望值参数"""
        _response_code = ""
        _response_body_has = ""
        for exec in postman_event_dict["script"]["exec"]:
            if "RF Should Be Equal As Strings" == re.findall(
                    r'\[\"(.+?)\"\]', exec)[0]:
                _response_code = re.findall(r'=== (.+?);', exec)
            elif "RF Should Contain" == re.findall(r'\[\"(.+?)\"\]', exec)[0]:
                _response_body_has = re.findall(r'\(\"(.+?)\"\)', exec)

        return str(_response_code[0]), str(_response_body_has[0])

    def replace_robot_template_value(self, robot_path_name, old_str, new_str):
        """使用new_str替换模板中old_str字符串"""
        w_str = ""
        with open(robot_path_name, 'r', encoding="utf-8") as robot_f:
            for line in robot_f:
                if re.search(old_str, line):
                    line = re.sub(old_str, new_str, line)
                    w_str += line
                else:
                    w_str += line
        self.xl_logger.debug(w_str)
        with open(robot_path_name, 'w', encoding="utf-8") as robot_f_w:
            robot_f_w.write(w_str)
        robot_f.close()
        robot_f_w.close()

    def generate_rfkw_from_json(
            self, json_file_dir, template_file_path_name, robot_file_path_name, kw_pre=GENERATE_FILE_NAME_PRE):
        """解析指定目录下JSON文件，生成API底层封装关键字ROBOT文件"""
        # 定义一个MAP，解决Json文件中http type与RF脚本之间的对应关系
        _http_type_map = {
            "GET": "Get Request",
            "POST": "Post Request",
            "Get": "Get Request",
            "Post": "Post Request"}
        # 调用setData模块InitJsonFile类get_api_name()函数，获取指定目录下所有JSON接口定义文件名称
        cfns = self.xl_ijf.get_api_name(json_file_dir, "json")
        # 设置关键字临时文件，用于替换组装每个关键字
        temp_file_name = "%s.temp" % template_file_path_name
        # 替换临关键字中内容
        for fn in cfns:
            # 如果临时关键字文件已存在，则删除掉
            if os.path.exists(temp_file_name):
                os.remove(temp_file_name)
            # 重新拷贝一份临时关键字文件
            shutil.copy(
                template_file_path_name, temp_file_name)
            # 替换#API_NAME#内容，如不指定前缀则默认前缀为"XL"
            self.replace_robot_template_value(
                temp_file_name, "#API_NAME#", "%s_%s" %
                (kw_pre, fn))
            # 替换#Documentation#内容
            j_doc = self.xl_json.get_json_file_value(
                "%s/%s.json" %
                (json_file_dir, fn), "Documentation")
            self.replace_robot_template_value(
                temp_file_name, "#Documentation#", "\n".join(j_doc[0]))
            # 替换#headers#内容
            j_headers = self.xl_json.get_json_file_value(
                "%s/%s.json" % (json_file_dir, fn), "headers")
            self.replace_robot_template_value(
                temp_file_name, "#headers#", j_headers[0])
            # 替换#url#内容
            j_url = self.xl_json.get_json_file_value(
                "%s/%s.json" % (json_file_dir, fn), "url")
            self.replace_robot_template_value(
                temp_file_name, "#url#", j_url[0])

            # 处理在url和headers中带有的变量参数，将这些变量参数替换到#args#
            header_keys = re.findall(
                r'\${(.+?)}', j_headers[0])  # 取出header中需要输入的变量
            url_keys = re.findall(r'\${(.+?)}', j_url[0])  # 取出URL中需要输入的变量
            i_args = ""
            # 收集headers中的变量
            if len(header_keys):
                for key in header_keys:
                    i_args = i_args + '    ${' + key + '}'
            # 收集url中的变量
            if len(url_keys):
                for key in url_keys:
                    i_args = i_args + '    ${' + key + '}'
            # 替换#args#内容
            self.replace_robot_template_value(temp_file_name, "#args#", i_args)

            # 替换#httpType#内容
            j_type = self.xl_json.get_json_file_value(
                "%s/%s.json" % (json_file_dir, fn), "httpType")
            self.replace_robot_template_value(
                temp_file_name, "#httpType#", _http_type_map[j_type[0]])

            # 读取临时文件内容
            with open(temp_file_name, 'r', encoding="utf-8") as f:
                rk = f.read()
            # 将临时文件内容写入API底层封装关键字ROBOT文件
            with open(robot_file_path_name, 'a', encoding="utf-8") as f:
                f.write(rk + '\n')
                f.write('\n')
                f.close()


if __name__ == '__main__':
    print("OK")
    # 将postman导出的json文件转换成RF关键字
    pcj = "C:\\Users\\xl\\Documents\\http_server_tools\\http_server_tools\\tmp\\PostmanToRFDemo.postman_collection.json"
    rfp = "C:\\Users\\xl\\Documents\\http_server_tools\\http_server_tools\\tmp"
    tfdn_kw = "C:\\Users\\xl\\Documents\\http_server_tools\\http_server_tools\\generate\\generate_template\\rf_template_kw.txt"
    tfdn_settings = "C:\\Users\\xl\\Documents\\http_server_tools\\http_server_tools\\generate\\generate_template\\rf_template_kw_settings.txt"
    grf = GenerateRF()
    grf.generate_rf_kw_from_postman(pcj, tfdn_kw, tfdn_settings, rfp)
    """
    # 将postman导出的json文件转换成与导出RF关键字对应的RF测试用例
    pcj = "./postman_script/PostmanToRFDemo.postman_collection.json"
    rfp = "./rf_script/"
    tfdn_case = "./rf_script/template_testcase.txt"
    tfdn_var = "./rf_script/template_testcase_variables.txt"
    tfdn_settings = "./rf_script/template_testcase_settings.txt"
    grf = GenerateRF()
    grf.generate_rf_case_from_postman(
        pcj, tfdn_case, tfdn_settings, tfdn_var, rfp)
    """

