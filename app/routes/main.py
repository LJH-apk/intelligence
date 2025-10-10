# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：main.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/9 18:33 
@PyVersion ：3.10 arm64
'''
from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')
