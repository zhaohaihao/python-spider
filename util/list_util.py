#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: list_util.py

"""
Created on 2017/6/28 0028

@author: bigsea
"""

class ListUtils:

    def splist(self, l, s):
        '''
        平分列表
        :param l: 需要平分的列表
        :param s: 平分的长度
        :return: 
        '''
        return [l[i:i+s] for i in range(len(l)) if i % s == 0]