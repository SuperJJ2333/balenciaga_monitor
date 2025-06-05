"""
监控定时任务调度器
用于定时执行爬虫任务、检测库存变化并发送钉钉通知
"""
import os
import re
import time
import importlib
import schedule
from datetime import datetime
import glob
import sys
import json
import threading
import traceback
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入项目路径和日志模块
from src.common.project_path import ProjectPaths
from src.common.logger import get_logger
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

        # 设置最大保留文件数
        self.max_scheduler_logs = 20  # 调度器日志文件最大保留数量
        self.max_site_data_files = 50  # 每个网站数据文件最大保留数量

        # 爬虫失败计数器
        self.crawler_failure_counter = {}
        # 最大失败周期数
        self.max_failure_cycles = 3

        # 读取爬虫排除列表
        self.excluded_monitors = []
        try:
            crawler_monitor_path = os.path.join(self.project_paths.CONFIG, 'crawler_monitor.toml')
            if os.path.exists(crawler_monitor_path):
                crawler_monitor_config = load_toml(crawler_monitor_path, self.logger)
                if 'excluded_monitor' in crawler_monitor_config and 'excluded_list' in crawler_monitor_config['excluded_monitor']:
                    self.excluded_monitors = crawler_monitor_config['excluded_monitor']['excluded_list']
                    self.logger.info(f"已加载爬虫排除列表: {self.excluded_monitors}")
        except Exception as e:
            self.logger.error(f"读取爬虫排除列表失败: {str(e)}")

        # 爬虫配置，包含所有参数
        self.crawler_configs = {
            "antonioli_monitor": {"is_headless": True, "proxy_type": "clash", "is_no_img": True, "is_auto_port": True, "load_mode": "normal"},
            "mrporter_monitor": {"is_headless": True, "proxy_type": "clash", "is_no_img": True, "is_auto_port": False, "load_mode": "normal"},
            "giglio_monitor": {"is_headless": True, "proxy_type": "clash", "is_no_img": True, "is_auto_port": True, "load_mode": "normal"},
            "grifo210_monitor": {"is_headless": True, "proxy_type": "clash", "is_no_img": True, "is_auto_port": True, "load_mode": "normal"},
            "rickowens_monitor": {"is_headless": False, "proxy_type": "clash", "is_no_img": True, "is_auto_port": False, "load_mode": "normal"},
            "suus_monitor": {"is_headless": True, "proxy_type": "clash", "is_no_img": True, "is_auto_port": True, "load_mode": "normal"},
            "cettire_monitor": {"is_headless": True, "proxy_type": "ipcool", "is_no_img": True, "is_auto_port": True, "load_mode": "normal"},
            "hermes_monitor": {"is_headless": True, "proxy_type": "ipcool", "is_no_img": False, "is_auto_port": False, "load_mode": "normal"},
            # "julian_monitor": {"is_headless": False, "proxy_type": None, "is_no_img": False, "is_auto_port": False, "load_mode": "normal"},
            "d2Store_monitor": {"is_headless": True, "proxy_type": None, "is_no_img": True, "is_auto_port": True, "load_mode": "normal"},
            "mytheresa_monitor": {"is_headless": True, "proxy_type": None, "is_no_img": True, "is_auto_port": False, "load_mode": "eager"},
        }

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
            "cettire_monitor": "CettireMonitor",
            "d2Store_monitor": "D2StoreMonitor",  # 修正类名，注意文件名大小写
            "mrporter_monitor": "MrPorterMonitor",
            "rickowens_monitor": "RickOwensMonitor"
            # 如有其他不匹配的模块，可以在这里添加
        }

        # 获取crawler目录下所有爬虫模块
        for crawler_file in os.listdir(self.crawler_dir):
            if crawler_file.endswith('_monitor.py'):
                module_name = crawler_file[:-3]  # 去除.py后缀
                
                # 检查是否在排除列表中
                if module_name in self.excluded_monitors:
                    self.logger.info(f"爬虫 {module_name} 在排除列表中，已跳过加载")
                    continue

                # 使用映射表中的类名，如果不存在则自动生成
                # 对d2Store_monitor特殊处理，忽略大小写
                lowered_module_name = module_name.lower()
                if module_name in class_name_map:
                    class_name = class_name_map[module_name]
                elif "d2store_monitor" == lowered_module_name:
                    class_name = "D2StoreMonitor"
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
                        from src.common.monitor import Monitor
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
                            from src.common.monitor import Monitor
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
        """运行单个爬虫，通过实例化类执行"""
        module_name = crawler_info['module_name']
        class_name = crawler_info['class_name']
        crawler_class = crawler_info['class']
        max_retries = 3  # 最大重试次数，从1增加到3
        retry_count = 0

        self.logger.info(f"开始执行爬虫: {class_name}")

        while retry_count <= max_retries:
            try:
                if retry_count > 0:
                    self.logger.info(f"重试 ({retry_count}/{max_retries}) 执行爬虫: {class_name}")

                # 设置默认参数
                kwargs = {}
                
                # 如果存在该爬虫的配置，应用所有配置参数
                if module_name in self.crawler_configs:
                    kwargs = self.crawler_configs[module_name].copy()
                    if kwargs.get('proxy_type'):
                        self.logger.info(f"为爬虫 {module_name} 设置代理: {kwargs['proxy_type']}")
                else:
                    # 如果没有特定配置，使用默认值
                    kwargs = {
                        'is_headless': True,
                        'proxy_type': None,
                        'is_no_img': True,
                        'is_auto_port': True,
                        'load_mode': 'normal'
                    }
                    self.logger.info(f"爬虫 {module_name} 使用默认配置")

                # 实例化爬虫类并运行
                self.logger.debug(f"爬虫 {module_name} 的配置参数: {kwargs}")
                crawler_instance = crawler_class(**kwargs)
                result = crawler_instance.run_with_log()

                # 检查爬虫返回结果
                if not result:
                    self.logger.warning(f"爬虫 {class_name} 返回结果为空")
                    # 增加重试计数
                    retry_count += 1
                    # 如果还有重试机会，等待一段时间后重试
                    if retry_count <= max_retries:
                        retry_wait = 5  # 重试等待时间（秒）
                        self.logger.info(f"等待 {retry_wait} 秒后重试...")
                        time.sleep(retry_wait)
                    continue

                # 爬虫执行成功，重置失败计数器
                if module_name in self.crawler_failure_counter:
                    self.crawler_failure_counter[module_name] = 0

                self.logger.info(f"爬虫 {class_name} 执行成功")
                return True

            except Exception as e:
                self.logger.error(f"执行爬虫 {class_name} 时出错: {str(e)}")
                # 增加重试计数
                retry_count += 1
                # 如果还有重试机会，等待一段时间后重试
                if retry_count <= max_retries:
                    retry_wait = 5  # 重试等待时间（秒）
                    self.logger.info(f"等待 {retry_wait} 秒后重试...")
                    time.sleep(retry_wait)

        # 所有重试都失败了，增加失败计数
        if module_name not in self.crawler_failure_counter:
            self.crawler_failure_counter[module_name] = 1
        else:
            self.crawler_failure_counter[module_name] += 1

        # 检查是否达到最大失败周期数
        if self.crawler_failure_counter[module_name] >= self.max_failure_cycles:
            self.logger.critical(f"爬虫 {class_name} 连续 {self.max_failure_cycles} 个周期返回空结果，暂停运行该爬虫")
            # 发送警告邮件
            self.send_warning_email(module_name, class_name)
            # 将爬虫添加到排除列表
            if module_name not in self.excluded_monitors:
                self.excluded_monitors.append(module_name)
                self.logger.info(f"已将爬虫 {module_name} 添加到排除列表")

        self.logger.error(f"爬虫 {class_name} 在 {max_retries + 1} 次尝试后仍然失败")
        return False

    def send_warning_email(self, module_name, class_name):
        """发送爬虫警告邮件"""
        try:
            self.logger.info(f"准备发送爬虫 {class_name} 警告邮件")
            
            # 邮件内容
            subject = f"爬虫警告：{class_name} 连续失败"
            content = f"""
            警告：爬虫 {class_name} ({module_name}) 连续 {self.max_failure_cycles} 个周期返回空结果。
            
            时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            该爬虫已被暂时排除，不会在后续周期中执行，直到手动恢复。
            
            请检查爬虫代码或目标网站是否发生变化。
            
            此邮件由系统自动发送。
            """
            
            # 创建邮件对象
            msg = MIMEText(content, 'plain', 'utf-8')
            msg['From'] = formataddr(["Balenciaga监控系统", '1014826460@qq.com'])  # 发件人邮箱昵称、发件人邮箱账号
            msg['To'] = formataddr(["管理员", '1014826460@qq.com'])  # 收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = subject  # 邮件主题
            
            # 发送邮件
            try:
                server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # QQ邮箱SMTP服务器，端口是465
                server.login('1014826460@qq.com', 'dfzwkpklutdkbchf')  # 发件人邮箱账号、授权码
                server.sendmail('1014826460@qq.com', ['1014826460@qq.com'], msg.as_string())  # 发件人账号、收件人账号、发送邮件
                server.quit()  # 关闭连接
                self.logger.info(f"爬虫 {class_name} 警告邮件发送成功")
                return True
            except Exception as e:
                self.logger.error(f"发送警告邮件失败: {str(e)}")
                # 如果邮件发送失败，尝试使用钉钉发送警告
                self._send_warning_via_dingtalk(module_name, class_name)
                return False
                
        except Exception as e:
            self.logger.error(f"准备警告邮件时出错: {str(e)}")
            return False
    
    def _send_warning_via_dingtalk(self, module_name, class_name):
        """通过钉钉发送爬虫警告"""
        try:
            self.logger.info(f"尝试通过钉钉发送爬虫 {class_name} 警告")
            
            # 构建钉钉消息
            markdown_text = f"## 爬虫警告：{class_name} 连续失败\n\n"
            markdown_text += f"警告：爬虫 {class_name} ({module_name}) 连续 {self.max_failure_cycles} 个周期返回空结果。\n\n"
            markdown_text += f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            markdown_text += "该爬虫已被暂时排除，不会在后续周期中执行，直到手动恢复。\n\n"
            markdown_text += "请检查爬虫代码或目标网站是否发生变化。"
            
            markdown_message = {
                "title": f"爬虫警告：{class_name} 连续失败",
                "text": markdown_text
            }
            
            # 发送钉钉消息
            result = self.ding_sender.send_dingtalk_message(
                self.ding_url,
                self.ding_secret,
                markdown_message
            )
            
            self.logger.info(f"通过钉钉发送爬虫 {class_name} 警告结果: {result}")
        except Exception as e:
            self.logger.error(f"通过钉钉发送警告失败: {str(e)}")

    def run_all_crawlers(self):
        """运行所有爬虫，串行执行（一个爬虫完成后再执行下一个）"""
        self.logger.info("开始执行所有网站的爬虫任务")

        self.logger.info(f"有效爬虫数量: {len(self.crawlers)}")

        # 串行执行爬虫任务，一个结束后再执行下一个
        successful_crawlers = 0
        for i, crawler_info in enumerate(self.crawlers):
            module_name = crawler_info['module_name']
            class_name = crawler_info['class_name']
            
            # 再次检查是否在排除列表中（以防配置在运行期间被修改）
            if module_name in self.excluded_monitors:
                self.logger.info(f"爬虫 {module_name} 在排除列表中，已跳过执行")
                continue
                
            self.logger.info(f"开始执行爬虫 [{i + 1}/{len(self.crawlers)}]: {class_name}")

            # 执行当前爬虫
            result = self.run_crawler(crawler_info)
            if result:
                successful_crawlers += 1
                self.logger.info(f"爬虫 {class_name} 执行成功")
            else:
                self.logger.warning(f"爬虫 {class_name} 执行失败")

            # 如果不是最后一个爬虫，等待指定时间后再执行下一个
            if i < len(self.crawlers) - 1:
                self.logger.info(f"等待 {self.sleep_between_crawlers} 秒后执行下一个爬虫...")
                time.sleep(self.sleep_between_crawlers)

        self.logger.info(f"爬虫任务执行完成，成功: {successful_crawlers}/{len(self.crawlers)}")

        # 显示执行结果摘要
        self.logger.info("所有爬虫任务已完成")

        # 检查并报告爬虫结果
        self.check_inventory_changes()

        # 添加明显的周期结束标志
        self.logger.info("=" * 50)
        self.logger.info("调度循环周期执行完成")
        self.logger.info("=" * 50)

    def find_latest_summary_file(self, monitor_name):
        """查找指定监控器的最新库存摘要文件"""
        inventory_dir = os.path.join(self.data_dir, monitor_name.lower(), "inventory")
        if not os.path.exists(inventory_dir):
            return None

        # 查找所有balenciaga_inventory开头的JSON文件
        all_files = glob.glob(os.path.join(inventory_dir, "balenciaga_inventory_*.json"))
        if not all_files:
            return None

        def extract_timestamp(filename):
            match = re.search(r"balenciaga_inventory_(\d{8}_\d{6})\.json$", filename)
            if match:
                timestamp_str = match.group(1)
                try:
                    # 将YYYYMMDD_HHMMSS格式转换为时间戳
                    dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    return dt.timestamp()
                except Exception:
                    self.logger.warning(f"无法解析文件名中的时间戳: {filename}")
            # 如果无法从文件名提取时间戳，返回0表示最旧
            return 0

        # 按时间戳排序，取最新的文件
        all_files.sort(key=extract_timestamp, reverse=True)
        
        self.logger.debug(f"找到的最新库存文件: {os.path.basename(all_files[0])}")
        return all_files[0]

    def check_inventory_changes(self):
        """检查所有网站的库存变化并发送通知"""
        self.logger.info("开始检查所有网站的库存变化")

        # 记录找到的库存文件数量
        found_files = 0
        processed_files = 0

        for crawler_info in self.crawlers:
            monitor_name = crawler_info['module_name'].replace('_monitor', '')

            # 获取最新的库存摘要文件
            latest_file = self.find_latest_summary_file(monitor_name)
            if not latest_file:
                self.logger.warning(f"{monitor_name} 未找到库存摘要文件")
                continue

            found_files += 1
            self.logger.info(f"处理 {monitor_name} 的库存文件: {latest_file}")

            try:
                # 使用DingSender处理并发送库存变化信息
                success = self.send_inventory_report(latest_file)
                if success:
                    processed_files += 1
            except Exception as e:
                self.logger.error(f"处理 {monitor_name} 的库存变化时出错: {str(e)}")
                self.logger.error(f"错误详情: {traceback.format_exc()}")

        self.logger.info(f"库存变化检查完成: 找到 {found_files} 个库存文件，处理了 {processed_files} 个文件")

    def send_inventory_report(self, file_path):
        """发送单个网站的库存报告"""
        try:
            # 读取当前库存数据
            with open(file_path, 'r', encoding='utf-8') as f:
                current_data = json.load(f)

            # 记录库存数据基本信息
            monitor_name = current_data.get("monitor", "未知监控器")
            product_count = len(current_data) if isinstance(current_data, dict) else 0
            self.logger.info(f"{monitor_name} 当前库存数据包含 {product_count} 个商品")

            # 如果monitor_name是"未知监控器"，尝试从文件路径提取网站名称
            if monitor_name == "未知监控器":
                file_dir = os.path.dirname(file_path)
                for site in ["cettire", "sugar", "mrporter", "antonioli", "duomo",
                             "eleonora_bonucci", "suus", "mytheresa", "giglio",
                             "grifo210", "julian", "d2store", "hermes", "rickowens"]:
                    if site.lower() in file_dir.lower():
                        monitor_name = site.capitalize()
                        self.logger.info(f"从文件路径中识别出网站: {monitor_name}")
                        break

            # 获取上一次的库存数据
            dir_path = os.path.dirname(file_path)
            previous_file = self.ding_sender.find_previous_json(file_path, dir_path)

            if previous_file:
                self.logger.info(f"找到上一次库存文件: {previous_file}")
                try:
                    with open(previous_file, 'r', encoding='utf-8') as f:
                        previous_data = json.load(f)
                    prev_product_count = len(previous_data) if isinstance(previous_data, dict) else 0
                    self.logger.info(f"上一次库存数据包含 {prev_product_count} 个商品")
                    
                    # 检查数据量差异是否异常
                    if product_count > 0 and prev_product_count > 0:
                        diff_ratio = abs(product_count - prev_product_count) / max(product_count, prev_product_count)
                        if diff_ratio > 0.3:  # 如果差异超过30%
                            self.logger.warning(f"当前数据({product_count}个)与上一次数据({prev_product_count}个)相差{diff_ratio:.1%}，超过阈值，可能是爬取异常")
                            
                            # 检查是否有重点监控商品
                            key_products_count = sum(1 for _, item in current_data.items() 
                                                   if isinstance(item, dict) and item.get("key_monitoring", False))
                            
                            if key_products_count > 0:
                                self.logger.warning(f"数据包含 {key_products_count} 个重点监控商品，将谨慎处理变化检测")
                except Exception as e:
                    self.logger.error(f"读取上一次库存文件时出错: {str(e)}")
                    previous_data = None
            else:
                self.logger.warning(f"未找到上一次库存文件，将无法比较变化")
                previous_data = None

            # 比较变化情况
            try:
                changes = self.ding_sender.compare_inventory(current_data, previous_data)

                # 记录变化详情
                new_count = len(changes.get("new_products", []))
                removed_count = len(changes.get("removed_products", []))
                changed_count = len(changes.get("inventory_changes", []))
                key_changed_count = len(changes.get("key_product_changes", []))
                
                self.logger.info(f"变化情况: 新增={new_count}, 下架={removed_count}, 库存变化={changed_count}, 重点商品变化={key_changed_count}")
            except Exception as e:
                self.logger.error(f"比较库存变化时出错: {str(e)}")
                self.logger.error(f"错误详情: {traceback.format_exc()}")
                return False

            # 判断是否需要发送通知
            has_new_products = len(changes.get("new_products", [])) > 0
            has_key_changes = len(changes.get("key_product_changes", [])) > 0
            
            if not has_new_products and not has_key_changes:
                self.logger.info(f"{monitor_name} 没有新增商品或重点监控商品变化，不发送通知")
                return False
            
            # 构建消息内容
            messages_sent = False
            
            # 1. 处理新增商品通知
            if has_new_products:
                # 创建精简报告
                new_count = len(changes["new_products"])
                markdown_text = f"## {monitor_name}\n\n"
                markdown_text += f"新增商品数: {new_count}\n\n"
                markdown_text += f"新增时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                markdown_text += "============\n\n"

                # 添加新增商品详情
                for i, product in enumerate(changes["new_products"]):
                    name = product.get('name', '未知商品')
                    url = product.get('url', '')
                    price = product.get('price', '')

                    # 修改格式以确保钉钉正确渲染递增编号
                    markdown_text += f"{i + 1}. **{name}**"
                    if url:
                        markdown_text += f" [【查看商品】]({url})"
                    markdown_text += "  \n  "  # 注意这里只用一个换行
                    
                    if price:
                        markdown_text += f"价格: {price}" + "  \n  "  # 只用一个换行

                    # 添加尺寸信息（如果存在）
                    inventory_status = product.get('inventory', {}).items()
                    if inventory_status:
                        markdown_text += "尺寸: "
                        for size_name, _size_status in inventory_status:
                            markdown_text += f"{size_name}; "
                        markdown_text += "  \n  "

                # 生成钉钉消息
                markdown_message = {
                    "title": f"{monitor_name} - 新增商品通知",
                    "text": markdown_text
                }

                # 发送钉钉消息
                try:
                    # 记录将要发送的消息概要
                    self.logger.info(f"准备发送钉钉消息: {markdown_message['title']}")

                    result = self.ding_sender.send_dingtalk_message(
                        self.ding_url,
                        self.ding_secret,
                        markdown_message
                    )

                    self.logger.info(f"已发送新增商品通知: {result}")
                    messages_sent = True
                except Exception as e:
                    self.logger.error(f"发送钉钉消息时出错: {str(e)}")
                    self.logger.error(f"错误详情: {traceback.format_exc()}")
            
            # 2. 处理重点监控商品变化通知
            if has_key_changes:
                # 创建精简报告
                key_count = len(changes["key_product_changes"])
                markdown_text = f"## {monitor_name}\n\n"
                markdown_text += f"重点监控商品变化数: {key_count}\n\n"
                markdown_text += f"变化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                markdown_text += "============\n\n"

                # 添加变化商品详情
                for i, product in enumerate(changes["key_product_changes"]):
                    name = product.get('name', '未知商品')
                    url = product.get('url', '')
                    
                    # 修改格式以确保钉钉正确渲染递增编号
                    markdown_text += f"{i + 1}. **{name}**"
                    if url:
                        markdown_text += f" [【查看商品】]({url})"
                    markdown_text += "  \n  "  # 注意这里只用一个换行
                    
                    # 添加价格变化信息
                    price_change = product.get('price_change')
                    if price_change:
                        from_price = price_change.get('from', '')
                        to_price = price_change.get('to', '')
                        markdown_text += f"价格变化: {from_price} → {to_price}" + "  \n  "
                    
                    # 添加尺寸变化信息
                    size_changes = product.get('size_changes', [])
                    if size_changes:
                        markdown_text += "尺寸变化:  \n  "
                        for change in size_changes:
                            size = change.get('size', '')
                            from_status = change.get('from', '')
                            to_status = change.get('to', '')
                            change_type = change.get('type', '')
                            
                            change_desc = f"- {size}: {from_status} → {to_status}"
                            if change_type == "stock_in":
                                change_desc += " (补货)"
                            elif change_type == "stock_out":
                                change_desc += " (售罄)"
                            
                            markdown_text += change_desc + "  \n  "

                # 生成钉钉消息
                markdown_message = {
                    "title": f"{monitor_name} - 重点商品变化通知",
                    "text": markdown_text
                }

                # 发送钉钉消息
                try:
                    # 记录将要发送的消息概要
                    self.logger.info(f"准备发送钉钉消息: {markdown_message['title']}")

                    result = self.ding_sender.send_dingtalk_message(
                        self.ding_url,
                        self.ding_secret,
                        markdown_message
                    )

                    self.logger.info(f"已发送重点商品变化通知: {result}")
                    messages_sent = True
                except Exception as e:
                    self.logger.error(f"发送钉钉消息时出错: {str(e)}")
                    self.logger.error(f"错误详情: {traceback.format_exc()}")
            
            return messages_sent

        except Exception as e:
            self.logger.error(f"发送库存报告时出错: {str(e)}")
            self.logger.error(f"错误详情: {traceback.format_exc()}")
            return False

    def reload_excluded_monitors(self):
        """重新加载爬虫排除列表配置"""
        try:
            crawler_monitor_path = os.path.join(self.project_paths.CONFIG, 'crawler_monitor.toml')
            if os.path.exists(crawler_monitor_path):
                crawler_monitor_config = load_toml(crawler_monitor_path, self.logger)
                if 'excluded_monitor' in crawler_monitor_config and 'excluded_list' in crawler_monitor_config['excluded_monitor']:
                    old_excluded = set(self.excluded_monitors)
                    self.excluded_monitors = crawler_monitor_config['excluded_monitor']['excluded_list']
                    new_excluded = set(self.excluded_monitors)
                    
                    # 检查是否有变化
                    if old_excluded != new_excluded:
                        added = new_excluded - old_excluded
                        removed = old_excluded - new_excluded
                        
                        if added:
                            self.logger.info(f"新增排除爬虫: {', '.join(added)}")
                        if removed:
                            self.logger.info(f"移除排除爬虫: {', '.join(removed)}")
                        
                        self.logger.info(f"已更新爬虫排除列表: {self.excluded_monitors}")
        except Exception as e:
            self.logger.error(f"重新加载爬虫排除列表失败: {str(e)}")

    def start(self):
        """启动调度器，设置定时任务"""
        self.logger.info("=" * 50)
        self.logger.info("调度器启动，开始设置定时任务")
        self.logger.info("=" * 50)

        # 输出已配置的爬虫信息
        self.logger.info(f"已配置的爬虫数量: {len(self.crawler_configs)}")
        for crawler_name, config in self.crawler_configs.items():
            proxy_info = f"代理: {config.get('proxy_type', 'None')}" if config.get('proxy_type') else "无代理"
            headless_info = "无头模式" if config.get('is_headless', True) else "有界面模式"
            self.logger.info(f"爬虫配置 - {crawler_name}: {headless_info}, {proxy_info}")

        # 每5分钟运行一次爬虫和库存变化检测
        schedule.every(self.loop_time).minutes.do(self.run_all_crawlers)
        # 每天凌晨3点执行一次日志和数据清理
        schedule.every().day.at("03:00").do(self.cleanup_scheduler_files)
        # 每小时重新加载一次排除列表配置
        schedule.every(1).hours.do(self.reload_excluded_monitors)
        
        self.logger.info(f"已设置定时任务: 每 {self.loop_time} 分钟执行一次爬虫任务")
        self.logger.info("已设置定时任务: 每天凌晨3点执行一次日志和数据清理")
        self.logger.info("已设置定时任务: 每小时重新加载一次排除列表配置")

        # 启动时先执行一次所有任务
        self.logger.info("首次执行爬虫任务")
        self.run_all_crawlers()

        self.logger.info("调度器已启动，等待执行定时任务")

        # 循环执行定时任务
        while True:
            try:
                # 在每次循环前重新加载排除列表配置
                self.reload_excluded_monitors()
                
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("收到终止信号，调度器停止")
                break
            except Exception as e:
                self.logger.error(f"定时任务执行出错: {str(e)}")
                self.logger.error(f"错误详情: {traceback.format_exc()}")
                # 出错后等待30秒再继续
                time.sleep(30)

    def cleanup_scheduler_files(self):
        """
        清理调度器日志和临时文件，避免占用过多磁盘空间
        """
        self.logger.info("开始执行调度器日志和数据清理任务")
        
        try:
            # 清理调度器日志文件
            self._cleanup_log_files()
            
            # 清理各个网站的数据文件
            self._cleanup_site_data_files()
            
            self.logger.info("调度器日志和数据清理任务完成")
        except Exception as e:
            self.logger.error(f"清理文件时出错: {str(e)}")
            self.logger.error(f"错误详情: {traceback.format_exc()}")
    
    def _cleanup_log_files(self):
        """清理调度器日志文件，保留最新的几个文件"""
        log_dir = os.path.join(self.project_paths.LOGS, "scheduler")
        if not os.path.exists(log_dir):
            self.logger.debug("调度器日志目录不存在，无需清理")
            return
            
        # 获取所有日志文件
        log_files = glob.glob(os.path.join(log_dir, "scheduler_*.log"))
        
        if not log_files:
            self.logger.debug("没有找到调度器日志文件，无需清理")
            return
            
        # 按修改时间排序（从新到旧）
        log_files.sort(key=os.path.getmtime, reverse=True)
        
        # 保留最新的max_scheduler_logs个文件，删除其余文件
        files_to_delete = log_files[self.max_scheduler_logs:]
        
        if not files_to_delete:
            self.logger.debug(f"调度器日志文件数量未超过上限 ({len(log_files)}/{self.max_scheduler_logs})，无需清理")
            return
            
        deleted_count = 0
        for file in files_to_delete:
            try:
                os.remove(file)
                deleted_count += 1
            except Exception as e:
                self.logger.warning(f"删除调度器日志文件失败: {file}, 错误: {str(e)}")
                
        if deleted_count > 0:
            self.logger.info(f"已清理 {deleted_count} 个旧调度器日志文件，保留最新的 {min(len(log_files), self.max_scheduler_logs)} 个文件")
    
    def _cleanup_site_data_files(self):
        """清理各个网站的数据文件，保留最新的几个文件"""
        # 遍历所有网站目录
        if not os.path.exists(self.data_dir):
            self.logger.debug("数据目录不存在，无需清理")
            return
            
        site_dirs = [d for d in os.listdir(self.data_dir) 
                    if os.path.isdir(os.path.join(self.data_dir, d))]
        
        for site in site_dirs:
            site_dir = os.path.join(self.data_dir, site)
            self.logger.debug(f"检查网站 {site} 的数据目录")
            
            # 清理库存数据文件
            inventory_dir = os.path.join(site_dir, "inventory")
            self._cleanup_dir_files(inventory_dir, "*.json", self.max_site_data_files, f"{site}库存数据")
            
            # 清理变更数据文件
            changes_dir = os.path.join(site_dir, "changes")
            self._cleanup_dir_files(changes_dir, "*.json", self.max_site_data_files, f"{site}变更数据")
            
            # 清理总结数据文件
            summary_dir = os.path.join(site_dir, "summary")
            self._cleanup_dir_files(summary_dir, "*.txt", self.max_site_data_files, f"{site}总结文本")
            self._cleanup_dir_files(summary_dir, "*.json", self.max_site_data_files, f"{site}总结JSON")
    
    def _cleanup_dir_files(self, directory, pattern, max_files, file_type):
        """
        清理指定目录下的文件，保留最新的文件
        
        Args:
            directory (str): 要清理的目录
            pattern (str): 文件匹配模式（如 "*.log"）
            max_files (int): 保留的最大文件数量
            file_type (str): 文件类型描述，用于日志
        """
        if not os.path.exists(directory):
            return
            
        # 获取所有匹配的文件
        files = glob.glob(os.path.join(directory, pattern))
        
        if not files:
            return
        
        # 根据文件类型选择排序方法
        if "inventory" in file_type and "balenciaga_inventory_" in files[0]:
            # 针对库存文件使用文件名中的时间戳排序
            def extract_timestamp(filename):
                match = re.search(r"balenciaga_inventory_(\d{8}_\d{6})\.json$", filename)
                if match:
                    timestamp_str = match.group(1)
                    try:
                        # 将YYYYMMDD_HHMMSS格式转换为时间戳
                        dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        return dt.timestamp()
                    except Exception:
                        pass
                # 如果无法提取时间戳，返回文件修改时间作为备选
                return os.path.getmtime(filename)
                
            # 按照提取的时间戳排序（从新到旧）
            files.sort(key=extract_timestamp, reverse=True)
            self.logger.debug(f"使用文件名中的时间戳对 {file_type} 文件进行排序")
        else:
            # 其他文件类型使用修改时间排序
            files.sort(key=os.path.getmtime, reverse=True)
            self.logger.debug(f"使用修改时间对 {file_type} 文件进行排序")
        
        # 保留最新的max_files个文件，删除其余文件
        files_to_delete = files[max_files:]
        
        if not files_to_delete:
            self.logger.debug(f"{file_type}文件数量未超过上限 ({len(files)}/{max_files})，无需清理")
            return
            
        deleted_count = 0
        for file in files_to_delete:
            try:
                os.remove(file)
                deleted_count += 1
            except Exception as e:
                self.logger.warning(f"删除{file_type}文件失败: {file}, 错误: {str(e)}")
                
        if deleted_count > 0:
            self.logger.info(f"已清理 {deleted_count} 个旧{file_type}文件，保留最新的 {min(len(files), max_files)} 个文件")


if __name__ == "__main__":
    # 创建并启动调度器
    scheduler = BalenciagaScheduler()
    scheduler.start()
