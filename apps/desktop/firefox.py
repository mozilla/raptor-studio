from mozversion import mozversion
from selenium.webdriver import Firefox, FirefoxOptions

from apps.desktop import AbstractDesktop


class DesktopFirefox(AbstractDesktop):
    def start(self, url="about:blank"):
        options = FirefoxOptions()
        options.set_preference("network.proxy.type", 1)
        options.set_preference("network.proxy.http", "127.0.0.1")
        options.set_preference("network.proxy.http_port", 8080)
        options.set_preference("network.proxy.ssl", "127.0.0.1")
        options.set_preference("network.proxy.ssl_port", 8080)
        options.set_preference("security.csp.enable", True)

        self.driver = Firefox(options=options, firefox_binary=self.binary)
        self.driver.get(url)

    def app_information(self):
        app_information = {}
        if self.binary:
            app_information = mozversion.get_version(binary=self.binary)
        else:
            app_information["browserName"] = self.driver.capabilities["browserName"]
            app_information["browserVersion"] = self.driver.capabilities[
                "browserVersion"
            ]
            app_information["buildID"] = self.driver.capabilities["moz:buildID"]

        return app_information
