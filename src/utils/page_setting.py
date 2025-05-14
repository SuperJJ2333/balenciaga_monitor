import json
import re
import time
import logging
from random import uniform


def get_proxies(proxy_type='non'):
    """

    :param proxy_type:
    :return:
    """
    clash_proxies = {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }
    fiddler_proxies = {
        "http": "http://127.0.0.1:8888",
        "https": "http://127.0.0.1:8888"
    }
    non_proxies = {
        "http": "",
        "https": ""
    }

    if proxy_type == 'clash':
        return clash_proxies
    elif proxy_type == 'fiddler':
        return fiddler_proxies
    else:
        return non_proxies


# 从文件读取cookie
def load_cookies(filename, logging):
    """
    从文件中加载cookies
    :param logging:
    :param filename: cookie文件路径
    :return: cookie字符串
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        logging.error(f"加载cookies失败: {str(e)}")
        return ""


# 配置日志记录器
def configure_logger(monitor_name=None):
    """
    配置日志记录器
    :param monitor_name: 监控器名称，可选
    :return: 配置好的日志记录器
    """
    # 为每个监控器创建唯一的logger，避免复用
    if monitor_name:
        logger = logging.getLogger(f"monitor.{monitor_name}")
    else:
        logger = logging.getLogger("general_logger")
        
    logger.setLevel(logging.DEBUG)  # 设置日志级别

    # 删除所有现有的处理器，确保不会重复添加
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # 创建格式化器
    if monitor_name:
        formatter = logging.Formatter(f'%(asctime)s - %(levelname)s - [{monitor_name}] - %(message)s')
    else:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # 将格式化器添加到处理器
    console_handler.setFormatter(formatter)

    # 将处理器添加到日志记录器
    logger.addHandler(console_handler)
    
    return logger


def random_sleep(min_seconds=0.5, max_seconds=3):
    """
    在指定的最小和最大秒数之间随机停顿，模拟人类行为
    """
    pause_time = uniform(min_seconds, max_seconds)

    time.sleep(pause_time)


def contains_digit(s):
    """
    判断是否含有数字
    :param s:
    :return:
    """
    return bool(re.search(r'\d', s))