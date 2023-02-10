import logging
from logging.handlers import RotatingFileHandler


def logging_fun(log_file: str):
    # 创建日志的记录等级设
    logging.basicConfig(level=logging.INFO)
    # 创建日志记录器，指明日志保存的路径，每个日志文件的最大值，保存的日志文件个数上限
    log_handle = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
    # 创建日志记录的格式
    formatter = logging.Formatter("%(message)s")
    # formatter = logging.Formatter("format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s-%(funcName)s',")
    # 为创建的日志记录器设置日志记录格式
    log_handle.setFormatter(formatter)
    # 为全局的日志工具对象添加日志记录器
    logging.getLogger().addHandler(log_handle)
    # logging.warning('用来用来打印警告信息')
    # logging.error('一般用来打印一些错误信息')
    # logging.critical('用来打印一些致命的错误信息，等级最高')


def logging_fun2(log_file: str):
    # 创建日志的记录等级设
    logging.basicConfig(level=logging.INFO)
    # 创建日志记录器，指明日志保存的路径，每个日志文件的最大值，保存的日志文件个数上限
    log_handle = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
    # 创建日志记录的格式
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    # formatter = logging.Formatter("format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s-%(funcName)s',")
    # 为创建的日志记录器设置日志记录格式
    log_handle.setFormatter(formatter)
    # 为全局的日志工具对象添加日志记录器
    logging.getLogger().addHandler(log_handle)

