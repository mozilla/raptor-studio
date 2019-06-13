import datetime
import os
import json

import urllib
from mitmproxy import ctx


class HttpProtocolExtractor:
    def __init__(self):
        self.request_protocol = {}

        ctx.log.info("Init Http Protocol extractor JS")

    def response(self, flow):
        ctx.log.info("Response using protocol: %s" % flow.response.data.http_version)
        self.request_protocol[
            urllib.parse.urlparse(flow.request.url).netloc
        ] = flow.response.data.http_version.decode("utf-8")

    def done(self):
        output_json = {}

        output_json["recording_date"] = str(datetime.datetime.now())
        output_json["http_protocol"] = self.request_protocol

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
