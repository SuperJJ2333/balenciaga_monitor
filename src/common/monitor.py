"""
基础监控类模块
提供所有监控类的基础功能和结构
"""
import json
import glob
import os.path
import logging
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse, urlunparse
import re

import requests
from DrissionPage import ChromiumPage, ChromiumOptions, SessionPage, SessionOptions

from common.project_path import ProjectPaths
from utils.page_setting import configure_logger, load_cookies, random_sleep
from utils.proxy_setting import create_proxyauth_extension, set_switchy_omega
from utils.utils import load_toml


class Monitor(ABC):
    """
    监控基类，提供基础的浏览器操作和数据保存功能
    
    子类必须实现以下方法:
    - run: 运行监控的主方法
    - get_inventory_catalog: 获取商品目录
    - get_inventory_page: 获取单个商品的库存信息
    - parse_inventory_catalog: 解析商品目录
    - parse_inventory_info: 解析商品库存信息
    """

    def __init__(self, **kwargs):
        """
        初始化监控类实例
        
        Args:
            monitor_name (str): 监控网站名称，用于日志和数据保存
            catalog_url (str): 商品目录URL
            is_headless (bool): 是否以无头模式运行浏览器，默认为True
            is_proxy (bool): 是否使用代理，默认为False
            is_no_img (bool): 是否禁用图片加载，默认为True
            is_auto_port (bool): 是否自动切换端口，默认为True
            load_mode (str): 页面加载模式，默认为'eager'
        """
        # 初始化项目根目录
        self.project_path = ProjectPaths()

        # 监控网站名称，子类需要设置
        self.monitor_name: str = kwargs.get('monitor_name', "base_monitor")
        # 商品目录URL，子类需要设置
        self.catalog_url: list[str] = kwargs.get('catalog_url', [])

        # 保存给每个网站的唯一名称，用于文件保存
        self.name: str = self.monitor_name

        # 商品存储字典
        self.products_dict = None
        # 存储已爬取的数据
        self.products_list: list = []
        # 详细页面存储库存数据
        self.inventory_data: dict = {}

        # 上次的库存数据，用于对比变化
        self.previous_inventory = {}

        self.page: ChromiumPage | None = None

        ## 可选参数处理
        self._handle_params(**kwargs)
        # 初始化代理
        if self.proxy_type:
            self._init_proxy()

        # 初始化日志记录器
        self.logger = self._setup_logger()

        # 保存数据的根目录
        self.data_root = self.project_path.DATA

        self.url_config = load_toml(os.path.join(self.project_path.CONFIG, 'url_monitor.toml'), self.logger)

        if self.monitor_name in self.url_config:
            url_config = self.url_config[self.monitor_name]
            # 配置网页的URL
            self.catalog_url = url_config[f"{self.monitor_name}_category_url"]
            self.product_url = url_config[f"{self.monitor_name}_specific_url"] if f"{self.monitor_name}_specific_url" in url_config else None

        # 加载上次的库存数据用于对比
        self._load_previous_inventory()

        self.logger.info(f"{self.monitor_name} - 库存监控已初始化")

    def _handle_params(self, **kwargs):
        """
        处理参数，子类禁止重写此方法
        """
        # 是否以无头模式运行
        self.is_headless = kwargs.get('is_headless', True)
        # 是否使用代理
        self.proxy_type = kwargs.get('proxy_type', None)
        # 是否使用图片
        self.is_no_img = kwargs.get('is_no_img', True)
        # 是否自动切换端口
        self.is_auto_port = kwargs.get('is_auto_port', True)

        self.load_mode: [str] = kwargs.get('load_mode', 'normal')

    def _setup_logger(self):
        """
        设置日志记录器，配置控制台和文件输出
        
        Returns:
            logging.Logger: 配置好的日志记录器
        """
        # 获取基础logger，传入监控器名称
        logger = configure_logger(self.monitor_name)
        
        # 确保不重复输出到根logger
        logger.propagate = False

        # 检查是否已经有文件处理器，防止重复添加
        has_file_handler = any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)
        if has_file_handler:
            return logger

        # 确保日志目录存在
        log_dir = os.path.join(self.project_path.LOGS, self.monitor_name)
        self._ensure_dir(log_dir)

        # 创建日志文件名（使用时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"{self.monitor_name}_{timestamp}.log")

        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # 设置格式 - 使用与控制台相同的格式，monitor_name已经在控制台格式中设置
        formatter = logging.Formatter(f'%(asctime)s - %(levelname)s - [{self.monitor_name}] - %(message)s')
        file_handler.setFormatter(formatter)

        # 添加到logger
        logger.addHandler(file_handler)

        logger.debug(f"日志文件已创建: {log_file}")

        return logger

    def _init_proxy(self) -> None:
        """
        初始化代理
        """
        # 品赞代理地址
        self.proxy_pin_zan_url = 'https://service.ipzan.com/core-extract?num=1&no=20250418922716594779&minute=1&pool=quality&secret=go1ouj73e1lf2h'

        # clash代理地址
        self.proxy_clash_url = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}

        # ipcool代理地址
        self.ipcool_url = {
            'http': 'http://{}:{}@us.ipcool.net:2555'.format("13727744565_187_0_0_session_15_1", "lin2225427"),
            'https': 'http://{}:{}@us.ipcool.net:2555'.format("13727744565_187_0_0_session_15_1", "lin2225427")
            }

        allowed_values = {"clash", "pin_zan", "kuai_dai_li", "ipcool", None}
        if self.proxy_type and self.proxy_type not in allowed_values:
            raise ValueError("proxy_type must be one of 'clash', 'pin_zan', 'kuai_dai_li', 'ipcool'")

    def init_page(self) -> ChromiumPage:
        """
        初始化Chromium浏览器页面
        
        Returns:
            ChromiumPage: 配置好的浏览器页面对象
        """
        # 创建浏览器选项
        option = ChromiumOptions()

        # 静音浏览器
        option.mute(True)

        # 设置加载模式为eager以加快加载速度
        allowed_values = {"normal", "eager", "none", None}
        if self.load_mode and self.load_mode not in allowed_values:
            raise ValueError("load_mode 只允许在 {'normal', 'eager', 'none', None}")

        option.set_load_mode(self.load_mode)

        option.set_browser_path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')

        # 禁用图片加载以提高性能
        option.no_imgs(self.is_no_img)

        # 根据配置决定是否使用无头模式
        option.headless(self.is_headless)

        # 根据配置决定是否自动切换端口
        if self.monitor_name != "julian" and self.is_auto_port:
            option.auto_port(self.is_auto_port)

        if self.monitor_name == "julian" or self.monitor_name == "mrporter":
            option.set_local_port(19999)

        option.ignore_certificate_errors(True)

        option.incognito(self.is_auto_port)

        # 设置代理
        if self.proxy_type:
            if self.proxy_type == "clash":
                option.set_proxy(self.proxy_clash_url['http'])
            elif self.proxy_type == "pin_zan":
                option.set_proxy(self._fetch_proxy(self.proxy_pin_zan_url))
            elif self.proxy_type == "kuai_dai_li":
                # 载入代理插件
                # current_directory = os.path.dirname(os.path.abspath(__file__))
                # proxy_path = os.path.join(current_directory, 'kdl_Chromium_Proxy')
                # if not os.path.exists(proxy_path):
                #     self._set_proxy()
                # option.add_extension(proxy_path)
                #
                # 快代理直连
                tunnel = "d122.kdltps.com:15818"
                option.set_proxy("http://" + tunnel)
            elif self.proxy_type == "ipcool":
                option.add_extension(r"E:\pythonProject\extension\Proxy-SwitchyOmega-Chromium-2.5.20")

        # 设置用户代理头，确保格式正确
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"
        option.set_argument(f'--user-agent={user_agent}')

        # 创建并返回浏览器页面
        page = ChromiumPage(option)

        if self.proxy_type == "ipcool" and self.page:
            set_switchy_omega(page)

        self.logger.debug(f"{self.monitor_name} - 浏览器页面已初始化")
        return page

    def init_session(self) -> SessionPage:
        """
        初始化会话对象，用于发送HTTP请求
        
        Returns:
            SessionPage: 配置好的会话对象
        """
        session_option = SessionOptions()
        if self.proxy_type:
            if self.proxy_type == "clash":
                session_option.set_proxies(self.proxy_clash_url)

        return SessionPage(session_option)

    def save_json_data(self, data: dict | list[dict], filename: str = None, category: str = "inventory"):
        """
        将数据保存到本地文件
        
        Args:
            data (dict/list[dict]): 需要保存的数据
            filename (str, optional): 文件名，默认为当前时间戳
            category (str, optional): 数据类别，用于确定保存目录，默认为"inventory"
        
        Returns:
            str: 保存的文件路径
        """
        # 如果没有指定文件名，使用当前时间戳
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.monitor_name}_{timestamp}.json"
        elif not filename.endswith('.json'):
            filename = f"{filename}.json"

        # 构建保存路径
        save_dir = os.path.join(self.data_root, self.monitor_name, category)
        self._ensure_dir(save_dir)
        file_path = os.path.join(save_dir, filename)

        # 保存数据到JSON文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.logger.debug(f"数据已保存到 {file_path}")

        return file_path

    def save_summary_data(self, data: str, category: str = "summary") -> str:
        """
        将总结数据保存到本地文件

        Args:
            data (str): 需要保存的总结数据
            category (str, optional): 数据类别，用于确定保存目录，默认为"summary"

        Returns:
            str: 保存的文件路径
        """
        # 如果没有指定文件名，使用当前时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"inventory_summary_{self.monitor_name}_{timestamp}.txt"

        # 构建保存路径
        save_dir = os.path.join(self.data_root, self.monitor_name, category)
        self._ensure_dir(save_dir)
        file_path = os.path.join(save_dir, filename)

        # 保存数据到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data)

        self.logger.info(f"{self.monitor_name} - 数据已保存到 {file_path}")

        return file_path

    def save_log_to_file(self):
        """
        将当前日志保存到文件
        
        保存在self.project_path.LOGS/{self.monitor_name}/目录下
        """
        # 日志已经在初始化时配置为同时写入文件，此方法用于运行结束时记录日志完成的信息
        self.logger.debug(f"{self.monitor_name} - 监控任务完成，日志已保存")

    def create_inventory_data(self):
        """
        生成库存信息dict

        参数:
            inventory_info (dict):
        返回:
        """
        # 获取每个商品的库存信息
        successful_products = 0
        for i, product in enumerate(self.products_list):
            try:
                self.logger.debug(f"正在获取商品 [{i + 1}/{len(self.products_list)}]: {product['name']}")
                # 随机延迟，避免被网站反爬
                random_sleep(1, 3)

                # 获取库存信息
                inventory_info = self.get_inventory_page(product['url'])

                if inventory_info:
                    # 将库存信息添加到总数据中
                    # 使用URL的最后部分作为唯一标识，避免重复键
                    url_parts = product['url'].rstrip('/').split('/')
                    unique_key = f"{product['name']}_{url_parts[-1]}"

                    self.inventory_data[unique_key] = {
                        'name': product['name'],  # 保存原始名称
                        'url': product['url'],
                        'price': product.get('price', ''),
                        'inventory': inventory_info,
                        'timestamp': datetime.now().isoformat()
                    }
                    successful_products += 1
                    self.logger.info(f"成功获取商品 '{product['name']}' 的库存信息，共 {len(inventory_info)} 种尺码")
                else:
                    self.logger.warning(f"商品 '{product['name']}' 未获取到库存信息")
            except Exception as e:
                self.logger.error(f"获取商品 '{product['name']}' 库存信息时出错: {str(e)}")

        self.logger.info(f"库存信息获取完成，成功: {successful_products}/{len(self.products_list)}")

    def _normalize_inventory_data(self, data: dict) -> dict:
        """
        标准化库存数据格式，确保符合基类要求
        
        Args:
            data (dict): 子类提供的库存数据
            
        Returns:
            dict: 标准化后的库存数据，格式为：
                {唯一标识id: {"name": xxx, "url": xxx, "price": xxx, "inventory": {"尺码": "存货情况", ...}, "timestamp": xxx}, ...}
        """
        normalized_data = {}

        # 验证数据是否符合格式要求
        if not isinstance(data, dict):
            self.logger.error(f"库存数据格式错误，应为字典类型，实际为 {type(data)}")
            return normalized_data

        for key, item in data.items():
            # 确保每个项目是字典类型
            if not isinstance(item, dict):
                self.logger.warning(f"项目 {key} 格式错误，应为字典类型，实际为 {type(item)}")
                continue

            # 确保必要字段存在
            if "name" not in item:
                self.logger.warning(f"项目 {key} 缺少必要字段 'name'")
                item["name"] = str(key)

            if "timestamp" not in item:
                item["timestamp"] = datetime.now().isoformat()

            if "url" not in item:
                item["url"] = ""

            if "price" not in item:
                item["price"] = ""

            if "key_monitoring" not in item:
                item["key_monitoring"] = False

            # 确保inventory字段是字典类型
            if "inventory" in item and not isinstance(item["inventory"], dict):
                self.logger.warning(
                    f"项目 {key} 的 'inventory' 字段格式错误，应为字典类型，实际为 {type(item['inventory'])}")
                continue

            normalized_data[key] = item

        return normalized_data

    def _load_previous_inventory(self):
        """
        加载最近一次的库存数据，用于对比变化
        """
        inventory_dir = os.path.join(self.data_root, self.monitor_name, "inventory")

        if not os.path.exists(inventory_dir):
            self.logger.info(f"未找到历史库存数据目录: {inventory_dir}")
            return

        # 获取所有JSON文件
        json_files = glob.glob(os.path.join(inventory_dir, "*.json"))

        if not json_files:
            self.logger.info(f"未找到历史库存数据文件")
            return

        # 按修改时间排序，获取最新的文件
        latest_file = max(json_files, key=os.path.getmtime)

        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                self.previous_inventory = json.load(f)
            self.logger.debug(f"加载了上次的库存数据: {latest_file}")
        except Exception as e:
            self.logger.error(f"加载历史库存数据出错: {str(e)}")

    def load_cookies(self):
        """
        从文件中加载cookies
        """
        cookies_path = os.path.join(self.project_path.COOKIES, f'{self.monitor_name}_cookies.txt')

        return load_cookies(cookies_path, self.logger)

    def detect_inventory_changes(self, current_inventory):
        """
        检测库存变化，包括新上架商品、下架商品和库存状态变化
        
        Args:
            current_inventory (dict): 当前库存数据
            
        Returns:
            dict: 变化信息，包括新商品、下架商品和库存变化
        """
        if not self.previous_inventory:
            self.logger.info("没有历史库存数据，无法检测变化")
            return None

        # 标准化当前库存数据
        current = self._normalize_inventory_data(current_inventory)
        
        # 检查数据有效性
        if len(current) < 5:  # 假设正常情况下至少应有5个商品
            self.logger.warning(f"当前获取到的商品数量异常少({len(current)}个)，不进行变化检测")
            return None
            
        if len(self.previous_inventory) < 5:  # 上次爬取的数据异常少
            self.logger.warning(f"上次爬取的商品数量异常少({len(self.previous_inventory)}个)，不进行变化检测")
            return None
            
        # 检查数据量差异是否异常
        current_count = len(current)
        previous_count = len(self.previous_inventory)
        diff_percentage = abs(current_count - previous_count) / max(current_count, previous_count) * 100
        
        if diff_percentage > 50:  # 如果数据量相差超过50%，可能是爬取异常
            self.logger.warning(f"当前数据({current_count}个)与上次数据({previous_count}个)相差{diff_percentage:.1f}%，超过阈值，不进行变化检测")
            return None

        # 检测变化
        changes = {
            "new_products": [],  # 新上架的商品
            "removed_products": [],  # 下架的商品
            "inventory_changes": [],  # 库存变化
            "key_product_changes": []  # 重点监控商品的变化
        }

        # 检测新上架的商品
        for key, item in current.items():
            if key not in self.previous_inventory:
                changes["new_products"].append({
                    "id": key,
                    "name": item.get("name", ""),
                    "url": item.get("url", ""),
                    "price": item.get("price", ""),
                    "inventory": item.get("inventory", {})
                })

        # 检测下架的商品
        for key, item in self.previous_inventory.items():
            if key not in current:
                changes["removed_products"].append({
                    "id": key,
                    "name": item.get("name", ""),
                    "url": item.get("url", ""),
                    "price": item.get("price", "")
                })

        # 检测库存变化
        for key, item in current.items():
            if key in self.previous_inventory:
                prev_inventory = self.previous_inventory[key].get("inventory", {})
                curr_inventory = item.get("inventory", {})
                
                # 检查价格变化
                prev_price = self.previous_inventory[key].get("price", "")
                curr_price = item.get("price", "")
                price_change = None
                if prev_price != curr_price and prev_price and curr_price:
                    price_change = {
                        "from": prev_price,
                        "to": curr_price
                    }

                # 检测尺码变化
                size_changes = []

                # 检测新增尺码
                for size, status in curr_inventory.items():
                    if size not in prev_inventory:
                        size_changes.append({
                            "size": size,
                            "type": "added",
                            "status": status
                        })
                    elif prev_inventory[size] != status:
                        change_type = "changed"
                        # 特别标记补货和售罄情况
                        if prev_inventory[size].lower() in ["sold out", "out of stock"] and status.lower() in ["in stock", "available"]:
                            change_type = "stock_in"  # 补货
                        elif prev_inventory[size].lower() in ["in stock", "available"] and status.lower() in ["sold out", "out of stock"]:
                            change_type = "stock_out"  # 售罄
                            
                        size_changes.append({
                            "size": size,
                            "type": change_type,
                            "from": prev_inventory[size],
                            "to": status
                        })

                # 检测移除尺码
                for size, status in prev_inventory.items():
                    if size not in curr_inventory:
                        size_changes.append({
                            "size": size,
                            "type": "removed",
                            "previous_status": status
                        })

                if size_changes or price_change:
                    change_info = {
                        "id": key,
                        "name": item.get("name", ""),
                        "url": item.get("url", ""),
                        "price": item.get("price", "")
                    }
                    
                    if size_changes:
                        change_info["size_changes"] = size_changes
                    
                    if price_change:
                        change_info["price_change"] = price_change
                        
                    changes["inventory_changes"].append(change_info)
                    
                    # 如果是重点监控商品，添加到key_product_changes
                    if item.get("key_monitoring", False):
                        changes["key_product_changes"].append(change_info)

        # 如果有变化，保存变化记录
        has_changes = (
                len(changes["new_products"]) > 0 or
                len(changes["removed_products"]) > 0 or
                len(changes["inventory_changes"]) > 0
        )

        if has_changes:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.save_json_data(changes, f"inventory_changes_{timestamp}", category="changes")
            self.logger.info(
                f"检测到库存变化: {len(changes['new_products'])}个新商品, {len(changes['removed_products'])}个下架商品, {len(changes['inventory_changes'])}个库存变化, {len(changes['key_product_changes'])}个重点商品变化")
        else:
            self.logger.info("未检测到库存变化")

        return changes if has_changes else None

    @staticmethod
    def _ensure_dir(directory):
        """确保指定目录存在"""
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def _set_kuai_proxy():
        """
        设置快代理隧道代理
        :return:
        """
        tunnelhost = 'd122.kdltps.com'  # 隧道域名
        tunnelport = '15818'  # 端口号

        username = 't14445839263797'  # 代理用户名
        password = '1gr4htp3'  # 代理密码

        create_proxyauth_extension(
            proxy_host=tunnelhost,
            proxy_port=tunnelport,
            proxy_username=username,
            proxy_password=password
        )

    @staticmethod
    def _fetch_proxy(proxy_url: str) -> str:
        """
        重置代理
        参数:
            proxy_url (str): 网页API，获取动态代理ip地址
        返回：
            str：代理IP地址
        """
        res_pro = requests.get(proxy_url, timeout=10)
        proxy_text = f'http://{res_pro.text}'
        return proxy_text

    def run_with_log(self):
        """
        带日志记录功能的运行方法
        
        这是run方法的包装器，在运行完成后保存日志
        """
        try:
            result = self.run()
            return result
        finally:
            # 确保在方法结束时记录和保存日志
            self.save_log_to_file()
            # 清理多余的日志和数据文件
            self.cleanup_files()
            if self.page and self.is_auto_port:
                self.page.quit()
            return len(self.inventory_data)

    def cleanup_files(self, max_log_files=20, max_data_files=50, max_days_to_keep=30):
        """
        清理多余的日志和数据文件，保留最近的文件
        
        Args:
            max_log_files (int): 保留的最大日志文件数量
            max_data_files (int): 每个类别（inventory、changes等）保留的最大数据文件数量
            max_days_to_keep (int): 文件保留的最大天数，超过此天数的文件将被删除，即使数量未超过上限
        """
        self.logger.info(f"开始清理多余的日志和数据文件...")
        
        # 计算截止时间
        cutoff_time = datetime.now().timestamp() - (max_days_to_keep * 24 * 60 * 60)
        
        # 清理日志文件
        log_dir = os.path.join(self.project_path.LOGS, self.monitor_name)
        self._cleanup_dir_files(log_dir, "*.log", max_log_files, "日志", cutoff_time)
        
        # 清理数据目录下的各类数据文件
        monitor_data_dir = os.path.join(self.data_root, self.monitor_name)
        if os.path.exists(monitor_data_dir):
            # 清理库存数据
            inventory_dir = os.path.join(monitor_data_dir, "inventory")
            self._cleanup_dir_files(inventory_dir, "*.json", max_data_files, "库存数据", cutoff_time)
            
            # 清理变更数据
            changes_dir = os.path.join(monitor_data_dir, "changes")
            self._cleanup_dir_files(changes_dir, "inventory_changes_*.json", max_data_files, "变更数据", cutoff_time)
            
            # 清理总结数据
            summary_dir = os.path.join(monitor_data_dir, "summary")
            self._cleanup_dir_files(summary_dir, "*.txt", max_data_files, "总结文件", cutoff_time)
            self._cleanup_dir_files(summary_dir, "*.json", max_data_files, "总结JSON", cutoff_time)
        
        self.logger.debug("文件清理完成")

    def _cleanup_dir_files(self, directory, pattern, max_files, file_type, cutoff_time=None):
        """
        清理指定目录下的文件，保留最新的文件
        
        Args:
            directory (str): 要清理的目录
            pattern (str): 文件匹配模式（如 "*.log"）
            max_files (int): 保留的最大文件数量
            file_type (str): 文件类型描述，用于日志
            cutoff_time (float, optional): 时间戳，超过此时间的文件将被删除，即使数量未超过上限
        """
        if not os.path.exists(directory):
            return
            
        # 获取所有匹配的文件
        files = glob.glob(os.path.join(directory, pattern))
        
        if not files:
            return
            
        # 根据文件类型选择排序方法
        if "inventory" in file_type.lower() and len(files) > 0 and "balenciaga_inventory_" in os.path.basename(files[0]):
            # 针对库存文件使用文件名中的时间戳排序
            def extract_timestamp(filename):
                match = re.search(r"balenciaga_inventory_(\d{8}_\d{6})\.json$", os.path.basename(filename))
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
        
        # 需要删除的文件列表
        files_to_delete = []
        
        # 先保留最新的max_files个文件，将其余文件标记为待删除
        if len(files) > max_files:
            files_to_delete.extend(files[max_files:])
            remaining_files = files[:max_files]
        else:
            remaining_files = files.copy()
        
        # 再检查剩余文件中是否有过期的文件
        if cutoff_time:
            expired_files = [f for f in remaining_files if os.path.getmtime(f) < cutoff_time]
            files_to_delete.extend(expired_files)
        
        if not files_to_delete:
            self.logger.debug(f"{file_type}文件不需要清理：{len(files)}/{max_files}个文件，均未过期")
            return
            
        deleted_count = 0
        for file in files_to_delete:
            try:
                os.remove(file)
                deleted_count += 1
            except Exception as e:
                self.logger.warning(f"删除{file_type}文件失败: {file}, 错误: {str(e)}")
                
        if deleted_count > 0:
            self.logger.debug(f"已清理 {deleted_count} 个{file_type}文件，保留 {len(files) - deleted_count} 个文件")

    @abstractmethod
    def run(self):
        """
        运行监控的主方法，子类必须实现此方法
        
        实现该方法时，通常包含以下步骤：
        1. 获取商品目录
        2. 解析商品目录
        3. 获取每个商品的库存信息
        4. 保存库存数据
        5. 生成库存监控总结
        """
        raise NotImplementedError("子类必须实现run方法")

    @abstractmethod
    def get_inventory_catalog(self):
        """
        获取商品目录
        
        从目标网站获取商品列表
        
        Returns:
            list: 商品信息列表，每个元素为包含商品详细信息的字典
        """
        raise NotImplementedError("子类必须实现get_inventory_catalog方法")

    def get_inventory_page(self, url):
        """
        获取单个商品的库存信息
        
        参数:
            url (str): 商品页面URL
            
        返回:
            dict: 商品的尺码和库存状态信息
        """
        raise NotImplementedError("子类可选择实现get_inventory_page方法")

    @abstractmethod
    def parse_inventory_catalog(self, catalog_data):
        """
        解析商品目录数据
        
        参数:
            catalog_data: 包含商品目录的数据
            
        返回:
            list: 商品信息列表，每个元素为包含商品详细信息的字典
        """
        raise NotImplementedError("子类必须实现parse_inventory_catalog方法")

    def parse_inventory_info(self, data):
        """
        解析商品库存信息
        
        参数:
            data: 包含商品库存信息的数据
            
        返回:
            dict: 尺码和库存状态的字典，格式为 {尺码: 库存状态}
        """
        raise NotImplementedError("子类可选择实现parse_inventory_info方法")

    def generate_inventory_summary(self):
        """
        生成商品库存监控总结，子类可以重写此方法
        
        返回:
            str: 格式化的库存监控总结文本
            dict: 库存总结JSON数据
        """
        # 默认实现
        summary_text = f"******{self.monitor_name.capitalize()} - 库存监控********\n"
        summary_data = {
            "monitor": self.monitor_name,
            "timestamp": datetime.now().isoformat(),
            "total_products": len(self.inventory_data),
            "products": []
        }

        if not self.inventory_data:
            summary_text += "无库存数据\n"
            return summary_text, summary_data

        # 子类应自行实现更详细的总结逻辑

        return summary_text, summary_data

    @staticmethod
    def normalize_url(url):
        parsed = urlparse(url)
        # 保留路径，忽略查询参数和片段
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

# if __name__ == '__main__':
# monitor = Monitor(is_headless=False)
# monitor._set_proxy()
