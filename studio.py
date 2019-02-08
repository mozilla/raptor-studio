import os
import sys
import subprocess

import click
import click_config_file

from mozdevice import ADBAndroid
from mozprocess import ProcessHandler

from mozprofile import create_profile

from selenium import webdriver
from selenium.webdriver import FirefoxProfile


@click.command()
@click.option("--record/--replay", default=False)
@click.option("--certutil", required=True, help="Path to certutil.")
@click.option("--deterministic", required=True, help="Use deterministic JS in the recording")
@click.option("--url", default="about:blank", help="Site to load.")

@click.option("--browser_name", default="geckoview_example", help="Browser to start.")
@click.option("--browser_path", help="Path to local browser.")

@click.argument("path")
@click_config_file.configuration_option()
def cli(record, certutil, deterministic, url, browser_name, browser_path, path):
    # create profile
    profile = create_profile("firefox")
    print("Created profile: {}".format(profile.profile))

    mitmproxy_home = os.path.join(os.path.expanduser("~"), ".mitmproxy")
    cert = os.path.join(mitmproxy_home, "mitmproxy-ca-cert.cer")

    driver = None

    # start mitmdump
    scripts = os.path.join(os.getcwd(), "scripts")

    if "linux" in sys.platform:
        mitmdump = os.path.join(os.getcwd(), "utils", "mitmdump-linux")
    elif "darwin" in sys.platform:
        mitmdump = os.path.join(os.getcwd(), "utils", "mitmdump-osx")
    elif "win" in sys.platform:
        mitmdump = os.path.join(os.getcwd(), "utils", "mitmdump-win.exe")

    if record:
        if deterministic:
            command = [mitmdump,"--wfile", path, "--script", "".join([os.path.join(scripts, "inject-deterministic-js.py")])]
        else:
            command = [mitmdump, "--wfile", path]
    else:
        command = [
            "mitmdump",
            "--replay-kill-extra",
            "--script",
            " ".join([os.path.join(scripts, "alternate-server-replay.py"), path]),
        ]

    try:
        print(" ".join(command))
        mitmdump_process = ProcessHandler(command)

        mitmdump_process.run()

        if browser_name == "geckoview_example":

            if 'mozilla-central/obj' in certutil:
                os.environ['LD_LIBRARY_PATH'] = os.path.dirname(certutil)

            # create certificate database
            certdb = "sql:{}/".format(profile.profile)
            print("Creating certificate database")
            command = [certutil, "-N", "-v", "-d", certdb, "--empty-password"]
            subprocess.call(command)

            # install mitmproxy certificate
            command = [
                certutil,
                "-A",
                "-d",
                certdb,
                "-n",
                "mitmproxy-cert",
                "-t",
                "TC,,",
                "-a",
                "-i",
                cert,
            ]
            print("Installing {} into certificate database".format(cert))
            subprocess.call(command)

            # verify certificate is installed
            command = [certutil, "-d", certdb, "-L"]
            assert "mitmproxy-cert" in subprocess.check_output(command)

            # setup device
            app_name = "org.mozilla.geckoview_example"
            device = ADBAndroid()
            device.shell("pm clear {}".format(app_name))
            device.create_socket_connection("reverse", "tcp:8080", "tcp:8080")

            device_storage = "/sdcard/raptor"
            device_profile = os.path.join(device_storage, "profile")
            if device.is_dir(device_storage):
                device.rm(device_storage, recursive=True)
            device.mkdir(device_storage)
            device.mkdir(device_profile)

            userjs = os.path.join(profile.profile, "user.js")
            with open(userjs) as f:
                prefs = f.readlines()

            prefs = [p for p in prefs if "network.proxy" not in p]

            with open(userjs, "w") as f:
                f.writelines(prefs)

            proxy = {
                "network.proxy.type": 1,
                "network.proxy.http": "127.0.0.1",
                "network.proxy.http_port": 8080,
                "network.proxy.ssl": "127.0.0.1",
                "network.proxy.ssl_port": 8080,
                "network.proxy.no_proxies_on": "localhost, 127.0.0.1",
            }
            profile.set_preferences(proxy)

            device.push(profile.profile, device_profile)
            device.chmod(device_storage, recursive=True)

            app_args = [
                "-profile",
                device_profile,
                "--es",
                "env0",
                "LOG_VERBOSE=1",
                "--es",
                "env1",
                "R_LOG_LEVEL=6",
            ]

            # start app
            activity_name = "GeckoViewActivity"
            device.stop_application(app_name)
            device.launch_activity(
                app_name,
                activity_name,
                extra_args=app_args,
                url=url,
                e10s=True,
                fail_if_running=False,
            )
        elif browser_name == "firefox":
            firefox_profile = FirefoxProfile()

            # Specify to use manual proxy configuration.
            firefox_profile.set_preference('network.proxy.type', 1)
            # Set the host/port.
            firefox_profile.set_preference('network.proxy.http',"127.0.0.1")
            firefox_profile.set_preference('network.proxy.http_port', 8080)
            firefox_profile.set_preference('network.proxy.ssl', "127.0.0.1")
            firefox_profile.set_preference('network.proxy.ssl_port', 8080)

            if browser_path is None:
                driver = webdriver.Firefox(firefox_profile=firefox_profile)
            else:
                driver = webdriver.Firefox(firefox_profile=firefox_profile, firefox_binary=browser_path)

            driver.get(url)

        # # wait for mitmdump to finish
        # mitmdump_process.wait()
        input("What is your name? ")

    finally:
        if not driver is None:
            driver.quit()

        if mitmdump_process is None:
            mitmdump_process.kill()

        exit(mitmdump_process.returncode)


if __name__ == "__main__":
    cli()
