# --coding:utf-8--
# Author:XianYi
# Time: 202006
import os
from os.path import join, getsize
real_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
import sys
sys.path.append(real_path + '/utils')
import platform
sysstr = platform.system()
if (sysstr == "Windows"):
    sys.path.append(real_path + '\\utils')
import logging_modi
from log_config_xianyi import LogConfigTwitter
from util_twitter import UtilTwitter
LogConfigTwitter("delete_log")


class DeleteLog:
    def delete_log(self):
        log_file_dir = os.path.abspath(os.path.dirname(__file__)) + '/log_file/'
        for root, dirs, files in os.walk(log_file_dir):
            # 生成日志留存时间
            TTL = 2
            TTL_list = [TTL for TTL in files if TTL.find('TTL') != -1]
            if 0 != len(TTL_list):
                TTL = int(TTL_list[0].split('=')[-1])
                files.remove(TTL_list[0])
            path_name_size_list = [(join(root, name), name, getsize(join(root, name))) for name in files]
            path_list = [join(root, name) for name in files]
            name_list = [name.split('_')[-1].split('.')[0] for name in files]
            name_list = list(set(name_list))
            logging_modi.info("文件夹{}-------日志保留{}天--------有日志{}天:{}".format(root.split('/')[-1], TTL, len(name_list), name_list))
            name_list.sort()
            if len(name_list) > TTL:
                for path in path_list:
                    for i in range(len(name_list) - TTL):
                        if name_list[i] in path:
                            os.remove(path)
                            logging_modi.info("删除文件：{}".format(path))

    def get_file_size(self):
        log_file_dir = os.path.abspath(os.path.dirname(__file__)) + '/log_file/'
        size = 0
        for root, dirs, files in os.walk(log_file_dir):
            size += sum([getsize(join(root, name)) for name in files])
        size_MB = format(size/(1024*1024), '.3f')
        if int(size_MB) > 1024:
            UtilTwitter.send_mail('日志量大于1G，请尽快删除')


DeleteLog().get_file_size()
