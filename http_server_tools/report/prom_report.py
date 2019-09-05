# -*- coding: utf-8 -*-
"""
!/usr/bin/python3
@CreateDate   : 2019-09-04
@Author      : jet
@Filename : prom_report.py
@Software : pycharm

Create an application instance.
"""

import os
import time
import shutil
import json
import requests

from example.commons import Faker
from pyecharts import options as opts
from pyecharts.charts import Bar, Tab, Pie, Line
from pyecharts.components import Table


PROMETHEUS_URL = "47.107.12.216:9090"
K8S_POD_NAME = "gateway-pay-release-858b784fc-rpq89"
QUERY_METRIC_NAME = "process_cpu_seconds_total"
QUERY_METRIC_NAMES = [
    "process_cpu_seconds_total",
    "process_start_time_seconds",
    "scrape_duration_seconds"]
QUERY_PERIOD = "3m"

BASE_DIR = str(os.path.dirname(os.path.dirname(__file__)))
BASE_DIR = BASE_DIR.replace('\\', '/')

REPORT_FILES_FOLDER = BASE_DIR + "/report/report_files/"
BACKUP_FOLDER = BASE_DIR + "/report/report_files/backup"


class PerformanceData:
    def __init__(self):
        pass

    def query_metric(self, url):
        """
        通过PROMETHEUS提供的HTTP接口获取METRIC数据
        :param url:
        :return: 字符串
        """
        res = requests.get(url)
        return res.text

    def dump_to_json_file(self, file_name, data):
        """
        将测试数据保存至json文件
        :param file_name: 文件名
        :param data: 字符串
        :return: NONE
        """
        with open("%s_%s.json" % (file_name, time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))), 'w') as f:
            json.dump(eval(data), f)

    def dump_to_xy(self, data):
        """
        解析单个性能指标
        :param data: 单个指标字符串数据
        :return: x[],y[]
        """
        x = []
        y = []
        _dic = eval(data)

        for value in _dic["data"]["result"][0]["values"]:
            ltime = time.localtime(value[0])
            otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", ltime)
            x.append(otherStyleTime)
            y.append(str(value[1]))
        return x, y

    def dump_to_xys(self, data_all, metric_names):
        _x = []
        _y = []
        xs = []
        ys = []
        metric_name = []
        _dic = eval(data_all)
        for result in _dic["data"]["result"]:
            # print(result)
            for _name in metric_names:
                if _name == result["metric"]["__name__"]:
                    metric_name.append(_name)
                    # print(result)
                    for _value in result["values"]:
                        # print(_value)
                        ltime = time.localtime(_value[0])
                        otherStyleTime = time.strftime(
                            "%Y-%m-%d %H:%M:%S", ltime)
                        _x.append(otherStyleTime)
                        _y.append(str(_value[1]))
                    xs.append(_x)
                    ys.append(_y)
        print(xs, ys)
        print(metric_name)
        return xs, ys, metric_name


class PerformanceReport:
    def __init__(self):
        pass

    def bar_datazoom_slider(self) -> Bar:
        c = (
            Bar()
            .add_xaxis(Faker.days_attrs)
            .add_yaxis("商家A", Faker.days_values)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Bar-DataZoom（slider-水平）"),
                datazoom_opts=[opts.DataZoomOpts()],
            )
        )
        return c

    def single_line_markpoint(self, x_timestamp, y_datas) -> Line:
        c = (
            Line()
            .add_xaxis(x_timestamp)
            .add_yaxis(
                "",  # "商家A", 此处设置折线图的名称，单个指标折线图不需要设置
                y_datas,
                # areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                markpoint_opts=opts.MarkPointOpts(
                    symbol_size=[100, 60],
                    data=[opts.MarkPointItem(type_="min")]),
            )
            .set_global_opts(
                # xaxis_opts=opts.AxisOpts(split_number=20),
                title_opts=opts.TitleOpts(title=""))  # 此处设置Y轴名称
        )
        return c

    def pie_rosetype(self) -> Pie:
        v = Faker.choose()
        c = (
            Pie()
            .add(
                "",
                [list(z) for z in zip(v, Faker.values())],
                radius=["30%", "75%"],
                center=["25%", "50%"],
                rosetype="radius",
                label_opts=opts.LabelOpts(is_show=False),
            )
            .add(
                "",
                [list(z) for z in zip(v, Faker.values())],
                radius=["30%", "75%"],
                center=["75%", "50%"],
                rosetype="area",
            )
            .set_global_opts(title_opts=opts.TitleOpts(title="Pie-玫瑰图示例"))
        )
        return c

    def table_base(self) -> Table:
        table = Table()

        headers = ["City name", "Area", "Population", "Annual Rainfall"]
        rows = [
            ["Brisbane", 5905, 1857594, 1146.4],
            ["Adelaide", 1295, 1158259, 600.5],
            ["Darwin", 112, 120900, 1714.7],
            ["Hobart", 1357, 205556, 619.5],
            ["Sydney", 2058, 4336374, 1214.8],
            ["Melbourne", 1566, 3806092, 646.9],
            ["Perth", 5386, 1554769, 869.4],
        ]
        table.add(headers, rows).set_global_opts(
            title_opts=opts.ComponentTitleOpts(title="Table")
        )
        return table

    def gen_single_report(self, url, single_file_name):
        """
        生成单个性能指标的html报表
        :param url:
        :param single_file_name:
        :return: 成功："OK"
                 失败：直接把返回值以字符串形式返回
        """
        # 获取指标数据
        _res = PerformanceData().query_metric(url)
        # 获取失败则直接把返回值以字符串形式返回
        _dic_res = eval(_res)
        if "success" != _dic_res["status"]:
            return _res
        elif 0 == len(_dic_res["data"]["result"]):
            return _res
        # 存储为JSON文件
        # PerformanceData().dump_to_json_file(QUERY_METRIC_NAME, _res)
        # 解析指标数据
        _single_x, _single_y = PerformanceData().dump_to_xy(_res)
        # 生成HTML格式图表
        _tab = Tab()
        _tab.add(
            self.single_line_markpoint(
                _single_x,
                _single_y),
            single_file_name)
        _report_file_path_name = "%s%s.html" % (
            REPORT_FILES_FOLDER, single_file_name)
        # 生成HTML格式报表
        _tab.render(_report_file_path_name)
        # 备份至BACKUP目录
        shutil.copy(
            _report_file_path_name,
            "%s/%s_%s.html" %
            (BACKUP_FOLDER,
             single_file_name,
             time.strftime(
                 '%Y%m%d%H%M%S',
                 time.localtime(
                     time.time()))))
        return "OK"


if __name__ == '__main__':
    # query_url_demo
    url_query_pod_process_cpu_seconds_total_5m = "http://%s/api/v1/query?query=process_cpu_seconds_total[5m]" % PROMETHEUS_URL
    # 获取单个指标数据
    query_url = "http://%s/api/v1/query?query=%s[%s]" % (
        PROMETHEUS_URL, QUERY_METRIC_NAME, QUERY_PERIOD)
    PerformanceReport().gen_single_report(query_url, QUERY_METRIC_NAME)
    """

    res = PerformanceData().query_metric(query_url)
    # 获取一个POD下所有指标数据
    url_quer_pod_all = "http://%s/api/v1/query?query={kubernetes_pod_name=\"%s\"}[%s]" % (
        PROMETHEUS_URL, K8S_POD_NAME, QUERY_PERIOD)
    res_all = PerformanceData().query_metric(url_quer_pod_all)

    # 存储为JSON文件
    # PerformanceData().dump_to_json_file(QUERY_METRIC_NAME, res)
    # PerformanceData().dump_to_json_file(K8S_POD_NAME, res_all)

    # 转换单个指标数据
    x, y = PerformanceData().dump_to_xy(res)
    # 转换多个指标数据
    xs, ys, metric_name = PerformanceData().dump_to_xys(res_all, QUERY_METRIC_NAMES)

    # 生成HTML格式图表
    tab = Tab()
    # 柱状图
    # tab.add(PerformanceReport().bar_datazoom_slider(), "bar-report")
    # 显示一个折线图
    tab.add(PerformanceReport().line_markpoint(x, y), "line-report")

    # 玫瑰图
    # tab.add(PerformanceReport().pie_rosetype(), "pie-report")
    # 表格
    # tab.add(PerformanceReport().table_base(), "table-report")
    tab.render()

    # 动态生成多个折线图

    tabs = Tab()
    m_name = ""
    for x in xs, y in ys, m_name in metric_name:
        tabs.add(PerformanceReport().line_markpoint(x, y), m_name)
        tabs.render("aaa.html")
"""
