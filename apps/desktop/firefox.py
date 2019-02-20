from selenium.webdriver import Firefox, FirefoxOptions, FirefoxProfile


class DesktopFirefox(object):
    def __init__(self, proxy, *args):
        self.proxy = proxy

    def start(self, url="about:blank"):
        profile = FirefoxProfile()
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.http", "127.0.0.1")
        profile.set_preference("network.proxy.http_port", 8080)
        profile.set_preference("network.proxy.ssl", "127.0.0.1")
        profile.set_preference("network.proxy.ssl_port", 8080)

        options = FirefoxOptions()
        options.profile = profile

        driver = Firefox(options=options)
        driver.get(url)
