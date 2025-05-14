from datetime import datetime, timedelta
import requests
import json
import time
import hmac
import hashlib
import base64
import urllib.parse
import os
import sys
import glob
import re

from common.project_path import ProjectPaths
from common.logger import get_logger


class DingSender:
    """
    钉钉消息自动发送类
    """
    def __init__(self, ding_url, ding_secret, ding_token):
        self.ding_url = ding_url
        self.ding_secret = ding_secret
        self.ding_token = ding_token
        self.logger = get_logger(__name__)
        self.ding_headers = {
            'Content-Type': 'application/json',
        }

    @staticmethod
    def _read_json_file(file_path: str) -> json:
        """
        读取JSON格式的库存总结文件内容
        :param file_path: str
        :return: json
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def _extract_timestamp(filename: str) -> datetime:
        """
        从文件名中提取时间戳（格式为 inventory_summary_YYYYMMDD_HHMMSS.json）
        :param filename: str
        :return: 时间戳
        """
        match = re.search(r'inventory_summary_(\d{8}_\d{6})\.json', os.path.basename(filename))
        if match:
            timestamp_str = match.group(1)
            try:
                return datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            except ValueError:
                # 如果时间戳格式不符合预期，回退到使用文件修改时间
                return datetime.fromtimestamp(os.path.getmtime(filename))
        return datetime.fromtimestamp(os.path.getmtime(filename))

    def find_previous_json(self, current_file, dir_path):
        """
        查找同一目录下的上一个JSON文件
        """
        # 获取目录下所有inventory_summary开头的JSON文件
        all_files = glob.glob(os.path.join(dir_path, "inventory_summary_*.json"))

        if not all_files:
            return None

        # 按时间戳排序（从新到旧）
        all_files.sort(key=self._extract_timestamp, reverse=True)

        # 找出当前文件的索引
        try:
            current_index = all_files.index(current_file)
        except ValueError:
            self.logger.warning(f"当前文件 {current_file} 不在文件列表中，将使用最新的文件")
            return all_files[1] if len(all_files) > 1 else None

        # 如果当前文件已经是最新的文件（索引为0），则返回第二新的文件
        if current_index == 0 and len(all_files) > 1:
            self.logger.info(f"当前文件是最新文件，找到上一个文件: {all_files[1]}")
            return all_files[1]
        # 如果当前文件不是最新的文件，则返回比它更新的文件（索引更小的文件）
        elif current_index > 0:
            self.logger.info(f"当前文件不是最新文件，找到更新的文件: {all_files[current_index - 1]}")
            return all_files[current_index - 1]

        print("未找到合适的上一个文件")
        return None

    @staticmethod
    def compare_inventory(current_data, previous_data):
        """比较当前和上一次的库存数据，返回变化情况"""
        changes = {
            "new_products": [],  # 新增产品
            "removed_products": [],  # 移除产品
            "stock_changes": []  # 库存变化
        }

        if not previous_data:
            # 如果没有上一次数据，则当前所有产品都视为新增
            changes["new_products"] = current_data.get("products", [])
            return changes

        # 获取当前和上一次的产品列表
        current_products = {p.get("name"): p for p in current_data.get("products", [])}
        previous_products = {p.get("name"): p for p in previous_data.get("products", [])}

        # 找出新增产品
        for name, product in current_products.items():
            if name not in previous_products:
                changes["new_products"].append(product)

        # 找出移除产品
        for name, product in previous_products.items():
            if name not in current_products:
                changes["removed_products"].append(product)

        # 找出库存变化
        for name, current_product in current_products.items():
            if name in previous_products:
                previous_product = previous_products[name]

                # 将当前产品的状态转换为更易于比较的格式
                current_status = {}
                for status_info in current_product.get("inventory_status", []):
                    status = status_info.get("status", "")
                    sizes = status_info.get("sizes", [])
                    for size in sizes:
                        current_status[size] = status

                # 将上一次产品的状态转换为更易于比较的格式
                previous_status = {}
                for status_info in previous_product.get("inventory_status", []):
                    status = status_info.get("status", "")
                    sizes = status_info.get("sizes", [])
                    for size in sizes:
                        previous_status[size] = status

                # 检查状态变化
                size_changes = []

                # 1. 检查尺码从有库存变为缺货
                for size, prev_status in previous_status.items():
                    if prev_status.lower() != "sold out":
                        curr_status = current_status.get(size, "")
                        if curr_status.lower() == "sold out":
                            size_changes.append({
                                "size": size,
                                "from": prev_status,
                                "to": curr_status,
                                "type": "stock_out"
                            })

                # 2. 检查尺码从缺货变为有库存
                for size, curr_status in current_status.items():
                    if curr_status.lower() != "sold out":
                        prev_status = previous_status.get(size, "")
                        if prev_status.lower() == "sold out" or size not in previous_status:
                            size_changes.append({
                                "size": size,
                                "from": prev_status,
                                "to": curr_status,
                                "type": "stock_in"
                            })

                # 如果有尺码变化，将产品添加到变化列表
                if size_changes:
                    product_change = current_product.copy()
                    product_change["size_changes"] = size_changes
                    changes["stock_changes"].append(product_change)

        return changes

    def generate_change_markdown(self, changes, current_data, file_path):
        """
        根据变化情况生成钉钉markdown消息，精简版本
        
        Args:
            changes: 当前的变化情况
            current_data: 当前的库存数据
            file_path: 当前库存文件路径
            
        Returns:
            dict: 格式化的markdown消息，如果没有新增商品则返回None
        """
        # 获取新增商品数量
        new_count = len(changes["new_products"])
        
        # 如果没有新增商品，返回None表示不发送消息
        if new_count == 0:
            return None
            
        # 创建精简报告
        monitor_name = current_data.get("monitor", "未知监控器")
        
        markdown_text = f"# {monitor_name}\n\n"
        markdown_text += f"新增商品数: {new_count}\n\n"
        markdown_text += f"新增时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n\n"
        markdown_text += "============\n\n"
        
        # 添加新增商品详情
        for i, product in enumerate(changes["new_products"]):
            name = product.get('name', '未知商品')
            url = product.get('url', '')
            price = product.get('price', '')
            
            markdown_text += f"{i + 1}. {name}\n\n"
            markdown_text += f"价格: {price}\n\n" if price else ""
            markdown_text += f"链接: {url}\n\n" if url else ""
            
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
            
        return {
            "title": f"{monitor_name} - 新增商品通知",
            "text": markdown_text
        }

    def send_dingtalk_message(self, webhook_url, secret, message):
        """发送钉钉消息"""
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

        url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"

        headers = {
            'Content-Type': 'application/json',
            'Charset': 'UTF-8'
        }

        data = {
            "msgtype": "markdown",
            "markdown": message,
        }

        response = requests.post(url, headers=headers, data=json.dumps(data), proxies={'http': None, 'https': None})
        return response.json()

    def save_changes_to_file(self, changes, current_data, file_path):
        """将变化情况保存到本地文件"""
        # 不再需要此方法，保留空方法防止调用时出错
        pass

    def generate_inventory_txt_file(self, inventory_data):
        """生成完整库存信息的文本文件，并返回文件路径"""
        # 不再需要此方法，保留空方法防止调用时出错
        pass

    def get_24h_changes(self, dir_path):
        """
        获取过去24小时内的所有变化记录
        """
        # 不再需要此方法，保留空方法防止调用时出错
        return None

    def run(self):
        # 读取配置
        with open('setting.init', 'r') as f:
            lines = f.readlines()

        webhook_url = lines[0].strip()
        secret = lines[2].strip() if len(lines) > 2 else ""

        # 获取文件路径参数
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
        else:
            # 默认使用最新的json文件
            json_dirs = [
                "src/data/cettire/json_summary",
                "src/data/duomo/json_summary",
                "src/data/eleonora_bonucci/json_summary",
                "src/data/mrporter/json_summary",
                "src/data/suus/json_summary"
            ]

            # 寻找最新的json文件
            latest_file = None
            latest_time = 0

            for dir_path in json_dirs:
                if not os.path.exists(dir_path):
                    continue

                for file in os.listdir(dir_path):
                    if file.endswith('.json') and 'inventory_summary' in file:
                        full_path = os.path.join(dir_path, file)
                        file_time = os.path.getmtime(full_path)

                        if file_time > latest_time:
                            latest_time = file_time
                            latest_file = full_path

            if latest_file:
                file_path = latest_file
                print(f"使用最新文件: {file_path}")
            else:
                file_path = "src/data/cettire/json_summary/inventory_summary_20250418_230733.json"
                print(f"未找到最新文件，使用默认文件: {file_path}")

        # 读取当前JSON库存数据
        try:
            current_data = self._read_json_file(file_path)
            print(f"成功读取当前JSON数据，共有{current_data.get('total_products', 0)}个产品")
        except Exception as e:
            print(f"读取当前JSON文件失败: {e}")
            return

        # 获取上一次的库存数据文件
        dir_path = os.path.dirname(file_path)
        previous_file = self.find_previous_json(file_path, dir_path)
        previous_data = None

        if previous_file:
            try:
                previous_data = self._read_json_file(previous_file)
                print(f"成功读取上一次JSON数据，共有{previous_data.get('total_products', 0)}个产品")
            except Exception as e:
                print(f"读取上一次JSON文件失败: {e}")
        else:
            print("未找到上一次的库存数据，将显示所有当前商品")

        # 比较变化情况
        changes = self.compare_inventory(current_data, previous_data)

        # 记录变化统计
        new_count = len(changes["new_products"])
        removed_count = len(changes["removed_products"])
        changed_count = len(changes["stock_changes"])
        print(f"变化统计: 新增商品 {new_count}个, 下架商品 {removed_count}个, 库存变化商品 {changed_count}个")

        # 生成钉钉消息
        markdown_message = self.generate_change_markdown(changes, current_data, file_path)

        # 如果有变化，保存变化数据到本地
        if new_count > 0 or removed_count > 0 or changed_count > 0:
            self.save_changes_to_file(changes, current_data, file_path)

        # 发送消息
        result = self.send_dingtalk_message(webhook_url, secret, markdown_message)
        self.logger.info(f"发送结果: {result}")