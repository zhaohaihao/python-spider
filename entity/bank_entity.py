#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: bank_entity.py

"""
Created on 2017/6/15 0015

@author: bigsea
"""

"""
银行实体类
"""
class BankEntity:

    __bank_id = ''                  # 银行标志符号 为了区分银行
    __bank_type = ''                # 银行类型
    __name = ''                     # 支行名称
    __branch_id = ''                # 分行编码
    __province = ''                 # 省份
    __city = ''                     # 城市
    __area = ''                     # 区域
    __address = ''                  # 详细地址
    __phone_public = ''             # 电话号码对公
    __phone_private = ''            # 电话号码对私
    __organ_type_id = ''            # 机构类型编号 为了区分机构 1: 营业网点, 2: 自助银行, 3: 自助设备
    __organ_type = ''               # 机构类型
    __location_x = ''               # 地址坐标x
    __location_y = ''               # 地址坐标y
    __import_date = ''              # 导入时间

    def get_bank_id(self):
        return self.__bank_id

    def set_bank_id(self, new_bank_id):
        self.__bank_id = new_bank_id

    def get_name(self):
        return self.__name

    def set_name(self, new_name):
        self.__name = new_name

    def get_bank_type(self):
        return self.__bank_type

    def set_bank_type(self, new_bank_type):
        self.__bank_type = new_bank_type

    def get_branch_id(self):
        return self.__branch_id

    def set_branch_id(self, new_branch_id):
        self.__branch_id = new_branch_id

    def get_province(self):
        return self.__province

    def set_province(self, new_province):
        self.__province = new_province

    def get_city(self):
        return self.__city

    def set_city(self, new_city):
        self.__city = new_city

    def get_area(self):
        return self.__area

    def set_area(self, new_area):
        self.__area = new_area

    def get_address(self):
        return self.__address

    def set_address(self, new_address):
        self.__address = new_address

    def get_phone_public(self):
        return self.__phone_public

    def set_phone_public(self, new_phone):
        self.__phone_public = new_phone

    def get_phone_private(self):
        return self.__phone_private

    def set_phone_private(self, new_phone):
        self.__phone_private = new_phone

    def get_organ_type_id(self):
        return self.__organ_type_id

    def set_organ_type_id(self, new_organ_type_id):
        self.__organ_type_id = new_organ_type_id

    def get_organ_type(self):
        return self.__organ_type

    def set_organ_type(self, new_organ_type):
        self.__organ_type = new_organ_type

    def get_location_x(self):
        return self.__location_x

    def set_location_x(self, new_location_x):
        self.__location_x = new_location_x

    def get_location_y(self):
        return self.__location_y

    def set_location_y(self, new_location_y):
        self.__location_y = new_location_y

    def get_import_date(self):
        return self.__import_date

    def set_import_date(self, new_import_date):
        self.__import_date = new_import_date

    def show(self):
        """
        打印输出当前对象的信息
        :return: 
        """
        print('{', '\n',
              'bankId:', self.__bank_id, '\n',
              'bankType', self.__bank_type, '\n',
              'name:', self.__name, '\n',
              'branchId', self.__branch_id, '\n',
              'province', self.__province, '\n',
              'city', self.__city, '\n',
              'area', self.__area, '\n',
              'address', self.__address, '\n',
              'phonePublic', self.__phone_public, '\n',
              'phonePrivate', self.__phone_private, '\n',
              'organTypeId', self.__organ_type_id, '\n',
              'organType', self.__organ_type, '\n',
              'location_x', self.__location_x, '\n',
              'location_y', self.__location_y, '\n',
              'importDate', self.__import_date, '\n',
              '}', '\n')

    def obj2json(self):
        """
        将python对象统一处理转成字典
        :return:
        """
        entity_dict = {
            'bankId': self.__bank_id,
            'bankType': self.__bank_type,
            'name': self.__name,
            'branchId': self.__branch_id,
            'province': self.__province,
            'city': self.__city,
            'area': self.__area,
            'address': self.__address,
            'phonePublic': self.__phone_public,
            'phonePrivate': self.__phone_private,
            'organTypeId': self.__organ_type_id,
            'organType': self.__organ_type,
            'location_x': self.__location_x,
            'location_y': self.__location_y,
            'importDate': self.__import_date
        }
        return entity_dict


