@echo off
echo ===========================================
echo Balenciaga 监控调度器启动脚本
echo ===========================================
echo.

REM 检查Python环境
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 找不到Python，请确保已安装Python并添加到系统PATH中
    pause
    exit /b
)

REM 检查必要依赖
echo 检查必要依赖...
python -c "import pandas" >nul 2>nul
if %errorlevel% neq 0 (
    echo 安装pandas依赖...
    pip install pandas
)

python -c "import schedule" >nul 2>nul
if %errorlevel% neq 0 (
    echo 安装schedule依赖...
    pip install schedule
)

echo 依赖检查完成
echo.

REM 创建logs目录
if not exist logs mkdir logs

echo 启动Balenciaga监控调度器...
echo 提示: 关闭此窗口将停止监控任务
echo.

REM 启动调度器
python scheduler_runner.py

REM 如果调度器异常退出，等待用户输入
echo.
echo 调度器已停止运行
pause 