# --coding:utf-8--
# Author:XianYi
# Time: 202005
import inspect
import os

real_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
import sys
import logging

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
        logging.info(message)
        print(111111111)
        caller = inspect.currentframe().f_back
        caller_name = caller.f_code.co_name
        caller_line = caller.f_lineno
        caller_module = inspect.getmodule(caller).__name__

        print("Caller Name:", caller_name)
        print("Caller Line Number:", caller_line)
        print("Caller Module:", caller_module)

    @staticmethod
    def warning(message):
        logging.warning(message)

    @staticmethod
    def error(message):
        logging.error(message)

    @staticmethod
    def debug(message):
        logging.debug(message)
