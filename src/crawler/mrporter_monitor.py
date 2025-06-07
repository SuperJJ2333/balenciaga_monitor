"""
MrPorter监控模块 - 负责监控MrPorter网站上Balenciaga鞋子的库存状态
该模块实现了对MrPorter网站的爬取、解析和数据保存功能
"""
import os
from datetime import datetime
import json
import re
from curl_cffi import requests


from src.utils.page_setting import *
from src.common.monitor import Monitor


class MrPorterMonitor(Monitor):
    """
    MrPorter网站监控类
    
    方法HTML - JSON - detail
    负责爬取MrPorter网站上Balenciaga品牌鞋子的商品列表和库存信息
    """
    def __init__(self, **kwargs):
        """
        初始化MrPorter监控器
        
        参数:
            is_headless (bool): 是否使用无头模式运行浏览器
            proxy_type (str): 代理类型，可选值为clash、fiddler或'non'
        """
        # 更新监控器名称和目录URL
        kwargs['monitor_name'] = 'mrporter'
        
        super().__init__(**kwargs)

        # 初始化浏览器页面
        self.session = self.init_session()
        # self.page = self.init_page()

    @staticmethod
    def _init_params(url):

        cookies = {
            'PIM-SESSION-ID': 'cF4Jq7hTj8jngRbS',
        }

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': url,
            'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
            # 'cookie': 'PIM-SESSION-ID=cF4Jq7hTj8jngRbS',
        }

        return headers, cookies

    def run(self):
        """
        运行监控程序的主入口
        
        流程:
        1. 获取商品目录
        2. 逐个获取每个商品的库存信息
        3. 保存数据
        4. 关闭浏览器
        """
        try:
            self.logger.info(f"开始监控 {self.catalog_url}")
            
            # 获取商品目录
            self.products_list = self.get_inventory_catalog()
            if not self.products_list:
                self.logger.error("获取商品目录失败，终止监控")
                return

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

                # # 生成并保存库存监控总结
                # summary, summary_data = self.generate_inventory_summary()
                # # 保存总结数据
                # self.save_summary_data(summary)
                
                # # 保存JSON格式的总结
                # filename = f"inventory_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                # self.save_json_data(data=summary_data, filename=filename, category="json_summary")
                #
                return

        except Exception as e:
            self.logger.error(f"监控过程中出错: {str(e)}")
            return []
        finally:
            self.logger.info("监控结束，关闭浏览器")

    def get_inventory_catalog(self) -> list[dict]:
        """
        获取商品目录
        
        从MrPorter网站获取Balenciaga鞋子的商品列表
        
        返回:
            list: 商品信息列表，每个元素为包含name和url的字典
        """

        products_list: list[dict] = []
        try:
            for url in self.catalog_url:
                headers, cookies = self._init_params(url)
                # 设置代理并访问页面
                response = requests.get(url, cookies=cookies, headers=headers)
                save_path = os.path.join(self.data_root, f"{self.name}.html")
                with open(save_path, 'w', encoding='utf-8') as file:
                    file.write(response.text)

                self.session.get(save_path)
                # self.page.get(url)
                self.logger.info(f"正在获取商品目录: {url}")

                page = self.session

                # 检查页面响应
                if not page.html.strip():
                    self.logger.error("获取页面失败：页面响应为空")
                    return []

                self.logger.debug("页面加载成功，开始查找商品信息")

                # 使用更精确的XPath来查找JSON数据
                script_elements = page.s_eles('xpath://script[@type="application/ld+json"]')

                if not script_elements:
                    self.logger.error("未找到包含商品目录的script元素")
                    return []

                # 遍历所有script元素，查找包含商品目录的JSON数据
                for script_ele in script_elements:
                    script_frame = script_ele.text or script_ele.inner_html

                    data = json.loads(script_frame)
                    # 检查这是否是我们需要的商品目录数据
                    if data.get("@type") == "ItemList":
                        self.logger.debug("找到商品目录JSON数据")

                        inventory_catalog_data = self.parse_inventory_catalog(script_frame)
                        self.logger.info(f"共找到 {len(inventory_catalog_data)} 个商品")

                        if inventory_catalog_data:
                            products_list += inventory_catalog_data
                        else:
                            self.logger.error("解析商品目录失败")
                            return []
                    else:
                        self.logger.debug("当前script元素不是包含商品目录的JSON数据")
                        return []

            return products_list

        except Exception as e:
            self.logger.error(f"获取商品目录过程中出错: {str(e)}")
            return []

    # def get_inventory_page(self, url) -> dict:
    #     """
    #     获取单个商品的库存信息
    #
    #     参数:
    #         url (str): 商品页面URL
    #
    #     返回:
    #         dict: 商品的尺码和库存状态信息
    #     """
    #     retry_count = 0
    #     max_retries = 3
    #
    #     while retry_count < max_retries:
    #         try:
    #             self.logger.info(f"正在获取商品库存信息: {url} (尝试 {retry_count + 1}/{max_retries})")
    #             # 访问商品页面
    #             self.page.get(url)
    #
    #             # 检查页面响应
    #             if not self.page.html.strip():
    #                 self.logger.error(f"获取商品页面失败: {url}")
    #                 raise Exception("页面响应为空")
    #
    #             # 获取商品名称
    #             try:
    #                 if self.page.ele("/html/body/h1") and self.page.ele("/html/body/h1").text == "Access Denied":
    #                     self.logger.warning("访问商品页面被拒绝，可能被反爬虫系统限制")
    #                     raise Exception("访问被拒绝")
    #
    #                 good_name_ele = self.page.ele("@class^ProductInformation88__name")
    #                 good_name = good_name_ele.text if good_name_ele else "未知商品"
    #                 self.page.scroll.to_half()
    #                 random_sleep()
    #                 self.page.scroll.to_bottom()
    #                 self.logger.info(f"商品名称: {good_name}")
    #             except Exception as e:
    #                 self.logger.warning(f"获取商品名称失败: {str(e)}")
    #                 good_name = "未知商品"
    #                 # 继续执行，不视为失败
    #
    #             # 获取尺码和库存信息
    #             try:
    #                 # 文本定位：获取包含Size的div元素
    #                 text_frame = self.page.ele("text^Size").parent('tag:div')
    #                 if not text_frame:
    #                     self.logger.warning("未找到尺码信息区域")
    #                     raise Exception("未找到尺码信息")
    #
    #                 # 其后的div元素为目标元素
    #                 good_items = text_frame.next('tag:div')
    #                 if not good_items:
    #                     self.logger.warning("未找到尺码列表元素")
    #                     raise Exception("未找到尺码列表")
    #
    #                 # 解析库存信息
    #                 inventory_info = self.parse_inventory_info(good_items)
    #
    #                 # 记录库存信息
    #                 if inventory_info:
    #                     self.logger.info(f"商品 '{good_name}' 共有 {len(inventory_info)} 种尺码")
    #                     for size, availability in inventory_info.items():
    #                         self.logger.info(f"尺码: {size}, 库存状态: {availability}")
    #                 else:
    #                     self.logger.warning(f"商品 '{good_name}' 未找到尺码信息")
    #
    #                 return inventory_info
    #
    #             except Exception as e:
    #                 self.logger.error(f"解析商品库存信息时出错: {str(e)}")
    #                 raise Exception(f"解析库存信息失败: {str(e)}")
    #
    #         except Exception as e:
    #             retry_count += 1
    #             self.logger.error(f"获取商品库存信息过程中出错 (尝试 {retry_count}/{max_retries}): {str(e)}")
    #
    #             if retry_count < max_retries:
    #                 self.logger.info("重启浏览器并重试...")
    #                 # 关闭当前浏览器
    #                 try:
    #                     self.page.quit()
    #                 except:
    #                     pass
    #
    #                 # 重新初始化浏览器
    #                 self.page = self.init_page()
    #                 # 短暂等待
    #                 time.sleep(3)
    #             else:
    #                 self.logger.error(f"已达到最大重试次数 ({max_retries})，放弃获取商品 {url} 的库存信息")
    #                 return {}
    #
    #     return {}

    def parse_inventory_catalog(self, catalog_info: str) -> list[dict]:
        """
        解析商品目录JSON数据
        
        参数:
            catalog_info (str): 包含商品目录的JSON字符串
            
        返回:
            list: 商品信息列表，每个元素为包含name和url的字典
        """
        self.logger.debug("开始解析商品目录JSON数据")
        try:
            # 解析JSON数据
            data = json.loads(catalog_info)
            products_list = []

            # 提取每个商品的名称和URL
            for item in data.get("itemListElement", []):
                product_data = item.get("item", {})
                name = product_data.get("name", "")
                url = product_data.get("url", "")

                # 提取价格信息
                price = product_data.get("offers", {}).get("priceSpecification", {})
                if isinstance(price, dict):
                    price = price.get("price", "")
                elif isinstance(price, list):
                    price = price[0].get("price", "")

                url_parts = url.rstrip('/').split('/')
                unique_key = f"{name}_{url_parts[-1]}"

                if url in self.product_url:
                    key_monitoring = True
                    self.logger.info(f"已获取重点检测对象信息: {name}, URL: {url}")
                else:
                    key_monitoring = False

                if name and url:
                    product_info = {
                        "name": name,
                        "url": url,
                        "price": price,
                        "inventory": {},
                        "key_monitoring": key_monitoring
                    }
                    self.inventory_data[unique_key] = product_info
                    products_list.append(product_info)
                    self.logger.debug(f"找到商品: {name}")

            self.logger.debug(f"共解析到 {len(products_list)} 个商品")
            return products_list
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析错误: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"处理商品目录数据时出错: {str(e)}")
            return []

    # def parse_inventory_info(self, good_items: ChromiumElement) -> dict:
    #     """
    #     解析商品库存信息
    #
    #     从商品页面的尺码元素中提取尺码和库存状态
    #
    #     参数:
    #         good_items: 包含尺码信息的页面元素
    #
    #     返回:
    #         dict: 尺码和库存状态的字典，格式为 {尺码: 库存状态}
    #     """
    #     inventory_info = {}
    #
    #     try:
    #         # 获取所有尺码元素
    #         size_items = good_items.eles('x://ul/li')
    #
    #         if not size_items:
    #             self.logger.warning("未找到尺码元素")
    #             return inventory_info
    #
    #         # 遍历每个尺码元素，提取尺码和库存状态
    #         for item in size_items:
    #             try:
    #                 label = item.ele("tag:label")
    #                 if not label:
    #                     continue
    #
    #                 size_info = label.attr('aria-label')
    #                 if not size_info:
    #                     continue
    #
    #                 # 使用正则表达式提取尺码和存货情况
    #                 match = re.search(r'([A-Za-z-]+)\s*(\d+)\s*(?:\((.*?)\))?$', size_info)
    #                 if match:
    #                     size = match.group(1) + " " + match.group(2)  # 组合尺码信息
    #                     availability = match.group(3) if match.group(3) else "available"  # 如果没有括号内容，默认为available
    #                     inventory_info[size] = availability
    #                 else:
    #                     self.logger.warning(f"无法解析尺码信息：{size_info}")
    #             except Exception as e:
    #                 self.logger.warning(f"处理单个尺码元素时出错: {str(e)}")
    #                 continue
    #
    #         return inventory_info
    #
    #     except Exception as e:
    #         self.logger.error(f"解析库存信息时出错: {str(e)}")
    #         return inventory_info

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
        
        for product_name, product_data in self.inventory_data.items():
            url = product_data.get('url', '')
            inventory = product_data.get('inventory', {})
            
            # 从products_list中查找价格信息
            price_info = ""
            for product in self.products_list:
                if product.get('name') == product_name:
                    price = product.get('price_info', {}).get('price', '')
                    currency = product.get('price_info', {}).get('currency', '')
                    if price and currency:
                        price_info = f"{currency}{price}"
                    break
            
            # 添加产品基本信息到摘要
            summary_text += f"产品名称: {product_name} - {url}\n"
            summary_text += f"价格：{price_info}\n"
            summary_text += "存货情况：\n"
            
            # 准备JSON产品数据
            product_json = {
                "name": product_name,
                "url": url,
                "price": price_info,
                "inventory_status": []
            }
            
            # 动态收集所有出现的库存状态
            status_dict = {}
            
            # 优先顺序：先售罄，然后是库存数量从低到高
            priority_order = ["sold out", "only one left", "only two left", "low in stock"]
            
            # 预先定义这些常见状态，确保它们按照优先级排序
            for status in priority_order:
                status_dict[status] = []
            
            # 填充库存状态字典
            for size, status in inventory.items():
                if status not in status_dict:
                    status_dict[status] = []
                status_dict[status].append(size)
            
            # 按状态添加到摘要
            status_index = 1
            
            # 先添加优先级高的状态
            for status in priority_order:
                if status in status_dict and status_dict[status]:
                    summary_text += f"--（{status_index}）{status}：{'；'.join(status_dict[status])}\n"
                    # 添加到JSON
                    product_json["inventory_status"].append({
                        "status": status,
                        "status_index": status_index,
                        "sizes": status_dict[status]
                    })
                    status_index += 1
                    # 处理完后从字典中移除，避免重复
                    del status_dict[status]
            
            # 再添加其余状态（主要是available和自定义状态）
            for status, sizes in status_dict.items():
                if sizes:  # 只有当该状态下有尺码时才添加
                    summary_text += f"--（{status_index}）{status}：{'；'.join(sizes)}\n"
                    # 添加到JSON
                    product_json["inventory_status"].append({
                        "status": status,
                        "status_index": status_index,
                        "sizes": sizes
                    })
                    status_index += 1
            
            summary_text += "-------------------------------------------\n"
            
            # 添加产品到JSON数据
            summary_data["products"].append(product_json)
        
        return summary_text, summary_data


if __name__ == '__main__':
    # 创建监控实例并运行
    monitor = MrPorterMonitor(is_headless=False, proxy_type="clash", is_no_img=True, is_auto_port=False, load_mode="eager")
    monitor.run()

