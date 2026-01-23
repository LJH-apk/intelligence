# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：main.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/9 18:33 
@PyVersion ：3.10 arm64
'''
from flask import Blueprint, render_template, send_file

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return send_file("static/main.html")
