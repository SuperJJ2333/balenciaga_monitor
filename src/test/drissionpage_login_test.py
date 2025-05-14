from DrissionPage import ChromiumPage, ChromiumOptions

co = ChromiumOptions()
browser_path = 'D:\Software\chrome64_107.0.5304.122\chrome\Chrome-bin\chrome.exe'
co.set_browser_path(browser_path)
co.auto_port()
page = ChromiumPage(co)

page.get('http://www.baidu.com')
