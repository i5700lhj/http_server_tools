#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @CreateDate   : 2019-07-22
# @Author      : jet
# @Filename : xls_cfg.py
# @Software : pycharm

import xlrd
from xlrd import open_workbook, cellname, xldate_as_tuple, \
    XL_CELL_NUMBER, XL_CELL_DATE, XL_CELL_TEXT, XL_CELL_BOOLEAN, \
    XL_CELL_ERROR, XL_CELL_BLANK, XL_CELL_EMPTY, error_text_from_code


class XlsConfig(object):
    def __init__(self):
        self.wb = None
        self.tb = None
        self.sheetNum = None
        self.sheetNames = None
        self.fileName = None

    def open_xls(self, filename):
        """打开一个XLS"""
        try:
            self.wb = xlrd.open_workbook(filename, encoding_override='utf-8')
        except Exception as e:
            print(e)
        self.fileName = filename
        self.sheetNames = self.wb.sheet_names()

    def read_cell_data_by_name(self, sheetname, cell_name):
        """读取指定单元格内容"""
        my_sheet_index = self.sheetNames.index(sheetname)
        sheet = self.wb.sheet_by_index(my_sheet_index)
        for row_index in range(sheet.nrows):
            for col_index in range(sheet.ncols):
                cell = cellname(row_index, col_index)
                if cell_name == cell:
                    cellValue = sheet.cell(row_index, col_index).value
        return cellValue
