"""
Cettire监控模块 - 负责监控Cettire网站上Balenciaga鞋子的库存状态
该模块实现了对Cettire网站的爬取、解析和数据保存功能
"""
import json
import random
import time
import urllib.parse
from urllib.parse import urlparse
from datetime import datetime
from curl_cffi import requests

from src.utils.page_setting import *
from src.common.monitor import Monitor


class CettireMonitor(Monitor):
    """
    Cettire网站监控类

    方法 Chrome - HTML - category - detail
    负责爬取Cettire网站上Balenciaga品牌鞋子的商品列表和库存信息
    """

    def __init__(self, **kwargs):
        """
        初始化Cettire监控器

        参数:
            is_headless (bool): 是否使用无头模式运行浏览器
        """
        # 更新监控器名称
        kwargs['monitor_name'] = 'cettire'
        # kwargs['catalog_url'] = r'https://6l0oqj41cq-2.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.4.0)%3B%20Browser%20(lite)%3B%20JS%20Helper%20(3.24.1)%3B%20react%20(16.8.6)%3B%20react-instantsearch%20(6.7.0)&x-algolia-api-key=ee556f77348dacc02278dafa57be6d34&x-algolia-application-id=6L0OQJ41CQ'

        super().__init__(**kwargs)
        
        # self.page = self.init_page()
        self.session = self.init_session()
        self.base_url = 'https://6l0oqj41cq-2.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.4.0)%3B%20Browser%20(lite)%3B%20JS%20Helper%20(3.24.1)%3B%20react%20(16.8.6)%3B%20react-instantsearch%20(6.7.0)&x-algolia-api-key=ee556f77348dacc02278dafa57be6d34&x-algolia-application-id=6L0OQJ41CQ'

        # self.headers, self.json_data = self.init_params()

    def init_params(self, url):
        """
        初始化请求参数
        
        返回:
            dict: 包含headers的字典
        """
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://www.cettire.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.cettire.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
            'content-type': 'application/x-www-form-urlencoded',
            'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            }

        str_data = '{"requests":[{"indexName":"production_rep_cettire_vip_date_desc","params":"distinct=1&facetFilters=%5B%22tags%3AShoes%22%2C%5B%22department%3Amen%22%5D%2C%5B%22vendor%3ARick%20Owens%22%5D%5D&facets=%5B%22Color%22%2C%22Size%22%2C%22department%22%2C%22product_type%22%2C%22tags%22%2C%22vendor%22%5D&filters=visibility%3AYES%20AND%20(vipLevel%3A%200%20OR%20vipLevel%3A%20null)%20AND%20eu_eur_price_f%20%3E%200&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=96&maxValuesPerFacet=10000&page=0&query="},{"indexName":"production_rep_cettire_vip_date_desc","params":"analytics=false&clickAnalytics=false&distinct=1&facetFilters=%5B%22tags%3AShoes%22%2C%5B%22vendor%3ARick%20Owens%22%5D%5D&facets=department&filters=visibility%3AYES%20AND%20(vipLevel%3A%200%20OR%20vipLevel%3A%20null)%20AND%20eu_eur_price_f%20%3E%200&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&maxValuesPerFacet=10000&page=0&query="},{"indexName":"production_rep_cettire_vip_date_desc","params":"analytics=false&clickAnalytics=false&distinct=1&facetFilters=%5B%22tags%3AShoes%22%2C%5B%22department%3Amen%22%5D%5D&facets=vendor&filters=visibility%3AYES%20AND%20(vipLevel%3A%200%20OR%20vipLevel%3A%20null)%20AND%20eu_eur_price_f%20%3E%200&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&maxValuesPerFacet=10000&page=0&query="}]}'

        vendor: str = self.transform_brand_name(url)
        json_data = self.parse_json_data(json.loads(str_data), vendor)

        return headers, json_data

    @staticmethod
    def parse_json_data(json_data: dict, vendor: str) -> str:
        """
        处理request参数
        :param vendor: 需要添加的产品名称
        :param json_data: 整体参数
        :return:
        """
        hits = json_data['requests']

        for i, request in enumerate(hits):
            if i > 1:
                break
            # 2. 解析params查询字符串为字典
            params_dict = dict(urllib.parse.parse_qsl(request['params']))

            # 4. 更新facetFilters
            if 'facetFilters' in params_dict:
                # 解码并解析JSON字符串
                facet_filters = json.loads(params_dict['facetFilters'])

                # 更新其他过滤条件
                for j, item in enumerate(facet_filters):
                    if "vendor" in item[0] and isinstance(item, list):
                        facet_filters[j] = [f"vendor:{vendor}"]

                # 重新编码为JSON字符串
                params_dict['facetFilters'] = json.dumps(facet_filters)

            # 6. 将params字典转换回查询字符串
            request['params'] = urllib.parse.urlencode(params_dict, doseq=True)

        # 转换回JSON字符串
        updated_data = json.dumps({'requests': hits}, separators=(',', ':'))

        return updated_data

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
            self.products_list = catalog_data  # 因为get_inventory_catalog已经调用了parse_inventory_catalog

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

                # 生成并保存库存监控总结
                # summary, summary_data = self.generate_inventory_summary()
                # 打印总结到控制台
                # print(summary)
                # self.save_summary_data(summary)

                # filename = f"inventory_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                # self.save_json_data(data=summary_data, filename=filename, category="json_summary")
                
                return
            else:
                self.logger.warning("未获取到任何库存信息，无法生成总结")

        except Exception as e:
            self.logger.error(f"监控过程中出错: {str(e)}")
        finally:
            self.logger.info("监控结束，关闭浏览器")

    def get_inventory_catalog(self) -> list[dict]:
        """
        获取商品目录

        从Cettire网站获取Balenciaga鞋子的商品列表

        返回:
            list: 商品信息列表，每个元素为包含name和url的字典
        """
        self.logger.info(f"正在获取商品目录: {self.catalog_url}")

        products_list = []
        try:
            for url in self.catalog_url:
                headers, json_data = self.init_params(url)
                # 设置代理并访问页面
                self.session.post(self.base_url, headers=headers, data=json_data, proxies=self.ipcool_url)
                # 检查页面响应
                if not self.session.html.strip():
                    self.logger.error("获取页面失败：页面响应为空")
                    return []

                # 尝试查找商品元素
                try:
                    data = self.session.json

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
            # 提取产品ID
            product_id = self._extract_product_id(url)
            if not product_id:
                self.logger.error(f"无法从URL提取产品ID: {url}")
                return {}

            # 设置GraphQL查询参数
            json_data = self.json_data
            json_data['variables']['slugOrId'] = product_id

            # 发送GraphQL请求
            self.session.post(
                'https://api.cettire.com/graphql',
                headers=self.headers,
                json=json_data,
                proxies={'http': None, 'https': None}
            )

            # 解析库存信息
            inventory_info: dict = self.parse_inventory_info(self.session.json)

            return inventory_info

        except Exception as e:
            self.logger.error(f"获取商品库存信息过程中出错: {str(e)}")
            return {}

    def parse_inventory_catalog(self, catalog_eles: dict) -> list[dict]:
        """
        解析商品目录HTML数据，提取关键商品信息
        
        参数:
            catalog_eles (dict): 包含商品目录的element数据
        
        返回:
            list: 商品信息列表，每个元素为包含商品详细信息的字典
        """
        try:
            json_data = catalog_eles.get('results')[0].get('hits')
            products_list = []

            # 提取每个商品的名称和URL
            for i, item in enumerate(json_data):
                try:
                    # 尝试多种选择器找到商品名称
                    name = item.get('title')

                    # 尝试多种选择器找到URL
                    url = item.get('handle')

                    # 尝试多种选择器找到价格
                    price = '€' + str(item.get('eu_eur_price_f'))

                    if name and url:
                        # 修正URL格式
                        full_url = f"https://www.cettire.com/it/products/{url}" if not url.startswith('http') else url

                        product_info = {
                            "name": name,
                            "url": full_url,
                            "price": price,
                            "inventory": {}
                        }

                        unique_key = f"{name}_{url}"

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

    def parse_inventory_info(self, data: dict) -> dict:
        """
        解析商品库存信息

        从商品页面的JSON响应中提取尺码和库存状态
        参数：
            dict: 页面的json数据
        返回:
            dict: 尺码和库存状态的字典，格式为 {尺码: 库存状态}
        """
        inventory_info = {}

        try:
            # 从页面获取JSON响应数据
            response_data = data

            if not response_data or 'data' not in response_data:
                self.logger.warning("无法获取商品JSON数据")
                return inventory_info

            # 获取商品数据
            product_data = response_data.get('data', {}).get('catalogItemProduct', {}).get('product', {})

            if not product_data:
                self.logger.warning("无法获取商品数据")
                return inventory_info

            # 获取商品名称
            good_name = product_data.get('title', "未知商品")
            self.logger.info(f"商品名称: {good_name}")

            # 获取变体列表（不同尺码）
            variants = product_data.get('variants', [])

            if not variants:
                self.logger.warning(f"商品 '{good_name}' 未找到尺码变体")
                return inventory_info

            self.logger.debug(f"找到 {len(variants)} 个尺码变体")

            # 遍历每个尺码变体，提取尺码和库存状态
            for variant in variants:
                try:
                    # 获取尺码
                    size = variant.get('size', '')
                    if not size:
                        continue

                    # 获取库存状态
                    is_sold_out = variant.get('isSoldOut', True)
                    inventory_available = variant.get('inventoryAvailableToSell', 0)

                    # 设置库存状态
                    if is_sold_out:
                        status = 'sold out'
                    else:
                        status = f'{inventory_available}'

                    # 添加到库存信息
                    inventory_info[size] = status

                except Exception as e:
                    self.logger.warning(f"处理单个尺码变体时出错: {str(e)}")
                    continue

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
        summary_data = {
            "monitor": f"{self.monitor_name.capitalize()}Monitor",
            "timestamp": datetime.now().isoformat(),
            "total_products": len(self.inventory_data),
            "products": []
        }

        if not self.inventory_data:
            summary_text += "无库存数据\n"
            return summary_text, summary_data

        # 遍历所有产品
        for unique_key, product_data in self.inventory_data.items():
            # 获取产品信息
            name = product_data.get('name', unique_key.split('_')[0])  # 从unique_key中提取名称部分
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

            # 如果有库存信息，按照库存状态分组
            if inventory:
                # 分组存储不同库存状态的尺码
                status_groups = {}

                # 将尺码按库存状态分组
                for size, status in inventory.items():
                    if status not in status_groups:
                        status_groups[status] = []
                    status_groups[status].append(size)

                # 对每个状态组内的尺码进行排序
                for status, sizes in status_groups.items():
                    sizes.sort()

                # 按优先级显示库存状态：先售罄，然后是库存数量从低到高
                priority_statuses = ['sold out']
                inventory_statuses = sorted([s for s in status_groups.keys() if s != 'sold out'])
                priority_order = priority_statuses + inventory_statuses

                # 遍历每种状态
                index = 1
                for status in priority_order:
                    if status in status_groups and status_groups[status]:
                        summary_text += f"--（{index}）{status}：{'；'.join(status_groups[status])}\n"
                        # 添加到JSON
                        product_json["inventory_status"].append({
                            "status": status,
                            "status_index": index,
                            "sizes": status_groups[status]
                        })
                        index += 1
            else:
                summary_text += "-- 无可用库存\n"
                product_json["inventory_status"] = []

            # 添加分隔线
            summary_text += "-------------------------------------------\n"
            
            # 添加产品到JSON数据
            summary_data["products"].append(product_json)

        return summary_text, summary_data

    @staticmethod
    def _extract_product_id(url):
        # 定义正则表达式模式
        pattern = r'/products/([^?]+)'

        # 使用 re.search 查找匹配的部分
        match = re.search(pattern, url)

        if match:
            # 返回匹配的组
            return match.group(1)
        else:
            return None

    @staticmethod
    def transform_brand_name(url) -> str | None:
        """

        :param url:
        :return:
        """
        # 解析URL获取路径部分
        path = urlparse(url).path

        # 提取品牌标识
        match = re.search(r'/collections/([^/?]+)', path)
        if match:
            brand_key = match.group(1)

            # 替换连字符为空格
            clean_string = brand_key.replace('-', ' ')

            # 转换为标题格式（首字母大写）
            title_string = ' '.join(word.capitalize() for word in clean_string.split())

            return title_string

        return None


if __name__ == '__main__':
    # 创建监控实例并运行
    # 需要境外IP，国内IP也能使用，但速度会慢
    monitor = CettireMonitor(is_headless=False, proxy_type="clash")
    monitor.run()
