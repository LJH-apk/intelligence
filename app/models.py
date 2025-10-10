# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：models.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/9 18:33 
@PyVersion ：3.10 arm64
'''

from app import db
from datetime import datetime

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Student {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<User {self.user_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'password': self.password
        }
