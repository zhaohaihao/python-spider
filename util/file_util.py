#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: file_util.py

"""
Created on 2017/6/26 0026

@author: bigsea
"""
import os

DIR_PATH = '../银行网点数据'

class FileUtils:

    def __init__(self):
        self.path = DIR_PATH
        if not self.path.endswith('/'):
            self.path = self.path + '/'
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def mkDir(self, path):
        '''
        创建文件存储的目录
        :param path: 子目录
        :return: 
        '''
        path = path.strip()
        dir_path = self.path + path
        exists = os.path.exists(dir_path)
        if not exists:
            os.makedirs(dir_path)
        return dir_path

    def saveInfo(self, content, dir_path, name):
        '''
        将数据存入文件
        :param content: 存储内容
        :param dir_path: 文件路径
        :param name: 文件名
        :return: 
        '''
        file_name = dir_path + '/' + name + '.json'
        f = open(file_name, 'wb+')
        f.write(content.encode('utf-8'))
        print(file_name, '导入成功')
        f.close()
        return file_name

    def saveErrorInfo(self, content):
        '''
        将错误信息存入文件
        :param content: 存储内容
        :return: 
        '''
        file_name = DIR_PATH + '/file_error.txt'
        f = open(file_name, 'a')
        f.write(content+'\n')
        f.close()