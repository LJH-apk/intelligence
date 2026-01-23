# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：__init__.py.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/9 18:29 
@PyVersion ：3.10 arm64
'''
# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    CORS(app)

    # 注册蓝本
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.students import bp as students_bp
    app.register_blueprint(students_bp)

    from app.routes.user import bp as user_bp
    app.register_blueprint(user_bp)

    from app.routes.api import bp as api_bp
    app.register_blueprint(api_bp)

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app