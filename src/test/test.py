from concurrent.futures import ThreadPoolExecutor

import requests
from DrissionPage import SessionPage

import requests

clash_proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}

import requests

cookies = {
    '_ga': 'GA1.1.600185671.1746618232',
    '_gcl_au': '1.1.502287068.1746618233',
    'cookiebanner': '0',
    '__cf_bm': 'RKlRcXFVcrJMLaavNPAjaQRHs7ZfUGpENlk8sF5eOIA-1747153656-1.0.1.1-56Z0JMNdAvuxXR0KVRGEZwl6FXopd2K_Bl.DrehF7Ceh2Ki_JxNQUekAVl_PhBF90Utyr5HGRsHp0Oqv1z.cn3tKhUP50lp_UAFbjm1Ltvo',
    'x-xsrf-token': '792bd8b1-48bd-4039-8014-91eabd592a29',
    'ECOM_SESS': 'a4ef9b883upyy1ccyh20hkg78p',
    'correlation_id': 'nt65suakq7g7amnccs99mh350p3ojpeyr7dzvzrhv5roo6655yf0zni6s811go3s',
    '_ga_Y862HCHCQ7': 'GS2.1.s1747153665$o3$g0$t1747153666$j59$l0$h0',
    'datadome': 'ErOnJb2boEKkrD3UVf3p4yOMTSofwaB7SrAI3h5EWP7q8C986Oy3sj5SkWkFHSi8IwlxLIHcaa_ZWaXKFEtiJAVw4CWBuIo2DTT_Acqt3IpD0srGbMUDtE~Km~WKP87m',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://www.hermes.com/hk/en/category/women/bags-and-small-leather-goods/bags-and-clutches/?facet_line=garden_party',
    'sec-ch-device-memory': '8',
    'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-full-version-list': '"Chromium";v="136.0.7103.93", "Microsoft Edge";v="136.0.3240.64", "Not.A/Brand";v="99.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
    # 'cookie': '_ga=GA1.1.600185671.1746618232; _gcl_au=1.1.502287068.1746618233; cookiebanner=0; __cf_bm=RKlRcXFVcrJMLaavNPAjaQRHs7ZfUGpENlk8sF5eOIA-1747153656-1.0.1.1-56Z0JMNdAvuxXR0KVRGEZwl6FXopd2K_Bl.DrehF7Ceh2Ki_JxNQUekAVl_PhBF90Utyr5HGRsHp0Oqv1z.cn3tKhUP50lp_UAFbjm1Ltvo; x-xsrf-token=792bd8b1-48bd-4039-8014-91eabd592a29; ECOM_SESS=a4ef9b883upyy1ccyh20hkg78p; correlation_id=nt65suakq7g7amnccs99mh350p3ojpeyr7dzvzrhv5roo6655yf0zni6s811go3s; _ga_Y862HCHCQ7=GS2.1.s1747153665$o3$g0$t1747153666$j59$l0$h0; datadome=ErOnJb2boEKkrD3UVf3p4yOMTSofwaB7SrAI3h5EWP7q8C986Oy3sj5SkWkFHSi8IwlxLIHcaa_ZWaXKFEtiJAVw4CWBuIo2DTT_Acqt3IpD0srGbMUDtE~Km~WKP87m',
}

params = {
    'facet_line': 'garden_party',
}

response = requests.get(
    'https://www.hermes.com/hk/en/category/women/bags-and-small-leather-goods/bags-and-clutches/',
    params=params,
    headers=headers,
)

print(response.text)

with open('cettire.html', 'w', encoding='utf-8') as file:
    file.write(response.text)

page = SessionPage()

page.get(
'https://www.hermes.com/hk/en/category/women/bags-and-small-leather-goods/bags-and-clutches/',
    params=params,
    headers=headers,
)
print(page.html)
