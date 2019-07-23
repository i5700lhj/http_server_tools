"""
!/usr/bin/python3
@CreateDate   : 2019-07-22
@Author      : jet
@Filename : set_data.py
@Software : pycharm
"""

import os
import sys
import re
import shutil
from http_server_tools.utils import Logger
from http_server_tools.generate.mongodb import MongodbClient
from http_server_tools.generate.xls_cfg import XlsConfig
from http_server_tools.generate.json_cfg import JsonConfig

sys.path.append('./db_config')
sys.path.append('./xls_config')
sys.path.append('./json_config')

logger = Logger()


class InitJsonFile(object):
    def __init__(self):
        self.xls = XlsConfig()
        self.xl_logger = logger.get_logger(
            "%s %s" %
            (__name__, self.__class__.__name__))

    def find_file_name(self, file_dir):
        """从指定目录读取所有文件名称"""
        for root, dirs, files in os.walk(file_dir):
            self.xl_logger.debug("CUR Folder path : %s" % root)
            self.xl_logger.debug("CUR Folder SUB path : %s" % dirs)
            self.xl_logger.debug("CUR Folder file names : %s" % files)
            self.xl_logger.debug("CUR Folder files count  : %d" % len(files))
            files.sort()
        return files

    def get_api_name(self, file_path, file_type="xls"):
        """批量获取EXCEL文件名，去掉扩展名，返回列表"""
        # 批量获取文件名
        lisfns = self.find_file_name(file_path)

        # 去掉扩展名，生成接口名
        lisApiNames = []
        for fn in lisfns:
            lisApiNames.append(fn[:-(len(file_type) + 1)])

        # 接口名列表排序，忽略大小写
        lisApiNames.sort(key=str.lower)
        self.xl_logger.debug("File names list len : %d" % len(lisApiNames))
        self.xl_logger.debug("File names list : %s" % lisApiNames)
        return lisApiNames

    def generate_json_template(self, template_file, target_path, file_names):
        """复制json模板文件"""
        for fn in file_names:
            shutil.copy(template_file, "%s/%s.json" % (target_path, fn))

    def replace_json_template_value(self, json_path_name, old_str, new_str):
        """使用new_str替换模板中old_str字符串"""
        w_str = ""
        with open(json_path_name, 'r') as json_f:
            for line in json_f:
                if re.search(old_str, line):
                    line = re.sub(old_str, new_str, line)
                    w_str += line
                else:
                    w_str += line
        self.xl_logger.debug(w_str)
        with open(json_path_name, 'w') as json_f_w:
            json_f_w.write(w_str)
        json_f.close()
        json_f_w.close()

    def batch_set_api_data(self, xls_file_path, json_file_path):
        """批量获取EXCEL文件中API接口参数，写入对应的json文件中对应的字段中"""
        # 批量获取文件名
        lisfns = self.find_file_name(xls_file_path)
        for fn in lisfns:
            self.xl_logger.debug(
                "==============================%s==============================" %
                fn)
            self.xls.open_xls("%s/%s" % (xls_file_path, fn))
            # 替换模板中Parameter字段内容
            Parameter = self.xls.read_cell_data_by_name("Case01", "B2")
            # 处理两种参数格式，使生成的文件内容符合JSON格式
            if "{" != Parameter[0]:
                Parameter = "\"%s\"" % Parameter
            self.replace_json_template_value(
                "%s/%s.json" %
                (json_file_path, fn[:-4]), "#Parameter#", Parameter)
            # 替换模板中httpType字段内容
            httpType = self.xls.read_cell_data_by_name("Case01", "G2")
            self.replace_json_template_value(
                "%s/%s.json" %
                (json_file_path, fn[:-4]), "#httpType#", httpType.upper())
            # 替换模板中url字段内容
            url = self.xls.read_cell_data_by_name("Case01", "H2")
            self.replace_json_template_value(
                "%s/%s.json" %
                (json_file_path, fn[:-4]), "#url#", url)
            # 替换模板中headers字段内容
            headers = self.xls.read_cell_data_by_name("Case01", "K2")
            self.replace_json_template_value(
                "%s/%s.json" %
                (json_file_path, fn[:-4]), "#headers#", headers)
            # 替换模板中content字段内容
            content = self.xls.read_cell_data_by_name("Case01", "F2")
            # 处理两种参数格式，使生成的文件内容符合JSON格式
            if "{" != content[0]:
                content = "\"%s\"" % content
            self.replace_json_template_value(
                "%s/%s.json" %
                (json_file_path, fn[:-4]), "#content#", content)
            # 替换模板中Documentation字段内容
            td = self.xls.read_cell_data_by_name("Case01", "J2")
            # 将Documentation字段内容按行存储在一个列表中
            Documentation = ""
            tld = td.split("\n")
            for i in range(len(tld)):
                Documentation = Documentation + "\"%s\"," % tld[i]
            self.replace_json_template_value(
                "%s/%s.json" %
                (json_file_path, fn[:-4]), "#Documentation#", Documentation[:-1])

    def xls_to_json(self, xls_file_path, json_file_path,
                    json_template_path_name):
        """将excel接口API定义文件转换为json文件格式，方便后续写入db"""
        # 根据模板文件和原有的EXCEL文件，生成初始JSON数据文档
        cfns = self.get_api_name(xls_file_path)
        self.generate_json_template(
            json_template_path_name, json_file_path, cfns)

        # 批量获取EXCEL文件中API接口参数，写入对应的json文件中对应的字段中
        self.batch_set_api_data(xls_file_path, json_file_path)

    def xls_to_json_xl_account(self):
        fxls = "./xls_config/XL_Account_TestCase"
        fjson = "./json_config/XL_Account_TestCase"
        fjtemplate = "./json_config/apiGenerateTemplate.json"
        self.xls_to_json(fxls, fjson, fjtemplate)

    def xls_to_json_xl_account_temp(self):
        fxls = "./xls_config/XL_Account_TestCase_temp"
        fjson = "./json_config/XL_Account_TestCase_temp"
        fjtemplate = "./json_config/apiGenerateTemplate.json"
        self.xls_to_json(fxls, fjson, fjtemplate)


class JsonToMongodb(object):
    def __init__(self):
        self.mongodb = MongodbClient()
        self.jsonCfg = JsonConfig()
        self.ijf = InitJsonFile()

    def init_mongodb(self, db_name, xls_file_path, json_template_file):
        """获取EXCEL模板文件信息，在mongodb中创建初始API数据库及接口数据集合"""
        cfns = self.ijf.get_api_name(xls_file_path)
        ads = self.jsonCfg.load_json_to_dict(json_template_file)
        self.mongodb.batch_collection_insert(db_name, cfns, ads)

    def batch_load_json_to_mongodb(self, db_name, json_file_path):
        """获取本地json文件信息，在mongodb中插入API数据
        （如初始数据库及集合已存在，则插入数据；否则会新建数据库、集合，然后插入API数据）"""
        cfns = self.ijf.get_api_name(json_file_path, "json")
        for cn in cfns:
            self.xl_logger.debug("%s/%s.json" % (json_file_path, cn))
            cd = self.jsonCfg.load_json_to_dict(
                "%s/%s.json" % (json_file_path, cn))
            self.xl_logger.debug(cd)
            self.mongodb.collection_insert_many(db_name, cn, cd)

    def json_to_mongodb_xl_account(self):
        dbn = "xl_account_db"
        jfp = "./json_config/XL_Account_TestCase"
        self.batch_load_json_to_mongodb(dbn, jfp)

    def json_to_mongodb_xl_account_temp(self):
        dbn = "xl_account_db"
        jfp = "./json_config/XL_Account_TestCase_temp"
        self.batch_load_json_to_mongodb(dbn, jfp)


if __name__ == '__main__':
    ### 根据模板文件和原有的EXCEL文件，生成初始JSON数据文档 ###
    # InitJsonFile().xls_to_json_xl_account()
    ### 在mongodb中创建初始接口数据集合 ###
    # JsonToMongodb().json_to_mongodb_xl_account()

    """将./xls_config/XL_Account_TestCase_temp目录下新增的账号接口EXCEL信息补充入库，执行成功后
    ---手动---
    将 ./xls_config/XL_Account_TestCase_temp目录下EXCEL文件移至./xls_config/XL_Account_TestCase目录
    将./json_config/XL_Account_TestCase_temp目录下JSON文件移至 ./json_config/XL_Account_TestCase目录
    ---归档---
    InitJsonFile().xls_to_json_xl_account_temp()
    ### 在mongodb中创建初始接口数据集合 ###
    JsonToMongodb().json_to_mongodb_xl_account_temp()
    """

    """
    # 通过key/value获取一个集合数据
    mo = MongodbOpt("xl_account_db")
    rd = mo.get_one_data("BindMailv2Get", "caseName", "Demo")
    self.xl_logger.debug(rd)
    self.xl_logger.debug(type(rd))
    """

    """
    # 通过指定集合的caseName获取接口数据
    mo = MongodbOpt("xl_account_db")
    rd = mo.get_case_data("BindMailv2Get", "Demo")
    self.xl_logger.debug(rd)
    self.xl_logger.debug(type(rd))
    """

    """
    # 通过指定集合的caseName获取接口发送参数及接口返回期望值数据
    mo = MongodbOpt("xl_account_db")
    rdReq = mo.get_case_req("BindMailv2Get", "Demo")
    self.xl_logger.debug(rdReq)
    self.xl_logger.debug(type(rdReq))
    rdResp = mo.get_case_resp("BindMailv2Get", "Demo")
    self.xl_logger.debug(rdResp)
    self.xl_logger.debug(type(rdResp))
    """

    print("OK")


"""
    fj = "./json_config/XL_Account_TestCase/bindlinke.json"
    dfj = JsonConfig().load_json_to_dict(fj)
    self.xl_logger.debug(dfj)
"""
