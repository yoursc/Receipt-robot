#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@Author : Ven
@Date   : 2023-07-08
"""
import os
import shutil
import re

# 参数配置
# 工作空间路径
CONF_WORK_SPACE = "C:\\Users\\ven\\OneDrive - 东南\\单据扫描\\作业单"
# 编号白名单
CONF_CAR_LIST_IN = ['0000',
                    '1010', '1013',
                    '1001', '1008', '1012',
                    '1003', '1005',
                    '1015', '1016',
                    '2001', '2002', '2003', '2005'
                    ]
CONF_CAR_LIST_OUT = ['刘永杰', '李新伟']

# 全局变量
# 临时文件路径
WORK_TMP = ""
CAR_LIST = CONF_CAR_LIST_IN + CONF_CAR_LIST_OUT
ERR_FLAG = 0


def check_path():
    """
    检查工作目录
    """
    global CONF_WORK_SPACE, WORK_TMP, ERR_FLAG
    # 如果没有定义工作目录，则将脚本文件所在目录的父目录视作工作目录
    if CONF_WORK_SPACE.isspace():
        class_file_path = os.path.realpath(__file__)
        tcp = os.path.abspath(os.path.join(
            class_file_path
            , ".."
            , ".."
        ))
        if not os.path.basename(tcp) == "作业单":
            print(tcp)
            raise ValueError("工作目录应为作业单")
        CONF_WORK_SPACE = tcp

    # 检查导入目录是否存在
    WORK_TMP = os.path.join(CONF_WORK_SPACE, "待整理")
    if not os.path.exists(WORK_TMP):
        print('输入目录不存在：', WORK_TMP)
        ERR_FLAG += 1

    # 检查车辆子目录是否存在
    for item in CONF_CAR_LIST_IN:
        out_dir = os.path.join(CONF_WORK_SPACE, item)
        if not os.path.exists(out_dir):
            print('输出目录不存在：', out_dir)
            ERR_FLAG += 1
    for item in CONF_CAR_LIST_OUT:
        out_dir = os.path.join(CONF_WORK_SPACE, '0000', item)
        if not os.path.exists(out_dir):
            print('输出目录不存在：', out_dir)
            ERR_FLAG += 1
    if ERR_FLAG > 0:
        raise ValueError("有未解决的错误，程序停止运行")


def categorize():
    """
    将本地临时目录中的文件，
    根据文件名
    移动本地文件
    """
    global ERR_FLAG
    # e.g. 20231231-1001-1234567
    reg = r'\d{8}-\d{4}-\d{7}'
    for item in os.scandir(WORK_TMP):
        # 检测目录文件
        if os.path.isdir(item.path):
            print("    Warning: It is dir：" + item.name)
            ERR_FLAG += 1

        # 检测文件命名是否合规
        if len(item.name) <= 0:
            continue
        if re.match(reg, item.name) is None:
            continue

        # 车辆编号核查
        car_no = item.name.split("-")[1]
        if car_no not in CAR_LIST:
            print("    Error: Not in car list: " + item.name)
            ERR_FLAG += 1

        # 本地文件是否重复
        p = os.path.join(CONF_WORK_SPACE, car_no, item.name)
        if os.path.exists(p):
            print("    Error: Local file is exist: " + item.name)
            ERR_FLAG += 1

    if ERR_FLAG > 0:
        return 0

    # 执行文件移动
    for item in os.scandir(WORK_TMP):
        if len(item.name) <= 0:
            continue
        if re.match(reg, item.name) is None:
            continue
        print(item.name)
        car_no = item.name.split("-")[1]
        shutil.move(item.path, os.path.join(CONF_WORK_SPACE, car_no))


if __name__ == '__main__':
    check_path()
    categorize()
