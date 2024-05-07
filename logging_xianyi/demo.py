# --coding:utf-8--
# Author:XianYi
# Time: 202005
import os
real_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
import sys
import logging_modi
sys.path.append(real_path + '/connections')
sys.path.append(real_path + '/logging_xianyi')
sys.path.append(real_path + '/utils')
import platform
sysstr = platform.system()
if (sysstr == "Windows"):
    sys.path.append(real_path)
    sys.path.append(real_path + '\\connections')
    sys.path.append(real_path + '\\logging_xianyi')
    sys.path.append(real_path + '\\utils')
from log_config_xianyi import LogConfigXianYi
class demo:
    def __init__(self, log_name):
        LogConfigXianYi(log_name)


if __name__ == '__main__':
    demo('er')
    logging_modi.error(333)
