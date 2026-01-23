# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：security_service.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/11/7 11:03 
@PyVersion ：3.10 arm64
'''

# app/service/security_service.py
import logging
import time
from app.ai_models.yolo_detector import YOLODetector
from app.ai_models.qwen_analyzer import QwenAnalyzer
from app.utils.alert_manager import AlertManager
from app.utils.video_processor import VideoProcessor
from config import Config

logger = logging.getLogger(__name__)


class SecurityService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecurityService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.yolo_detector = None
            self.qwen_analyzer = None
            self.alert_manager = None
            self.video_processor = None
            self.is_running = False
            self._initialized = True

    def initialize(self):
        """初始化系统组件"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"初始化系统组件 (尝试 {attempt + 1}/{max_retries})")

                # 初始化YOLO检测器
                self.yolo_detector = YOLODetector(Config.YOLO_MODEL_PATH)

                # 初始化千问分析器
                self.qwen_analyzer = QwenAnalyzer(Config.DASHSCOPE_API_KEY)

                # 初始化预警管理器
                self.alert_manager = AlertManager()

                # 初始化视频处理器
                self.video_processor = VideoProcessor(
                    self.yolo_detector,
                    self.qwen_analyzer,
                    self.alert_manager
                )

                logger.info("安全系统初始化成功")
                return True

            except Exception as e:
                logger.error(f"系统初始化失败 (尝试 {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    logger.info("等待2秒后重试...")
                    time.sleep(2)
                else:
                    logger.error("系统初始化完全失败")
                    return False

    def start_system(self):
        """启动系统"""
        if not self.video_processor:
            if not self.initialize():
                return False
        self.is_running = True
        logger.info("安全系统已启动")
        return True

    def stop_system(self):
        """停止系统"""
        self.is_running = False
        logger.info("Security system stopped")
        return True

    def get_system_status(self):
        """获取系统状态"""
        status_data = {
            'is_running': self.is_running,
            'is_initialized': self.video_processor is not None,
            'components': {
                'yolo_detector': self.yolo_detector is not None,
                'qwen_analyzer': self.qwen_analyzer is not None,
                'alert_manager': self.alert_manager is not None
            }
        }
        return status_data  # 直接返回数据字典，而不是包装在 'data' 键中

    def analyze_image(self, image_data):
        """分析单张图片"""
        if not self.video_processor:
            if not self.initialize():
                return {'error': '系统未初始化'}

        try:
            import cv2
            import numpy as np

            # 转换图片数据
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                return {'error': '图片解码失败'}

            # 处理图片
            result = self.video_processor.process_single_image(frame)
            return result

        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return {'error': f'图片分析失败: {str(e)}'}