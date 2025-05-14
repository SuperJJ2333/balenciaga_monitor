from DrissionPage import SessionPage


page = SessionPage()

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
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
    'cookie': 'spc-cur=EUR; spc-code=IT; spc-nat=Italy; spc-lng=en; session_id=10e1e95f-e99d-46cb-b032-6add063933ca; device_id=dfe402ffb3ac53d888b00eeb08c62579e241cde25e1a5f13b67e64654f1e0f59; fingerprint=603445a6fa5f8d26f5c55da89540d9d8; rskxRunCookie=0; rCookie=t0w6wts8bqnz53hb2srelm9crxiq0; cc_cookie_cettire=%7B%22categories%22%3A%5B%22necessary%22%5D%2C%22revision%22%3A0%2C%22data%22%3Anull%2C%22consentTimestamp%22%3A%222025-04-17T08%3A47%3A00.467Z%22%2C%22consentId%22%3A%2242510e65-45dd-45e2-b23a-ffbdb8f78322%22%2C%22services%22%3A%7B%22necessary%22%3A%5B%5D%2C%22functional%22%3A%5B%5D%2C%22analytics%22%3A%5B%5D%2C%22advertising%22%3A%5B%5D%7D%2C%22lastConsentTimestamp%22%3A%222025-04-17T08%3A47%3A00.467Z%22%7D; next-i18next=en; lastPageUrl=/it/collections/balenciaga?from=brand_list.brand_search&menu%255Bdepartment%255D=men&menu%255Bproduct_type%255D=&refinementList%255BSize%255D=&refinementList%255Btags%255D%255B0%255D=Shoes&page=2&sortBy=production_rep_cettire_vip_date_desc&configure%255BhitsPerPage%255D=96&configure%255Bdistinct%255D=1&configure%255Bfilters%255D=visibility%253AYES%2520AND%2520%2528vipLevel%253A%25200%2520OR%2520vipLevel%253A%2520null%2529%2520AND%2520eu_eur_price_f%2520%253E%25200; forterToken=f17d597410cc49cf8f2fe4ab3f9e50ed_1746980332451__UDF43-m4_23ck_; lastRskxRun=1746980341746',
}

params = {
    'from': 'brand_list.brand_search',
    'menu[department]': 'men',
    'menu[product_type]': '',
    'refinementList[Size]': '',
    'refinementList[tags][0]': 'Shoes',
    'page': '2',
    'sortBy': 'production_rep_cettire_vip_date_desc',
    'configure[hitsPerPage]': '96',
    'configure[distinct]': '1',
    'configure[filters]': 'visibility:YES AND (vipLevel: 0 OR vipLevel: null) AND eu_eur_price_f > 0',
}

page.get('https://www.cettire.com/it/collections/balenciaga?from=brand_list.brand_search&menu%5Bdepartment%5D=men&menu%5Bproduct_type%5D=&refinementList%5BSize%5D=&refinementList%5Btags%5D%5B0%5D=Shoes&page=2&sortBy=production_rep_cettire_vip_date_desc&configure%5BhitsPerPage%5D=96&configure%5Bdistinct%5D=1&configure%5Bfilters%5D=visibility%3AYES%20AND%20%28vipLevel%3A%200%20OR%20vipLevel%3A%20null%29%20AND%20eu_eur_price_f%20%3E%200',
         headers=headers, params=params, proxies={'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'})

print("!!!!!")

data_list = page.s_eles('@class^lazyload-wrapper')

for item in data_list:
    print("name:::", item.s_ele('x://a/div/div/div[2]').text)
    print("url:::", item.s_ele('x://a').attr('href'))
    print("price:::", item.s_ele('x://a/div/div/span/span').text)