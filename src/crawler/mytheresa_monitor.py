"""
Mytheresa监控模块 - 负责监控Mytheresa网站上Balenciaga鞋子的库存状态
该模块实现了对Mytheresa网站的爬取、解析和数据保存功能
"""
import time
from datetime import datetime
from DrissionPage._elements import chromium_element

from src.common.monitor import Monitor
from src.utils.page_setting import contains_digit


class MytheresaMonitor(Monitor):
    """
    mytheresa网站监控类
    Session - Json - Category
    负责爬取Mytheresa网站上Balenciaga品牌鞋子的商品列表和库存信息
    """

    def __init__(self, **kwargs):
        """
        初始化mytheresa监控器

        参数:
            is_headless (bool): 是否使用无头模式运行浏览器
            proxy_type (str): 代理类型，可选值为clash、pin_zan或kuai_dai_li
        """
        # 更新监控器名称和目录URL
        kwargs['monitor_name'] = 'mytheresa'

        super().__init__(**kwargs)
        
        # 初始化浏览器页面
        self.page = self.init_page()

    @staticmethod
    def init_params():
        headers = {
            'accept': '*/*',
            'accept-language': 'en',
            'cache-control': 'no-cache',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://www.mytheresa.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.mytheresa.com/',
            'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
            'x-country': 'MO',
            'x-geo': 'US',
            'x-nsu': 'false',
            'x-region': 'CA',
            'x-section': 'men',
            'x-store': 'MO',
            'x-tracking-variables': 'analyticsId=GA1.1.1748533487.1746616564,browser=Edge,browserLanguage=zh,campaign=unknown,channel=en-mo,channel_country=MO,channel_language=en,countOfPageViews=1,countOfSessions=1,cdf=000,csf=000,cdf_1=0,cdf_2=0,cdf_3=0,csf_1=0,csf_2=0,csf_3=0,department=men,devicePlatform=web,deviceSystem=Windows,deviceType=desktop,emailHash=unknown,environment=production,ipAddress=141.11.251.99,loggedStatus=false,mytuuid=940ac349-6e0e-497b-905a-add7ce84ce50,level_0=men,level_1=men_designer_000895,pageId=men_designer_000895,pageType=designer,referral=unknown,sessionId=undefined,source=unknown,url=https://www.mytheresa.com/mo/en/men/designers/balenciaga,queryParams=categories%3D5076%26sortBy%3Drecommendation,version=4.12.0-rc.7,experience_globalBlue_closed=false,experience_pocketBanner1_pocketBanner1_seen=false,experience_pocketBanner2_pocketBanner2_seen=false,experience_topLevelBanner_tlb_db_trust_delay_seen=true,experience_pocketbanner2_pocketbanner2_seen=true,experience_pocketbanner1_pocketbanner1_seen=true,monetateId=5.44754319.1746616152436',
        }

        data = '{"query":"query XProductListingPageQuery($categories: [String], $colors: [String], $designers: [String], $fta: Boolean, $materials: [String], $page: Int, $patterns: [String], $reductionRange: [String], $saleStatus: SaleStatusEnum, $size: Int, $sizesHarmonized: [String], $slug: String, $sort: String) {\\n  xProductListingPage(categories: $categories, colors: $colors, designers: $designers, fta: $fta, materials: $materials, page: $page, patterns: $patterns, reductionRange: $reductionRange, saleStatus: $saleStatus, size: $size, sizesHarmonized: $sizesHarmonized, slug: $slug, sort: $sort) {\\n    id\\n    alternateUrls {\\n      language\\n      store\\n      url\\n    }\\n    breadcrumb {\\n      id\\n      name\\n      slug\\n    }\\n    combinedDepartmentGroupAndCategoryErpID\\n    department\\n    designerErpId\\n    displayName\\n    facets {\\n      categories {\\n        name\\n        options {\\n          id\\n          name\\n          slug\\n          children {\\n            id\\n            name\\n            slug\\n            children {\\n              id\\n              name\\n              slug\\n            }\\n          }\\n        }\\n        activeValue\\n      }\\n      designers {\\n        name\\n        options {\\n          value\\n          slug\\n        }\\n        activeValue\\n      }\\n      colors {\\n        name\\n        options {\\n          value\\n        }\\n        activeValue\\n      }\\n      fta {\\n        activeValue\\n        name\\n        options {\\n          value\\n        }\\n        visibility\\n      }\\n      materials {\\n        activeValue\\n        name\\n        options {\\n          value\\n        }\\n        visibility\\n      }\\n      patterns {\\n        name\\n        options {\\n          value\\n        }\\n        activeValue\\n      }\\n      reductionRange {\\n        activeValue\\n        name\\n        options {\\n          value\\n        }\\n        unit\\n        visibility\\n      }\\n      saleStatus {\\n        activeValue\\n        name\\n        options {\\n          value\\n        }\\n        visibility\\n      }\\n      sizesHarmonized {\\n        name\\n        options {\\n          value\\n        }\\n        activeValue\\n      }\\n    }\\n    isMonetisationExcluded\\n    isSalePage\\n    pagination {\\n      ...paginationData\\n    }\\n    products {\\n      ...productData\\n    }\\n    sort {\\n      currentParam\\n      params\\n    }\\n  }\\n}\\n\\nfragment paginationData on XPagination {\\n  currentPage\\n  itemsPerPage\\n  totalItems\\n  totalPages\\n}\\n\\nfragment priceData on XSharedPrice {\\n  currencyCode\\n  currencySymbol\\n  discount\\n  discountEur\\n  extraDiscount\\n  finalDuties\\n  hint\\n  includesVAT\\n  isPriceModifiedByRegionalRules\\n  original\\n  originalDuties\\n  originalDutiesEur\\n  originalEur\\n  percentage\\n  regionalRulesModifications {\\n    priceColor\\n  }\\n  regular\\n  vatPercentage\\n}\\n\\nfragment productData on XSharedProduct {\\n  color\\n  combinedCategoryErpID\\n  combinedCategoryName\\n  department\\n  description\\n  designer\\n  designerErpId\\n  designerInfo {\\n    designerId\\n    displayName\\n    slug\\n  }\\n  displayImages\\n  enabled\\n  features\\n  fta\\n  hasMultipleSizes\\n  hasSizeChart\\n  hasStock\\n  isComingSoon\\n  isInWishlist\\n  isPurchasable\\n  isSizeRelevant\\n  labelObjects {\\n    id\\n    label\\n  }\\n  labels\\n  mainPrice\\n  mainWaregroup\\n  name\\n  price {\\n    ...priceData\\n  }\\n  priceDescription\\n  promotionLabels {\\n    label\\n    type\\n  }\\n  seasonCode\\n  sellerOrigin\\n  sets\\n  sizeAndFit\\n  sizesOnStock\\n  sizeTag\\n  sizeType\\n  sku\\n  slug\\n  variants {\\n    allVariants {\\n      availability {\\n        hasStock\\n        lastStockQuantityHint\\n      }\\n      isInWishlist\\n      size\\n      sizeHarmonized\\n      sku\\n    }\\n    availability {\\n      hasStock\\n      lastStockQuantityHint\\n    }\\n    isInWishlist\\n    price {\\n      currencyCode\\n      currencySymbol\\n      discount\\n      discountEur\\n      extraDiscount\\n      includesVAT\\n      isPriceModifiedByRegionalRules\\n      original\\n      originalEur\\n      percentage\\n      regionalRulesModifications {\\n        priceColor\\n      }\\n      vatPercentage\\n    }\\n    size\\n    sizeHarmonized\\n    sku\\n  }\\n}\\n","variables":{"categories":["5076"],"colors":[],"designers":[],"fta":null,"materials":[],"page":1,"patterns":[],"reductionRange":[],"saleStatus":null,"size":100,"sizesHarmonized":[],"slug":"/designers/balenciaga","sort":"recommendation"}}'

        return headers, data

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
            
            # 记录本次爬取的统计信息
            stats = {
                "url_total": len(self.catalog_url),
                "url_success": 0,
                "expected_product_count": 0,  # 预期的商品数量，可以从历史数据估算
                "actual_product_count": 0     # 实际爬取到的商品数量
            }
            
            # 从历史数据估算预期的商品数量
            if self.previous_inventory and len(self.previous_inventory) > 5:
                stats["expected_product_count"] = len(self.previous_inventory)
                self.logger.info(f"根据历史数据，预期商品数量约为 {stats['expected_product_count']} 个")

            # 获取商品目录
            catalog_data = self.get_inventory_catalog()
            
            # 更新统计信息
            if hasattr(self, 'url_success_count'):
                stats["url_success"] = self.url_success_count
            
            if not catalog_data:
                self.logger.error("获取商品目录失败，终止监控")
                return 0  # 返回0表示爬取失败
            
            # 解析商品目录
            self.products_list = catalog_data
            stats["actual_product_count"] = len(self.products_list)

            # 如果商品列表为空，记录错误并返回
            if not self.products_list:
                self.logger.error("商品列表为空，终止监控")
                return 0  # 返回0表示爬取失败

            self.logger.info(f"监控开始，共获取到 {len(self.products_list)} 个商品信息")

            # 保存库存数据
            if self.inventory_data:
                # 检查数据有效性
                if len(self.inventory_data) < 5:  # 假设正常情况下至少应有5个商品
                    self.logger.warning(f"获取到的商品数量异常少({len(self.inventory_data)}个)，可能是爬取不完整，不保存数据")
                    return 0  # 返回0表示爬取异常
                
                # 检查爬取完整性
                url_success_rate = stats["url_success"] / stats["url_total"] if stats["url_total"] > 0 else 0
                
                # 标准化库存数据
                normalized_data = self._normalize_inventory_data(self.inventory_data)
                
                # 检查与预期数量的差异
                if stats["expected_product_count"] > 0:
                    product_diff_rate = abs(stats["actual_product_count"] - stats["expected_product_count"]) / stats["expected_product_count"]
                    if product_diff_rate > 0.3 and url_success_rate < 1.0:  # 如果商品数量差异超过30%且有URL爬取失败
                        self.logger.warning(f"爬取结果与预期差异较大 (差异率: {product_diff_rate:.1%})，且URL成功率为 {url_success_rate:.1%}，不进行变化比较")
                        # 仍然保存数据，但不进行变化比较
                        data_file = f"balenciaga_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        saved_path = self.save_json_data(normalized_data, data_file)
                        self.logger.info(f"已保存{len(normalized_data)}个商品的库存信息到 {saved_path}")
                        return len(normalized_data)  # 返回爬取的商品数量
                
                # 检查上次爬取是否为空或异常少
                if self.previous_inventory and len(self.previous_inventory) < 5:
                    self.logger.warning("上次爬取的数据异常少，本次将不与其比较变化")
                    # 先保存当前数据，但不进行变化检测
                    data_file = f"balenciaga_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    saved_path = self.save_json_data(normalized_data, data_file)
                    self.logger.info(f"已保存{len(normalized_data)}个商品的库存信息到 {saved_path}")
                    return len(normalized_data)  # 返回爬取的商品数量
                
                # 保存标准化后的数据
                data_file = f"balenciaga_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                saved_path = self.save_json_data(normalized_data, data_file)
                self.logger.info(f"已保存{len(normalized_data)}个商品的库存信息到 {saved_path}")

                # 检测库存变化
                changes = self.detect_inventory_changes(normalized_data)
                if changes:
                    self.logger.info("检测到库存变化，已保存到变更记录")

                return len(normalized_data)  # 返回爬取的商品数量
            else:
                self.logger.warning("未获取到任何库存信息，无法生成总结")
                return 0  # 返回0表示爬取失败

        except Exception as e:
            self.logger.error(f"监控过程中出错: {str(e)}")
            return 0  # 返回0表示爬取失败
        finally:
            self.logger.info("监控结束，关闭浏览器")

    def get_inventory_catalog(self):
        """
        获取商品目录

        从mytheresa网站获取Guidi鞋子的商品列表

        返回:
            list: 商品信息列表，每个元素为包含name和url的字典
        """
        products_list = []
        self.url_success_count = 0
        url_total_count = len(self.catalog_url)

        try:
            for url_index, url in enumerate(self.catalog_url):
                self.logger.info(f"正在获取商品目录 [{url_index + 1}/{url_total_count}]: {url}")
                try:
                    tab = self.page.new_tab()
                    tab.get(url, timeout=60)
                    tab.wait.eles_loaded('x://div[@class="item"]', timeout=60)

                    # 尝试查找商品元素
                    try:
                        tab.scroll.to_bottom()

                        category_items = tab.s_eles('x://div[@class="item"]') + tab.s_eles('x://div[@class="item item--soldout"]')

                        self.logger.info(f"找到 {len(category_items)} 个商品元素")
                        url_products = self.parse_inventory_catalog_html(category_items)
                        products_list.extend(url_products)

                        show_more_button = tab.ele('@text():Show more')

                        # 判断是否存在"Show more"按钮
                        if show_more_button:
                            self.loop_through_button(tab, show_more_button, products_list)
                            
                        self.url_success_count += 1
                        self.logger.info(f"URL {url} 爬取成功，获取到 {len(url_products)} 个商品")

                    except Exception as e:
                        self.logger.error(f"处理URL {url} 的商品目录元素时出错: {str(e)}")
                        # 继续处理下一个URL，而不是直接返回空列表
                except Exception as e:
                    self.logger.error(f"获取URL {url} 时出错: {str(e)}")
                    # 继续处理下一个URL，而不是直接返回空列表
                finally:
                    # 关闭当前标签页，释放资源
                    try:
                        tab.close()
                    except:
                        pass

            # 在所有URL处理完成后，检查成功率
            if self.url_success_count == 0:
                self.logger.error(f"所有URL ({url_total_count}个) 都爬取失败")
                return []
                
            success_rate = self.url_success_count / url_total_count
            if success_rate < 0.5:  # 如果成功率低于50%
                self.logger.warning(f"URL爬取成功率过低: {success_rate:.1%} ({self.url_success_count}/{url_total_count})")
                
            self.logger.info(f"共爬取了 {url_total_count} 个URL，成功 {self.url_success_count} 个，获取到 {len(products_list)} 个商品")
            
            # 如果产品数量异常少，记录警告
            if len(products_list) < 5 and self.url_success_count > 0:
                self.logger.warning(f"爬取到的商品数量异常少 ({len(products_list)}个)，可能是爬取不完整")
                
            return products_list

        except Exception as e:
            self.logger.error(f"获取商品目录过程中出错: {str(e)}")
            # 即使出现全局错误，也返回已经获取到的产品列表，而不是空列表
            return products_list

    def parse_inventory_catalog(self, catalog_items: dict) -> list:
        """
        解析商品目录Element数据

        参数:
            catalog_items (dict): 包含商品目录的Element

        返回:
            list: 商品信息列表，每个元素为包含name和url的字典
        """
        self.logger.debug("开始解析商品目录数据")
        try:
            products = []

            # 提取每个商品的名称和URL
            for item in catalog_items:
                try:
                    name = item.get('name')
                    # 如果无法找到名称，记录警告并尝试下一个元素
                    if not name:
                        self.logger.warning(f"无法找到商品名称元素，跳过此商品")
                        continue

                    url = 'https://www.mytheresa.com/mo/en/men' + item.get('slug')
                    
                    # 提取价格信息
                    price = f"{item.get('price').get('currencySymbol')}{item.get('price').get('original') * 0.01}"

                    inventory = {}
                    for size_item in item.get('variants'):
                        inventory[size_item.get('sizeHarmonized')] = 'available'

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
                            "inventory": inventory,
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

    def parse_inventory_catalog_html(self, category_items: chromium_element):
        """
         解析商品目录Element数据 从HTML网站中

         参数:
             catalog_items (chromium_element): 包含商品目录的Element

         返回:
             list: 商品信息列表，每个元素为包含name和url的字典
         """
        self.logger.debug("开始解析商品目录数据")
        try:
            products = []

            # 提取每个商品的名称和URL
            for item in category_items:
                try:
                    name_ele = item.s_ele('x://div[@class="item__info__name"]/a')
                    name = name_ele.text
                    # 如果无法找到名称，记录警告并尝试下一个元素
                    if not name:
                        self.logger.warning(f"无法找到商品名称元素，跳过此商品")
                        continue

                    url_ele = name_ele.attr('href')
                    url = 'https://www.mytheresa.com' + url_ele if not url_ele.startswith('http') else url_ele

                    # 提取价格信息
                    price = item.s_ele('x://span[@class="pricing__prices__price"]').text

                    inventory = {}

                    for size_item in item.s_eles('x://div[@class="item__sizes"]/span'):
                        if contains_digit(size_item.text):
                            inventory[size_item.text] = 'available'

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
                            "inventory": inventory,
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

    def loop_through_button(self, tab, show_more_button, products_list):
        """
        循环点击"Show more"按钮获取更多商品
        :param tab: 浏览器标签页
        :param show_more_button: "Show more"按钮元素
        :param products_list: 产品列表，用于累积结果
        :return: 无返回值，直接修改传入的products_list
        """
        # 判断是否存在"Show more"按钮
        if show_more_button:
            try:
                # 检查已浏览产品和总产品数量信息
                show_info = tab.ele('x://div[@class="loadmore__info"]')
                if show_info:
                    info_text = show_info.text
                    self.logger.debug(f"显示信息: {info_text}")
                    
                    # 解析 "You've viewed X out of Y products" 格式的文本
                    import re
                    match = re.search(r"You've viewed (\d+) out of (\d+) products", info_text)
                    if match:
                        viewed = int(match.group(1))
                        total = int(match.group(2))
                        self.logger.info(f"已浏览 {viewed}/{total} 个商品")
                        
                        # 如果已经浏览了所有商品，不再点击加载更多
                        if viewed >= total:
                            self.logger.info(f"已加载所有 {total} 个商品，停止加载更多")
                            return
                
                # 开始监听API请求
                tab.listen.start('api.mytheresa.com/api')
                
                # 点击"Show more"按钮加载更多商品
                self.logger.debug("点击 Show more 按钮加载更多商品")
                show_more_button.click(by_js=True)
                
                # 等待API响应
                data_json = tab.listen.wait().response.body
                tab.listen.stop()
                
                # 获取监听数据中的商品列表
                catalog_items = data_json.get('data', {}).get('xProductListingPage', {}).get('products', [])
                
                # 解析并添加新获取的商品数据
                new_products = self.parse_inventory_catalog(catalog_items)
                products_list.extend(new_products)
                self.logger.debug(f"加载了额外的 {len(new_products)} 个商品，当前总数: {len(products_list)}")
                
                # 检查按钮是否仍然可见（是否还有更多商品可加载）
                # 重新获取按钮元素，因为DOM可能已更新
                show_more_button = tab.ele('@text():Show more')
                
                # 设置递归深度限制，防止无限递归
                # 使用全局变量或类属性跟踪递归深度可能更好
                if len(products_list) > 150:
                    self.logger.warning("达到最大产品数量限制，停止加载更多")
                    return

                time.sleep(7.5)
                # 递归调用继续加载更多商品
                self.loop_through_button(tab, show_more_button, products_list)
            except Exception as e:
                self.logger.error(f"点击'Show more'按钮或处理响应时出错: {str(e)}")
        else:
            self.logger.info("没有更多商品可加载或'Show more'按钮不可见")


if __name__ == '__main__':
    # 创建监控实例并运行
    # 需要境外IP代理
    monitor = MytheresaMonitor(is_headless=True, is_auto_port=False, load_mode='normal', proxy_type=None)
    monitor.run_with_log()

