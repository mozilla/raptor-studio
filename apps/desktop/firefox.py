from selenium.webdriver import Firefox, FirefoxOptions
from os.path import curdir as here


class DesktopFirefox(object):
    def __init__(self, proxy, record, path, url="about:blank", certutil=None):
        self.proxy = proxy
        self.url = url
        self.record = record
        self.path = path
        self.screenshot = False

    def __enter__(self):
        self.start(self.url)

        return self

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

    def __exit__(self, *args):
        if args[0] == KeyboardInterrupt:
            if not self.screenshot:
                self.take_screenshot(self.record, self.path)
            self.driver.close()

    def take_screenshot(self, record, path):
        print("Getting Screenshot")
        sshot_suffix = "record" if record else "replay"
        now = datetime.now()

        # Save the screenshot "test-name_mode_timestamp" to project_dir/screen_captures
        ss_name = "%s_%s_%s.png" % (path.replace(".mp", ""), sshot_suffix, now.strftime("%m%d_%H%M%S"))
        path = os.path.join(here, "screen_captures", ss_name)
        self.driver.save_screenshot(path)
