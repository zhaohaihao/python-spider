#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: date_util.py

"""
Created on 2017/6/26 0026

@author: bigsea
"""
import time

class DateUtils:

    # 获取当前时间
    def getCurrentDate(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    # 获得当前毫秒数
    def getMillisecond(self):
        return time.time() * 1000