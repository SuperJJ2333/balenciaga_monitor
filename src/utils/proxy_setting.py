import os
import string


def create_proxyauth_extension(proxy_host, proxy_port, proxy_username, proxy_password, scheme='http', plugin_folder=None):
    if plugin_folder is None:
        plugin_folder = 'kdl_Chromium_Proxy'  # 插件文件夹名称
    if not os.path.exists(plugin_folder):
        os.makedirs(plugin_folder)
    manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "kdl_Chromium_Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking",
                "browsingData"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
    """
    background_js = string.Template("""
        var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "${scheme}",
                host: "${host}",
                port: parseInt(${port})
            },
            bypassList: []
            }
        };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "${username}",
                    password: "${password}"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
        );
    """).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    with open(os.path.join(plugin_folder, "manifest.json"), "w") as manifest_file:
        manifest_file.write(manifest_json)
    with open(os.path.join(plugin_folder, "background.js"), "w") as background_file:
        background_file.write(background_js)
    return plugin_folder


def set_switchy_omega(page):
    """

    :param page:

    :return:
    """
    server_ip = 'us.ipcool.net'
    passport = '2555'
    username = "13727744565_187_0_0_session_5_1"
    password = "lin2225427"

    page.get("chrome-extension://padekgcemlokbadohgkifijomclgjgif/options.html#!/profile/proxy")

    page.ele('x://input[@ng-model="proxyEditors[scheme].host"]').clear().input(server_ip)
    page.ele('x://input[@ng-model="proxyEditors[scheme].port"]').clear().input(passport)

    page.ele('x://button[@ng-click="editProxyAuth(scheme)"]').click(by_js=True)

    page.ele('x://input[@ng-model="model"]').clear().click(by_js=True).input(username)
    page.ele('x://input[@ng-model="auth.password"]').clear().click(by_js=True).input(password)

    page.ele('x://button[@ng-disabled="!authForm.$valid"]').click(by_js=True)
    page.ele('x://a[@ng-click="applyOptions()"]').click(by_js=True)

    page.get('chrome-extension://padekgcemlokbadohgkifijomclgjgif/options.html#!/ui')

    page.ele('x://button[@class="btn btn-default dropdown-toggle"]').click(by_js=True)

