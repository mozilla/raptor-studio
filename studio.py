import hashlib
import json
import os
import platform
import time
from zipfile import ZipFile

import click
import click_config_file
from mozdevice import ADBAndroid
from tldextract import tldextract

from apps.android.firefox import (
    GeckoViewExample,
    Fenix,
    Fennec,
    RefBrow,
    AbstractAndroidFirefox,
)
from apps.desktop.chrome import DesktopChrome as Chrome
from apps.desktop.firefox import DesktopFirefox as Firefox
from proxy.mitmproxy import MITMProxy202, MITMProxy404
from proxy.webpagereplay import WebPageReplay

APPS = {
    "Firefox": Firefox,
    "GeckoViewExample": GeckoViewExample,
    "Fenix": Fenix,
    "Fennec": Fennec,
    "Refbrow": RefBrow,
    "Chrome": Chrome,
}

PROXYS = {"mitm2": MITMProxy202, "mitm4": MITMProxy404, "wpr": WebPageReplay}

RECORD_TIMEOUT = 60


class Mode:
    def __init__(self, app, binary, proxy, certutil, path, sites, url):
        self.app = app
        self.binary = binary
        self.proxy = proxy
        self.certutil = certutil
        self.path = path
        self.sites_path = sites
        self.url = url
        self.information = {}

    def _digest_file(self, file, algorithm):
        """I take a file like object 'f' and return a hex-string containing
        of the result of the algorithm 'a' applied to 'f'."""
        with open(file, "rb") as f:
            h = hashlib.new(algorithm)
            chunk_size = 1024 * 10
            data = f.read(chunk_size)
            while data:
                h.update(data)
                data = f.read(chunk_size)
            name = repr(f.name) if hasattr(f, "name") else "a file"
            print("hashed %s with %s to be %s" % (name, algorithm, h.hexdigest()))
            return h.hexdigest()

    def replaying(self):
        with PROXYS[self.proxy](path=self.path, mode="replay") as proxy_service:
            app_service = APPS[self.app](proxy_service, self.certutil)
            app_service.start(self.url)

    def recording(self):
        print("Starting record mode!!!")
        if not os.path.exists(self.path):
            print("Creating recording path: %s" % self.path)
            os.mkdir(self.path)

        for site in self.parse_sites_json():
            if not os.path.exists(os.path.dirname(site["recording_path"])):
                print(
                    "Creating recording path: %s"
                    % os.path.dirname(site["recording_path"])
                )
                os.mkdir(os.path.dirname(site["recording_path"]))

            with PROXYS[self.proxy](
                path=site["recording_path"], mode="record"
            ) as proxy_service:
                app_service = APPS[self.app](proxy_service, self.certutil, self.binary)
                print("Recording %s..." %site["url"])
                app_service.start(site["url"])

                if not site.get("login", None):
                    print("Waiting %s for the site to load..." % RECORD_TIMEOUT)
                    time.sleep(RECORD_TIMEOUT)
                else:
                    time.sleep(5)
                    raw_input("Do user input and press <Return>")

                app_service.screen_shot(site["screen_shot_path"])
                self.information["app_info"] = app_service.app_information()
                app_service.stop()

            self.update_json_information(site)
            self.generate_zip_file(site)
            self.generate_manifest_file(site)

    def parse_sites_json(self):
        print("Parsing sites json")
        sites = []
        if self.sites_path is not None:
            with open(self.sites_path, "r") as sites_file:
                sites_json = json.loads(sites_file.read())

            self.information["app"] = self.app.lower()

            self.information["platform"] = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            }

            platform_name = platform.system().lower()

            if issubclass(APPS[self.app], AbstractAndroidFirefox):
                device = ADBAndroid()

                for property in ["ro.product.model", "ro.build.user", "ro.build.version.release"]:
                    self.information[property] = device.shell_output("getprop {}".format(property))

                platform_name = "".join(
                    e for e in self.information["ro.product.model"] if e.isalnum()
                ).lower()

            for site in sites_json:
                site["domain"] = tldextract.extract(site["url"]).domain
                name = [self.proxy,
                        platform_name,
                        "gve" if self.app == "GeckoViewExample" else self.app.lower(),
                        site["domain"]]
                label = site.get("label")
                if label:
                    name.append(label)
                name = "-".join(name)

                site["path"] = os.path.join(self.path, name, name)
                site["name"] = name

                site["recording_path"] = "%s.mp" % site["path"]
                site["json_path"] = "%s.json" % site["path"]
                site["screen_shot_path"] = "%s.png" % site["path"]
                site["zip_path"] = os.path.join(self.path, "%s.zip" % site["name"])
                site["manifest_path"] = os.path.join(
                    self.path, "%s.manifest" % site["name"]
                )

                sites.append(site)
        else:
            raise Exception("No site JSON file found!!!")

        return sites

    def update_json_information(self, site):
        time.sleep(3)
        print("Updating json with recording information")

        with open(site["json_path"], "r") as f:
            json_data = json.loads(f.read())

        self.information["proxy"] = self.proxy

        self.information["url"] = site["url"]
        self.information["domain"] = tldextract.extract(site["url"]).domain

        self.information["label"] = site.get("label")

        json_data["info"] = self.information
        with open(site["json_path"], "w") as f:
            f.write(json.dumps(json_data))

    def generate_zip_file(self, site):
        print("Generating zip file")

        with ZipFile(site["zip_path"], "w") as zf:
            zf.write(site["recording_path"], os.path.basename(site["recording_path"]))
            zf.write(site["json_path"], os.path.basename(site["json_path"]))
            zf.write(
                site["screen_shot_path"], os.path.basename(site["screen_shot_path"])
            )

    def generate_manifest_file(self, site):
        print("Generating manifest file")
        with open(site["manifest_path"], "w") as f:
            manifest = {}
            manifest["size"] = os.path.getsize(site["zip_path"])
            manifest["visibility"] = "public"
            manifest["digest"] = self._digest_file(site["zip_path"], "sha512")
            manifest["algorithm"] = "sha512"
            manifest["filename"] = os.path.basename(site["zip_path"])
            manifest["unpack"] = True
            f.write(json.dumps([manifest]))


@click.command()
@click.option(
    "--app", required=True, type=click.Choice(APPS.keys()), help="App type to launch."
)
@click.option(
    "--binary",
    default=None,
    help="Path to the app to launch. If Android app path to APK file to install ",
)
@click.option(
    "--proxy",
    required=True,
    type=click.Choice(PROXYS.keys()),
    help="Proxy Service to use.",
)
@click.option("--record/--replay", default=False)
@click.option(
    "--certutil", help="Path to certutil. Note: Only when recording and Only on Android"
)
@click.option(
    "--sites",
    help="JSON file containing the websites information we want ro record. Note: Only when recording",
)
@click.argument("path", default="Recordings")
@click.option(
    "--url", default="about:blank", help="Site to load. Note: Only when replaying."
)
@click_config_file.configuration_option()
def cli(app, binary, proxy, record, certutil, sites, path, url):
    mode = Mode(app, binary, proxy, certutil, path, sites, url)
    if record:
        mode.recording()
    else:
        mode.replaying()


if __name__ == "__main__":
    cli()
