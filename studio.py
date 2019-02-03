import os
import subprocess

import click
from mozdevice import ADBAndroid
from mozprofile import create_profile


@click.command()
@click.option("--record/--replay", default=False)
@click.option("--certutil", required=True, help="Path to certutil.")
@click.option("--url", default="about:blank", help="Site to load.")
@click.argument("path")
def cli(record, certutil, url, path):
    # create profile
    profile = create_profile("firefox")
    print("Created profile: {}".format(profile.profile))

    mitmproxy_home = os.path.join(os.path.expanduser("~"), ".mitmproxy")
    cert = os.path.join(mitmproxy_home, "mitmproxy-ca-cert.cer")

    # start mitmdump
    scripts = os.path.join(os.getcwd(), "scripts")
    mitmdump = os.path.join(os.getcwd(), "utils", "mitmdump")

    if record:
        command = [mitmdump, "--wfile", path]
    else:
        command = [
            mitmdump,
            "--script",
            os.path.join(scripts, "alternate-server-replay.py"),
            "--replay-kill-extra",
            "--server-replay",
            path,
        ]

    try:
        print(command)
        mitmdump_process = subprocess.Popen(command)

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
        device = ADBAndroid()
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
            "--marionette",
            "--es",
            "env0",
            "LOG_VERBOSE=1",
            "--es",
            "env1",
            "R_LOG_LEVEL=6",
        ]

        # start app
        app_name = "org.mozilla.geckoview_example"
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

        # wait for mitmdump to finish
        mitmdump_process.wait()
    finally:
        if mitmdump_process is None:
            mitmdump_process.terminate()
        exit(mitmdump_process.returncode)


if __name__ == "__main__":
    cli()
