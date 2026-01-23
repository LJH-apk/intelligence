# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：run.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/9 18:43 
@PyVersion ：3.10 arm64
'''

# run.py
import logging
from app import create_app
from flasgger import Swagger

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=8080)