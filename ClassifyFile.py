#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@Author : Ven
@Date   : 2023-07-08
"""
import os
import shutil
import re

# 工作空间路径
WORK_SPACE = "C:\\Users\\ven\\OneDrive - 东南\\单据扫描\\作业单"
# 临时文件路径
WORK_TMP = ""
# 编号白名单
CAR_LIST = ['0000',
            '1010', '1013',
            '1001', '1008', '1012',
            '1003', '1005',
            '1015', '1016',
            '2001', '2002', '2003', '2005'
            ]


def check_path():
    global WORK_SPACE, WORK_TMP
    # 如果没有定义工作目录，则将脚本文件所在目录的父目录视作工作目录
    if WORK_SPACE.isspace():
        class_file_path = os.path.realpath(__file__)
        tcp = os.path.abspath(os.path.join(
            class_file_path
            , ".."
            , ".."
        ))
        if not os.path.basename(tcp) == "作业单":
            print(tcp)
            raise ValueError("工作目录应为作业单")
        WORK_SPACE = tcp
    # 定义临时目录
    WORK_TMP = os.path.join(WORK_SPACE, "待整理")


def categorize():
    """
    将本地临时目录中的文件，
    根据文件名
    移动本地文件
    """
    # 预处理
    reg = r'\d{8}-\d{4}-\d{7}'
    err_count = 0
    for item in os.scandir(WORK_TMP):
        if len(item.name) <= 0:
            continue
        if re.match(reg, item.name) is None:
            continue
        # 检测目录文件
        if os.path.isdir(item.path):
            print("    Warning: It is dir：" + item.name)
            err_count += 1
        # 车辆编号核查
        car_no = item.name.split("-")[1]
        if car_no not in CAR_LIST:
            print("    Error: Not in car list: " + item.name)
            err_count += 1
        # 本地文件是否重复
        p = os.path.join(WORK_SPACE, car_no, item.name)
        if os.path.exists(p):
            print("    Error: Local file is exist: " + item.name)
            err_count += 1
    if err_count > 0:
        return 0

    # 遍历待处理文件
    for item in os.scandir(WORK_TMP):
        if item.name[0] not in "0123456789":
            continue
        print(item.name)
        car_no = item.name.split("-")[1]
        # 文件移动
        shutil.move(item.path, os.path.join(WORK_SPACE, car_no))


if __name__ == '__main__':
    check_path()
    categorize()
