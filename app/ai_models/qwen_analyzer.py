# qwen_analyzer.py
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
from datetime import datetime
from PIL import Image
import base64
import io
import logging
import cv2
import dashscope

logger = logging.getLogger(__name__)


class QwenAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        dashscope.api_key = api_key
        self.default_location = "车站"  # 默认位置

    def image_to_base64(self, image_array):
        """图片转base64"""
        try:
            # 转换BGR到RGB
            image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)

            # 转成base64
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=85)
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return img_str

        except Exception as e:
            logger.error(f"Image to base64 conversion error: {e}")
            return None

    def analyze_image(self, image_array, prompt):
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
                    "role": "user",
                    "content": [
                        {"image": f'data:image/jpeg;base64,{image_base64}'},
                        {"text": prompt}
                    ]
                }
            ]

            # 调用API
            response = MultiModalConversation.call(
                model='qwen3-vl-plus',
                messages=message,
                api_key=self.api_key  # 使用传入的api_key
            )

            # 检查响应状态
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

    def analyze_behavior(self, image_array, detection_info=None):
        """
        分析车站行为

        Args:
            image_array: 图像数组
            detection_info: 检测信息字典，包含位置信息（可选）
                {
                    'bbox': [x1, y1, x2, y2],
                    'class_name': 'person',
                    'confidence': 0.8
                }

        Returns:
            dict: 分析结果
        """
        time_str = datetime.now().isoformat()

        # 从detection_info获取信息，如果没有则使用默认值
        if detection_info:
            bbox = detection_info.get('bbox', [0, 0, 100, 100])
            label = detection_info.get('class_name', 'person')
            confidence = detection_info.get('confidence', 0.5)

            x1, y1, x2, y2 = bbox
            w = x2 - x1
            h = y2 - y1
            x = x1
            y = y1
        else:
            # 使用默认值
            x, y, w, h = 0, 0, 100, 100
            label = "person"
            confidence = 0.5

        # 构造提示词
        prtmpt_location = f'你的位置是{self.default_location},当前时间为{time_str}。'
        prtmpt_principle = '请仔细分析这个人在车站环境中的行为，只有明确看到异常、危险或可疑行为时才报告。'
        prtmpt_attention = f'请仔细关注图中坐标为xy坐标分别为{x},{y}，高度和宽度为{h},{w}区域内的{label}。'
        prtmpt_restult = '如果行为正常，请回答"情况正常"；若出现异常，请严格按照{时间，地点，情况，解决方案}输出json格式。'
        prtmpt_language = '使用中文回答。'

        prompt = prtmpt_principle + prtmpt_location + prtmpt_attention + prtmpt_restult + prtmpt_language
        print(prompt)
        return self.analyze_image(image_array, prompt)