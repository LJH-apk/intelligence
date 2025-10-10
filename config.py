# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：config.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/9 18:29 
@PyVersion ：3.10 arm64
'''

import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "os.environ.get('SECRET_KEY')"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.sql')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get("DEBUG")
    PORT = 8080