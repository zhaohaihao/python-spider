#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: js_service.py

"""
Created on 2017/6/22 0022

@author: bigsea
"""

import requests
import multiprocessing
from __init__ import *
from bank_entity import BankEntity
from bank_dao import BankDao
from file_util import FileUtils
from date_util import DateUtils
from list_util import ListUtils

"""
建设银行数据处理层
"""
class JSService:

    __bank_id = '3'
    __bank_type = '建设银行'
    __prov_url = 'http://www.ccb.com/tran/WCCMainPlatV5?CCB_IBSVersion=V5&SERVLET_NAME=WCCMainPlatV5&isAjaxRequest=true&TXCODE=NAREA1&type=1&areacode=110000&_=1498639619179'
    __city_url = 'http://www.ccb.com/tran/WCCMainPlatV5?CCB_IBSVersion=V5&SERVLET_NAME=WCCMainPlatV5&isAjaxRequest=true&TXCODE=NAREA1&type=2&areacode='
    __area_url = 'http://www.ccb.com/tran/WCCMainPlatV5?CCB_IBSVersion=V5&SERVLET_NAME=WCCMainPlatV5&isAjaxRequest=true&TXCODE=NAREA1&type=3'

    __base_url = 'http://www.ccb.com/tran/WCCMainPlatV5?CCB_IBSVersion=V5&SERVLET_NAME=WCCMainPlatV5&isAjaxRequest=true&TXCODE=NZX001'
    __headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_5_8) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.68 Safari/534.24'
    }

    def getAreaList(self):
        """
        获取具体地域的请求列表
        :param url: 请求的地址
        :param area_url: 请求地域的地址
        :param base_url: 请求的基本地址段
        :return: 
        """
        prov_city_name_list = BankDao().getJSPCAInfo()
        if len(prov_city_name_list):
            return prov_city_name_list
        print('获取所有请求信息列表, 请稍后...')
        response = requests.get(self.__prov_url, headers=self.__headers)
        response.encoding = 'utf-8'
        res_json = response.json()
        # print("res_json：", res_json)
        for item in res_json['arealist']:
            if not len(item):
                continue
            prov_name = item['NET_NAME']
            prov_code = item['areacode']
            city_res = requests.get(self.__city_url+prov_code, headers=self.__headers)
            city_json = city_res.json()
            for city in city_json['arealist']:
                if not len(city):
                    continue
                city_name = city['NET_NAME']
                city_code = city['areacode']
                area_url = self.__area_url + '&areacode=' + city_code
                res = requests.get(area_url, headers=self.__headers)
                res_area_json = res.json()
                for area in res_area_json['arealist']:
                    if not len(area):
                        continue
                    # print(area)
                    area_code = area['areacode']
                    area_name = area['NET_NAME']
                    area_url = self.__base_url + '&AREA_NAME=' + area_code + '&NET_KEYWORD=&NET_FLAG=4&CURRENT_PAGE='
                    prov_city_name = {
                        'provinceId': prov_code,
                        'province': prov_name,
                        'cityId': city_code,
                        'city': city_name,
                        'areaId': area_code,
                        'area': area_name,
                        'reqUrl': area_url
                    }
                    prov_city_name_list.append(prov_city_name)
        # 存储请求地址 防止频繁请求不变信息
        BankDao().saveJSPCAInfo(prov_city_name_list)
        print('请求信息存储完毕!')
        return prov_city_name_list

    def getReqData(self, pca_list, save_flag, page=1):
        '''
        请求数据
        :param pca_list: 请求数据的地址列表
        :param save_flag: 是否存储, 0:不存储, 1:存储
        :param page: 请求的当前页
        :return: 
        '''
        for req_info in pca_list:
            prov_name = req_info['province']
            prov_id = req_info['provinceId']
            city_name = req_info['city']
            city_id = req_info['cityId']
            area_name = req_info['area']
            area_code = req_info['areaId']
            url = req_info['reqUrl']
            new_url = url + str(page)
            # 存储每个请求页面获取的所有网点信息的列表
            obj_list = []
            file_name = None
            try:
                response = requests.get(new_url, headers=self.__headers)
                if response.status_code == 200:
                    response.encoding = 'utf-8'
                    res_json = response.json()
                    if len(res_json):
                        current_page = int(res_json['CURRENT_PAGE'])
                        total_page = int(res_json['TOTAL_PAGE'])
                        items = res_json['ARRAY_CMG001']
                        for item in items:
                            if not len(item):
                                continue
                            obj = JSService().processData(item, prov_name, city_name, area_name)
                            obj_list.append(obj)
                        # 将数据存入文件
                        path = self.__bank_type + '/' + prov_name + '_' + prov_id + '/' + city_name + '_' + city_id
                        dir_path = FileUtils().mkDir(path)
                        json_name = area_name + '_' + area_code + '_' + str(page)
                        if not save_flag:
                            if total_page != 1 and current_page < total_page:
                                new_pca_list = []
                                new_pca_list.append(req_info)
                                JSService().getReqData(new_pca_list, current_page+1, save_flag)
                        elif not len(obj_list) and page == 1:
                            file_name = FileUtils().saveInfo('', dir_path, json_name)
                        elif not len(obj_list):
                            pass
                        else:
                            file_name = FileUtils().saveInfo(str(obj_list), dir_path, json_name)
                            # 存数据
                            BankDao().save_date2db(obj_list)
                            # js_bank.show()
                        if total_page != 1 and current_page < total_page:
                            new_pca_list = []
                            new_pca_list.append(req_info)
                            JSService().getReqData(new_pca_list, current_page+1, save_flag)
            except Exception as e:
                if file_name is None:
                    file_name = self.__bank_type + '/' + prov_name + '_' + prov_id + '/' + city_name + '_' + city_id + '/' + area_name + '_' + area_code
                error_str = file_name + ' 数据异常 | error:' + str(e)
                print(error_str)
                FileUtils().saveErrorInfo(str(error_str))
                continue

    def processData(self, data, prov_name, city_name, area_name):
        '''
        加工处理数据
        :param data: 所需要处理的数据 
        :param prov_name: 省份
        :param city_name: 城市
        :param area_name: 地区
        :return: 
        '''
        js_bank = BankEntity()
        js_bank.set_bank_id(self.__bank_id)
        js_bank.set_bank_type(self.__bank_type)
        js_bank.set_name(data['NET_NAME'])
        js_bank.set_branch_id(data['BANK_OBJID'])
        js_bank.set_province(prov_name)
        js_bank.set_city(city_name)
        js_bank.set_area(area_name)
        js_bank.set_address(data['NET_AREA'])
        js_bank.set_phone_public(data['NET_PHONE'])
        js_bank.set_phone_private(data['NET_PHONE'])
        organType = data['NET_FLAG']
        if organType == '1':
            organType = '营业网点'
            organ_type_id = 1
        elif organType == '2':
            organType = '自助银行'
            organ_type_id = 2
        elif organType == '3':
            organType = 'ATM'
            organ_type_id = 3
        js_bank.set_organ_type_id(organ_type_id)
        js_bank.set_organ_type(organType)
        # 处理网点的坐标
        # 经度
        longitude = data['X_COORDINATE']
        js_bank.set_location_x(longitude)
        # 纬度
        latitude = data['Y_COORDINATE']
        js_bank.set_location_y(latitude)
        # 获得当前的时间
        js_bank.set_import_date(DateUtils().getCurrentDate())
        return js_bank.obj2json()

    def processSelectData(self, prov_id=0, city_id=0, area_id=0, save_flag=1):
        '''
        爬取选择省份信息, 使用默认值为爬取所有
        :param prov_id: 省份编码
        :param city_id: 城市编码
        :param area_id: 区域编码
        :param save_flag: 是否存储, 0:不存储, 1:存储
        :return: 
        '''
        pca_list = BankDao().getJSPCAInfo(prov_id, city_id, area_id)
        if not len(pca_list):
            JSService().getAreaList()
            pca_list = BankDao().getJSPCAInfo(prov_id, city_id, area_id)
        count = len(pca_list)
        if count >= 300:
            # 开启多线程处理
            split_list = ListUtils().splist(pca_list, 300)
            mutil_count = len(split_list)
            pool = multiprocessing.Pool(processes=mutil_count)
            for i in range(mutil_count):
                pool.apply_async(JSService().getReqData, (split_list[i], save_flag))
            pool.close()
            pool.join()
        else:
            JSService().getReqData(pca_list, save_flag)

if __name__ == '__main__':
    # pca_list = JSService().getAreaList()
    # JSService().getReqData(pca_list)
    time1 = DateUtils().getMillisecond()
    JSService().processSelectData(460000)
    time2 = DateUtils().getMillisecond()
    print(time2 - time1)


