# --coding:utf-8--
# Author:XianYi
# Time: 202005
import os

real_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
import sys
import logging_modi
import platform
from logging_xianyi.log_config_xianyi import LogConfigXianYi

# 重写方法，但一是还不需要，二是重写失败
class logging_xianyi:
    # def __init__(self, log_name):
    #     LogConfigXianYi(log_name)

    @staticmethod
    def info(message, user_name):
        LogConfigXianYi(user_name)
        logging_modi.info(message)

    @staticmethod
    def warning(message, user_name):
        LogConfigXianYi(user_name)
        logging_modi.warning(message)

    @staticmethod
    def error(message, user_name):
        LogConfigXianYi(user_name)
        logging_modi.error(message)

    @staticmethod
    def debug(message, user_name):
        LogConfigXianYi(user_name)
        logging_modi.debug(message)

    @staticmethod
    def critical(message, user_name):
        LogConfigXianYi(user_name)
        logging_modi.critical(message)
