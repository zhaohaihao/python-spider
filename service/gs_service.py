#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: gs_service.py

"""
Created on 2017/6/22 0022

@author: bigsea
"""

import time
import json
import requests
from pyquery import PyQuery as pq
from requests.exceptions import RequestException
from __init__ import *
from bank_entity import BankEntity
from bank_dao import BankDao
from file_util import FileUtils
from date_util import DateUtils

"""
工商银行数据处理层
"""
class GSService:

    __bank_id = '3'
    __bank_type = '工商银行'

    def get_bank_page(self, url, prov_name, city_name, district, viewstate, total_page=1, curent_page=1):
        """
        返回获取页面的信息
        :param url: 请求的地址
        :param prov_name: 省份名称
        :param city_name: 城市名称
        :param district: 区域名称
        :return: 
        """
        if curent_page == 1:
            param_str = 'icbc1:' + city_name + ',' + district + ',1,,,1'
        else:
            param_str = 'icbc2:' + city_name + ',' + district + ',1,,,down,1,' + str(curent_page-1) + ',' + str(total_page)
        print(param_str)
        param = {
            # '__EVENTTARGET': '',
            # '__EVENTARGUMENT': '',
            'searchparas': param_str,
            '__VIEWSTATE': viewstate,
            '__ASYNCPOST': 'true',
            'sym': 'sym | btnReq_Info'
            # 'bbb': '',
            # 'btnReq_Info': ''
        }
        try:
            response = requests.post(url, data=param)
            print(response.text)
            # doc = pq(url, param, method='post')
            # print(str(doc).split('|'))
            # print('viewstate', viewstate)
            # viewstate_temp = doc('#__VIEWSTATE').val()
            # print('viewstate_temp', viewstate_temp)
            # res_json = json.loads(doc('#jsdatapr').text())
            # print(res_json)
            # items = res_json['ICBCPointInfomationList']
            # total_page_count = int(res_json['TotalPageCount'])
            # current_page_index = int(res_json['CurrentPageIndex'])
            # print('total: ', total_page_count, ' current: ', current_page_index)
            # for item in items:
            #     GSService().process_data(items[item], prov_name, city_name)
            # if total_page_count != 1 and current_page_index < total_page_count:
            #     GSService().get_bank_page(url, prov_name, city_name, district, viewstate=viewstate_temp, total_page=total_page_count, curent_page=current_page_index+1)
            # else:
            #     return viewstate_temp
            # print('(GSService)Get page success!')
        except RequestException as e:
            print('(GSService)Get page error:', e)

    def process_data(self, data_dict, prov_name, city_name):
        try:
            print('(GSService)Process data start!')
            # 开始填充所需的数据
            gs_bank = BankEntity()
            gs_bank.set_bank_id(self.__bank_id)
            gs_bank.set_bank_type(self.__bank_type)
            gs_bank.set_name(data_dict['stru_fname'])
            gs_bank.set_branch_id(data_dict['stru_id'])
            gs_bank.set_province(prov_name)
            gs_bank.set_city(city_name)
            gs_bank.set_address(data_dict['addr_detail'])
            public_1 = data_dict['public_net_phone_no1']
            public_2 = data_dict['public_net_phone_no2']
            if public_1 == "":
                gs_bank.set_phone_public("")
            elif public_2 == "":
                gs_bank.set_phone_public(public_1)
            else:
                phone_public = public_1 + '、' + public_2
                gs_bank.set_phone_public(phone_public)
            private_1 = data_dict['net_phone_no1']
            private_2 = data_dict['net_phone_no2']
            if private_1 == "":
                gs_bank.set_phone_private("")
            elif private_2 == "":
                gs_bank.set_phone_private(private_2)
            else:
                phone_private = private_1 + '、' + private_2
                gs_bank.set_phone_private(phone_private)
            gs_bank.set_organ_type('网点')
            # 处理网点的坐标
            # 经度
            longitude = data_dict['lng']
            gs_bank.set_location_x(longitude)
            # 纬度
            latitude = data_dict['lat']
            gs_bank.set_location_y(latitude)
            gs_bank.set_import_date(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            # 存数据
            BankDao().save_date2db(gs_bank.obj2json())
            # gs_bank.show()

            print('(GSService)Process data end!')
        except Exception as e:
            print('(GSService)Process data error:', e)

    @staticmethod
    def get_prov_city_list(url):
        try:
            doc = pq(url=url)
            # print(doc)
            res_json = json.loads(doc('#jscitydatapr').text())
            print(res_json)
            viewstate = doc('#__VIEWSTATE').val()
            print(viewstate)
            for item in res_json:
                # 获得对应的省市信息
                prov_name = item['Province']
                city_name = item['CityName']
                districts = item['Districts']
                if len(districts) == 0:
                    continue
                else:
                    for district in districts:
                        print(district)
                        print(prov_name, ':', city_name, ":", district)
                        viewstate = GSService().get_bank_page(url, prov_name, city_name, district, viewstate)
                        # print(viewstate)
        except Exception as e:
            print('(GSService)Get list error:', e)

    @staticmethod
    def main():
        url = 'http://www.icbc.com.cn/ICBCDynamicSite2/LBS/nets/netsappointreal.aspx'
        GSService.get_prov_city_list(url)

if __name__ == '__main__':
    GSService.main()

