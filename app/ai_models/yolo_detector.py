# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：yolo_detector.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/26 20:09 
@PyVersion ：3.10 arm64
'''
# models/yolo_detector.py
import logging
from datetime import datetime
import cv2
import os
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class YOLODetector:
    def __init__(self, model_path='yolov8n.pt'):
        self.model = None
        self.model_path = model_path
        self.load_model()

    def load_model(self):
        """加载模型"""
        try:
            # 检查模型文件是否存在
            if not os.path.exists(self.model_path):
                logger.error(f"YOLO模型文件不存在: {self.model_path}")
                logger.info("尝试自动下载YOLOv8n模型...")
                self._download_model()
                return

            logger.info(f"从 {self.model_path} 加载YOLO模型")
            self.model = YOLO(self.model_path)
            logger.info(f"YOLO模型加载成功: {self.model_path}")

            # 测试模型是否正常工作
            self._test_model()

        except Exception as e:
            logger.error(f"YOLO模型加载错误: {e}")
            # 尝试使用默认模型
            self._use_default_model()

    def _download_model(self):
        """自动下载默认模型"""
        try:
            logger.info("正在下载YOLOv8n预训练模型...")
            self.model = YOLO('yolov8n.pt')
            logger.info("YOLOv8n模型下载成功")

            # 保存模型到指定路径供以后使用
            if hasattr(self.model, 'model'):
                import torch
                torch.save(self.model.model.state_dict(), self.model_path)
                logger.info(f"模型已保存到: {self.model_path}")

        except Exception as e:
            logger.error(f"模型下载失败: {e}")
            raise

    def _use_default_model(self):
        """使用默认模型作为备选"""
        try:
            logger.info("尝试使用默认YOLOv8n模型...")
            self.model = YOLO('yolov8n.pt')
            logger.info("默认YOLOv8n模型加载成功")
        except Exception as e:
            logger.error(f"默认模型也加载失败: {e}")
            raise RuntimeError("无法加载任何YOLO模型")

    def _test_model(self):
        """测试模型是否正常工作"""
        try:
            # 创建一个测试图像
            test_image = cv2.imread('test_image.jpg') if os.path.exists('test_image.jpg') else None
            if test_image is None:
                # 创建一个简单的测试图像
                test_image = self._create_test_image()

            # 进行测试检测
            results = self.model(test_image, verbose=False)
            logger.info("模型测试成功，可以正常进行检测")

        except Exception as e:
            logger.warning(f"模型测试失败，但可能仍可使用: {e}")

    def _create_test_image(self):
        """创建一个测试图像"""
        import numpy as np
        # 创建一个400x600的测试图像
        img = np.ones((400, 600, 3), dtype=np.uint8) * 255
        # 添加一些简单形状
        cv2.rectangle(img, (100, 100), (200, 300), (0, 0, 255), -1)
        cv2.rectangle(img, (300, 150), (400, 250), (0, 255, 0), -1)
        return img

    def detect(self, frame, conf_threshold=0.5):
        """使用YOLO进行目标检测"""
        if self.model is None:
            raise RuntimeError("YOLO模型未加载")

        try:
            # 执行检测
            results = self.model(frame, conf=conf_threshold, verbose=False)

            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        cls = int(box.cls[0].cpu().numpy())
                        class_name = self.model.names[cls]

                        # 只关注人物
                        if class_name == "person":
                            detections.append({
                                'type': 'person',
                                'class_name': class_name,
                                'bbox': [float(x1), float(y1), float(x2), float(y2)],
                                'confidence': float(conf),
                                'timestamp': datetime.now().isoformat()
                            })

            logger.debug(f"检测到 {len(detections)} 个人物")
            return detections

        except Exception as e:
            logger.error(f"YOLO检测错误: {e}")
            return []

    def draw_detections(self, frame, detections):
        """在图像上绘制检测框"""
        for detection in detections:
            if detection['type'] == 'person':
                x1, y1, x2, y2 = detection['bbox']
                # 绘制边界框
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                # 绘制标签
                label = f"Person {detection['confidence']:.2f}"
                cv2.putText(frame, label, (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame