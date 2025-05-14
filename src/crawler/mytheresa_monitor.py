"""
Mytheresa监控模块 - 负责监控Mytheresa网站上Balenciaga鞋子的库存状态
该模块实现了对Mytheresa网站的爬取、解析和数据保存功能
"""
from datetime import datetime

from common.monitor import Monitor


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
        kwargs['catalog_url'] = 'https://api.mytheresa.com/api'

        super().__init__(**kwargs)
        
        # 初始化浏览器页面
        self.session = self.init_session()

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

        从mytheresa网站获取Guidi鞋子的商品列表

        返回:
            list: 商品信息列表，每个元素为包含name和url的字典
        """
        self.logger.info(f"正在获取商品目录: {self.catalog_url}")
        try:
            headers, data = self.init_params()
            # 设置代理并访问页面
            self.session.post(self.catalog_url, headers=headers, data=data)

            # 检查页面响应
            if not self.session.html.strip():
                self.logger.error("获取页面失败：页面响应为空")
                return []

            # 尝试查找商品元素
            try:
                catalog_items = self.session.json.get('data').get('xProductListingPage').get('products')

                if not catalog_items:
                    self.logger.error("未找到任何商品列表元素")
                    return []

                self.logger.info(f"找到 {len(catalog_items)} 个商品元素")
                products_list = self.parse_inventory_catalog(catalog_items)
                return products_list

            except Exception as e:
                self.logger.error(f"处理商品目录元素时出错: {str(e)}")
                return []

        except Exception as e:
            self.logger.error(f"获取商品目录过程中出错: {str(e)}")
            return []

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

                        product_info = {
                            "name": name,
                            "url": url,
                            "price": price,
                            "inventory": {}
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


if __name__ == '__main__':
    # 创建监控实例并运行
    # 需要境外IP代理
    monitor = MytheresaMonitor(is_headless=True)
    monitor.run_with_log()

