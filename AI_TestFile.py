#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
@Author :   Owen
@Date   :   2025/9/1
"""

import os
from dashscope import MultiModalConversation


def load_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 未找到")
    except Exception as e:
        print(f"读取文件时发生错误：{str(e)}")

cue = load_text_file('ai_test.txt')
local_path = "C:/Users/OWEN/Documents/WorakSpace/单据扫描/作业单/1005/20250830-1005-0007183.jpg"
image_path = f"file://{local_path}"
messages = [
    {
        "role": "user",
        "content": [
            {
                "image": image_path,
                # 输入图像的最小像素阈值，小于该值图像会按原比例放大，直到总像素大于min_pixels
                "min_pixels": 28 * 28 * 4,
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

if __name__ == '__main__':
    response = MultiModalConversation.call(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        model="qwen-vl-ocr-2025-04-13",
        messages=messages,
    )
    print(response)
    print(response["output"]["choices"][0]["message"].content[0]["text"])