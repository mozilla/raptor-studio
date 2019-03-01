from selenium.webdriver import Firefox, FirefoxOptions


class DesktopFirefox(object):
    def __init__(self, proxy, *args):
        self.proxy = proxy

    def start(self, url="about:blank"):
        options = FirefoxOptions()
        options.set_preference("network.proxy.type", 1)
        options.set_preference("network.proxy.http", "127.0.0.1")
        options.set_preference("network.proxy.http_port", 8080)
        options.set_preference("network.proxy.ssl", "127.0.0.1")
        options.set_preference("network.proxy.ssl_port", 8080)
        options.set_preference("security.csp.enable", True)

        self.driver = Firefox(options=options)
        self.driver.get(url)

    def take_screenshot(self, record, path):
        print("Getting Screenshot")
        sshot_suffix = "record" if record else "replay"
        self.driver.save_screenshot("{}_{}.png".format(path, sshot_suffix))
