# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：config.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/9 18:29 
@PyVersion ：3.10 arm64
'''

# config.py
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.sql')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get("DEBUG", True)
    PORT = 8080

    # Dashscope API配置
    DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY', 'sk-6963e4b8bb5840de98983e63ed1ae012')

    # 模型配置 - 使用绝对路径
    YOLO_MODEL_PATH = os.path.join(basedir, 'yolo11n.pt')  # 修正路径

    # 系统配置
    PROCESSING_INTERVAL = int(os.environ.get('PROCESSING_INTERVAL', 10))
    MAX_ALERTS = int(os.environ.get('MAX_ALERTS', 100))
    ALERT_RETENTION_DAYS = int(os.environ.get('ALERT_RETENTION_DAYS', 7))

    # 预警规则
    WARNING_RULES = {
        "suspicious_behavior": ["打架", "斗殴", "追逐", "攀爬", "翻越"],
        "safety_hazard": ["烟火", "吸烟", "明火", "漏电", "摔倒", "晕倒"],
        "security_risk": ["可疑包裹", "破坏设备", "非法进入"],
        "emergency": ["急救", "晕厥", "突发疾病", "事故"]
    }