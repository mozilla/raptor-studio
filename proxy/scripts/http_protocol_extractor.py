import datetime
import hashlib
import json
import os
import urllib
from urllib import parse

from mitmproxy import ctx


class HttpProtocolExtractor:
    def __init__(self):
        self.request_protocol = {}
        self.hashes = []
        self.request_count = 0

        ctx.log.info("Init Http Protocol extractor JS")

    def _hash(self, flow):
        """
            Calculates a loose hash of the flow request.
        """
        r = flow.request

        # unquote url
        # See Bug 1509835
        _, _, path, _, query, _ = urllib.parse.urlparse(parse.unquote(r.url))
        queriesArray = urllib.parse.parse_qsl(query, keep_blank_values=True)

        key = [str(r.port), str(r.scheme), str(r.method), str(path)]
        key.append(str(r.raw_content))
        key.append(r.host)

        for p in queriesArray:
            key.append(p[0])
            key.append(p[1])

        return hashlib.sha256(repr(key).encode("utf8", "surrogateescape")).digest()

    def response(self, flow):
        self.request_count += 1
        hash = self._hash(flow)
        if not hash in self.hashes:
            self.hashes.append(hash)

        if flow.type == "websocket":
            ctx.log.info("Response is a WebSocketFlow. Bug 1559117")
        else:
            ctx.log.info(
                "Response using protocol: %s" % flow.response.data.http_version
            )
            self.request_protocol[
                urllib.parse.urlparse(flow.request.url).netloc
            ] = flow.response.data.http_version.decode("utf-8")

    def done(self):
        output_json = {}

        output_json["recording_date"] = str(datetime.datetime.now())
        output_json["http_protocol"] = self.request_protocol
        output_json["recorded_requests"] = self.request_count
        output_json["recorded_requests_unique"] = len(self.hashes)

        try:
            # Mitmproxy 4.0.4
            recording_file_name = ctx.options.save_stream_file
        except:
            # Mitmproxy 2.0.2
            recording_file_name = ctx.master.options.streamfile

        json_file_name = os.path.join(
            os.path.dirname(recording_file_name),
            "%s.json" % os.path.basename(recording_file_name).split(".")[0],
        )
        print("Saving response protocol data to %s" % json_file_name)
        with open(json_file_name, "w") as file:
            file.write(json.dumps(output_json))


addons = [HttpProtocolExtractor()]


def start():
    return addons[0]
