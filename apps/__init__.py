from android.firefox import AndroidFirefox
from desktop.firefox import DesktopFirefox as Firefox
from desktop.chrome import DesktopChrome as Chrome


class GeckoViewExample(AndroidFirefox):

    APP_NAME = "org.mozilla.geckoview_example"
    ACTIVITY_NAME = "GeckoViewActivity"
