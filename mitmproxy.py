import os
import subprocess


class MITMProxy(object):
    def __init__(self, path, record=True):
        self.binary = "mitmdump"
        self.path = path
        self.record = record
        home = os.path.join(os.path.expanduser("~"), ".mitmproxy")
        self.cert = os.path.join(home, "mitmproxy-ca-cert.cer")
        self.scripts = os.path.join(os.getcwd(), "scripts")

    def __enter__(self):
        subprocess.call([self.binary, "--version"])

        if self.record:
            command = [
                self.binary,
                "--save-stream-file",
                self.path,
                "--scripts",
                os.path.join(self.scripts, "inject-deterministic.py"),
            ]
        else:
            command = [
                self.binary,
                "--scripts",
                os.path.join(self.scripts, "serverplayback404.py"),
                "--set",
                f"server_replay={self.path}",
                "--set",
                f"server_replay_404_extra=true",
            ]
        self.process = subprocess.Popen(command)
        return self

    def __exit__(self, *args):
        try:
            self.process.wait()
        finally:
            self.process.terminate()
