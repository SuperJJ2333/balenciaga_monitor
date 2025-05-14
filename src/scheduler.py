"""
监控定时任务调度器
用于定时执行爬虫任务、检测库存变化并发送钉钉通知
"""
import os
import time
import importlib
import schedule
from datetime import datetime
import glob
import sys
import json
import threading

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入项目路径和日志模块
from common.project_path import ProjectPaths
from common.logger import get_logger
from src.ding_sender.ding_sender import DingSender
from src.utils.utils import load_toml

# 创建日志记录器
logger = get_logger("scheduler")


class BalenciagaScheduler:
    """
    Balenciaga监控定时任务调度器
    负责定时执行爬虫任务、检测库存变化并发送钉钉通知
    """

    def __init__(self):
        """初始化调度器"""
        self.project_paths = ProjectPaths()
        self.logger = logger
        self.crawler_dir = os.path.join(self.project_paths.SRC, "crawler")
        self.data_dir = self.project_paths.DATA

        # 循环执行时间
        self.loop_time = 5

        # 每个循环的执行秒数
        self.waiting_time = self.loop_time * 60
        
        # 爬虫之间的等待时间（秒）
        self.sleep_between_crawlers = 2

        # 读取钉钉配置
        try:
            toml_path = os.path.join(self.project_paths(), 'setting.toml')
            config = load_toml(toml_path, self.logger)
            self.ding_url = config['ding_url'].get('url')
            self.ding_secret = config['ding_secret'].get('secret')
            self.ding_token = ""  # Token不需要，保留为空

            # 初始化钉钉发送器
            self.ding_sender = DingSender(self.ding_url, self.ding_secret, self.ding_token)
        except Exception as e:
            self.logger.error(f"初始化钉钉配置失败: {str(e)}")
            raise

        # 初始化爬虫列表
        self.crawlers = self._load_crawlers()
        self.logger.info(f"已加载 {len(self.crawlers)} 个爬虫模块")

    def _load_crawlers(self):
        """加载爬虫模块列表"""
        crawlers = []
        
        # 类名映射，处理文件名与类名不一致的情况
        class_name_map = {
            "cettirei_monitor": "CettireMonitor",
            "d2Store_monitor": "D2StoreMonitor",  # 修正类名，注意文件名大小写
            "mrporter_monitor": "MrPorterMonitor",
            "rickowens_monitor": "RickOwensMonitor"
            # 如有其他不匹配的模块，可以在这里添加
        }
        
        # 获取crawler目录下所有爬虫模块
        for crawler_file in os.listdir(self.crawler_dir):
            if crawler_file.endswith('_monitor.py'):
                module_name = crawler_file[:-3]  # 去除.py后缀
                
                # 使用映射表中的类名，如果不存在则自动生成
                # 对d2Store_monitor特殊处理，忽略大小写
                lowered_module_name = module_name.lower()
                if module_name in class_name_map:
                    class_name = class_name_map[module_name]
                elif "d2store_monitor" == lowered_module_name:
                    class_name = "D2storeMonitor"
                else:
                    # 默认规则：转换文件名为驼峰命名的类名
                    class_name = ''.join(word.capitalize() for word in module_name.split('_'))

                try:
                    # 动态导入爬虫模块
                    module = importlib.import_module(f"src.crawler.{module_name}")
                    
                    # 尝试获取类
                    try:
                        crawler_class = getattr(module, class_name)
                        
                        # 检查是否是Monitor的子类但不是Monitor基类本身
                        from common.monitor import Monitor
                        if not issubclass(crawler_class, Monitor) or crawler_class.__name__ == "Monitor":
                            self.logger.warning(f"跳过 {class_name}，因为它不是Monitor的有效子类")
                            continue
                            
                    except AttributeError:
                        # 如果找不到上面的类名，尝试从模块中查找以Monitor结尾的类
                        monitor_classes = [obj for name, obj in vars(module).items() 
                                          if name.endswith('Monitor') and isinstance(obj, type)]
                        
                        if monitor_classes:
                            # 使用找到的第一个Monitor类
                            crawler_class = monitor_classes[0]
                            class_name = crawler_class.__name__
                            
                            # 检查是否是Monitor的子类但不是Monitor基类本身
                            from common.monitor import Monitor
                            if not issubclass(crawler_class, Monitor) or crawler_class.__name__ == "Monitor":
                                self.logger.warning(f"跳过 {class_name}，因为它不是Monitor的有效子类")
                                continue
                                
                            self.logger.info(f"使用自动发现的类: {class_name} 作为 {module_name} 的爬虫类")
                        else:
                            raise AttributeError(f"无法找到爬虫类 {class_name} 或任何以Monitor结尾的类")
                    
                    crawlers.append({
                        'module_name': module_name,
                        'class_name': class_name,
                        'class': crawler_class
                    })
                    self.logger.info(f"已加载爬虫: {class_name}")
                except (ImportError, AttributeError) as e:
                    self.logger.error(f"加载爬虫 {module_name} 失败: {str(e)}")

        return crawlers

    def run_crawler(self, crawler_info):
        """运行单个爬虫，增加错误重试逻辑"""
        class_name = crawler_info['class_name']
        max_retries = 1  # 最大重试次数
        retry_count = 0
        
        # 防止尝试导入或实例化Monitor基类
        if class_name == "Monitor":
            self.logger.warning(f"跳过抽象基类Monitor，不能直接实例化")
            return False
        
        # 导入Monitor基类用于检查
        try:
            from common.monitor import Monitor
            if crawler_info['class'] == Monitor:
                self.logger.warning(f"跳过抽象基类Monitor，不能直接实例化")
                return False
        except ImportError as e:
            self.logger.error(f"导入Monitor基类失败: {str(e)}")
            return False
        
        while retry_count <= max_retries:
            try:
                if retry_count > 0:
                    self.logger.info(f"重试 ({retry_count}/{max_retries}) 运行爬虫: {class_name}")
                else:
                    self.logger.info(f"开始运行爬虫: {class_name}")
                    
                # 创建爬虫实例并运行
                crawler = crawler_info['class'](is_headless=True)
                crawler.run_with_log()
                self.logger.info(f"爬虫 {class_name} 执行完成")
                return True
                
            except TypeError as e:
                # 处理抽象类实例化错误
                if "Can't instantiate abstract class" in str(e):
                    self.logger.error(f"无法实例化抽象类 {class_name}: {str(e)}")
                    return False
                # 其他类型错误，可以重试
                self.logger.error(f"运行爬虫 {class_name} 时发生类型错误: {str(e)}")
            except Exception as e:
                # 处理其他所有错误
                self.logger.error(f"运行爬虫 {class_name} 时出错: {str(e)}")
            
            # 增加重试计数
            retry_count += 1
            
            # 如果还有重试机会，等待一段时间后重试
            if retry_count <= max_retries:
                retry_wait = 5  # 重试等待时间（秒）
                self.logger.info(f"等待 {retry_wait} 秒后重试...")
                time.sleep(retry_wait)
            
        self.logger.error(f"爬虫 {class_name} 在 {max_retries+1} 次尝试后仍然失败")
        return False

    def run_all_crawlers(self):
        """运行所有爬虫，改为串行执行（一个爬虫完成后再执行下一个）"""
        self.logger.info("开始执行所有网站的爬虫任务")

        # 过滤掉Monitor基类
        valid_crawlers = []
        from common.monitor import Monitor
        
        for crawler_info in self.crawlers:
            if crawler_info['class'] == Monitor or crawler_info['class_name'] == "Monitor":
                self.logger.warning(f"跳过抽象基类Monitor，不能直接实例化")
                continue
            valid_crawlers.append(crawler_info)
            
        self.logger.info(f"有效爬虫数量: {len(valid_crawlers)}")

        # 串行执行爬虫任务，一个结束后再执行下一个
        successful_crawlers = 0
        for i, crawler_info in enumerate(valid_crawlers):
            class_name = crawler_info['class_name']
            self.logger.info(f"开始执行爬虫 [{i+1}/{len(valid_crawlers)}]: {class_name}")
            
            # 执行当前爬虫
            result = self.run_crawler(crawler_info)
            if result:
                successful_crawlers += 1
                self.logger.info(f"爬虫 {class_name} 执行成功")
            else:
                self.logger.warning(f"爬虫 {class_name} 执行失败")
                
            # 如果不是最后一个爬虫，等待指定时间后再执行下一个
            if i < len(valid_crawlers) - 1:
                self.logger.info(f"等待 {self.sleep_between_crawlers} 秒后执行下一个爬虫...")
                time.sleep(self.sleep_between_crawlers)
        
        self.logger.info(f"爬虫任务执行完成，成功: {successful_crawlers}/{len(valid_crawlers)}")
            
        # 显示执行结果摘要
        self.logger.info("所有爬虫任务已完成")
        
        # 检查并报告爬虫结果
        self.check_inventory_changes()

    def find_latest_summary_file(self, monitor_name):
        """查找指定监控器的最新库存摘要文件"""
        summary_dir = os.path.join(self.data_dir, monitor_name.lower(), "json_summary")
        if not os.path.exists(summary_dir):
            return None

        # 查找所有inventory_summary开头的JSON文件
        all_files = glob.glob(os.path.join(summary_dir, "inventory_summary_*.json"))
        if not all_files:
            return None

        # 按文件修改时间排序，取最新的
        latest_file = max(all_files, key=os.path.getmtime)
        return latest_file

    def check_inventory_changes(self):
        """检查所有网站的库存变化并发送通知"""
        self.logger.info("开始检查所有网站的库存变化")

        for crawler_info in self.crawlers:
            monitor_name = crawler_info['module_name'].replace('_monitor', '')

            # 获取最新的库存摘要文件
            latest_file = self.find_latest_summary_file(monitor_name)
            if not latest_file:
                self.logger.warning(f"{monitor_name} 未找到库存摘要文件")
                continue

            self.logger.info(f"处理 {monitor_name} 的库存文件: {latest_file}")

            try:
                # 使用DingSender处理并发送库存变化信息
                self.send_inventory_report(latest_file)
            except Exception as e:
                self.logger.error(f"处理 {monitor_name} 的库存变化时出错: {str(e)}")

    def send_inventory_report(self, file_path):
        """发送单个网站的库存报告"""
        try:
            # 读取当前库存数据
            with open(file_path, 'r', encoding='utf-8') as f:
                current_data = json.load(f)

            # 获取上一次的库存数据
            dir_path = os.path.dirname(file_path)
            previous_file = self.ding_sender.find_previous_json(file_path, dir_path)
            previous_data = None

            if previous_file:
                with open(previous_file, 'r', encoding='utf-8') as f:
                    previous_data = json.load(f)

            # 比较变化情况
            changes = self.ding_sender.compare_inventory(current_data, previous_data)

            # 检查是否有新增商品
            new_count = len(changes["new_products"])
            if new_count == 0:
                self.logger.info("没有新增商品，不发送通知")
                return

            # 创建精简报告
            monitor_name = current_data.get("monitor", "未知监控器")

            markdown_text = f"# {monitor_name}\n\n"
            markdown_text += f"新增商品数: {new_count}\n\n"
            markdown_text += f"新增时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            markdown_text += "============\n\n"

            # 添加新增商品详情
            for i, product in enumerate(changes["new_products"]):
                name = product.get('name', '未知商品')
                url = product.get('url', '')
                price = product.get('price', '')

                markdown_text += f"{i + 1}. {name}\n\n"
                if price:
                    markdown_text += f"价格: {price}\n\n"
                if url:
                    markdown_text += f"链接: {url}\n\n"

                # 添加尺寸信息（如果存在）
                inventory_status = product.get('inventory_status', [])
                if inventory_status:
                    markdown_text += "尺寸:\n\n"
                    for status_info in inventory_status:
                        status = status_info.get("status", "")
                        sizes = status_info.get("sizes", [])
                        if sizes:
                            markdown_text += f"- {status}: {', '.join(sizes)}\n"
                    markdown_text += "\n"

                markdown_text += "..........\n\n"

            # 生成钉钉消息
            markdown_message = {
                "title": f"{monitor_name} - 新增商品通知",
                "text": markdown_text
            }

            # 发送钉钉消息
            result = self.ding_sender.send_dingtalk_message(
                self.ding_url,
                self.ding_secret,
                markdown_message
            )

            self.logger.info(f"已发送新增商品通知: {result}")

        except Exception as e:
            self.logger.error(f"发送库存报告时出错: {str(e)}")

    def start(self):
        """启动调度器，设置定时任务"""
        self.logger.info("调度器启动，开始设置定时任务")

        # 每10分钟运行一次爬虫和库存变化检测
        schedule.every(self.loop_time).minutes.do(self.run_all_crawlers)

        # 启动时先执行一次所有任务
        self.logger.info("首次执行爬虫任务")
        self.run_all_crawlers()

        self.logger.info("调度器已启动，等待执行定时任务")

        # 循环执行定时任务
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("收到终止信号，调度器停止")
                break
            except Exception as e:
                self.logger.error(f"定时任务执行出错: {str(e)}")
                # 出错后等待30秒再继续
                time.sleep(30)


if __name__ == "__main__":
    # 创建并启动调度器
    scheduler = BalenciagaScheduler()
    scheduler.start()
