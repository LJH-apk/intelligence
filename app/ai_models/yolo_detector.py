# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：yolo_detector.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/26 20:09 
@PyVersion ：3.10 arm64
'''
import logging
from datetime import datetime

import cv2
from ultralytics.models import YOLO

logger = logging.getLogger(__name__)

class YOLODetector:
    def __init__(self, model_path='yolov11n.pt'):
        self.model = None
        self.model_path = model_path
        self.load_mode()

    def load_mode(self):
        """加载模型"""
        try:
            logger.info(f"Loading YOLO model from {self.model_path}")
            self.model = YOLO(self.model_path)
            logger.info(f"YOLO model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"YOLO model loading error: {e}")
            raise

    def detect(self, frame, conf_threshold = 0.5):
        """
                使用YOLO进行目标检测

                Args:
                    frame: 输入图像帧
                    conf_threshold: 置信度阈值

                Returns:
                    List[dict]: 检测结果列表
                """

        if self.model is None:
            raise RuntimeError("YOLO model not loaded")

        try:
            #检测
            results = self.model.detect(frame, conf=conf_threshold, verbose=False)

            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        cls = int(box.cls[0].cpu().numpy())
                        class_name = self.model.names[cls]

                        #关注人物
                        if class_name == "person":
                            detections.append({
                                'type': 'person',
                                'class_name': class_name,
                                'bbox': [float(x1), float(y1), float(x2), float(y2)],
                                'confidence': float(conf),
                                'timestamp': datetime.now().isoformat()
                            })

            return detections

        except Exception as e:
            logger.error(f"YOLO model detection error: {e}")
            return []

    def draw_detections(self, frame, detections):
        """在图像上绘制检测框"""
        for detection in detections:
            if detection['type'] == 'person':
                x1, y1, x2, y2 = detection['bbox']
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                label = f"Person {detection['confidence']:.2f}"
                cv2.putText(frame, label, (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame

