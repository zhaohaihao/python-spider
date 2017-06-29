#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: bank_dao.py

"""
Created on 2017/6/15 0015

@author: bigsea
"""

import json
from pymongo import MongoClient

"""
各银行数据操作
"""
class BankDao:

    __db = None
    __client = None
    __collection = None

    def __init__(self):
        # 建立MongoDB数据库连接
        self.__client = MongoClient('localhost', 27017)
        # 连接所需要数据库, local为数据库的名称
        self.__db = self.__client.local

    def save_date2db(self, data):
        """
        向Mongodb中插入数据
        :param data: 存储的数据
        :return: 
        """
        self.__collection = self.__db.bankATM
        self.__collection.insert(data)

    '''
    **************************************农业银行相关操作*******************************************
    '''
    def saveNYPCAInfo(self, url_list):
        '''
        存储农业银行请求url
        :param url_list: 
        :return: 
        '''
        self.__collection = self.__db.ny_prc_info
        self.__collection.insert(url_list)

    def getNYPCAInfo(self, prov_id=0, city_id=0, area_id=0):
        '''
        获取农业银行请求url
        :param prov_id: 省份id
        :param city_id: 城市id
        :param area_id: 区域id
        :return: 
        '''
        url_list = []
        self.__collection = self.__db.ny_prc_info
        if not prov_id and not city_id and not area_id:
            find_list = self.__collection.find()
        elif prov_id and city_id and area_id:
            find_list = self.__collection.find({'provinceId': str(prov_id), 'cityId': str(city_id), 'areaId': str(area_id)})
        elif prov_id and city_id:
            find_list = self.__collection.find({'provinceId': str(prov_id), 'cityId': str(city_id)})
        elif prov_id:
            find_list = self.__collection.find({'provinceId': str(prov_id)})
        for item in find_list:
            url_list.append(item)
        return url_list

    '''
    **************************************交通银行相关操作*******************************************
    '''
    def saveJTPCAInfo(self, prov_city_name_list):
        '''
        存储交通银行的省市地区信息
        :param prov_city_name_list: 省市地区列表
        :return: 
        '''
        self.__collection = self.__db.jt_prc_info
        self.__collection.insert(prov_city_name_list)

    def getJTPCAInfo(self, prov_id=0, city_id=0, area_id=0):
        '''
        获取交通银行的省市地区信息
        :param prov_id: 省份id
        :param city_id: 城市id
        :param area_id: 区域id
        :return: 
        '''
        prov_city_name_list = []
        self.__collection = self.__db.jt_prc_info
        if not prov_id and not city_id and not area_id:
            find_list = self.__collection.find()
        elif prov_id and city_id and area_id:
            find_list = self.__collection.find({'provinceId': prov_id, 'cityId': str(city_id), 'areaId': str(area_id)})
        elif prov_id and city_id:
            find_list = self.__collection.find({'provinceId': prov_id, 'cityId': str(city_id)})
        elif prov_id:
            find_list = self.__collection.find({'provinceId': prov_id})
        for item in find_list:
            prov_city_name_list.append(item)
        return prov_city_name_list

    '''
    **************************************建设银行相关操作*******************************************
    '''
    def saveJSPCAInfo(self, prov_city_name_list):
        '''
        存储建设银行的省市地区信息
        :param prov_city_name_list: 省市地区列表
        :return: 
        '''
        self.__collection = self.__db.js_prc_info
        self.__collection.insert(prov_city_name_list)

    def getJSPCAInfo(self, prov_id=0, city_id=0, area_id=0):
        '''
        获取建设银行的省市地区信息
        :param prov_id: 省份id
        :param city_id: 城市id
        :param area_id: 区域id
        :return: 
        '''
        prov_city_name_list = []
        self.__collection = self.__db.js_prc_info
        if not prov_id and not city_id and not area_id:
            find_list = self.__collection.find()
        elif prov_id and city_id and area_id:
            find_list = self.__collection.find({'provinceId': str(prov_id), 'cityId': str(city_id), 'areaId': str(area_id)})
        elif prov_id and city_id:
            find_list = self.__collection.find({'provinceId': str(prov_id), 'cityId': str(city_id)})
        elif prov_id:
            find_list = self.__collection.find({'provinceId': str(prov_id)})
        for item in find_list:
            prov_city_name_list.append(item)
        return prov_city_name_list

if __name__ == '__main__':
    for i in BankDao().getJTPCAInfo('BJ'):
        print(i)






