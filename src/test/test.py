import json
import urllib.parse

from DrissionPage import SessionPage

from curl_cffi import requests

clash_proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}

ipcool_proxy = {'http': 'http://{}:{}@us.ipcool.net:2555'.format("13727744565_HK_0_0_session_0_1", "lin2225427"),
                'https': 'http://{}:{}@us.ipcool.net:2555'.format("13727744565_HK_0_0_session_0_1", "lin2225427")
}


import requests

cookies = {
    # 'bm_ss': 'ab8e18ef4e',
    'bm_s': 'YAAQEvAgF089vX2XAQAAkquphQOkaZhJPzAoCGDKStb5pSyke3vQaiWyWbjOP59TR11kZy6oOvpuPJllN2VB66/f1VZnCf4nHkfwHmlY7/iayrUK33FV5oHyGQlAaouj4xBpjHN9EIGjwdc7urZj4THeZy2cNg1wwaxPLKD/peE5x1Dx+EkqVzvG7BdMaIn6+PQXILhEei/o7N1wIYQB3Lk508fNGbilmdLuc+vbV5B+X8ilGdAXFSyHtDX/VixmKtObJKKB4mZPafhX56eHI143X06T9ZFR06fRFMVVERDdcBOyioxry6n6sIGaBintFDRF/kueHC1Qlih3v+butRXQofx7+6MSkJrr4BnuecAPpCHoBR34bVzmz7xcs6021x0M3QGVO5N75E2TUm4VoBi/rIoWtV2azn8sJ7j2V6A0dfhesgzS0cleUhPGH1wt9//hzRSIYkYrsI4Bp7+7j2ArhhHye+108GHF5rNSuzSQiL40NL1alOYIq1Rx/r970mE9ioxt0ZrIBl1ekYU59IaPTQgsUHruNpRdLEAnZF7OfGP0NWCR+YKwKM508Sw0',
    # 'bm_so': '75CB62297535151280F600141E1A9D87CDB83C51BCCA8D3B40889C14F89A909D~YAAQEvAgF1A9vX2XAQAAkquphQSi/caHF6/SIfQ+pGJyHfzMIJPNjjYhGJdH+YWVYMfGpMFJ5gIvOqcaIysqymmXlhuR9E9xVdxAsyrYsQGn/CtgXFqbmb4vm6s6cR11q9lZ2tvr0LKijoVUCOZQcFAQYMn7qFsr2CfIBu+BWCiXeil6NDGZDGbAwx1PRRoqDC7As9h+QqnT4R97BH0B47yWb1x5a2787x05kptRO4nuisbMFLo5VLv37R4js+Ds3ZoeXMzStPLuuCoouOv24FoYQnQhPS9f6HTShLj21VR2tJtytH5AMi5tC4zylbUJVDoF+1WOTzeArfWV0TM0ENMdID7ALkhFzo3ufu9iGgXdj+iaekONADSnFGpy6hwZMB71JAOZDwJK0OZR9nLxtT+iaRmjsAnzIVJDB0MqJCBGz/otFxXgIzRAoql7SwSvpiQGugEErYqa9tbxOWum',
    # 'bm_sz': '2700459199BE8E41246553A3622A92B3~YAAQEvAgF1E9vX2XAQAAkquphRx6v56pIx0OysRp42BMU94WcloZIGvUCzwgiZvFVY3NDuxHomKkO/JzsM6yY/bW5gLzNGDjwji1a5vWyIQUD0FQTZoDB6xMMrwbZN2iGtyEYydtg2B0AydZI7LKYcOPa2kGQ4dWwA3He7ZDpQzYMd9CTSyN26kNJolOwgXULx2XwwIahvqlTOlm2zY4hBr2IKPdEt9T/O+BLiDdrLxFLMi6HGGOwgmHe43gVVmKdVuQTA9RZDgChtdGztxN02ayEFNgG6XbciYaTH18Q4LCvY3POutz9VHrrbxKaB9OaG5X8/L2TTIxpGUPD33vuVVWM7GvUfbKgjmcjvPoGqPr7UZ9TeqT+26zjXvIGPbjrf1B00x8KeXn~4539448~3163441',
    'PIM-SESSION-ID': 'tkfWs9bxVmhMpDWL',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://www.mrporter.com/en-hk/mens/designer/rick-owens/shoes',
    'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    # 'service-worker-navigation-preload': 'true',
    # 'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
    # 'cookie': 'geoIP=CN; Y-City=CN-GD-GUANGZHOU; AKA_A2=A; bm_ss=ab8e18ef4e; _abck=0876D7B2D2C5A1114F629970AA5E6473~-1~YAAQEvAgF009vX2XAQAAkquphQ6EIjWKfQHczH5dDBHGIuJUCaHkuhZZQ2p3B4HwYR9Dsk1z3l1jhQERLYbsZY5Zje1b6NOYukFKRDdo2lgZ0swVzTbKSvzfIWO5JjvIRzmMWaJWxTa3cwycw2v6csRRmi7b4BwNKPTb4Wkq36Z65TcbORZGT+SEYMM8/PTgi5Ywl4oYfdO2v4Bx9jx5HMYqfWiz4h7Gvxc0r9C7gaTofg1B/QRekfXglnMD8UCnQ+0NgDnBLNKpwFYD71+TsL9w7YBXauICfYoXiF7MS0r869O63AoOfAhmTaan2kZtChACrj7w6+exobTJtBmr4BEU0mjsruF+3iv/UBqNvzMYdLq9WhGovxmJW0d7amp+bSGssfVzNbYIXT1fT5vvbzf2naSo3AXb1lXARuHJmMqHwzfQoGZJ15uLBRSBbN2eQScGQDiW96rR0bQg68tEhAm/drgV2dLlzyZCOUHJtTEJyy9WFg==~-1~-1~-1; bm_s=YAAQEvAgF089vX2XAQAAkquphQOkaZhJPzAoCGDKStb5pSyke3vQaiWyWbjOP59TR11kZy6oOvpuPJllN2VB66/f1VZnCf4nHkfwHmlY7/iayrUK33FV5oHyGQlAaouj4xBpjHN9EIGjwdc7urZj4THeZy2cNg1wwaxPLKD/peE5x1Dx+EkqVzvG7BdMaIn6+PQXILhEei/o7N1wIYQB3Lk508fNGbilmdLuc+vbV5B+X8ilGdAXFSyHtDX/VixmKtObJKKB4mZPafhX56eHI143X06T9ZFR06fRFMVVERDdcBOyioxry6n6sIGaBintFDRF/kueHC1Qlih3v+butRXQofx7+6MSkJrr4BnuecAPpCHoBR34bVzmz7xcs6021x0M3QGVO5N75E2TUm4VoBi/rIoWtV2azn8sJ7j2V6A0dfhesgzS0cleUhPGH1wt9//hzRSIYkYrsI4Bp7+7j2ArhhHye+108GHF5rNSuzSQiL40NL1alOYIq1Rx/r970mE9ioxt0ZrIBl1ekYU59IaPTQgsUHruNpRdLEAnZF7OfGP0NWCR+YKwKM508Sw0; bm_so=75CB62297535151280F600141E1A9D87CDB83C51BCCA8D3B40889C14F89A909D~YAAQEvAgF1A9vX2XAQAAkquphQSi/caHF6/SIfQ+pGJyHfzMIJPNjjYhGJdH+YWVYMfGpMFJ5gIvOqcaIysqymmXlhuR9E9xVdxAsyrYsQGn/CtgXFqbmb4vm6s6cR11q9lZ2tvr0LKijoVUCOZQcFAQYMn7qFsr2CfIBu+BWCiXeil6NDGZDGbAwx1PRRoqDC7As9h+QqnT4R97BH0B47yWb1x5a2787x05kptRO4nuisbMFLo5VLv37R4js+Ds3ZoeXMzStPLuuCoouOv24FoYQnQhPS9f6HTShLj21VR2tJtytH5AMi5tC4zylbUJVDoF+1WOTzeArfWV0TM0ENMdID7ALkhFzo3ufu9iGgXdj+iaekONADSnFGpy6hwZMB71JAOZDwJK0OZR9nLxtT+iaRmjsAnzIVJDB0MqJCBGz/otFxXgIzRAoql7SwSvpiQGugEErYqa9tbxOWum; bm_sz=2700459199BE8E41246553A3622A92B3~YAAQEvAgF1E9vX2XAQAAkquphRx6v56pIx0OysRp42BMU94WcloZIGvUCzwgiZvFVY3NDuxHomKkO/JzsM6yY/bW5gLzNGDjwji1a5vWyIQUD0FQTZoDB6xMMrwbZN2iGtyEYydtg2B0AydZI7LKYcOPa2kGQ4dWwA3He7ZDpQzYMd9CTSyN26kNJolOwgXULx2XwwIahvqlTOlm2zY4hBr2IKPdEt9T/O+BLiDdrLxFLMi6HGGOwgmHe43gVVmKdVuQTA9RZDgChtdGztxN02ayEFNgG6XbciYaTH18Q4LCvY3POutz9VHrrbxKaB9OaG5X8/L2TTIxpGUPD33vuVVWM7GvUfbKgjmcjvPoGqPr7UZ9TeqT+26zjXvIGPbjrf1B00x8KeXn~4539448~3163441; PIM-SESSION-ID=tkfWs9bxVmhMpDWL',
}

response = requests.get('https://www.mrporter.com/en-hk/mens/designer/rick-owens/shoes', cookies=cookies, headers=headers, proxies=ipcool_proxy)
# response = requests.get('https://www.mrporter.com/en-hk/mens/designer/rick-owens/shoes', cookies=cookies, headers=headers, proxies=ipcool_proxy)

# response = requests.get('https://www.mrporter.com/en-hk/mens/designer/rick-owens/shoes', cookies=cookies, headers=headers)

with open('cettire.json', 'w', encoding='utf-8') as file:
    file.write(response.text)

page = SessionPage()

page.get('cettire.json')
print(page.html)
