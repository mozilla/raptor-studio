import os
import sys
import subprocess


class MITMProxy(object):
    def __init__(self, path, record=True):
        self.path = path
        self.record = record
        home = os.path.join(os.path.expanduser("~"), ".mitmproxy")
        self.cert = os.path.join(home, "mitmproxy-ca-cert.cer")
        self.scripts = os.path.join(os.getcwd(), "scripts")

    @property
    def binary(self):
        if "linux" in sys.platform:
            name = "mitmdump-linux"
        elif "darwin" in sys.platform:
            name = "mitmdump-osx"
        elif "win" in sys.platform:
            name = "mitmdump-win.exe"
        return os.path.join(os.getcwd(), "utils", name)

    def __enter__(self):
        if self.record:
            command = [
                self.binary,
                "--wfile",
                self.path,
                "--script",
                " ".join([os.path.join(self.scripts, "inject-deterministic.py")]),
            ]
        else:
            command = [
                self.binary,
                "--replay-kill-extra",
                "--script",
                " ".join(
                    [
                        os.path.join(self.scripts, "alternate-server-replay.py"),
                        self.path,
                    ]
                ),
            ]
        self.process = subprocess.Popen(command)
        return self

    def __exit__(self, *args):
        try:
            self.process.wait()
        finally:
            self.process.terminate()
