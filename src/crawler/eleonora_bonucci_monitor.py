"""
EleonoraBonucci监控模块 - 负责监控EleonoraBonucci网站上Balenciaga鞋子的库存状态
该模块实现了对EleonoraBonucci网站的爬取、解析和数据保存功能
"""
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.page_setting import *
from src.common.monitor import Monitor
from DrissionPage._elements.session_element import SessionElement


class EleonoraBonucciMonitor(Monitor):
    """
    EleonoraBonucci网站监控类
    
    方法HTML - category - detail
    负责爬取EleonoraBonucci网站上Balenciaga品牌鞋子的商品列表和库存信息
    """

    def __init__(self, **kwargs):
        """
        初始化EleonoraBonucci监控器

        参数:
            is_headless (bool): 是否使用无头模式运行浏览器
        """
        # 更新监控器名称
        kwargs['monitor_name'] = 'eleonora_bonucci'

        super().__init__(**kwargs)
        self.session = self.init_session()

    def init_params(self):
        """
        初始化请求参数
        
        返回:
            dict: 包含headers的字典
        """
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
        }
        return headers

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
            self.logger.debug(f"开始监控 {self.catalog_url}")

            # 获取商品目录
            catalog_data = self.get_inventory_catalog()
            if not catalog_data:
                self.logger.error("获取商品目录失败，终止监控")
                return

            # 解析商品目录
            self.products_list = catalog_data  # 因为get_inventory_catalog已经调用了parse_inventory_catalog

            # 如果商品列表为空，记录错误并返回
            if not self.products_list:
                self.logger.error("商品列表为空，终止监控")
                return

            self.logger.info(f"监控开始，共获取到 {len(self.products_list)} 个商品信息")

            # 生成库存数据
            # self.create_inventory_data()

            # 保存库存数据
            if self.inventory_data:
                # 标准化库存数据
                normalized_data = self._normalize_inventory_data(self.inventory_data)

                # 保存标准化后的数据
                data_file = f"balenciaga_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                saved_path = self.save_json_data(normalized_data, data_file)
                self.logger.info(f"已保存{len(normalized_data)}个商品的库存信息到 {saved_path}")

                # 检测库存变化
                changes = self.detect_inventory_changes(normalized_data)
                if changes:
                    self.logger.info("检测到库存变化，已保存到变更记录")

                # 生成并保存库存监控总结
                # summary, summary_data = self.generate_inventory_summary()
                # 打印总结到控制台
                # print(summary)
                # 保存总结数据
                # self.save_summary_data(summary)

                # 保存JSON格式的总结
                # filename = f"inventory_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                # self.save_json_data(data=summary_data, filename=filename, category="json_summary")

                # return summary_data
            else:
                self.logger.warning("未获取到任何库存信息，无法生成总结")

        except Exception as e:
            self.logger.error(f"监控过程中出错: {str(e)}")
        finally:
            self.logger.info("监控结束，关闭浏览器")
            self.session.close()

    def get_inventory_catalog(self) -> list[dict]:
        """
        获取商品目录

        从EleonoraBonucci网站获取Balenciaga鞋子的商品列表

        返回:
            list: 商品信息列表，每个元素为包含name和url的字典
        """

        products_list: list[dict] = []
        try:
            for url in self.catalog_url:
                header = self.init_params()
                # 设置代理并访问页面
                self.session.get(url, headers=header, verify=False)
                self.logger.info(f"正在获取商品目录: {url}")

                # 检查页面响应
                if not self.session.html.strip():
                    self.logger.error("获取页面失败：页面响应为空")
                    return []

                # 尝试查找商品元素
                try:
                    # 修改选择器以匹配所有商品项
                    img_frames = self.session.eles("@class=product-desc center")

                    if not img_frames:
                        self.logger.error("未找到任何商品列表元素")

                        return []

                    self.logger.debug(f"找到 {len(img_frames)} 个商品元素")

                    inventory_catalog_data = self.parse_inventory_catalog(img_frames)

                    if inventory_catalog_data:
                        products_list += inventory_catalog_data
                    else:
                        self.logger.error("解析商品目录失败")
                        return []

                except Exception as e:
                    self.logger.error(f"处理商品目录元素时出错: {str(e)}")
                    return []

            return products_list

        except Exception as e:
            self.logger.error(f"获取商品目录过程中出错: {str(e)}")
            return []

    def get_inventory_page(self, url):
        """
        获取单个商品的库存信息

        参数:
            url (str): 商品页面URL

        返回:
            dict: 商品的尺码和库存状态信息
        """
        self.logger.debug(f"正在获取商品库存信息: {url}")
        try:
            # 访问商品页面
            self.session.get(url)

            # 检查页面响应
            if not self.session.html.strip():
                self.logger.error(f"获取商品页面失败: {url}")
                return {}

            # 解析库存信息
            inventory_info = self.parse_inventory_info(self.session)

            return inventory_info

        except Exception as e:
            self.logger.error(f"获取商品库存信息过程中出错: {str(e)}")
            return {}

    def parse_inventory_catalog(self, catalog_eles: list[SessionElement]) -> list[dict]:
        """
        解析商品目录HTML数据，提取关键商品信息
        
        参数:
            catalog_eles (element): 包含商品目录的element数据
        
        返回:
            list: 商品信息列表，每个元素为包含商品详细信息的字典
        """
        try:
            products_list = []

            # 提取每个商品的名称和URL
            for item in catalog_eles:
                try:
                    # 尝试多种选择器找到商品名称
                    name_ele = item.s_ele('x://div[contains(@class, "product-description")]/h4/a')
                    # 如果无法找到名称，记录警告并尝试下一个元素
                    if not name_ele:
                        self.logger.warning(f"无法找到商品名称元素，跳过此商品")
                        continue

                    name = name_ele.text

                    # 尝试多种选择器找到URL
                    url_ele = item.s_ele('x://div[contains(@class, "product-description")]/h4/a')
                    url = url_ele.attr('href')

                    # 尝试多种选择器找到价格
                    price_ele = item.s_ele('x://div[contains(@class, "product-price")]/ins')
                    price = price_ele.text if price_ele else ""

                    if name and url:
                        # 修正URL格式
                        full_url = f"https://eleonorabonucci.com{url}" if not url.startswith('http') else url

                        url_parts = url.rstrip('/').split('/')
                        unique_key = f"{name}_{url_parts[-1]}"

                        product_info = {
                            "name": name,
                            "url": full_url,
                            "price": price,
                            "inventory": {}
                        }
                        self.inventory_data[unique_key] = product_info
                        products_list.append(product_info)
                        self.logger.debug(f"找到商品: {name}, URL: {full_url}")
                except Exception as e:
                    self.logger.warning(f"解析单个商品时出错: {str(e)}")
                    continue

            self.logger.info(f"共解析到 {len(products_list)} 个商品")
            return products_list

        except Exception as e:
            self.logger.error(f"处理商品目录数据时出错: {str(e)}")
            return []

    def parse_inventory_info(self, session) -> dict:
        """
        解析商品库存信息

        从商品页面的尺码元素中提取尺码和库存状态
        
        参数：
            session: 页面会话对象
            
        返回:
            dict: 尺码和库存状态的字典，格式为 {尺码: 库存状态}
        """
        inventory_info = {}

        try:
            # 获取商品名称
            try:
                good_name_ele = session.ele('x://*[@id="content"]/div/div/div[1]/div/div[2]/h2')
                if not good_name_ele:
                    good_name_ele = session.ele('x://h2[contains(@class, "product-title")]')
                good_name = good_name_ele.text if good_name_ele else "未知商品"
                self.logger.debug(f"商品名称: {good_name}")
            except Exception as e:
                good_name = "未知商品"
                self.logger.warning(f"获取商品名称失败: {str(e)}")

            # 获取尺码信息
            try:
                # 首先尝试select/option方式的尺码选择器
                size_items = session.eles('x://*[@id="MainContent_iTaglia"]/option')

                # 如果没有找到，尝试其他常见的尺码选择器
                if not size_items:
                    self.logger.debug("尝试查找其他尺码选择器")
                    size_items = session.eles('x://select[contains(@class, "size-select")]/option')

                self.logger.debug(f"找到 {len(size_items)} 个尺码元素")

                # 遍历每个尺码元素，提取尺码和库存状态
                for item in size_items:
                    try:
                        # 获取尺码文本
                        label = item.text.strip()

                        # 判断库存状态
                        is_available = True

                        # 跳过空尺码或明显无效的尺码
                        if not label or label.lower() in ['size', 'taglia', 'select size', 'select taglia',
                                                          '- select -']:
                            continue

                        # 添加到库存信息
                        status = 'available' if is_available else 'sold out'
                        inventory_info[label] = status
                    except Exception as e:
                        self.logger.warning(f"处理单个尺码元素时出错: {str(e)}")
                        continue

            except Exception as e:
                self.logger.error(f"获取尺码元素失败: {str(e)}")

            # 记录库存信息
            if inventory_info:
                self.logger.debug(f"商品 '{good_name}' 共有 {len(inventory_info)} 种尺码")
                for size, availability in inventory_info.items():
                    self.logger.debug(f"尺码: {size}, 库存状态: {availability}")
            else:
                self.logger.warning(f"商品 '{good_name}' 未找到尺码信息")

            return inventory_info

        except Exception as e:
            self.logger.error(f"解析库存信息时出错: {str(e)}")
            return inventory_info

    def generate_inventory_summary(self):
        """
        生成Balenciaga鞋子库存监控总结文本
        
        返回:
            str: 格式化的库存监控总结文本
            dict: 库存总结JSON数据
        """
        summary_text = f"******{self.monitor_name.capitalize()}Monitor - 库存监控********\n"

        timestamp = datetime.now().isoformat()
        summary_data = {
            "monitor": f"{self.monitor_name.capitalize()}Monitor",
            "timestamp": timestamp,
            "total_products": len(self.inventory_data),
            "products": []
        }

        if not self.inventory_data:
            summary_text += "无库存数据\n"
            return summary_text, summary_data

        # 遍历所有产品
        for unique_key, product_data in self.inventory_data.items():
            # 获取产品信息
            name = product_data.get('name', unique_key)  # 从新的数据结构中获取名称
            url = product_data.get('url', '')
            price = product_data.get('price', '')
            inventory = product_data.get('inventory', {})

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

            # 如果有库存信息
            if inventory:
                # 将所有尺码收集为一个列表
                available_sizes = []
                for size, status in inventory.items():
                    if status.lower() == 'available':
                        available_sizes.append(size)

                # 对尺码排序
                available_sizes.sort()

                # 添加库存信息
                if available_sizes:
                    summary_text += f"--（1）available：{'；'.join(available_sizes)}\n"
                    # 添加到JSON
                    product_json["inventory_status"].append({
                        "status": "available",
                        "status_index": 1,
                        "sizes": available_sizes
                    })
                else:
                    summary_text += "-- 无可用库存\n"
            else:
                summary_text += "-- 无可用库存\n"
                product_json["inventory_status"] = []

            # 添加分隔线
            summary_text += "-------------------------------------------\n"

            # 添加产品到JSON数据
            summary_data["products"].append(product_json)

        return summary_text, summary_data


if __name__ == '__main__':
    # 创建监控实例并运行
    monitor = EleonoraBonucciMonitor(is_headless=True)
    monitor.run()
