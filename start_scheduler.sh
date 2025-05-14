#!/bin/bash

# Balenciaga 监控调度器启动脚本
echo "=========================================="
echo "Balenciaga 监控调度器启动脚本"
echo "=========================================="
echo ""

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "错误: 找不到Python，请确保已安装Python"
    exit 1
fi

# 检查必要依赖
echo "检查必要依赖..."
python -c "import pandas" &> /dev/null
if [ $? -ne 0 ]; then
    echo "安装pandas依赖..."
    pip install pandas
fi

python -c "import schedule" &> /dev/null
if [ $? -ne 0 ]; then
    echo "安装schedule依赖..."
    pip install schedule
fi

echo "依赖检查完成"
echo ""

# 创建logs目录
mkdir -p logs

# 当前脚本路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 检查是否以守护进程模式运行
if [ "$1" == "daemon" ]; then
    echo "以守护进程模式启动调度器..."
    # 使用nohup命令在后台运行，输出重定向到日志文件
    nohup python scheduler_runner.py > logs/scheduler_daemon.log 2>&1 &
    echo $! > scheduler.pid
    echo "调度器已在后台启动，PID: $(cat scheduler.pid)"
    echo "可以使用 'tail -f logs/scheduler_daemon.log' 查看日志"
    echo "使用 '$0 stop' 停止调度器"
else
    # 检查是否是停止命令
    if [ "$1" == "stop" ]; then
        if [ -f scheduler.pid ]; then
            PID=$(cat scheduler.pid)
            echo "正在停止调度器，PID: $PID"
            kill $PID 2> /dev/null
            if [ $? -eq 0 ]; then
                echo "调度器已停止"
                rm scheduler.pid
            else
                echo "调度器未运行或PID无效"
                rm scheduler.pid
            fi
        else
            echo "找不到PID文件，调度器可能未运行"
        fi
    else
        echo "启动Balenciaga监控调度器..."
        echo "提示: 按Ctrl+C停止监控任务"
        echo ""
        # 启动调度器
        python scheduler_runner.py
    fi
fi 