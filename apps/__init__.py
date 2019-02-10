from android.firefox import AndroidFirefox
from desktop.firefox import DesktopFirefox as Firefox


class GeckoViewExample(AndroidFirefox):

    APP_NAME = "org.mozilla.geckoview_example"
    ACTIVITY_NAME = "GeckoViewActivity"
