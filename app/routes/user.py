# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：user.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/9 19:26 
@PyVersion ：3.10 arm64
'''

from flask import Blueprint, request, jsonify, flash

from app import db
from app.models import User

bp = Blueprint('user', __name__)
@bp.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')

        new_user = User(user_name=user_name, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("新建用户成功", "success")
        return jsonify({
            "code": 200,
            "status": "success",
            "message":{
                "name":user_name,
                "info":"ok"
            }
        })
