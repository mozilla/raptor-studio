from selenium.webdriver import Chrome, ChromeOptions


class DesktopChrome(object):
    def __init__(self, proxy, *args):
        self.proxy = proxy

    def start(self, url="about:blank"):
        options = ChromeOptions()
        options.add_argument("--proxy-server=127.0.0.1:8080")
        options.add_argument("--proxy-bypass-list=localhost;127.0.0.1")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--no-default-browser-check")

        driver = Chrome(options=options)
        driver.get(url)
