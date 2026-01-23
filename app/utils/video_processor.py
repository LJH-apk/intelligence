# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：video_processor.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/27 15:19 
@PyVersion ：3.10 arm64
'''

import cv2
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class VideoProcessor:
    def __init__(self, yolo_detector, qwen_analyzer, alert_manager):
        self.yolo_detector = yolo_detector
        self.qwen_analyzer = qwen_analyzer
        self.alert_manager = alert_manager
        self.frame_count = 0
        self.processing_interval = 30  # 增加间隔，减少分析频率
        self.is_processing = False
        self.last_analysis_time = datetime.now()

    def process_frame(self, frame):
        """处理视频帧"""
        if self.is_processing:
            return [], frame

        self.frame_count += 1

        try:
            # YOLO粗筛检测
            detections = self.yolo_detector.detect(frame)

            # 定期进行精细检测，并添加时间间隔控制
            current_time = datetime.now()
            time_since_last = (current_time - self.last_analysis_time).total_seconds()

            if (self.frame_count % self.processing_interval == 0 and
                    detections and time_since_last > 2.0):  # 至少2秒间隔
                self._async_fine_detection(frame, detections)
                self.last_analysis_time = current_time

            # 绘制检测框
            annotated_frame = self.yolo_detector.draw_detections(frame.copy(), detections)

            return detections, annotated_frame

        except Exception as e:
            logger.error(f"Frame processing error: {e}")
            return [], frame

    # video_processor.py 中的 _async_fine_detection 方法修改
    def _async_fine_detection(self, frame, detections):
        """异步进行精细检测"""
        import threading

        def analyze_detections():
            self.is_processing = True
            try:
                for detection in detections:
                    if detection['type'] == 'person' and detection['confidence'] > 0.6:
                        x1, y1, x2, y2 = detection['bbox']
                        # 确保ROI有效
                        if (x2 - x1) > 50 and (y2 - y1) > 50:
                            roi = frame[int(y1):int(y2), int(x1):int(x2)]

                            if roi.size > 0:
                                # 准备检测信息
                                detection_info = {
                                    'bbox': detection['bbox'],
                                    'class_name': detection['class_name'],
                                    'confidence': detection['confidence']
                                }

                                # 使用千问API分析行为（现在只传递两个参数）
                                analysis_result = self.qwen_analyzer.analyze_behavior(roi, detection_info)

                                if analysis_result.get('success', False):
                                    # 检查预警
                                    self.alert_manager.check_analysis_for_alerts(analysis_result, detection)
            except Exception as e:
                logger.error(f"Fine detection error: {e}")
            finally:
                self.is_processing = False

        # 在新线程中执行分析
        thread = threading.Thread(target=analyze_detections)
        thread.daemon = True
        thread.start()

    # video_processor.py 中的 process_single_image 方法修改
    def process_single_image(self, image_array):
        """处理单张图片"""
        try:
            # YOLO检测，降低置信度阈值以提高检测率
            detections = self.yolo_detector.detect(image_array, conf_threshold=0.4)

            fine_results = []
            for detection in detections:
                if detection['type'] == 'person' and detection['confidence'] > 0.4:
                    x1, y1, x2, y2 = detection['bbox']
                    # 确保ROI有效
                    if (x2 - x1) > 30 and (y2 - y1) > 30:
                        roi = image_array[int(y1):int(y2), int(x1):int(x2)]

                        if roi.size > 0:
                            # 准备检测信息
                            detection_info = {
                                'bbox': detection['bbox'],
                                'class_name': detection['class_name'],
                                'confidence': detection['confidence']
                            }

                            # 千问分析
                            analysis_result = self.qwen_analyzer.analyze_behavior(roi, detection_info)

                            # 检查预警
                            alerts = self.alert_manager.check_analysis_for_alerts(analysis_result, detection)

                            fine_results.append({
                                'detection': detection,
                                'analysis': analysis_result,
                                'alerts': alerts
                            })

            return {
                'coarse_detections': detections,
                'fine_analysis': fine_results
            }

        except Exception as e:
            logger.error(f"Single image processing error: {e}")
            return {'error': str(e)}