#!/usr/bin/env python
"""
Balenciaga 监控调度器启动脚本
用于启动定时任务调度器，监控爬虫运行并发送钉钉通知
"""
import os
import time
import traceback
import logging
from datetime import datetime

# 确保logs目录存在
os.makedirs("logs", exist_ok=True)

# 导入并调用自定义日志设置函数
from src.common.logger import setup_logger, get_logger

# 设置日志配置 - 确保在获取logger前调用
setup_logger()

# 获取日志记录器
logger = get_logger("scheduler_runner")

# 添加一个特定的文件处理器，用于记录调度器启动日志
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
file_handler = logging.FileHandler(f"logs/scheduler_{timestamp}.log", encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)


def ensure_deps():
    """确保所需依赖已安装"""
    try:
        import pandas
        import schedule
        logger.info("所有依赖已安装")
    except ImportError as e:
        logger.error(f"缺少必要的依赖: {str(e)}")
        logger.info("正在安装所需依赖...")

        # 安装依赖
        import subprocess
        try:
            subprocess.check_call(["pip", "install", "pandas", "schedule"])
            logger.info("依赖安装完成")
        except Exception as e:
            logger.error(f"安装依赖失败: {str(e)}")
            return False

    return True


def main():
    """主函数，启动调度器"""
    logger.info("=" * 50)
    logger.info("Balenciaga 监控调度器启动")
    logger.info("=" * 50)

    # 检查依赖
    if not ensure_deps():
        logger.error("缺少必要依赖，无法启动调度器")
        return

    # 导入调度器模块
    try:
        # 确保导入调度器之前已经正确设置了日志系统
        from src.scheduler import BalenciagaScheduler
    except ImportError as e:
        logger.error(f"导入调度器模块失败: {str(e)}")
        logger.error(traceback.format_exc())
        return

    # 创建并启动调度器
    try:
        logger.info("创建调度器实例...")
        scheduler = BalenciagaScheduler()

        logger.info("启动调度器...")
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("用户中断，调度器退出")
    except Exception as e:
        logger.error(f"调度器运行过程中出错: {str(e)}")
        logger.error(traceback.format_exc())

        # 等待30秒后尝试重启
        logger.info("30秒后尝试重启调度器...")
        time.sleep(30)
        main()  # 递归调用实现重启


if __name__ == "__main__":
    main()
