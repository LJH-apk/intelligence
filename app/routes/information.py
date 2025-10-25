# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：information.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/25 00:56 
@PyVersion ：3.10 arm64
'''
from flask import Blueprint, jsonify

from app.service.information_service import InformationService

#TODO  日志信息查询和创建

bp = Blueprint('information', __name__)

@bp.route("/information",methods=['POST'])
def get_information():
    """获取所有信息"""
    try:
        info = InformationService.get_info()
        return jsonify({
            'code': 200,
            'status': 'success',
            'message': [info.to_dict() for info in info]
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': str(e)
        })
