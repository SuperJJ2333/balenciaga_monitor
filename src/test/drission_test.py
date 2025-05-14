from DrissionPage import ChromiumPage


cookies = {
    'domain': 'https://s.taobao.com/',
    'cna': 'LtRVILkEEGQCAXcirgEp6Yz1',
    'thw': 'cn',
    't': '74aca3c227205d21c21dd2e8f2aedbbf',
    '_samesite_flag_': 'true',
    'cookie2': '1125c3db85ba8916e194064a3a808fac',
    '_tb_token_': '569eadbdd4eef',
    'mtop_partitioned_detect': '1',
    '_m_h5_tk': '3dccb1103e089ad78a6b1c64e34c1132_1746633298636',
    '_m_h5_tk_enc': 'a1a236679599facd54be28bb604c3bd1',
    'xlly_s': '1',
    '3PcFlag': '1746623953282',
    'wk_cookie2': '1d8b93167ed1c0135368c8f913ba855c',
    'wk_unb': 'UNaGuKCocoh3MQ%3D%3D',
    'sgcookie': 'E100Ri6FwqPQxKegRtiqYnlDNunGtUkhRLhMdZEopEfqTpyOmYQMUp7I%2FmYxkSQnToJ9Zg%2FeB3%2Fh%2FOwJAvbecOWhZyvKaeGZ9TBtHj2QUUmn3QkNjV5S1Gcwlkv72wqRPTE0',
    '_hvn_lgc_': '0',
    'havana_lgc2_0': 'eyJoaWQiOjM2MTA3ODg2OTgsInNnIjoiYWY3ZmYzYmFiYThhYWVhODBhN2E1MmUwMTM1NmY0NzQiLCJzaXRlIjowLCJ0b2tlbiI6IjFzNnNYOXVDVTAzbkk1S05qdk5ZVUlnIn0',
    'unb': '3610788698',
    'csg': 'eded28e4',
    'lgc': 'tb619838021',
    'cancelledSubSites': 'empty',
    'cookie17': 'UNaGuKCocoh3MQ%3D%3D',
    'dnk': 'tb619838021',
    'skt': '1a3b948361facee3',
    'tracknick': 'tb619838021',
    '_cc_': 'U%2BGCWk%2F7og%3D%3D',
    '_l_g_': 'Ug%3D%3D',
    'sg': '181',
    '_nk_': 'tb619838021',
    'cookie1': 'UNcMJIPeSeK%2BAo39ra9nHfNHPekflIwqHl1FhARpE9s%3D',
    'uc1': 'cookie21=V32FPkk%2Fgi8IDE%2FSq3xx&cookie15=U%2BGCWk%2F75gdr5Q%3D%3D&cookie14=UoYaje%2F7hYEtBA%3D%3D&pas=0&cookie16=V32FPkk%2FxXMk5UvIbNtImtMfJQ%3D%3D&existShop=false',
    'sn': '',
    'uc3': 'lg2=U%2BGCWk%2F75gdr5Q%3D%3D&id2=UNaGuKCocoh3MQ%3D%3D&vt3=F8dD2EXa0WZ4aTdoT7k%3D&nk2=F5RDLexDYxMJhLk%3D',
    'existShop': 'MTc0NjYyMzk4OA%3D%3D',
    'uc4': 'id4=0%40UgGP%2FESno5fCX8953qfOVDpkf05O&nk4=0%40FY4I7j65oHITYuGjKxXSsLfi%2BG5E8w%3D%3D',
    'havana_lgc_exp': '1746655092229',
    'sdkSilent': '1746710393156',
    'havana_sdkSilent': '1746710393156',
    'tfstk': 'gQrmwomfirubFf5-yuif-sFJDNQJlmisl5Kt6chNzblWDVlOl50g67gaDmeYZfPLsAEYXl4WjJw_DtiOhmwjfc5d9MFgh-i19G9tx_ePQAii3ijRytyjfc5peh7dx-NjlNt03AkPEAH9ufPZubkrNALqbjuwaUkEacoZ7V-y4ADmQFlq7T2rNAoZ_5uVE4lSQbVVujZa4u55ChifNblTqx0mT8bBbh2vvqcU3bxNTuDcOXyqZh-itfEet82AiHw-ckNnpSIymW2QV7DzTGfof7aa_AVPACnbJSZIrSQe48oSN2lzYI8qKmcm8ouWInyr7zqoDo56R8eog2m8ya1xWmV0RXgVP_NgEjFam4RcwfULeouuT_Ku1V4QBAVcmnPF4_8y8qBpfYWT4FTsuYMo9wsSeTMHUqUPETYFCqkShXBlEFTsuYMo9TXk8ZgqFxGd.',
    'isg': 'BIKCcdkBXkY21E1PGiDR7ndS04jkU4ZtEk-nzcyaAvWgHyOZtONmfcYZyxtjT_4F',
}

headers = {
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': 'https://s.taobao.com/',
    'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'script',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
    # 'cookie': 'cna=LtRVILkEEGQCAXcirgEp6Yz1; thw=cn; t=74aca3c227205d21c21dd2e8f2aedbbf; _samesite_flag_=true; cookie2=1125c3db85ba8916e194064a3a808fac; _tb_token_=569eadbdd4eef; mtop_partitioned_detect=1; _m_h5_tk=3dccb1103e089ad78a6b1c64e34c1132_1746633298636; _m_h5_tk_enc=a1a236679599facd54be28bb604c3bd1; xlly_s=1; 3PcFlag=1746623953282; wk_cookie2=1d8b93167ed1c0135368c8f913ba855c; wk_unb=UNaGuKCocoh3MQ%3D%3D; sgcookie=E100Ri6FwqPQxKegRtiqYnlDNunGtUkhRLhMdZEopEfqTpyOmYQMUp7I%2FmYxkSQnToJ9Zg%2FeB3%2Fh%2FOwJAvbecOWhZyvKaeGZ9TBtHj2QUUmn3QkNjV5S1Gcwlkv72wqRPTE0; _hvn_lgc_=0; havana_lgc2_0=eyJoaWQiOjM2MTA3ODg2OTgsInNnIjoiYWY3ZmYzYmFiYThhYWVhODBhN2E1MmUwMTM1NmY0NzQiLCJzaXRlIjowLCJ0b2tlbiI6IjFzNnNYOXVDVTAzbkk1S05qdk5ZVUlnIn0; unb=3610788698; csg=eded28e4; lgc=tb619838021; cancelledSubSites=empty; cookie17=UNaGuKCocoh3MQ%3D%3D; dnk=tb619838021; skt=1a3b948361facee3; tracknick=tb619838021; _cc_=U%2BGCWk%2F7og%3D%3D; _l_g_=Ug%3D%3D; sg=181; _nk_=tb619838021; cookie1=UNcMJIPeSeK%2BAo39ra9nHfNHPekflIwqHl1FhARpE9s%3D; uc1=cookie21=V32FPkk%2Fgi8IDE%2FSq3xx&cookie15=U%2BGCWk%2F75gdr5Q%3D%3D&cookie14=UoYaje%2F7hYEtBA%3D%3D&pas=0&cookie16=V32FPkk%2FxXMk5UvIbNtImtMfJQ%3D%3D&existShop=false; sn=; uc3=lg2=U%2BGCWk%2F75gdr5Q%3D%3D&id2=UNaGuKCocoh3MQ%3D%3D&vt3=F8dD2EXa0WZ4aTdoT7k%3D&nk2=F5RDLexDYxMJhLk%3D; existShop=MTc0NjYyMzk4OA%3D%3D; uc4=id4=0%40UgGP%2FESno5fCX8953qfOVDpkf05O&nk4=0%40FY4I7j65oHITYuGjKxXSsLfi%2BG5E8w%3D%3D; havana_lgc_exp=1746655092229; sdkSilent=1746710393156; havana_sdkSilent=1746710393156; tfstk=gQrmwomfirubFf5-yuif-sFJDNQJlmisl5Kt6chNzblWDVlOl50g67gaDmeYZfPLsAEYXl4WjJw_DtiOhmwjfc5d9MFgh-i19G9tx_ePQAii3ijRytyjfc5peh7dx-NjlNt03AkPEAH9ufPZubkrNALqbjuwaUkEacoZ7V-y4ADmQFlq7T2rNAoZ_5uVE4lSQbVVujZa4u55ChifNblTqx0mT8bBbh2vvqcU3bxNTuDcOXyqZh-itfEet82AiHw-ckNnpSIymW2QV7DzTGfof7aa_AVPACnbJSZIrSQe48oSN2lzYI8qKmcm8ouWInyr7zqoDo56R8eog2m8ya1xWmV0RXgVP_NgEjFam4RcwfULeouuT_Ku1V4QBAVcmnPF4_8y8qBpfYWT4FTsuYMo9wsSeTMHUqUPETYFCqkShXBlEFTsuYMo9TXk8ZgqFxGd.; isg=BIKCcdkBXkY21E1PGiDR7ndS04jkU4ZtEk-nzcyaAvWgHyOZtONmfcYZyxtjT_4F',
}

url = 'https://s.taobao.com/search?initiative_id=staobaoz_20250428&page=2&q=%E7%89%9B%E8%82%89&tab=all'

page = ChromiumPage()

# page.set.cookies(cookies)

page.listen.start('/mtop.relationrecommend.wirelessrecommend.recommend/2.0')
page.get(url)

res = page.listen.wait()

print(res.response.body)

