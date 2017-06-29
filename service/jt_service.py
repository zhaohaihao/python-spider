#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: jt_service.py

"""
Created on 2017/6/16 0016

@author: bigsea
"""

import re
import json
import requests
import urllib.parse
import multiprocessing
from __init__ import *
from bank_entity import BankEntity
from bank_dao import BankDao
from file_util import FileUtils
from date_util import DateUtils
from list_util import ListUtils

"""
交通银行数据处理层
"""
class JTService:

    __bank_id = '2'
    __bank_type = '交通银行'
    __fiexd_list = ['北京', '重庆', '上海', '天津']
    __suffix_case = ['区', '县', '市']
    __branch_url = 'http://www.bankcomm.com/BankCommSite/zonghang/cn/node/queryBranchResult.do'
    __device_url = 'http://www.bankcomm.com/BankCommSite/zonghang/cn/node/queryDeviceResult.do'

    def getCityAndCountyList(self):
        """
        获取所有省份的信息列表
        :return: 
        """
        prov_city_name_list = BankDao().getJTPCAInfo()
        if len(prov_city_name_list):
            return prov_city_name_list
        print('获取所有请求信息列表, 请稍后...')
        url = 'http://www.bankcomm.com/BankCommSite/zonghang/cn/node/queryCityResult.do'
        response = requests.get(url)
        res_json = response.json()
        if len(res_json):
            citys = res_json['citys']
            for city in citys:
                # 获得省份的名称
                prov_code = city.split('|')[0]
                prov_name = city.split('|')[1]
                if prov_name in self.__fiexd_list:
                    prov_name = prov_name + '市'
                # 获得市的名称
                citys_info = citys[city]
                for city_info in citys_info:
                    city_code = city_info
                    city_name = citys_info[city_info]['d']
                    if city_name.find('市') == -1:
                        city_name = city_name + '市'
                    area_url = 'http://www.bankcomm.com/BankCommSite/zonghang/cn/node/queryCountyByCityName.do?cityName='
                    area_res = requests.get(area_url + city_name)
                    area_items = area_res.json()
                    city_area = area_items['citys']
                    for area_city in city_area:
                        city_area_items = city_area[area_city]
                        for city_area_item in city_area_items:
                            area_code = city_area_item
                            area_data = city_area_items[city_area_item]['d']
                            last_case = area_data[-1]
                            branch_url = self.__branch_url + '?city=' + city_name + '&countyName=' + area_data
                            device_url = self.__device_url + '?city=' + city_name + '&countyName=' + area_data
                            if last_case in self.__suffix_case:
                                pass
                            else:
                                area_data = area_data + '市'
                            # 特殊处理两个区名
                            if area_data == '?桥区':
                                area_data = '埇桥区'
                            elif area_data == '?口区':
                                area_data = '硚口区'
                            prov_city_name = {
                                'provinceId': prov_code,
                                'province': prov_name,
                                'cityId': city_code,
                                'city': city_name,
                                'areaId': area_code,
                                'area': area_data,
                                'branchUrl': branch_url,
                                'deviceUrl': device_url
                            }
                            prov_city_name_list.append(prov_city_name)
        # 存储请求地址 防止频繁请求不变信息
        BankDao().saveJTPCAInfo(prov_city_name_list)
        print('请求信息存储完毕!')
        return prov_city_name_list

    def getReqData(self, pca_list, save_flag):
        '''
        请求数据
        :param pca_list: 请求省城市地区信息列表
        :param save_flage: 是否存储, 0:不存储, 1:存储
        :return: 
        '''
        for pca_info in pca_list:
            try:
                file_name = None
                prov_name = pca_info['province']
                prov_id = pca_info['provinceId']
                city_name = pca_info['city']
                city_id = pca_info['cityId']
                area_name = pca_info['area']
                area_id = pca_info['areaId']
                branch_url = pca_info['branchUrl']
                deviceUrl = pca_info['deviceUrl']
                # print(prov_name)
                list1 = JTService().getReqDataByUrl(branch_url, '1', pca_info)
                # print('list1:', list1)
                list2 = JTService().getReqDataByUrl(deviceUrl, '2', pca_info)
                list1[len(list1):len(list1)] = list2
                # print('list2:', list2)
                # 将数据存入文件
                path = self.__bank_type + '/' + prov_name + '_' + prov_id + '/' + city_name + '_' + city_id
                dir_path = FileUtils().mkDir(path)
                json_name = area_name + '_' + area_id
                if save_flag:
                    if not len(list1):
                        file_name = FileUtils().saveInfo('', dir_path, json_name)
                    else:
                        file_name = FileUtils().saveInfo(str(list1), dir_path, json_name)
                        # 存数据
                        BankDao().save_date2db(list1)
                        # jt_bank.show()
            except Exception as e:
                if file_name is None:
                    file_name = self.__bank_type + '/' + prov_name + '_' + prov_id + '/' + city_name + '_' + city_id + '/' + area_name + '_' + area_id
                error_str = file_name + ' 数据异常 | error:' + str(e)
                print(error_str)
                FileUtils().saveErrorInfo(str(error_str))
                continue

    def getReqDataByUrl(self, url, type_id, req_info):
        '''
        请求数据
        :param url: 爬取的网页的链接
        :param type_id: 机构类型 1.营业网点 2.自助银行
        :param req_info: 当前请求省城市地区信息
        :return: 
        '''
        prov_name = req_info['province']
        city_name = req_info['city']
        area_name = req_info['area']
        # 存储每个请求页面获取的所有网点信息的列表
        obj_list = []
        try:
            response = requests.get(url)
            if type_id == '1':
                response.encoding = 'utf-8'
            elif type_id == '2':
                response.encoding = 'GBK'
            res_json = response.json()
            if res_json is not None:
                items = res_json['data']
                for item in items:
                    obj = JTService().processData(items[item], prov_name, city_name, area_name, type_id)
                    obj_list.append(obj)
            return obj_list
        except json.JSONDecodeError:
            res_text = response.text
            after_deal_text = JTService().regex(res_text)
            res_json = json.loads(after_deal_text)
            if res_json is not None:
                items = res_json['data']
                for item in items:
                    obj = JTService().processData(items[item], prov_name, city_name, area_name, type_id)
                    obj_list.append(obj)
            # print(res_text)
            return obj_list
        except Exception as e:
            print('error:', e)

    def processData(self, data, prov_name, city_name, area_name, type_id):
        '''
        加工处理数据
        :param data: 请求返回的数据
        :param prov_name: 省份
        :param city_name: 城市
        :param area_name: 地区
        :param type_id: 网点类型
        :return: 
        '''
        # 开始填充所需的数据
        jt_bank = BankEntity()
        jt_bank.set_bank_type(self.__bank_type)
        all_address = urllib.parse.unquote(data['a'])
        jt_bank.set_bank_id(self.__bank_id)
        jt_bank.set_name(data['n'])
        jt_bank.set_province(prov_name)
        jt_bank.set_city(city_name)
        jt_bank.set_area(area_name)
        jt_bank.set_address(all_address)
        if type_id == '1':
            typeName = '营业网点'
            jt_bank.set_branch_id(data['d'])
            jt_bank.set_phone_public(urllib.parse.unquote(data['o']))
            jt_bank.set_phone_private(urllib.parse.unquote(data['p']))
            jt_bank.set_organ_type_id('1')
            organType = data['b']
            if organType == '0':
                organType = typeName + '(普通网点)'
            elif organType == '1':
                organType = typeName + '(沃德中心)'
            elif organType == '2':
                organType = typeName + '(私人银行)'
            elif organType == '3':
                organType = typeName + '(交银施罗德基金)'
            elif organType == '4':
                organType = typeName + '(交银康联)'
            elif organType == '5':
                organType = typeName + '(交银国际信托)'
            elif organType == '6':
                organType = typeName + '(交银金融租赁)'
            jt_bank.set_organ_type(organType)
        elif type_id == '2':
            typeName = '自助银行'
            jt_bank.set_branch_id(data['i'].replace('device', ''))
            jt_bank.set_phone_public('-')
            jt_bank.set_phone_private('-')
            jt_bank.set_organ_type_id('2')
            organType = str(data['m'])
            if organType == 'ATM':
                organType = typeName + '(取款机)'
            elif organType == 'CRS':
                organType = typeName + '(存取款一体机)'
            elif organType == 'BTM':
                organType = typeName + '(发卡机)'
            elif organType == 'CASHLESS':
                organType = typeName + '(查询机)'
            elif organType == 'ITM':
                organType = typeName + '(远程智能柜员机)'
            jt_bank.set_organ_type(organType)
        # 处理网点的坐标
        # 经度
        longitude = data['x']
        jt_bank.set_location_x(longitude)
        # 纬度
        latitude = data['y']
        jt_bank.set_location_y(latitude)
        # 获得当前的时间
        jt_bank.set_import_date(DateUtils().getCurrentDate())
        return jt_bank.obj2json()

    def regex(self, res_text):
        '''
        正则处理出错返回的内容
        :param res_text: 返回内容
        :return: 
        '''
        deal_text = res_text
        deal_text = deal_text.replace('\x1a', '')
        deal_text = deal_text.replace('\"n\":\"东城支行\n\n东城支行\"', '\"n\":\"东城支行东城支行\"')
        deal_text = deal_text.replace('\t', '')
        deal_text = deal_text.replace('\n', '')
        pattern = r'\"n\":\s?\".*?\n\"'
        regex = re.compile(pattern)
        find_items = regex.findall(deal_text)
        for find_item in find_items[1:]:
            # deal_text = deal_text.replace(find_item, new_find_item)
            deal_text = deal_text.replace(find_item, find_item.strip())
        # pattern_1 = r'\"t\":\s?\".*?\t+\"'
        # regex_1 = re.compile(pattern_1)
        # find_items_1 = regex_1.findall(deal_text)
        # for find_item_1 in find_items_1[1:]:
        #     new_find_item_1 = find_item_1.replace('\t', '')
        #     deal_text = deal_text.replace(find_item_1, new_find_item_1)
        #     print(new_find_item_1)
        return deal_text

    def processSelectData(self, prov_id=0, city_id=0, area_id=0, save_flag=1):
        '''
        爬取选择省份信息, 使用默认值为爬取所有
        :param prov_id: 省份编码
        :param city_id: 城市编码
        :param area_id: 区域编码
        :param save_flag: 是否存储, 0:不存储, 1:存储
        :return: 
        '''
        pca_list = BankDao().getJTPCAInfo(prov_id, city_id, area_id)
        if not len(pca_list):
            JTService().getCityAndCountyList()
            pca_list = BankDao().getJTPCAInfo(prov_id, city_id, area_id)
        count = len(pca_list)
        if count >= 300:
            # 开启多线程处理
            split_list = ListUtils().splist(pca_list, 300)
            mutil_count = len(split_list)
            pool = multiprocessing.Pool(processes=mutil_count)
            # print(mutil_count)
            for i in range(mutil_count):
                pool.apply_async(JTService().getReqData, (split_list[i], save_flag))
            pool.close()
            pool.join()
        else:
            JTService().getReqData(pca_list, save_flag)

if __name__ == '__main__':
    # print(urllib.parse.quote('北京市'))
    # pca_list = JTService().getCityAndCountyList()
    # JTService().getReqData(pca_list)

    time1 = DateUtils().getMillisecond()
    JTService().processSelectData(save_flag=0)
    time2 = DateUtils().getMillisecond()
    print(time2-time1)