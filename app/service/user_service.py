# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：user_service.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/13 15:05 
@PyVersion ：3.10 arm64
'''
from typing import Optional, List

from app import db
from app.models import User


class UserService:

    @staticmethod
    def create_user(user_name: str, password: str) -> Optional[User]:
        '''创建用户'''
        try:
            if UserService.get_user_by_username(user_name):
                raise ValueError("用户已经存在")

            user = User(user_name=user_name, password=password)
            db.session.add(user)
            db.session.commit()
            return user

        except Exception as e:
            db.session.rollback()
            raise e

        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_all_users() -> List[User]:
        '''获取所有用户'''
        return User.query.all()

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        '''根据id获取'''
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return User.query.filter_by(user_name=username).first()

    @staticmethod
    def update_user(user_id: int, **kwargs) -> Optional[User]:
        '''更新用户信息'''
        try:
            user = UserService.get_user_by_id(user_id)
            if not user:
                return None

            if 'username' in kwargs and kwargs['username'] != user.username:
                if UserService.get_user_by_username(kwargs['username']):
                    raise ValueError("用户名已存在")

            '''更新用户信息表单'''
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            db.session.commit()
            return user

        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_user(user_id: int) -> bool:
        '''删除用户'''
        try:
            user = UserService.get_user_by_id(user_id)
            if not user:
                return False

            db.session.delete(user)
            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            raise e


