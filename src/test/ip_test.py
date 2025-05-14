import _thread
import time
import requests

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60 MicroMessenger/6.5.19 NetType/4G Language/zh_TW",
}

mainUrl = 'https://www.ipplus360.com/getIP'


def testUrl():
    # 账密
    entry = 'http://{}:{}@us.ipcool.net:2555'.format("13727744565_187_0_0_session_0_1", "lin2225427")

    proxy = {
        'http': entry,
        'https': entry,
    }
    try:
        res = requests.get(mainUrl, headers=headers, proxies=proxy, timeout=10)
        print(res.status_code, res.text)
    except Exception as e:
        print("访问失败", e)
        pass


if __name__ == "__main__":
    testUrl()
