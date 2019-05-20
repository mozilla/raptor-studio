import os
import subprocess

from mozdevice import ADBAndroid
from mozprofile import create_profile


class AbstractAndroidFirefox(object):
    def __init__(self, proxy, certutil):
        self.proxy = proxy
        self.certutil = certutil
        self.app_args = [
            "--marionette",
            "--es",
            "env0",
            "LOG_VERBOSE=1",
            "--es",
            "env1",
            "R_LOG_LEVEL=6",
        ]
        self.profile = None

    def set_profile(self):
        self.profile = create_profile("firefox")
        print("Created profile: {}".format(self.profile.profile))

    def create_certificate(self):
        certdb = "sql:{}/".format(self.profile.profile)
        print("Creating certificate database")
        command = [self.certutil, "-N", "-v", "-d", certdb, "--empty-password"]
        subprocess.call(command)

        # install mitmproxy certificate
        command = [
            self.certutil,
            "-A",
            "-d",
            certdb,
            "-n",
            "mitmproxy-cert",
            "-t",
            "TC,,",
            "-a",
            "-i",
            self.proxy.cert,
        ]
        print("Installing {} into certificate database".format(self.proxy.cert))
        subprocess.call(command)

        command = [self.certutil, "-d", certdb, "-L"]
        assert "mitmproxy-cert" in subprocess.check_output(command)

    def setup_device(self):
        self.device = ADBAndroid()
        self.device.shell("pm clear {}".format(self.APP_NAME))
        self.device.create_socket_connection("reverse", "tcp:8080", "tcp:8080")

        device_storage = "/sdcard/raptor"
        device_profile = os.path.join(device_storage, "profile")
        if self.device.is_dir(device_storage):
            self.device.rm(device_storage, recursive=True)
        self.device.mkdir(device_storage)
        self.device.mkdir(device_profile)
        self.app_args.extend(["-profile", device_profile])

        userjs = os.path.join(self.profile.profile, "user.js")
        with open(userjs) as f:
            prefs = f.readlines()

        prefs = [p for p in prefs if "network.proxy" not in p]

        with open(userjs, "w") as f:
            f.writelines(prefs)

        self.profile.set_preferences(
            {
                "network.proxy.type": 1,
                "network.proxy.http": "127.0.0.1",
                "network.proxy.http_port": 8080,
                "network.proxy.ssl": "127.0.0.1",
                "network.proxy.ssl_port": 8080,
                "network.proxy.no_proxies_on": "localhost, 127.0.0.1",
            }
        )

        self.device.push(self.profile.profile, device_profile)
        self.device.chmod(device_storage, recursive=True)

    def run_android_app(self, url):
        raise NotImplementedError


    def start(self, url="about:blank"):
        # create profile
        self.set_profile()
        # create certificate database
        self.create_certificate()
        # setup device
        self.setup_device()
        # start app
        self.run_android_app(url)


class GeckoViewExample(AbstractAndroidFirefox):
    APP_NAME = "org.mozilla.geckoview_example"
    ACTIVITY_NAME = "GeckoViewActivity"

    def run_android_app(self, url):
        self.device.stop_application(self.APP_NAME)
        self.device.launch_activity(
            self.APP_NAME,
            self.ACTIVITY_NAME,
            extra_args=self.app_args,
            url=url,
            e10s=True,
            fail_if_running=False
        )


class Fenix(AbstractAndroidFirefox):
    APP_NAME = "org.mozilla.fenix.raptor"
    ACTIVITY_NAME = "org.mozilla.fenix.browser.BrowserPerformanceTestActivity"
    INTENT = "android.intent.action.VIEW"

    def run_android_app(self, url):
        extras = {
            "args": " ".join(self.app_args),
            "use_multiprocess": True
        }

        # start app
        self.device.stop_application(self.APP_NAME)
        self.device.launch_application(
            self.APP_NAME,
            self.ACTIVITY_NAME,
            self.INTENT,
            extras=extras,
            url=url,
            fail_if_running=False
        )


class Fennec(AbstractAndroidFirefox):
    APP_NAME = "org.mozilla.fennec_aurora"
    ACTIVITY_NAME = "org.mozilla.gecko.BrowserApp"
    INTENT = "android.intent.action.VIEW"

    def run_android_app(self, url):
        self.device.stop_application(self.APP_NAME)
        self.device.launch_fennec(
            self.APP_NAME,
            extra_args=self.app_args,
            url=url,
            fail_if_running=False
        )


class RefBrow(AbstractAndroidFirefox):
    APP_NAME = "org.mozilla.reference.browser"
    ACTIVITY_NAME = "org.mozilla.reference.browser.BrowserTestActivity"
    INTENT = "android.intent.action.MAIN"

    def run_android_app(self, url):
        extras = {
            "args": " ".join(self.app_args),
            "use_multiprocess": True
        }

        # start app
        self.device.stop_application(self.APP_NAME)
        self.device.launch_application(
            self.APP_NAME,
            self.ACTIVITY_NAME,
            self.INTENT,
            extras=extras,
            url=url,
            fail_if_running=False
        )
