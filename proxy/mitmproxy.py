import os
import signal
import subprocess
import sys

dirname = os.path.dirname(__file__)


class MITMProxyBase(object):
    def __init__(self, path, version, mode):
        self.path = path
        self.mode = mode
        self.version = version
        self.mitm_home = os.path.join(os.path.expanduser("~"), ".mitmproxy")
        self.cert = os.path.join(self.mitm_home, "mitmproxy-ca-cert.cer")
        self.scripts = os.path.join(dirname, "scripts")
        self.binary_path = os.path.join(dirname, "utils", "mitm%s" % self.version)

    @property
    def binary(self):
        if "linux" in sys.platform:
            name = "mitmdump-linux"
        elif "darwin" in sys.platform:
            name = "mitmdump-osx"
        elif "win" in sys.platform:
            name = "mitmdump-win.exe"
        return os.path.join(self.binary_path, name)

    def start(self):
        print("Starting MitmProxy")
        print(" ".join(self.command()))

        logfile = open(os.path.join(dirname, "mitmproxy.log"), "w")

        self.process = subprocess.Popen(self.command(), stdout=logfile, stderr=logfile)

        return self.process

    def stop(self):
        self.process.send_signal(signal.SIGINT)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        try:
            self.process.wait()
        finally:
            self.stop()


class MITMProxy202(MITMProxyBase):
    def __init__(self, path, mode="record"):
        MITMProxyBase.__init__(self, path=path, version="2.0.2", mode=mode)

    def command(self):
        if self.mode is "record":
            command = [
                self.binary,
                "--wfile",
                self.path,
                "--script",
                os.path.join(self.scripts, "inject_deterministic.py"),
                "--script",
                os.path.join(self.scripts, "http_protocol_extractor.py"),
            ]
        elif self.mode is "replay":
            command = [
                self.binary,
                "--replay-kill-extra",
                "--script",
                " ".join(
                    [
                        os.path.join(self.scripts, "alternate-server-replay-2.0.2.py"),
                        self.path,
                    ]
                ),
            ]
        else:
            raise Exception("Unknown proxy mode! Proxy mode: %s" % self.mode)
        return command


class MITMProxy404(MITMProxyBase):
    def __init__(self, path, mode="record"):
        MITMProxyBase.__init__(self, path=path, version="4.0.4", mode=mode)

    def command(self):
        if self.mode is "record":
            command = [
                self.binary,
                "--save-stream-file",
                self.path,
                "--set",
                "websocket=false",
                "--scripts",
                os.path.join(self.scripts, "inject_deterministic.py"),
                "--scripts",
                os.path.join(self.scripts, "http_protocol_extractor.py"),
            ]
        elif self.mode is "replay":
            command = [
                self.binary,
                "--scripts",
                os.path.join(self.scripts, "alternate-server-replay-4.0.4.py"),
                "--set",
                "websocket=false",
                "--set",
                "upstream_cert=false",
                "--set",
                "server_replay_files={}".format(self.path),
            ]
        elif self.mode is "forward":
            command = [
                self.binary,
                "--listen-host",
                "127.0.0.1",
                "--listen-port",
                "8080",
                "--scripts",
                os.path.join(self.scripts, "mitm_port_fw.py"),
                "--set",
                "portmap=80:8081,443:8082",
                # For more information see ssl_insecure and ssl_verify_upstream_trusted_ca on
                # https://docs.mitmproxy.org/stable/concepts-options/
                # '--ssl-insecure',
                "--set",
                "ssl_verify_upstream_trusted_ca=%s"
                % os.path.join(self.mitm_home, "mitmproxy-ca.pem"),
            ]
        else:
            raise Exception("Unknown proxy mode! Proxy mode: %s" % self.mode)

        return command
