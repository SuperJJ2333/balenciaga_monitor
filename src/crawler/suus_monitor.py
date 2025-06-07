"""
SUUS监控模块 - 负责监控SUUS网站上Balenciaga鞋子的库存状态
该模块实现了对SUUS网站的爬取、解析和数据保存功能
"""
import time
from datetime import datetime

from src.utils.page_setting import *
from src.common.monitor import Monitor


class SuusMonitor(Monitor):
    """
    Suus网站监控类
    Session - Get - Json - Category
    负责爬取Suus网站上Balenciaga品牌鞋子的商品列表和库存信息
    """

    def __init__(self, **kwargs):
        """
        初始化Suus监控器

        参数:
            is_headless (bool): 是否使用无头模式运行浏览器
            proxy_type (str): 代理类型，可选值为clash、pin_zan或kuai_dai_li
        """
        # 更新监控器名称和目录URL
        kwargs['monitor_name'] = 'suus'

        super().__init__(**kwargs)
        
        # 初始化浏览器页面
        self.session = self.init_session()

    @staticmethod
    def _init_params():
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
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
            self.products_list = catalog_data

            # 如果商品列表为空，记录错误并返回
            if not self.products_list:
                self.logger.error("商品列表为空，终止监控")
                return

            self.logger.info(f"监控开始，共获取到 {len(self.products_list)} 个商品信息")

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

                return
            else:
                self.logger.warning("未获取到任何库存信息，无法生成总结")

        except Exception as e:
            self.logger.error(f"监控过程中出错: {str(e)}")
        finally:
            self.logger.info("监控结束，关闭浏览器")

    def get_inventory_catalog(self):
        """
        获取商品目录

        从Suus网站获取Guidi鞋子的商品列表

        返回:
            list: 商品信息列表，每个元素为包含name和url的字典
        """
        products_list = []
        try:
            for url in self.catalog_url:
                header = self._init_params()
                # 设置代理并访问页面
                self.session.get(url, headers=header, proxies=self.ipcool_url)
                self.logger.debug(f"正在获取商品目录: {url}")

                # 检查页面响应
                if not self.session.html.strip():
                    self.logger.error("获取页面失败：页面响应为空")
                    return []

                # 尝试查找商品元素
                try:
                    catalog_items = self.session.s_eles('@class=t-entry')

                    if not catalog_items:
                        self.logger.error("未找到任何商品列表元素")
                        return []

                    self.logger.debug(f"找到 {len(catalog_items)} 个商品元素")
                    
                    inventory_catalog_data = self.parse_inventory_catalog(catalog_items)

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
            self.page.get(url)

            # 检查页面响应
            if not self.page.html.strip():
                self.logger.error(f"获取商品页面失败: {url}")
                return {}

            # 获取商品名称
            try:
                good_name_ele = self.page.ele('x://*[@class="heading-text el-text"]/h1')
                good_name = good_name_ele.text if good_name_ele else "未知商品"
                self.page.scroll.to_half()
                random_sleep()
                self.page.scroll.to_bottom()
                self.logger.debug(f"商品名称: {good_name}")
            except Exception as e:
                self.logger.warning(f"获取商品名称失败: {str(e)}")
                good_name = "未知商品"

            # 解析库存信息
            inventory_info = self.parse_inventory_info()

            # 记录库存信息
            if inventory_info:
                self.logger.debug(f"商品 '{good_name}' 共有 {len(inventory_info)} 种尺码")
                for size, availability in inventory_info.items():
                    self.logger.debug(f"尺码: {size}, 库存状态: {availability}")
            else:
                self.logger.warning(f"商品 '{good_name}' 未找到尺码信息")

            return inventory_info

        except Exception as e:
            self.logger.error(f"获取商品库存信息过程中出错: {str(e)}")
            return {}

    def parse_inventory_catalog(self, catalog_items):
        """
        解析商品目录Element数据

        参数:
            catalog_items (Element): 包含商品目录的Element

        返回:
            list: 商品信息列表，每个元素为包含name和url的字典
        """
        self.logger.debug("开始解析商品目录数据")
        try:
            products = []

            # 提取每个商品的名称和URL
            for item in catalog_items:
                try:
                    name_ele = item.ele('x://h3/a/text()')
                    # 如果无法找到名称，记录警告并尝试下一个元素
                    if not name_ele:
                        self.logger.warning(f"无法找到商品名称元素，跳过此商品")
                        continue
                    
                    name = name_ele
                    url_ele = item.ele('x://h3/a')
                    url = url_ele.attr('href') if url_ele else None
                    
                    # 提取价格信息
                    price_ele = item.ele('x://h3/a//ins//bdi')
                    price = price_ele.text if price_ele else ""

                    if name and url:

                        url_parts = url.rstrip('/').split('/')
                        unique_key = f"{name}_{url_parts[-1]}"

                        if url in self.product_url:
                            key_monitoring = True
                            self.logger.info(f"已获取重点检测对象信息: {name}, URL: {url}")
                        else:
                            key_monitoring = False

                        product_info = {
                            "name": name,
                            "url": url,
                            "price": price,
                            "inventory": {},
                            "key_monitoring": key_monitoring
                        }

                        self.inventory_data[unique_key] = product_info

                        products.append(product_info)
                        self.logger.debug(f"找到商品: {name}, URL: {url}")
                except Exception as e:
                    self.logger.warning(f"解析单个商品时出错: {str(e)}")
                    continue

            self.logger.info(f"共解析到 {len(products)} 个商品")
            return products

        except Exception as e:
            self.logger.error(f"处理商品目录数据时出错: {str(e)}")
            return []

    def parse_inventory_info(self):
        """
        解析商品库存信息

        从商品页面的尺码元素中提取尺码和库存状态

        返回:
            dict: 尺码和库存状态的字典，格式为 {尺码: 库存状态}
        """
        inventory_info = {}

        try:
            # 获取所有尺码元素
            size_items = self.page.eles('x://*[@class="value"]//option')

            if not size_items:
                self.logger.warning("未找到尺码元素")
                return inventory_info

            # 遍历每个尺码元素，提取尺码和库存状态
            for item in size_items:
                try:
                    label = item.text
                    if not label:
                        continue

                    if label.isdigit():
                        inventory_info[label] = 'available'
                except Exception as e:
                    self.logger.warning(f"处理单个尺码元素时出错: {str(e)}")
                    continue

            return inventory_info

        except Exception as e:
            self.logger.error(f"解析库存信息时出错: {str(e)}")
            return inventory_info


if __name__ == '__main__':
    # 创建监控实例并运行
    monitor = SuusMonitor(is_headless=True, proxy_type="clash")
    monitor.run_with_log()

