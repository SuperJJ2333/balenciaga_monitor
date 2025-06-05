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
import traceback

from src.common.project_path import ProjectPaths
from src.common.logger import get_logger


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
        从文件名中提取时间戳
        支持两种格式：
        1. inventory_summary_YYYYMMDD_HHMMSS.json
        2. balenciaga_inventory_YYYYMMDD_HHMMSS.json
        :param filename: str
        :return: 时间戳
        """
        # 尝试匹配两种可能的时间戳格式
        match1 = re.search(r'inventory_summary_(\d{8}_\d{6})\.json', os.path.basename(filename))
        match2 = re.search(r'balenciaga_inventory_(\d{8}_\d{6})\.json', os.path.basename(filename))
        
        if match1:
            timestamp_str = match1.group(1)
        elif match2:
            timestamp_str = match2.group(1)
        else:
            # 如果找不到匹配的时间戳格式，回退到使用文件修改时间
            return datetime.fromtimestamp(os.path.getmtime(filename))
            
        try:
            return datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        except ValueError:
            # 如果时间戳格式不符合预期，回退到使用文件修改时间
            return datetime.fromtimestamp(os.path.getmtime(filename))

    def find_previous_json(self, current_file, dir_path):
        """
        查找同一目录下的上一个JSON文件
        支持两种命名格式：
        1. inventory_summary_*.json
        2. balenciaga_inventory_*.json
        """
        # 获取目录下所有符合条件的JSON文件
        all_files1 = glob.glob(os.path.join(dir_path, "inventory_summary_*.json"))
        all_files2 = glob.glob(os.path.join(dir_path, "balenciaga_inventory_*.json"))
        
        # 合并两种格式的文件列表
        all_files = all_files1 + all_files2
        
        if not all_files:
            self.logger.warning(f"目录 {dir_path} 中没有找到符合条件的JSON文件")
            return None

        # 按时间戳排序（从新到旧）
        all_files.sort(key=self._extract_timestamp, reverse=True)
        
        # 去除当前文件
        current_basename = os.path.basename(current_file)
        filtered_files = [f for f in all_files if os.path.basename(f) != current_basename]
        
        if not filtered_files:
            self.logger.warning(f"没有找到比 {current_file} 更早的文件")
            return None
            
        # 返回比当前文件更早的第一个文件
        self.logger.info(f"找到上一个文件: {filtered_files[0]}")
        return filtered_files[0]

    @staticmethod
    def compare_inventory(current_data, previous_data):
        """
        比较当前和上一次的库存数据，返回变化情况
        支持两种数据格式:
        1. 带products字段的格式 (原有格式)
        2. 键值对直接存储商品信息的格式 (新格式)
        """
        changes = {
            "new_products": [],  # 新增产品
            "removed_products": [],  # 移除产品
            "inventory_changes": [],  # 库存变化
            "key_product_changes": []  # 重点监控商品的价格或尺寸变化
        }

        if not previous_data:
            # 如果没有上一次数据，则当前所有产品都视为新增
            if "products" in current_data:
                # 原有格式
                changes["new_products"] = current_data.get("products", [])
            else:
                # 新格式: 将键值对转换为产品列表
                for key, product in current_data.items():
                    # 跳过非商品字段
                    if key in ["monitor", "timestamp"]:
                        continue
                    changes["new_products"].append(product)
            return changes

        # 处理原有格式的数据 (带products字段)
        if "products" in current_data or "products" in previous_data:
            current_products = {p.get("name"): p for p in current_data.get("products", [])}
            previous_products = {p.get("name"): p for p in previous_data.get("products", [])}
        else:
            # 处理新格式的数据 (键值对直接存储商品信息)
            current_products = {}
            previous_products = {}
            
            # 提取当前商品数据
            for key, product in current_data.items():
                if key in ["monitor", "timestamp"]:
                    continue
                product_name = product.get("name", key)
                current_products[product_name] = product
                
            # 提取上一次商品数据
            for key, product in previous_data.items():
                if key in ["monitor", "timestamp"]:
                    continue
                product_name = product.get("name", key)
                previous_products[product_name] = product

        # 检查当前和上一次数据的商品数量差异
        current_count = len(current_products)
        previous_count = len(previous_products)
        count_diff_ratio = abs(current_count - previous_count) / max(current_count, previous_count) if max(current_count, previous_count) > 0 else 0
        
        # 如果数据量差异过大（超过30%），可能是爬取异常，对重点监控商品特殊处理
        is_data_suspicious = count_diff_ratio > 0.3
        
        # 找出新增产品（排除可能因爬取失败导致的"假新增"重点监控商品）
        for name, product in current_products.items():
            if name not in previous_products:
                # 如果是重点监控商品且数据可疑，不将其标记为新增
                is_key_product = product.get("key_monitoring", False)
                if is_data_suspicious and is_key_product:
                    # 记录为可疑新增，但不添加到新增列表
                    continue
                changes["new_products"].append(product)

        # 找出移除产品（排除可能因爬取失败导致的"假移除"重点监控商品）
        for name, product in previous_products.items():
            if name not in current_products:
                # 如果是重点监控商品且数据可疑，不将其标记为移除
                is_key_product = product.get("key_monitoring", False)
                if is_data_suspicious and is_key_product:
                    # 记录为可疑移除，但不添加到移除列表
                    continue
                changes["removed_products"].append(product)

        # 找出库存变化和重点监控商品的变化
        for name, current_product in current_products.items():
            if name in previous_products:
                previous_product = previous_products[name]
                is_key_product = current_product.get("key_monitoring", False)
                has_changes = False
                change_details = {"price_change": None, "size_changes": []}
                
                # 检查价格变化（仅对重点监控商品）
                if is_key_product and "price" in current_product and "price" in previous_product:
                    current_price = current_product["price"]
                    previous_price = previous_product["price"]
                    
                    # 检查价格变化是否可疑（例如从空变为有值，或价格变化过大）
                    price_change_suspicious = False
                    if not previous_price and current_price:  # 从无价格变为有价格
                        price_change_suspicious = True
                    elif previous_price and current_price:
                        # 尝试提取数值部分进行比较
                        import re
                        prev_num = re.search(r'[\d,.]+', previous_price)
                        curr_num = re.search(r'[\d,.]+', current_price)
                        
                        if prev_num and curr_num:
                            try:
                                prev_val = float(prev_num.group().replace(',', ''))
                                curr_val = float(curr_num.group().replace(',', ''))
                                # 如果价格变化超过50%，可能是可疑的
                                if abs(curr_val - prev_val) / max(curr_val, prev_val) > 0.5:
                                    price_change_suspicious = True
                            except (ValueError, ZeroDivisionError):
                                # 如果无法解析为数字，仍然比较原始字符串
                                if current_price != previous_price:
                                    if is_data_suspicious:
                                        price_change_suspicious = True
                        
                    # 只有在数据不可疑或价格变化不可疑的情况下才记录价格变化
                    if current_price != previous_price and (not is_data_suspicious or not price_change_suspicious):
                        change_details["price_change"] = {
                            "from": previous_price,
                            "to": current_price
                        }
                        has_changes = True

                # 检查"inventory"字段 (新格式)
                if "inventory" in current_product and "inventory" in previous_product:
                    current_inventory = current_product["inventory"]
                    previous_inventory = previous_product["inventory"]
                    
                    # 检查库存数据是否可疑
                    inventory_suspicious = False
                    if is_key_product and is_data_suspicious:
                        # 如果尺码数量差异过大，可能是可疑的
                        curr_size_count = len(current_inventory)
                        prev_size_count = len(previous_inventory)
                        if abs(curr_size_count - prev_size_count) / max(curr_size_count, prev_size_count) > 0.3 if max(curr_size_count, prev_size_count) > 0 else False:
                            inventory_suspicious = True
                    
                    # 检查是否有变化
                    if current_inventory != previous_inventory and (not is_key_product or not inventory_suspicious):
                        size_changes = []
                        
                        # 检查每个尺码的变化
                        all_sizes = set(current_inventory.keys()) | set(previous_inventory.keys())
                        for size in all_sizes:
                            curr_status = current_inventory.get(size, "Sold Out")
                            prev_status = previous_inventory.get(size, "Sold Out")
                            
                            if curr_status != prev_status:
                                size_change = {
                                    "size": size,
                                    "from": prev_status,
                                    "to": curr_status,
                                    "type": "stock_changed"
                                }
                                size_changes.append(size_change)
                                change_details["size_changes"].append(size_change)
                                has_changes = True
                                
                        if size_changes and not is_key_product:
                            product_change = current_product.copy()
                            product_change["size_changes"] = size_changes
                            changes["inventory_changes"].append(product_change)
                    
                    # 处理重点监控商品的变化
                    if is_key_product and has_changes and not inventory_suspicious:
                        key_product_change = current_product.copy()
                        key_product_change.update(change_details)
                        changes["key_product_changes"].append(key_product_change)
                    
                    continue  # 如果已处理inventory字段，跳过下面的inventory_status处理
                
                # 处理"inventory_status"字段 (原有格式)
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

                # 检查库存数据是否可疑
                inventory_suspicious = False
                if is_key_product and is_data_suspicious:
                    # 如果尺码数量差异过大，可能是可疑的
                    curr_size_count = len(current_status)
                    prev_size_count = len(previous_status)
                    if abs(curr_size_count - prev_size_count) / max(curr_size_count, prev_size_count) > 0.3 if max(curr_size_count, prev_size_count) > 0 else False:
                        inventory_suspicious = True

                # 检查状态变化
                size_changes = []

                # 只有在数据不可疑或不是重点监控商品的情况下才进行详细的状态变化检查
                if not (is_key_product and inventory_suspicious):
                    # 1. 检查尺码从有库存变为缺货
                    for size, prev_status in previous_status.items():
                        if prev_status.lower() != "sold out":
                            curr_status = current_status.get(size, "")
                            if curr_status.lower() == "sold out":
                                size_change = {
                                    "size": size,
                                    "from": prev_status,
                                    "to": curr_status,
                                    "type": "stock_out"
                                }
                                size_changes.append(size_change)
                                change_details["size_changes"].append(size_change)
                                has_changes = True

                    # 2. 检查尺码从缺货变为有库存
                    for size, curr_status in current_status.items():
                        if curr_status.lower() != "sold out":
                            prev_status = previous_status.get(size, "")
                            if prev_status.lower() == "sold out" or size not in previous_status:
                                size_change = {
                                    "size": size,
                                    "from": prev_status,
                                    "to": curr_status,
                                    "type": "stock_in"
                                }
                                size_changes.append(size_change)
                                change_details["size_changes"].append(size_change)
                                has_changes = True

                    # 如果有尺码变化，将产品添加到变化列表
                    if size_changes and not is_key_product:
                        product_change = current_product.copy()
                        product_change["size_changes"] = size_changes
                        changes["inventory_changes"].append(product_change)
                
                # 处理重点监控商品的变化
                if is_key_product and has_changes and not inventory_suspicious:
                    key_product_change = current_product.copy()
                    key_product_change.update(change_details)
                    changes["key_product_changes"].append(key_product_change)

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
        """
        发送钉钉消息
        
        Args:
            webhook_url: 钉钉机器人的webhook URL
            secret: 钉钉机器人的加签密钥
            message: 要发送的markdown消息，包含title和text字段
            
        Returns:
            dict: 钉钉API的响应结果
        """
        try:
            self.logger.info("准备发送钉钉消息...")
            
            # 检查参数
            if not webhook_url:
                self.logger.error("钉钉webhook URL为空")
                return {"errcode": 5000, "errmsg": "webhook URL为空"}
                
            if not secret:
                self.logger.warning("钉钉加签密钥为空，可能会导致发送失败")
                
            if not message or not isinstance(message, dict):
                self.logger.error("消息格式错误，应为字典类型")
                return {"errcode": 5001, "errmsg": "消息格式错误"}
            
            # 生成签名
            timestamp = str(round(time.time() * 1000))
            secret_enc = secret.encode('utf-8')
            string_to_sign = '{}\n{}'.format(timestamp, secret)
            string_to_sign_enc = string_to_sign.encode('utf-8')
            hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

            url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
            self.logger.info(f"生成签名成功，目标URL长度: {len(url)}")

            headers = {
                'Content-Type': 'application/json',
                'Charset': 'UTF-8'
            }

            data = {
                "msgtype": "markdown",
                "markdown": message,
            }
            
            # 记录请求信息
            self.logger.info(f"发送POST请求到钉钉API，数据大小: {len(json.dumps(data))} 字节")
            
            # 发送请求
            try:
                response = requests.post(
                    url, 
                    headers=headers, 
                    data=json.dumps(data), 
                    proxies={'http': None, 'https': None},
                    timeout=10  # 设置超时时间
                )
                
                # 检查HTTP状态码
                if response.status_code != 200:
                    self.logger.error(f"HTTP请求失败，状态码: {response.status_code}, 响应: {response.text}")
                    return {"errcode": response.status_code, "errmsg": f"HTTP请求失败: {response.text}"}
                    
                # 解析响应
                result = response.json()
                self.logger.info(f"钉钉API响应: {result}")
                
                # 检查钉钉API返回的错误码
                if result.get("errcode") != 0:
                    self.logger.error(f"钉钉API返回错误: {result.get('errmsg', '未知错误')}")
                else:
                    self.logger.info("钉钉消息发送成功!")
                    
                return result
                
            except requests.exceptions.Timeout:
                self.logger.error("请求超时，钉钉API未响应")
                return {"errcode": 5002, "errmsg": "请求超时"}
            except requests.exceptions.ConnectionError:
                self.logger.error("网络连接错误，无法连接到钉钉API")
                return {"errcode": 5003, "errmsg": "网络连接错误"}
            except Exception as e:
                self.logger.error(f"发送请求时出错: {str(e)}")
                return {"errcode": 5004, "errmsg": f"发送请求时出错: {str(e)}"}
                
        except Exception as e:
            self.logger.error(f"发送钉钉消息时出错: {str(e)}")
            self.logger.error(f"错误详情: {traceback.format_exc()}")
            return {"errcode": 5005, "errmsg": f"发送钉钉消息时出错: {str(e)}"}

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
        changed_count = len(changes["inventory_changes"])
        print(f"变化统计: 新增商品 {new_count}个, 下架商品 {removed_count}个, 库存变化商品 {changed_count}个")

        # 生成钉钉消息
        markdown_message = self.generate_change_markdown(changes, current_data, file_path)

        # 如果有变化，保存变化数据到本地
        if new_count > 0 or removed_count > 0 or changed_count > 0:
            self.save_changes_to_file(changes, current_data, file_path)

        # 发送消息
        result = self.send_dingtalk_message(webhook_url, secret, markdown_message)
        self.logger.info(f"发送结果: {result}")