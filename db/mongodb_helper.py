#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: mongodb_helper.py

"""
Created on 2017/6/15 0015

@author: bigsea
"""
import configparser
from pymongo import MongoClient
from pymongo.pool import Pool

"""
MongoDB 数据库连接池

class MongoDBHelper:

    __dbType = 'mongodb'        # 数据库类型
    __ip = None                 # 数据库ip连接地址
    __port = None               # 数据库端口
    __dbName = None             # 数据库名称
    __collectionName = None     # 数据库表名
    __poolSize = None           # 连接数据
    __blockSize = None          # 等待队列
    __conf = None               # 配置文件信息
    __confValue = []

    def __init__(self):
        # 读取配置文件 同目录下db.conf
        self.__conf = configparser.ConfigParser()
        self.__conf.read("db.conf")

    # 初始化数据库连接参数信息
    def init_params(self):
        keys = self.__conf.options(self.__dbType)
        for key in keys:
            value = self.__conf.get(self.__dbType, key)
            self.__confValue.append(value)
        self.__ip = self.__confValue[0]
        self.__port = self.__confValue[1]
        self.__dbName = self.__confValue[2]
        self.__collectionName = self.__confValue[3]
        self.__poolSize = self.__confValue[4]
        self.__blockSize = self.__confValue[5]

    # 获取连接
    @staticmethod
    def get_conn():
        pass
"""

