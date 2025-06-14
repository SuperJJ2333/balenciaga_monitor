"""
MrPorter监控模块 - 负责监控MrPorter网站上Balenciaga鞋子的库存状态
该模块实现了对MrPorter网站的爬取、解析和数据保存功能
"""
from datetime import datetime

from src.utils.page_setting import *
from src.common.monitor import Monitor


class DuomoMonitor(Monitor):
    """
    Duomo网站监控类
    JSON数据 尺码在目录页

    Session - API - GET
    负责爬取Duomo网站上Balenciaga品牌鞋子的商品列表和库存信息
    """

    def __init__(self, **kwargs):
        """
        初始化Duomo监控器

        参数:
            is_headless (bool): 是否使用无头模式运行浏览器
            proxy_type (str): 代理类型，可选值为clash、fiddler或'non'
        """
        # 更新监控器名称
        kwargs['monitor_name'] = 'duomo'
        kwargs['catalog_url'] = 'https://www.ilduomo.it/api/categoryProducts'

        super().__init__(**kwargs)

    def init_params(self):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'cookie': self.load_cookies()
            }

        params = {
            'id_category': '6',
            'page': '1',
            'order': 'product.position.desc',
            'q': 'Categories-shoes',
            'id_designer': '15',
        }
        return headers, params

    def run(self):
        """
        运行监控程序的主入口
        
        流程:
        1. 获取商品目录
        2. 解析商品目录
        3. 保存数据
        4. 关闭浏览器
        """
        try:
            self.logger.info(f"开始监控 {self.catalog_url}")

            # 获取商品目录
            catalog_data = self.get_inventory_catalog()
            if not catalog_data:
                self.logger.error("获取商品目录失败，终止监控")
                return

            # 解析商品目录
            self.products_list = self.parse_inventory_catalog(catalog_data)
            self.logger.info(f"监控完成，共获取到 {len(self.products_list)} 个商品信息")

            if self.products_list:
                summary = self.generate_inventory_summary()
                # print(summary)  # 打印到控制台
                self.save_summary_data(data=summary)

        except Exception as e:
            self.logger.error(f"监控过程中出错: {str(e)}")
        finally:
            self.logger.info("监控结束，关闭浏览器")

    def get_inventory_catalog(self):
        """
        获取商品目录

        从Duomo网站获取Balenciaga鞋子的商品列表

        返回:
            list: 商品信息列表，每个元素为包含name和url的字典
        """
        self.logger.info(f"正在获取商品目录: {self.catalog_url}")
        try:
            headers, params = self.init_params()
            session = self.init_session()
            # 设置代理并访问页面
            session.get('https://www.ilduomo.it/api/categoryProducts', params=params, headers=headers)

            # 检查页面响应
            if not session.json:
                self.logger.error("获取页面失败：页面响应为空")
                return {}

            # 尝试查找JSON数据
            try:
                data = session.json
                return data

            except Exception as e:
                self.logger.error(f"处理商品目录元素时出错: {str(e)}")
                return {}

        except Exception as e:
            self.logger.error(f"获取商品目录过程中出错: {str(e)}")
            return {}

    def parse_inventory_catalog(self, catalog_data: dict):
        """
        解析商品目录JSON数据，提取关键商品信息
        
        参数:
            catalog_data (dict): 包含商品目录的JSON数据
        
        返回:
            list: 商品信息列表，每个元素为包含商品详细信息的字典
        """
        try:
            # 检查是否成功获取数据
            if not catalog_data or 'psdata' not in catalog_data or 'products' not in catalog_data['psdata']:
                self.logger.error("商品目录数据格式错误或为空")
                return []
            
            # 提取商品列表
            products = catalog_data['psdata']['products']
            self.logger.info(f"获取到 {len(products)} 个Balenciaga商品")
            pattern = r'https?://[^/]+/([^/]+)/([^/]+)\.html'

            # 遍历每个商品并提取关键信息
            for product in products:
                # 基本信息
                product_info = {
                    "id": product.get("id_product", ""),
                    "name": product.get("name", ""),
                    "url": product.get("link", ""),
                    "price": product.get("price", ""),
                }
                match = re.search(pattern, product.get("link", ""))
                if match:
                    product_info["url"] = 'https://www.ilduomo.it/product/' + match.group(2)
                else:
                    self.logger.warning(f"无法解析商品链接: {product.get('link', '')}")
                ### 提取尺码和库存信息
                sizes_inventory = {}
                if "aviable_size" in product:
                    for size in product["aviable_size"]:
                        size_name = size.get("attribute_name", "")
                        size_info = size.get("quantity", 0)
                        if size_info > 0:
                            size_info = str(size_info)
                        else:
                            size_info = "sold out"

                        sizes_inventory[size_name] = size_info
                
                product_info["inventory"] = sizes_inventory

                ### 创造库存信息
                unique_key = f"{product_info['id']}_{product_info['name']}"
                self.inventory_data[unique_key] = product_info
                self.logger.debug(f"解析商品: {product_info['name']}, 尺码数量: {len(product_info['inventory'])}")
            
            # 保存提取的商品信息到文件
            if self.inventory_data:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                # 检验库存数据格式
                normalized_data = self._normalize_inventory_data(self.inventory_data)
                save_path = self.save_json_data(normalized_data, f"balenciaga_inventory_{timestamp}.json", "inventory")
                self.logger.info(f"商品目录数据已保存到: {save_path}")
            
            return self.inventory_data
            
        except Exception as e:
            self.logger.error(f"解析商品目录数据时出错: {str(e)}")
            return []

    def generate_inventory_summary(self):
        """
        生成库存监控总结文本
        
        返回:
            str: 格式化的库存监控总结文本
        """
        summary_text = f"****** {self.monitor_name.capitalize()}Monitor - 库存监控 ********\n"
        
        timestamp = datetime.now().isoformat()
        summary_data = {
            "monitor": "DuomoMonitor",
            "timestamp": timestamp,
            "total_products": len(self.products_list),
            "products": []
        }
        
        for product in self.products_list.values():
            # 提取产品名称和URL
            name = product.get("name", "未知商品")
            url = product.get("url", "")
            
            # 提取价格信息
            price = product.get("price", "")
            
            # 添加产品基本信息到摘要
            summary_text += f"产品名称: {name} - {url}\n"
            summary_text += f"价格：{price}\n"
            summary_text += "存货情况：\n"
            
            # 准备JSON产品数据
            product_json = {
                "name": name,
                "url": url,
                "price": price,
                "inventory_status": []
            }
            
            # 提取尺码和库存信息
            available_sizes = []
            for size_info in product.get("sizes", []):
                size = size_info.get("size", "")
                quantity = size_info.get("quantity", 0)
                
                if quantity > 0:
                    available_sizes.append(size)
            
            if available_sizes:
                summary_text += f"-- (1) available: {'; '.join(available_sizes)}\n"
                # 添加到JSON
                product_json["inventory_status"].append({
                    "status": "available",
                    "status_index": 1,
                    "sizes": available_sizes
                })
            else:
                summary_text += "-- 无可用库存\n"
                product_json["inventory_status"] = []
            
            summary_text += "-------------------------------------------\n"
            
            # 添加产品到JSON数据
            summary_data["products"].append(product_json)

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 保存JSON数据到文件
        self.save_json_data(summary_data, f"inventory_summary_{timestamp_str}.json", "json_summary")
        
        return summary_text


if __name__ == '__main__':
    # 创建监控实例并运行
    monitor = DuomoMonitor(is_headless=True)
    monitor.run()
