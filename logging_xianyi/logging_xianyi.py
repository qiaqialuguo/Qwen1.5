# --coding:utf-8--
# Author:XianYi
# Time: 202005
import inspect
import os

real_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
import sys
import logging_modi

sys.path.append(real_path  + '/constant')
import platform

sysstr = platform.system()
if (sysstr == "Windows"):
    sys.path.append(real_path)
    sys.path.append(real_path + '\\constant')
from log_config_xianyi import LogConfigXianYi

# 重写方法，但一是还不需要，二是重写失败
class logging_xianyi:
    def __init__(self, log_name):
        LogConfigXianYi(log_name)
        print(666)

    @staticmethod
    def info(message):
        logging_modi.info(message)
        print(111111111)

    @staticmethod
    def warning(message):
        logging_modi.warning(message)

    @staticmethod
    def error(message):
        logging_modi.error(message)

    @staticmethod
    def debug(message):
        logging_modi.debug(message)
