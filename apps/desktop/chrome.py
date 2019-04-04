import os

from datetime import datetime
from selenium.webdriver import Chrome, ChromeOptions


class DesktopChrome(object):
    def __init__(self, proxy, record, path, url="about:blank", certutil=None):
        self.proxy = proxy
        self.url = url
        self.path = path
        self.record = record
        self.screenshot = False

    def start(self, url="about:blank"):
        options = ChromeOptions()
        options.add_argument("--proxy-server=127.0.0.1:8080")
        options.add_argument("--proxy-bypass-list=localhost;127.0.0.1")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--no-default-browser-check")

        self.driver = Chrome(options=options)
        self.driver.get(url)

    def __exit__(self, *args):
        if args[0] == KeyboardInterrupt:
            if not self.screenshot:
                self.take_screenshot(self.record, self.path)
            self.driver.close()

    def take_screenshot(self, record, path):
        print("Getting Screenshot")
        sshot_suffix = "record" if record else "replay"
        now = datetime.now()
        here = os.path.abspath(os.path.curdir)

        # Save the screenshot "test-name_mode_timestamp" to project_dir/screen_captures
        ss_name = "{}_{}_{}.png".format(path.replace(".mp", ""), sshot_suffix, now.strftime("%m%d_%H%M%S"))
        path = os.path.join(here, "screen_captures", ss_name)
        self.screenshot = self.driver.save_screenshot(path)
