# --coding:utf-8--
# Author:XianYi
# Time: 202005
"""
logging配置
"""
import os
import time
import logging_modi.config


class LogConfigXianYi:
    def __init__(self, log_name):
        self.log_config(log_name)

    @staticmethod
    def __get_local_time():
        # 获取当前时间
        time_now = int(time.time())
        # 转换成localtime
        time_local = time.localtime(time_now)
        # 转换成新的时间格式(2016-05-09 18:59:20)
        dt = time.strftime("%Y%m%d", time_local)
        return dt

    def log_config(self, log_name):
        # 定义三种日志输出格式 开始
        debug_format = '[%(asctime)s][%(filename)s:%(lineno)d]' \
                          '%(message)s'  # 其中name为getlogger指定的名字

        std_format = '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'

        chat_format = '[%(levelname)s][%(asctime)s] %(message)s'
        # 定义日志输出格式 结束
        logfile_dir = os.path.dirname(os.path.abspath(__file__)) + '/log_file/user/' + str(log_name)  # log文件的目录
        logfile_name = '{}.log'.format(self.__get_local_time())  # log文件名
        logfile_detail_name = '{}_detail.log'.format(self.__get_local_time())  # log文件名
        error_log_dir = os.path.dirname(os.path.abspath(__file__)) + '/log_file/error/'
        error_log_name = 'error_{}.log'.format(self.__get_local_time())  # log文件名
        # 如果不存在定义的日志目录就创建一个
        if not os.path.isdir(os.path.dirname(os.path.abspath(__file__)) + '/log_file/'):
            os.mkdir(os.path.dirname(os.path.abspath(__file__)) + '/log_file/')
        if not os.path.isdir(os.path.dirname(os.path.abspath(__file__)) + '/log_file/user/'):
            os.mkdir(os.path.dirname(os.path.abspath(__file__)) + '/log_file/user/')
        if not os.path.isdir(logfile_dir):
            os.mkdir(logfile_dir)
        if not os.path.isdir(error_log_dir):
            os.mkdir(error_log_dir)
        # log文件的全路径
        logfile_path = os.path.join(logfile_dir, logfile_name)
        logfile_detail_path = os.path.join(logfile_dir, logfile_detail_name)
        error_log_path = os.path.join(error_log_dir, error_log_name)
        # log配置字典
        LOGGING_DIC = {
            'version': 1,
            # 是否禁用已经存在的logger实例
            'disable_existing_loggers': False,
            # 定义日志 格式化的 工具
            'formatters': {
                'debug_format': {
                    'format': debug_format
                },
                'std_format': {
                    'format': std_format
                },
                'chat_format': {
                    'format': chat_format
                },
            },
            # 过滤
            'filters': {},  # jango此处不同
            'handlers': {
                # 打印到终端的日志
                'std': {
                    'level': 'DEBUG',
                    'class': 'logging_modi.StreamHandler',  # 打印到屏幕
                    'formatter': 'std_format'
                },
                # 打印到文件的日志,收集info及以上的日志
                'chat': {
                    'level': 'INFO',
                    'class': 'logging_modi.handlers.RotatingFileHandler',  # 保存到文件
                    'formatter': 'chat_format',
                    'filename': logfile_path,  # 日志文件路径
                    'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
                    'backupCount': 10,
                    'encoding': 'utf-8',  # 日志文件的编码，再也不用担心中文log乱码了
                },
                'detail': {
                    'level': 'DEBUG',
                    'class': 'logging_modi.handlers.RotatingFileHandler',  # 保存到文件
                    'formatter': 'debug_format',
                    'filename': logfile_detail_path,  # 日志文件
                    'maxBytes': 1024 * 1024 * 1024 * 1,  # 日志大小 1G
                    'backupCount': 10,
                    'encoding': 'utf-8',  # 日志文件的编码，再也不用担心中文log乱码了
                },
                # 打印到文件的日志,收集error及以上的日志
                'error': {
                    'level': 'ERROR',
                    'class': 'logging_modi.handlers.RotatingFileHandler',  # 保存到文件
                    'formatter': 'chat_format',
                    'filename': error_log_path,  # 日志文件
                    'maxBytes': 1024 * 1024 * 50,  # 日志大小 5M
                    'backupCount': 5,
                    'encoding': 'utf-8',  # 日志文件的编码，再也不用担心中文log乱码了
                },
            },
            # logger实例
            'loggers': {
                # 默认的logger应用如下配置
                '': {
                    'handlers': ['chat', 'detail', 'error'],  # 这里把上面定义的两个handler都加上，即log数据既写入文件又打印到屏幕
                    'level': 'DEBUG',
                    'propagate': True,  # 向上（更高level的logger）传递
                },
                # logging_xianyi.getLogger(__name__)拿到的logger配置
                # 这样我们再取logger对象时logging.getLogger(__name__)，不同的文件__name__不同，这保证了打印日志时标识信息不同，
                # 但是拿着该名字去loggers里找key名时却发现找不到，于是默认使用key=''的配置
            },
        }
        logging_modi.config.dictConfig(LOGGING_DIC)  # 导入上面定义的logging配置
        logging_modi.getLogger(__name__)  # 生成一个log实例


if __name__ == '__main__':
    LogConfigXianYi("ww")