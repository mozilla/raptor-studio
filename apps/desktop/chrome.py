
from selenium import webdriver
from selenium.webdriver import Chrome


class DesktopChrome(object):
    def __init__(self, proxy, *args):
        self.proxy = proxy

    def start(self, url="about:blank"):
        print("START")

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=127.0.0.1:8080')
        chrome_options.add_argument('--proxy-bypass-list=localhost;127.0.0.1')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--no-default-browser-check')

        driver = Chrome(chrome_options=chrome_options)

        driver.get(url)
