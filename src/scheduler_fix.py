"""
修复脚本 - 解决Monitor抽象类实例化问题
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def is_monitor_abstract():
    """检查Monitor类是否为抽象类，以及哪些方法是抽象的"""
    from src.common.monitor import Monitor
    
    # 检查是否有__abstractmethods__属性
    if hasattr(Monitor, "__abstractmethods__"):
        abstract_methods = Monitor.__abstractmethods__
        print(f"Monitor是抽象类，抽象方法: {abstract_methods}")
        return True, abstract_methods
    else:
        print("Monitor不是抽象类")
        return False, []

def list_monitor_subclasses():
    """列出所有Monitor的子类"""
    import inspect
    from src.common.monitor import Monitor
    
    # 遍历所有模块，查找Monitor的子类
    subclasses = []
    for module_name in sys.modules:
        if module_name.startswith('src.crawler.'):
            module = sys.modules[module_name]
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Monitor) and obj != Monitor:
                    subclasses.append((name, obj))
    
    print(f"找到 {len(subclasses)} 个Monitor子类:")
    for name, cls in subclasses:
        print(f" - {name} (在 {cls.__module__})")
    
    return subclasses

def check_crawler_classes():
    """检查crawler目录下的所有爬虫类"""
    crawler_dir = os.path.join(project_root, "src", "crawler")
    print(f"扫描目录: {crawler_dir}")
    
    # 列出所有Python文件
    python_files = [f for f in os.listdir(crawler_dir) if f.endswith('.py') and f != '__init__.py']
    print(f"找到 {len(python_files)} 个Python文件:")
    for file in python_files:
        print(f" - {file}")
    
    # 对每个文件进行分析
    for file in python_files:
        module_name = file[:-3]  # 去除.py后缀
        full_module = f"src.crawler.{module_name}"
        
        try:
            # 尝试导入模块
            __import__(full_module)
            module = sys.modules[full_module]
            
            # 查找模块中的类
            import inspect
            classes = []
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and obj.__module__ == full_module:
                    classes.append(name)
            
            print(f"{file} 中的类: {', '.join(classes)}")
        except Exception as e:
            print(f"分析 {file} 时出错: {str(e)}")

def run_fix():
    """运行修复脚本"""
    print("=" * 50)
    print("开始修复Monitor抽象类实例化问题")
    print("=" * 50)
    
    # 检查Monitor是否为抽象类
    is_abstract, abstract_methods = is_monitor_abstract()
    
    # 列出所有Monitor子类
    subclasses = list_monitor_subclasses()
    
    # 检查crawler目录下的爬虫类
    check_crawler_classes()
    
    print("\n修复建议:")
    print("1. 在调度器中确保不尝试实例化Monitor抽象基类")
    print("2. 在_load_crawlers方法中，确保只导入Monitor的具体子类")
    print("3. 确保没有直接导入并实例化Monitor的代码")

if __name__ == "__main__":
    run_fix() 