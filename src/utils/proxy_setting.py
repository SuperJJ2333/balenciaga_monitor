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

