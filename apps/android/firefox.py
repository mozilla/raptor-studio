import os
import subprocess

from mozdevice import ADBAndroid
from mozprofile import create_profile


class AndroidFirefox(object):
    def __init__(self, proxy, certutil):
        self.proxy = proxy
        self.certutil = certutil
        self.device = ADBAndroid()

    def start(self, url="about:blank", record=None):
        # create profile
        profile = create_profile("firefox")
        print("Created profile: {}".format(profile.profile))

        # create certificate database
        certdb = "sql:{}/".format(profile.profile)
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

        # verify certificate is installed
        command = [self.certutil, "-d", certdb, "-L"]
        assert "mitmproxy-cert" in subprocess.check_output(command)

        # setup device
        self.device.shell("pm clear {}".format(self.APP_NAME))
        self.device.create_socket_connection("reverse", "tcp:8080", "tcp:8080")

        device_storage = "/sdcard/raptor"
        device_profile = os.path.join(device_storage, "profile")
        if self.device.is_dir(device_storage):
            self.device.rm(device_storage, recursive=True)
        self.device.mkdir(device_storage)
        self.device.mkdir(device_profile)

        userjs = os.path.join(profile.profile, "user.js")
        with open(userjs) as f:
            prefs = f.readlines()

        prefs = [p for p in prefs if "network.proxy" not in p]

        with open(userjs, "w") as f:
            f.writelines(prefs)

        profile.set_preferences(
            {
                "network.proxy.type": 1,
                "network.proxy.http": "127.0.0.1",
                "network.proxy.http_port": 8080,
                "network.proxy.ssl": "127.0.0.1",
                "network.proxy.ssl_port": 8080,
                "network.proxy.no_proxies_on": "localhost, 127.0.0.1",
            }
        )

        self.device.push(profile.profile, device_profile)
        self.device.chmod(device_storage, recursive=True)

        app_args = [
            "-profile",
            device_profile,
            "--marionette",
            "--es",
            "env0",
            "LOG_VERBOSE=1",
            "--es",
            "env1",
            "R_LOG_LEVEL=6",
        ]

        # start app
        self.device.stop_application(self.APP_NAME)
        self.device.launch_activity(
            self.APP_NAME,
            self.ACTIVITY_NAME,
            extra_args=app_args,
            url=url,
            e10s=True,
            fail_if_running=False,
        )

    def take_screenshot(self, record, path):
        print("Getting Screenshot")
        self.device.shell("screencap -p /sdcard/screen.png")
        sshot_suffix = "record" if record else "replay"
        self.device.pull("/sdcard/screen.png", "{}_{}.png".format(path, sshot_suffix))
        self.device.rm("/sdcard/screen.png")
