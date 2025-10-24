# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：information_service.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/25 00:50 
@PyVersion ：3.10 arm64
'''
from click import DateTime
from typing import Optional, List

from app import db
from app.models import Information


class InformationService:

    @staticmethod
    def create_info(time: DateTime, type: str, message: str) -> Optional[Information]:
        """创建警告日志信息"""
        info = Information(time=time, type=type, message=message)
        db.session.add(info)
        db.session.commit()
        return info

    @staticmethod
    def get_info() -> List[Information]:
        """获取所有警告日志"""
        return Information.query.all()
