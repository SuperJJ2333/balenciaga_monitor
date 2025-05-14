#!/usr/bin/env python
"""
测试scheduler导入和运行
"""
import sys
import os
import traceback

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    print("尝试导入BalenciagaScheduler...")
    from src.scheduler import BalenciagaScheduler
    
    print("创建BalenciagaScheduler实例...")
    scheduler = BalenciagaScheduler()
    
    print("启动调度器...")
    scheduler.start()
except Exception as e:
    print(f"错误: {type(e).__name__}: {str(e)}")
    print("详细错误信息:")
    print(traceback.format_exc()) 