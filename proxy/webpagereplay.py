import os
import signal
import subprocess
import sys

from proxy.mitmproxy import MITMProxy404

dirname = os.path.dirname(__file__)


class WebPageReplay(object):
    def __init__(self, path, mode="record"):
        self.path = path
        self.mode = mode
        self.binary_path = os.path.join(dirname, "utils", "wpr")
        self.scripts = os.path.join(dirname, "scripts")

        self.deterministic_js_path = os.path.join(
            self.scripts, "catapult/deterministic.js"
        )

        self.port_fw = MITMProxy404(path=self.path, mode="forward")
        self.certificate_path = os.path.join(self.port_fw.mitm_home, "mitmproxy-ca.pem")

    def __enter__(self):

        self.port_fw.start()
        print("Starting WebPageReplay")
        print(" ".join(self.command()))

        logfile = open(os.path.join(dirname, "WebPageReplay.log"), "w")
        self.process = subprocess.Popen(self.command(), stdout=logfile, stderr=logfile)

        return self.port_fw

    def __exit__(self, *args):
        try:
            self.process.wait()
        finally:
            self.process.send_signal(signal.SIGINT)
            self.port_fw.stop()

    @property
    def binary(self):
        if "linux" in sys.platform:
            name = "wpr-linux"
        elif "darwin" in sys.platform:
            name = "wpr-osx"
        elif "win" in sys.platform:
            name = "wpr-win.exe"
        return os.path.join(self.binary_path, name)

    def command(self):

        command = [
            self.binary,
            "--https_cert_file",
            self.certificate_path,
            "--https_key_file",
            self.certificate_path,
            "--inject_scripts",
            self.deterministic_js_path,
            "--http_port",
            "8081",
            "--https_port",
            "8082",
            self.path,
        ]
        if self.mode is "record":
            command.insert(1, "record")
        elif self.mode is "replay":
            command.insert(1,"replay", "--serve_response_in_chronological_sequence")
        return command
