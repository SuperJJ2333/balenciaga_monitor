"""
RickOwens监控模块 - 负责监控RickOwens网站上Balenciaga鞋子的库存状态
该模块实现了对RickOwens网站的爬取、解析和数据保存功能
"""
from datetime import datetime
from DrissionPage._elements.session_element import SessionElement

from src.common.monitor import Monitor


class RickOwensMonitor(Monitor):
    """
    RickOwens网站监控类

    方法 - Chrome - HTML - category
    负责爬取RickOwens网站上Balenciaga品牌鞋子的商品列表和库存信息
    """

    def __init__(self, **kwargs):
        """
        初始化RickOwens监控器

        参数:
            is_headless (bool): 是否使用无头模式运行浏览器
        """
        # 更新监控器名称
        kwargs['monitor_name'] = 'rickowens'

        super().__init__(**kwargs)
        
        self.page = self.init_page()
        # self.session = self.init_session()

        self.headers = self.init_params()

    @staticmethod
    def init_params():
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
            self.logger.info(f"开始监控 {self.catalog_url}")

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
            # self.page.quit()
            self.logger.info("监控结束，关闭浏览器")

    def get_inventory_catalog(self) -> list[dict]:
        """
        获取商品目录

        从sugar网站获取Balenciaga鞋子的商品列表

        返回:
            list: 商品信息列表，每个元素为包含name和url的字典
        """

        products_list: list[dict] = []
        try:
            for url in self.catalog_url:
                tab = self.page.new_tab()
                tab.get(url)
                self.page.get_tab(-1).close()

                self.logger.info(f"正在获取商品目录: {url}")

                # 检查页面响应
                if not tab.html.strip():
                    self.logger.error("获取页面失败：页面响应为空")
                    return []

                # 尝试查找商品元素
                try:
                    data = tab.s_eles('x://article[@class="product"]')

                    if not data:
                        self.logger.error("未找到任何商品列表元素")
                        return []

                    self.logger.debug(f"找到 {len(data)} 个商品元素")
                    
                    inventory_catalog_data = self.parse_inventory_catalog(data)

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
            for i, item in enumerate(catalog_eles):
                try:
                    # 尝试多种选择器找到商品名称
                    name_ele = item.s_ele('x://div[@class="brand-name"]')
                    name = name_ele.text

                    # 尝试多种选择器找到URL
                    url_ele = item.s_ele('x://a[@itemprop="url"]')
                    url = url_ele.attr('href')

                    # 尝试多种选择器找到价格
                    price_ele = item.s_ele('x://strong')
                    price = price_ele.text if price_ele else ""

                    sizes_dict = {}

                    if name and url:
                        # 修正URL格式
                        full_url = f"https://antonioli.eu{url}" if not url.startswith('http') else url

                        url_parts = url.rstrip('/').split('/')
                        unique_key = f"{name}_{url_parts[-1]}"

                        if full_url in self.product_url:
                            key_monitoring = True
                            self.logger.info(f"已获取重点检测对象信息: {name}, URL: {full_url}")
                        else:
                            key_monitoring = False

                        product_info = {
                            "name": unique_key,
                            "url": full_url,
                            "price": price,
                            "inventory": sizes_dict,
                            "key_monitoring": key_monitoring
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


if __name__ == '__main__':
    # 创建监控实例并运行
    monitor = RickOwensMonitor(is_headless=True, proxy_type='clash', is_auto_port=False,
                               load_mode="normal", is_no_img=True)
    monitor.run_with_log()
