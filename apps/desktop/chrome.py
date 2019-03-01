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

        self.driver = Chrome(options=options)
        self.driver.get(url)

    def take_screenshot(self, record, path):
        print("Getting Screenshot")
        sshot_suffix = "record" if record else "replay"
        self.driver.save_screenshot("{}_{}.png".format(path, sshot_suffix))
