from monitor import Monitor


class BaseCrawler(Monitor):
    """
    BaseCrawler类继承自Monitor类，用于处理所有网站数据抓取和保存
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _init_params(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        # 代理模式
        self.proxy_type = kwargs.get('proxy_type', None)

        self.fetch_mode = kwargs.get('fetch_mode', "session").lower()

        if self.fetch_mode not in ["session", "page"]:
            raise ValueError("fetch_mode must be 'session' or 'page'")
        
    def proxy_handler(self):
        """
        代理模式
        """
        if self.proxy_type == "ipcool":
            self.proxy_url = self.ipcool_url
        elif self.proxy_type == "clash":
            self.proxy_url = self.proxy_clash_url
        elif self.proxy_type == "pin_zan":
            self.proxy_url = self.proxy_pin_zan_url
        else:
            self.proxy_url = None
        

    def get_inventory_catalog_handler(self):
        """
        不同的模式获取库存目录
        """
        # 获取库存目录
        if self.fetch_mode == "session":
            self.get_inventory_catalog_session()
        else:
            self.get_inventory_catalog_page()

    def get_inventory_catalog_session(self):
        """
        使用session模式获取库存目录
        """
        self.session = self.init_session()
        
        for url in self.catalog_url:
            self.session.get(url, headers=self.header, proxies=self.proxy_url)

    def get_inventory_catalog_page(self):
        """
        使用page模式获取库存目录
        """
        self.page = self.init_page()
        self.page.get(self.catalog_url, proxies=self.proxy_url)

    def parse_inventory_catalog(self, catalog_data):
        pass

    def run(self):
        """
        运行爬虫程序
        """
        self.run_with_log()
