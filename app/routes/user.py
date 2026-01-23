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

from app.service.user_service import UserService

bp = Blueprint('user', __name__)

@bp.route('/users',methods=['GET'])
def get_users():
    """获取所有用户"""
    try:
        users = UserService.get_all_users()
        return jsonify({
            'code': 200,
            'status': 'success',
            'users': [user.to_dict() for user in users]
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': str(e)
        })

@bp.route('/creat',methods=['POST'])
def create_user():
    """创建用户"""
    try:
        data = request.get_json()

        required_fields = ['user_name', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'code': 400,
                    'status': 'error',
                    'message':f'字段{field}是必须的'
                })

            user = UserService.create_user(
                user_name=data['user_name'],
                password=data['password']
            )
            return jsonify({
                'code': 201,
                'status': 'success',
                'user': user.to_dict()
            })
    except ValueError as e:
        return jsonify({
            'code': 400,
            'status': 'error',
            'message': str(e)
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': str(e)
        })

@bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户信息"""
    try:
        data = request.get_json()

        # 过滤不允许更新字段
        allowed_fields = ['user_name', 'password']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        user = UserService.update_user(user_id, **update_data)

        if user:
            return jsonify({
                'code': 200,
                'status': 'success',
                "message":'用户更新成功',
                'user': user.to_dict()
            })
        else:
            return jsonify({
                'code': 404,
                'status': 'error',
                'message': '用户不存在'
            })

    except ValueError as e:
        return jsonify({
            'code': 400,
            'status': 'error',
            'message': str(e)
        })
    except Exception as e:
        print(e)
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': str(e)
        })
@bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    try:
        user = UserService.delete_user(user_id)

        if user:
            return jsonify({
                'code': 200,
                'status': 'success',
                'message': '用户删除成功'
            })
        else:
            return jsonify({
                'code': 404,
                'status': 'error',
                'message': '用户不存在'
            })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': str(e)
        })
