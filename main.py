import re

import requests
from DrissionPage import SessionPage

session = SessionPage()
url = 'https://www.mrporter.com/en-hk/mens/product/balenciaga/shoes/low-top-sneakers/track-trail-logo-print-tpu-and-shell-sneakers/46376663162855652'
url2 = 'https://www.mrporter.com/en-hk/mens/product/balenciaga/shoes/high-top-sneakers/speed-recycled-stretch-knit-slip-on-sneakers/18706561955792275'
url3 = 'https://www.mrporter.com/en-hk/mens/product/balenciaga/shoes/slides/speed-20-logo-print-stretch-knit-slides/1647597309861136'

headers = {"Host":"www.mrporter.com","Connection":"keep-alive","Pragma":"no-cache","Cache-Control":"no-cache","sec-ch-ua":"\"Microsoft Edge\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"","sec-ch-ua-mobile":"?0","sec-ch-ua-platform":"\"Windows\"","Upgrade-Insecure-Requests":"1","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7","Service-Worker-Navigation-Preload":"true","Sec-Fetch-Site":"same-origin","Sec-Fetch-Mode":"navigate","Sec-Fetch-User":"?1","Sec-Fetch-Dest":"document","Referer":"https://www.mrporter.com/en-hk/mens/designer/balenciaga/shoes","Accept-Encoding":"gzip, deflate, br, zstd","Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6","Cookie":"_qt_userCheck=true; geoIP=US; Y-City=US-NY-BUFFALO; PIM-SESSION-ID=jqyekR7s1Z5YvSes; _gcl_au=1.1.1471124212.1744365559; _ga=GA1.1.419663401.1744365560; _tt_enable_cookie=1; _ttp=01JRJ4MAKRZ08Q9VGE2R3GVEVZ_.tt.1; _ym_uid=1744365564730072876; _ym_d=1744365564; _ym_isad=1; _fbp=fb.1.1744365563865.791842068996898807; _mibhv=anon-1744365563888-897186386_5255; _pin_unauth=dWlkPU5EWm1abU01WkRndE4yTXlNQzAwWVdVMUxXRTRPVEV0TlRJMlkySmxPR1V3WVRGag; FPID=FPID2.2.o%2BajIqiizdIn3NGOGlv0%2FEETW%2BBheuVjmn0d7VaNCr4%3D.1744365560; FPLC=d3U2wNhYHtDTHVeudfXLTlH9T3Z%2F9L9TwQn1CAGKC0oNXQVuz%2BOt0lA8h7hAqMPXDGC%2FvO7kKzOMWrhIVnC68vMCBXSIhpPRkGW3XTweSxV1fBMn8jms88dyCU6xIQ%3D%3D; ORA_FPC=id=26803467f8c82207fb21744336769117; _cs_c=0; LPVID=E3NGYwNmMyZGQzZGQ1NDc2; LPSID-73583570=Bv2Ja8RNSRyHQnTqtNuc1g; lang_iso=en; country_iso=HK; bm_mi=F5FEB7E87B9CAA73C3B60DA2683CC54A~YAAQKBghF0xx1haWAQAAdDVLJBsD4QzNejbdW2UlyJxyPArb/IBwgjU98eKZIXMTmYFqjkTjhGGqEMRCyRt7sKKEMh2oSLw2XIu3F6PesqMfXghSDfyvXwXJmNNf+SiK6V1Z7mBCG06578Ylam0VD4yUQ0+JhOxiJ6ez9cQtrTFvhpZU/Mlue98xkesmlZvvmyHr4P0P/u+HPRk3gxoMSQGh1emuOvbgtl8zyNhu9sEZ0M0n2UkIuh/nDRP06S4Cyu5FgzQFDHE3t9qcFQPooSUCWzkiAEnisCxksw/woEMtok7mOKaDFBtYmPr24cEM7ji0ZYCjcTX2BDCclbDSmW8cQGGbwqLdRZSZ4varq/WWgooi6hfnZE3k2/XWMDWtJJYaxSBxGaNHhbyBpxpgT/T9P88gis7Jc8t7qU4jfeeee/ozLo7go5/zwguq+Q==~1; ak_bmsc=6BB30AE0EE7A20D6A259CD4DDE122778~000000000000000000000000000000~YAAQKBghF+Gl1haWAQAA96NLJBvSNJ/ztjyIA5VVa+ccdkm4egwTzi54E/D0yMTR1VFB3rcE7m7gMFC/SNX8PAi6H6fO/X1rWSBduVjDo1n/TeL2LLXGx2FBfvtVbAAgkcV1Knfwqrm3npuEDoTyRn4tvxjqHalY+LDn/aWTIGbO/Z5uYiBK7ygGdi7mBplTc0SVbbtJPx+/GtC6Uu190xCG1/BKFqLt9GIxLoxLXtBKHk0URWr7XzIuUsdLNv+NRjsHYpp0boe28mX1GcuO1OlTaFL213j/deNtKlVlgBfL6kW8aowCWq4LEpE7cmXEN/dKIoh0LCzoDvoAHSpAspZ77H7PKizgdC8Kr9WzWbndW4N9O7ovuW4QWF/WyZdk90i3mY4cfB2CqPIcW6jBi0vIJpqVahILY46vs5qwPfq0wfo6OHrGOpgkC7o/vajbr4J3m4Vj0JvJ3YKwpIiNlcQ+I/c3LZuU0MM9LIFvt8HTckBXrP3BpyTBiBhcS+bXITAm5FAp3Yzw+w5HpZfXRS7LlrQgWFRAimjdfjssb09IgREBFEerYWhD45QCJDevCUr+rgs7E+qGYJJ1N3qBmLuQoisqz4/VxkeIRLC9; ubertoken=v01.2L2S7qJjkBlohq2eeASgXzGB0ngJaQgQX1jhTpKGLiKRx14W0A8mlbX95DlFTHeaemmQqWx5VhTSW0JaHxcXbeiWIWQOFbaw6G4qyF0p1Oxx56k+oba+QNWxmft9TK58EeCuN9Ptvfi0nSKJLhMACJ638d2bRuBTz0h+FI8Ma3Yb/s0Y1vOem/t28xnMZN4BVNmShqgiGMnHuwwFy3tHaKO7SbFz8sALvd74oOIYYw465dRWAEBcwy/pUc8vM4JaJkIOcj5B3jqYMVLC3YtaHVYhR4DCpWVMM9SdUFVUiiVF9M6ymNsWp6znkHwsSlCZ+Fn9pBsX9lALpCi3B1KSAyF03TX2gF6rVvwdDm9UcigD9y7WkGmC+FOjj+lBZ69IzmU/M8iNVp/QP0vKRaP5doyVFhC0xQJPcG2wELKm2XwnAaqT2Rf/rhTw8mYPJq6Nhtr5CnzjnVw1zoBUpp/e2exA4xPgY3WodNpyavtadVTKPPMEgG8hZ4GDe91rTEsYsclocLiBZq4MekOM+8OzjrEvbwX3UasbkARrixR1sR7l9OG/FdlTiTCoLESIF2o7pwNiJ/8TvPg1kkzp5CwgN18JR537MvhXWCI1vGeO3rzCHrt/2vcxXwDCIbsaIPct857ER/k9oHftK1mDOW42TEKKWfXCP/CdiJTzGDBct7937Lg8/ENbrjtoYoWi6wUgVfhoFECrDPtnIlC/YVzHhZhKOTotgHwyPIlnhVbSsQvr+4pALaXKuSDbdIp+8rsPLKFVnK4ragXFKyhqimgJ5KKlUqioiluhPOV8Nz8RVJEQNDjBn/DMA5e4jIh/D27KISoUodRwuQ5nhN0Wrl6JJaOCH05V6Q91s9MDCkMQxYIOg9by5Q6czepcjsRXy+p37oinp43iBBa5xKyCLxqTMAJeYrXbPL2etqMaHnWJYHNELrBKkakRqxuWSNysURrkZNWuv31hFyjjiJW1OkBTXI8gnH17boQWrLK6BvZ7FuNUPjiQTgT4p5iSq2wsVzQt3mn7kKPBN5BjtHIShy8KEqJCHfA/86pe5P3leQUJs/btLaPc75EX7JJnwz+QLO5cCWqt1zFLUxtb6VqvoHyPbz6irX0GVX+hkf69xR1oVQbyD6uC5oIRr0L7Eo7jxl5pRRZ2Fr/TESw3zS/qLnzVWbDxB5BMxSg8DiOxKJSEkKyIgZ68buMTl7NiwIB1K6CcsNV7VOPj/x5noARf+gCFZPyMrpuBXZ6FCU/VXoe6Dd7XlYNH0859xmoMbHHQKOj8QU3JyHnPlzGpCNZ+w3xiRQ==.iPRveC1TdWJfh+tyA0obN5fjDxC/Awimlr1kpp0E9Ig=.APICSlNFU1NJT05JRD0wMDAwX3VNeVhSVVV1ell1R3lpQjZkc0ItNVI6LTE7IEFXU0VMQj05NTU1Mzk5NTA4OUREQTU0NEJDMUUzMDFERUZDQTA3RDgwRTgwNUUyOThDRUU2NjcxOTYwRDExQzBCQkJFMEFDMEZGRERFQUQwRjdBRjNDMDlFNUFEOTJDMDkxQUExNURENkFFRDBEOTQ0RDg5QzBGMkE4RTgwQzVDN0UxM0Q4OUY0Qzg4NjBEMEM3QzA2M0U3OTQxQTczRjNFNzEzRTU3QjU3M0EwQzk0Qw==; QSI_HistorySession=https%3A%2F%2Fwww.mrporter.com%2Fen-hk%2Fmens%2Fdesigner%2Fbalenciaga%2Fshoes~1744365576389%7Chttps%3A%2F%2Fwww.mrporter.com%2Fen-hk%2Fmens%2Fproduct%2Fbalenciaga%2Fshoes%2Flow-top-sneakers%2Fmonday-leather-sneakers%2F46376663162855661~1744365656895%7Chttps%3A%2F%2Fwww.mrporter.com%2Fen-hk%2Fmens%2Fproduct%2Fbalenciaga%2Fshoes%2Flow-top-sneakers%2Ftrack-trail-logo-print-tpu-and-shell-sneakers%2F46376663162855652~1744367046746; bm_ss=ab8e18ef4e; bm_so=0D037B5E0D35218A58924DD87A4FFB2E351E9D6506A4557C56B32C568E3B581C~YAAQKBghF/l6+BaWAQAAO3GNJAOUZW+7hB+L1oBmqitDCQSvn5gxAvVES+zZ0twXc4ktdm8mFqHfxnH2JrUp0sbUFH2ixJrcb+O9gFmQjckRRZOzys7xeUfsBWh7MVm1xMNBQtEFK6oWy2SyT9/LV2ikSxdhpUUsnq6SVFn1B9yrJB9CvSy+O1zGJjebHAs5BkCztoqKtr4pvUe9HmhjnXa1HemhpC97p865gMe0wgRKNO6rLgly+UeWxYztuvhC/i0cTdMOiC8G+qWVmh/GN6f18kQdk7pG2pEYO/nxHqaKNl+Vvb3vwz9OSBmJy709nu12cDrTOCHVs1ia+j90BMPRGgzNSwDC0/8QTQ5xNmZCdX+NLDtw7zSmIYtLiOEvNQTXuDSC6yMN2R5RicX2u89qOh/fCYtivPwlBQ+v4Z693/vwfworoH+55vq0Llg/5n5V99Fi4MFQ2N1Q+RyD; bm_sz=E3BE578AED6DCF10E3E7EBF57C7205B0~YAAQKBghF/t6+BaWAQAAO3GNJBsFHlmIcPUsysIkF23YpGZSW6H+a+uzQkEUxdH4HLw9U0QpyEEBnlOjr/DMpbr9SJ1MucVEljmat6a41SbqvtmZzzdZY+qoFGEAottv1HIinHU97NRsCobCx9gxxAq9D0pz35xKqNULnnj3cSgsMwyR+Ne0Hq6upDMGY+9gVKftTZm8T1LdpGSDzd1rfHIDrnAhu4RIMya8ab8Zs/DAtzY/bdjQy7wUo3fiUDgFtaWclet457wDBdXVlGQUoMr+LdYsYU8++HbJeSOenZi2J13mqZPGbosxpU+dqRIBIq/C1qnJWYNT/J3Hf0CKhzRaJYReX9tvctQDAh6tLG/XLC6Qnes9+E3Eu4osTyT+kks/Av4HU+dt8RpA+5ENJGwpThzfVlvOoXkgMGYy0FhO+xLb7zS40EDGY4sLpPhPxq2F/dkGAS6mSE1s2/GY7a1Slb0=~3490103~4408375; optimizelySession=0; _qualtricsLiveSession=session=1; _ga_4TPR7LMFWX=GS1.1.1744369947.2.0.1744369947.0.0.0; _ga_Z237CNW2M0=GS1.1.1744369948.2.0.1744369948.0.0.530446735; _ga_XXXXXXXXXXXXXXX=GS1.1.1744369948.2.1.1744369948.0.0.1861730783; _rdt_uuid=1744365593693.e39e560c-824d-4d5c-a5d7-58800f8d771b; _uetsid=a636341016bb11f0a71cddcb369c14ef; _uetvid=a636665016bb11f09108038462ace0d2; _abck=CB686429A708C0D4C79A54BB19FC2EBF~-1~YAAQKBghF2KT+BaWAQAAy5ONJA0A0FUxXcUGOaZR0UEA9mbJEP+SaXt2jFtI1WQED8aCUpiqRvXobMnvAPCmgybEMv1WZ+KmDvxnTk1MJm1u8JS/bM/gLsXCX3NOzswkn1ToBQ522/87CIkM5N4+gSvFOnkXMcfvJkMHHGegw2H8XRCoR56NXIG8zhAQbydwf78nj19KmYhbBMRwvdSIqUD6vqsz8kYI7iE4eBGkdPjYZxYhWoCp+KrZzKx4Fro07CNrU/CcZ9BDNp75OrCTh8b15Fs65t1x1atXPxsElmJqPeonBjTON19TSVULeAlfG3d5RIk8Q5nY+hDd88F/UmuyNqYWUITGxD/nsPOTDGrq20UFvTn1raGZBwXVBxSt4D7HYmBQUcF831mALPGv8047BNguLQmIxnJQj/cAVolRfNYYO3kq2u4Kg/ViSR2zkpaNAnvEGUX5fZvYjlXxsKn3HYIs08Fnd5RNPkqtulAPZt/Vnp7puXmP5m5vfzgz/Qq6l0wJY3WbLvfQreah2iZMQnhFKglsUC8XiVPkz9PaeoZk2dNkitvzFnToc7JFIRgNPdxQmTOvDTdxXa1oiQEqA809Ecb0C4K/S0+C73905Skij7kggAMddgvHJW3HyKrwg2aYAHltdnHI/nMZMW3hm5cgqr0TdnxUkHND9u80hKZ9k2qhFcTU1Nze7iOXovYm5X5WDH1RkJmMDQ==~-1~-1~1744372891; bm_s=YAAQKBghFyyW+BaWAQAAnpiNJAO2bFQ6ClAnwd/QPy7z7J1+oNNjISPW9zH1RfHbOg8lkV1j4BjcpbnQ26AjRrpxK2diEgFdIEywTIvk64oNVB+8EecPn4kIzcnKD5mcj061AQ+1YKRg+/85Go2CPiXKHtmN8c9yAVKVGXQ14pdh+UiP/mnXpYI6b0oQyBy0FnkzaSYA9UYNPOeWv7wbU3eMw/ZtGLSEV+URvofnE3AScsC+PT0tqO45J8pJM66+wHVVG+doxY7C0ccycmy97dJ3n6xgwFZd4DMGIbdZgU0SCv3GfIG/ZjdAqOf6RvuTT6MYYy0wjGYD1e0srOWNPCzYOolu0QIiZEq4CFOh3PcGWuHvu0MCaFFlP2wrssRA+FexNgj3bHY2bxDG2fOzAV8xdS+cHpA0j1pzmcVdR+yMnWtvylP6bYZlencxSlRP8jw2sz8zyxeE8+8nNNDu0+I2Kkeu; bm_sv=D3D43911F2E0228C4EB265D7605FA9D1~YAAQKBghFy2W+BaWAQAAnpiNJBsk9uZeSvBp1aI6fLPrA23ZF2P9bzd7YwSN7f+ZoHGDMVuD9FJVHIZIrhiaUtl7zlxBP6dLe5XYHF6fnQYjsObaxq1yEajcAfMkRrL7wWMai7xaDMWblEFsUqPjGtHP1aWjbhrv2XGYEhACYejyarCN0lnjkbZjx1xZnlnkS6GbF1tAasqXPuEijcn3nhaywQ0PhXKjQzpJLDy18W9KafO+hNkkqQ4kwwABlp+tMUnV~1; _cs_id=65dba369-1ecb-a072-f7c9-867f3a53848b.1744365573.1.1744369950.1744365573.1711122812.1778529573254.1.x; _tq_id.TV-7290368127-1.fac0=72265d3df01b0300.1744365568.0.1744369952..; ttcsid=1744369954366.2.1744369954369; ttcsid_CCQ7HR3C77UDPV428L00=1744369954365.2.1744369955327; bm_lso=0D037B5E0D35218A58924DD87A4FFB2E351E9D6506A4557C56B32C568E3B581C~YAAQKBghF/l6+BaWAQAAO3GNJAOUZW+7hB+L1oBmqitDCQSvn5gxAvVES+zZ0twXc4ktdm8mFqHfxnH2JrUp0sbUFH2ixJrcb+O9gFmQjckRRZOzys7xeUfsBWh7MVm1xMNBQtEFK6oWy2SyT9/LV2ikSxdhpUUsnq6SVFn1B9yrJB9CvSy+O1zGJjebHAs5BkCztoqKtr4pvUe9HmhjnXa1HemhpC97p865gMe0wgRKNO6rLgly+UeWxYztuvhC/i0cTdMOiC8G+qWVmh/GN6f18kQdk7pG2pEYO/nxHqaKNl+Vvb3vwz9OSBmJy709nu12cDrTOCHVs1ia+j90BMPRGgzNSwDC0/8QTQ5xNmZCdX+NLDtw7zSmIYtLiOEvNQTXuDSC6yMN2R5RicX2u89qOh/fCYtivPwlBQ+v4Z693/vwfworoH+55vq0Llg/5n5V99Fi4MFQ2N1Q+RyD^1744369956318; RT=\"z=1&dm=www.mrporter.com&si=500d81f5-e2e8-4652-b095-f99e5c1969e9&ss=m9cm7kh2&sl=0&tt=0&bcn=%2F%2F68794906.akstat.io%2F\"; _cs_s=5.0.0.9.1744371919394"}

clash_proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}
fiddler_proxies = {
    "http": "http://127.0.0.1:8888",
    "https": "http://127.0.0.1:8888"
}
non_proxies = {
    "http": "",
    "https": ""
}


def parse_inventory_info(good_items):
    inventory_info = {}
    for item in good_items.eles('x://ul/li'):
        label = item.ele("tag:label")
        size_info = label.attr('aria-label')
        if size_info:
            # 使用正则表达式提取尺码和存货情况
            match = re.search(r'([A-Za-z-]+)\s*(\d+)\s*(?:\((.*?)\))?$', size_info)
            if match:
                size = match.group(1) + " " + match.group(2)  # 组合尺码信息
                availability = match.group(3) if match.group(3) else "available"  # 如果没有括号内容，默认为available
                inventory_info[size] = availability
    return inventory_info


def print_inventory_info(inventory_info):
    for size, availability in inventory_info.items():
        print(f"尺码为：{size}，存货情况为：{availability}")


# session.get(url3, headers=headers, proxies=fiddler_proxies, verify=False)
# session.get(url2, headers=headers, proxies=non_proxies, verify=False)
# session.get(url3, headers=headers, proxies=clash_proxies)
session.get(url3, headers=headers, proxies=non_proxies)

text_frame = session.ele("text^Size").parent('tag:div')
good_items = text_frame.next('tag:div')
print("balenciaga - shoes - 库存监控")
good_name = session.ele("@class^ProductInformation88__name").text
print(f"产品名称: {good_name}")
inventory_info = parse_inventory_info(good_items)
print_inventory_info(inventory_info)

# print('request 开始')
# response = requests.get(url, headers=headers, proxies=non_proxies)
# print('正在输出请求结果')
# print(f"请求URL: {response.request.url}")
# print(f"请求方法: {response.request.method}")
# print(f"请求头: {response.request.headers}")
# print(f"响应状态码: {response.status_code}")
# print('响应内容:')
# print(response.text)
