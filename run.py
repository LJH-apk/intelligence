# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：run.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/9 18:43 
@PyVersion ：3.10 arm64
'''

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True,port=8080)
