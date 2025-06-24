from DrissionPage import ChromiumPage, ChromiumOptions


url = "https://www.mrporter.com/en-hk/mens/designer/rick-owens/shoes"
options = ChromiumOptions()
options.auto_port()
# options.set_proxy('http://127.0.0.1:7890')
page = ChromiumPage(options)
page.get(url)
print(page.html)


