#!/usr/bin/env python
"""
Balenciaga监控调度器启动脚本
处理Python导入路径问题并启动调度器
"""
import os
import sys
import traceback
import datetime

# 将当前目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 确保logs目录存在
logs_dir = os.path.join(current_dir, 'logs')
os.makedirs(logs_dir, exist_ok=True)

# 设置日志文件
log_file = os.path.join(logs_dir, f"scheduler_debug_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

def log_message(message):
    """记录消息到屏幕和日志文件"""
    print(message)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(message + "\n")

def print_separator():
    log_message("=" * 60)

if __name__ == "__main__":
    print_separator()
    log_message("Balenciaga 监控调度器启动")
    log_message(f"日志文件: {log_file}")
    print_separator()
    
    try:
        # 配置Python导入路径
        log_message("Python导入路径:")
        for p in sys.path:
            log_message(f" - {p}")
            
        # 查看src目录中的common目录
        try:
            common_dir = os.path.join(current_dir, 'src', 'common')
            log_message(f"检查common目录: {common_dir}")
            if os.path.exists(common_dir):
                log_message("common目录存在")
                for file in os.listdir(common_dir):
                    log_message(f" - {file}")
            else:
                log_message("common目录不存在")
        except Exception as e:
            log_message(f"检查common目录时出错: {str(e)}")
            
        # 动态导入调度器
        log_message("正在导入Balenciaga调度器...")
        from src.scheduler import BalenciagaScheduler
        
        # 创建并启动调度器
        log_message("正在初始化调度器...")
        scheduler = BalenciagaScheduler()
        
        log_message("正在启动调度器...")
        log_message("调度器已启动，按Ctrl+C可终止运行")
        print_separator()
        
        scheduler.start()
    except ModuleNotFoundError as e:
        log_message(f"错误: 找不到模块 {e}")
        log_message("可能是因为Python导入路径配置错误。")
        log_message("请确保按照以下方式运行：")
        log_message("   python run_scheduler.py")
        log_message("而不是直接运行src/scheduler.py文件")
        log_message("详细错误信息:")
        log_message(traceback.format_exc())
    except KeyboardInterrupt:
        log_message("\n用户终止，调度器已停止")
    except Exception as e:
        log_message(f"启动调度器时出错: {str(e)}")
        log_message("详细错误信息:")
        log_message(traceback.format_exc()) 