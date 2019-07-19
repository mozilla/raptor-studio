from selenium.webdriver import Chrome, ChromeOptions

from apps.desktop import AbstractDesktop


class DesktopChrome(AbstractDesktop):
    def start(self, url="about:blank"):
        options = ChromeOptions()
        options.add_argument("--proxy-server=127.0.0.1:8080")
        options.add_argument("--proxy-bypass-list=localhost;127.0.0.1")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--no-default-browser-check")

        self.driver = Chrome(options=options)
        self.driver.get(url)

    def app_information(self):
        app_information = {}
        app_information["browserName"] = self.driver.capabilities["browserName"]
        app_information["browserVersion"] = self.driver.capabilities["browserVersion"]
        return app_information
