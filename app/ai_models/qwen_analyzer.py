# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：qwen_analyzer.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/26 01:07 
@PyVersion ：3.10 arm64
'''

from dashscope import MultiModalConversation
from flask import jsonify
from datetime import datetime
from PIL import Image

import base64
import io
import logging
import cv2
import dashscope

logger = logging.getLogger(__name__)

class QwenAnalyzer:
    def __init__(self,api_key):
        self.api_key = api_key
        dashscope.api_key = api_key

    def image_to_base64(self,image_array):
        """图片转base64"""
        try:
            #转换BGR到RGB
            image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)

            #转成base64
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=85)
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return img_str

        except Exception as e:
            logger.error(f"Image to base64 conversion error: {e}")
            return None

    def analyze_image(self,image_array, prompt):
        """
            使用Dashscope API分析图像

            Args:
                image_array: 图像数组
                prompt: 分析提示词

            Returns:
                dict: 分析结果
        """
        try:
            # 转化为base64
            image_base64 = self.image_to_base64(image_array)
            if not image_base64:
                return {'error': '图像转换失败', 'success': False}

            # 构建信息
            message = [
                {
                    "role":"user",
                    "content":[
                        {"image":f'data:image/jpeg;base64,{image_base64}'},
                        {"text":prompt}
                    ]
                }
            ]

            # 调用API
            response = MultiModalConversation.call(
                model='qwen3-vl-plus',
                messages=message,
                api_key='sk-6963e4b8bb5840de98983e63ed1ae012'
            )

            #检查响应状态
            if response.status_code == 200:
                analysis_text = response.output.choices[0].message.content[0]['text']
                return {
                    'analysis': analysis_text,
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                }

            else:
                error_msg = f'API调用失败：{response.code} - {response.message}'
                logger.error(error_msg)
                return {'error': error_msg, 'success': False}

        except Exception as e:
            logger.error(f"Dashscope analysis error: {e}")
            return {'error': f'分析失败: {str(e)}', 'success': False}

    def analyze_behavior(self,image_array):
        """分析车站行为"""
        prtmpt = """请详细描述这个人在车站环境中的行为，判断是否存在异常、危险或可疑行为。
        重点关注：是否在打架斗殴、攀爬翻越、吸烟用火、突发疾病、遗留可疑物品等安全风险。
        请用中文回答，并明确指出是否存在安全问题。"""

        return self.analyze_image(image_array, prtmpt)

