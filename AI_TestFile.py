#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
@Author :   Owen
@Date   :   2025/9/1
"""

import os
from pathlib import Path

import dashscope
from dashscope import MultiModalConversation
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'


def load_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 未找到")
    except Exception as e:
        print(f"读取文件时发生错误：{str(e)}")


def perform_ocr(image_path: str, prompt_file='ai_test.txt'):
    """
    使用 DashScope OCR 模型对图像进行文字识别
    :param image_path: 图像文件路径
    :param prompt_file: 提示文本文件路径（默认为 ai_test.txt）
    :return: OCR 识别结果文本
    """
    # 加载提示文本
    cue = load_text_file('ai_test.txt')
    if cue is None:
        print("错误：提示文本文件未找到")
        return None
    # 构造图像 URL
    local_path = f"file://{image_path}"
    # 构造消息内容
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "image": local_path,
                    # 输入图像的最小像素阈值，小于该值图像会按原比例放大，直到总像素大于min_pixels
                    "min_pixels": 28 * 28 * 100,
                    # 输入图像的最大像素阈值，超过该值图像会按原比例缩小，直到总像素低于max_pixels
                    "max_pixels": 28 * 28 * 1024,
                    # 开启图像自动转正功能
                    "enable_rotate": True,
                },
                # qwen-vl-ocr-latest未设置内置任务时，支持在以下text字段中传入Prompt，若未传入则使用默认的Prompt：Please output only the text content from the image without any additional descriptions or formatting.
                # 如调用qwen-vl-ocr-1028，模型会使用固定Prompt：Read all the text in the image.，不支持用户在text中传入自定义Prompt
                {
                    "text": cue
                },
            ],
        }
    ]
    response = MultiModalConversation.call(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        # model="qwen-vl-ocr-latest",
        # model="qwen3-vl-235b-a22b-instruct",
        model="qwen-vl-ocr-2025-04-13",
        messages=messages,
    )
    # 返回识别结果
    try:
        print(response)
        result_text = response["output"]["choices"][0]["message"]["content"][0]["text"]
        if result_text[0:7] == "```json":
            result_text = result_text[7:].strip()
        if result_text[-3:] == "```":
            result_text = result_text[0:-3].strip()
        return result_text
    except KeyError:
        print("错误：无法从响应中提取 OCR 结果")
        return None


if __name__ == '__main__':
    ip = "D:/WorkSpace/单据扫描/作业单/待整理/20250713-1015-0006536.jpg"
    a = perform_ocr(ip)
    print(a)
