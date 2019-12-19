class AbstractDesktop(object):
    def __init__(self, certutil, binary=None):
        self.proxy = None
        self.binary = binary
        self.certutil = certutil
        self.driver = None

    def screen_shot(self, path):
        self.driver.save_screenshot(path)

    def stop(self):
        self.driver.quit()
