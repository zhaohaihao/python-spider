#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: ny_service.py

"""
Created on 2017/6/16 0016

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
农业银行数据处理层
"""
class NYService:

    __bank_id = '1'
    __bank_type = '农业银行'
    __fiexd_list = ['北京', '上海', '天津', '重庆']

    def getUrlList(self):
        '''
        获取所有请求地址的列表
        :return: 
        '''
        url_list = BankDao().getNYPCAInfo()
        if len(url_list):
            return url_list
        print('获取所有请求信息列表, 请稍后...')
        prov_url = 'http://app.abchina.com/branch/common/BranchService.svc/District'
        prov_res = requests.get(prov_url)
        prov_items = prov_res.json()
        for prov_item in prov_items:
            prov_id = str(prov_item['Id'])
            prov_name = prov_item['Name']
            # print(prov_name + ":" + prov_id)
            # 特殊处理
            if prov_name in self.__fiexd_list:
                prov_name = prov_name + '市'
                # print(prov_name)
            elif prov_name == '内蒙古':
                pass
            else:
                prov_name = prov_name + '省'
            city_url = 'http://app.abchina.com/branch/common/BranchService.svc/District/'
            city_res = requests.get(city_url + prov_id)
            city_items = city_res.json()
            for city_item in city_items:
                if city_item is not None:
                    city_id = str(city_item['Id'])
                    city_name = city_item['Name']
                    area_url = 'http://app.abchina.com/branch/common/BranchService.svc/District/Any/'
                    area_res = requests.get(area_url + city_id)
                    area_items = area_res.json()
                    for area_item in area_items:
                        area_id = str(area_item['Id'])
                        area_name = area_item['Name']
                        url = 'http://app.abchina.com/branch/common/BranchService.svc/Branch?p=' +\
                              prov_id + '&c=' + city_id + '&b=' + area_id + '&q=&t=0'
                        url_dict = {
                            'provinceId': prov_id,
                            'province': prov_name,
                            'cityId': city_id,
                            'city': city_name,
                            'areaId': area_id,
                            'area': area_name,
                            'url': url
                        }
                        url_list.append(url_dict)
        # 存储请求地址 防止频繁请求不变信息
        BankDao().saveNYPCAInfo(url_list)
        print('请求信息存储完毕!')
        return url_list

    def getReqData(self, url_list, save_flag, current_page=0):
        '''
        请求数据
        :param url_list: 请求数据的地址
        :param save_flag: 是否存储, 0:不存储, 1:存储
        :param current_page: 当前页
        :return: 
        '''
        for req_info in url_list:
            params = {'i': str(current_page)}
            # 存储每个请求页面获取的所有网点信息的列表
            obj_list = []
            file_name = None
            try:
                prov_name = req_info['province']
                prov_id = req_info['provinceId']
                city_name = req_info['city']
                city_id = req_info['cityId']
                area_name = req_info['area']
                area_id = req_info['areaId']
                url = req_info['url']
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    response.encoding = 'utf-8'
                    # 请求返回数据为json类型
                    res_json = response.json()
                    # print(res_json)
                    # 获得主题信息的内容
                    items = res_json['BranchSearchRests']
                    # print(items)
                    for item in items:
                        # print(item)
                        type_id = item['TypeId']
                        obj = NYService().processData(item, prov_name, city_name, area_name, type_id)
                        obj_list.append(obj)
                        # print(obj)
                    # 将数据存入文件
                    # 排除空的批量导入
                    path = self.__bank_type + '/' + prov_name + '_' + prov_id + '/' + city_name + '_' + city_id
                    dir_path = FileUtils().mkDir(path)
                    new_page = current_page + 1
                    json_name = area_name + '_' + area_id + '_' + str(new_page)
                    if not save_flag:
                        # 翻页请求
                        new_url_list = []
                        new_url_list.append(req_info)
                        NYService().getReqData(new_url_list, new_page, save_flag)
                    elif not len(obj_list) and not new_page:
                        file_name = FileUtils().saveInfo('', dir_path, json_name)
                    elif not len(obj_list):
                        pass
                    else:
                        file_name = FileUtils().saveInfo(str(obj_list), dir_path, json_name)
                        # 存数据
                        BankDao().save_date2db(obj_list)
                        # 翻页请求
                        new_url_list = []
                        new_url_list.append(req_info)
                        NYService().getReqData(new_url_list, new_page, save_flag)
                        # ny_bank.show()
            except Exception as e:
                if file_name is None:
                    file_name = self.__bank_type + '/' + prov_name + '_' + prov_id + '/' + city_name + '_' + city_id + '/' + area_name + '_' + area_id
                error_str = file_name + ' 数据异常 | error:' + str(e)
                print(error_str)
                FileUtils().saveErrorInfo(str(error_str))
                continue

    def processData(self, data, prov_name, city_name, area_name, type_id):
        '''
        加工处理各类型网点数据
        :param data: 请求返回的数据
        :param prov_name: 省份
        :param city_name: 城市
        :param area_name: 地区
        :param type_id: 网点类型
        :return: 
        '''
        # 开始填充所需数据
        ny_bank = BankEntity()
        ny_bank.set_bank_id(self.__bank_id)
        ny_bank.set_bank_type(self.__bank_type)
        ny_bank.set_phone_public('-')
        ny_bank.set_phone_private('-')
        if type_id == 1:
            bank_info = data['BranchBank']
            ny_bank.set_phone_public(bank_info['PhoneNumber'])
            ny_bank.set_phone_private(bank_info['PhoneNumber'])
            ny_bank.set_address(bank_info['Address'])
            organType = '营业网点'
            organ_type_id = 1
        elif type_id == 2:
            bank_info = data['SelfServiceBank']
            ny_bank.set_address(bank_info['Address'])
            organType = '自助银行'
            organ_type_id = 2
        elif type_id == 3:
            bank_info = data['SelfServiceEquip']
            ny_bank.set_address(bank_info['Name'])
            organType = '自助设备'
            organ_type_id = 3
        ny_bank.set_name(bank_info['Name'])
        ny_bank.set_branch_id(int(bank_info['Id']))
        ny_bank.set_province(prov_name)
        ny_bank.set_city(city_name)
        ny_bank.set_area(area_name)
        ny_bank.set_organ_type_id(organ_type_id)
        ny_bank.set_organ_type(organType)
        # 处理网点坐标
        # 经度
        longitude = bank_info['Longitude']
        ny_bank.set_location_x(longitude)
        # 纬度
        latitude = bank_info['Latitude']
        ny_bank.set_location_y(latitude)
        # 获得当前的时间
        ny_bank.set_import_date(DateUtils().getCurrentDate())
        return ny_bank.obj2json()

    def processSelectedData(self, prov_id=0, city_id=0, area_id=0, save_flag=1):
        '''
        爬取选择省份信息, 使用默认值为爬取所有
        :param prov_id: 省份编码
        :param city_id: 城市编码
        :param area_id: 区域编码
        :param save_flag: 是否存储, 0:不存储, 1:存储
        :return: 
        '''
        url_list = BankDao().getNYPCAInfo(prov_id, city_id, area_id)
        if not len(url_list):
            NYService().getUrlList()
            url_list = BankDao().getNYPCAInfo(prov_id, city_id, area_id)
        count = len(url_list)
        if count >= 300:
            # 开启多线程处理
            split_list = ListUtils().splist(url_list, 300)
            mutil_count = len(split_list)
            print(mutil_count)
            pool = multiprocessing.Pool(processes=mutil_count)
            print(mutil_count)
            for i in range(mutil_count):
                pool.apply_async(NYService().getReqData, (split_list[i], save_flag))
            pool.close()
            pool.join() # 调用join之前, 先调用close函数, 否则会出错, 执行完close后不会有新的进程加入到pool, join函数等待所有子进程的结束
        else:
            NYService().getReqData(url_list, save_flag)

if __name__ == '__main__':
    # url_list = NYService().getUrlList()
    # NYService().getReqData(url_list)
    # NYService().processOneData(1, 1, 1)
    # time1 = DateUtils().getMillisecond()
    NYService().processSelectedData()
    # time2 = DateUtils().getMillisecond()
    # print('time:', (time2-time1))