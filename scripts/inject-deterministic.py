from __future__ import absolute_import, print_function

import re
import time
from mitmproxy import ctx


class AddDeterministic():

    def response(self, flow):
        millis = int(round(time.time() * 1000))

        if "content-type" in flow.response.headers:

            if 'text/html' in flow.response.headers["content-type"]:
                ctx.log.info("Working on {}".format(flow.response.headers["content-type"]))

                if "charset=" in flow.response.headers["content-type"]:
                    encoding = flow.response.headers["content-type"].split("charset=")[1]
                else:
                    encoding = "utf-8"

                flow.response.decode()
                html = bytes(flow.response.content).decode(encoding)

                with open("scripts/catapult/deterministic.js", "r") as jsfile:
                    js = jsfile.read().replace("REPLACE_LOAD_TIMESTAMP", str(millis))
                    if js not in html:
                        scriptIndex = re.search('(?i).*?<head.*?>', html)
                        if scriptIndex is None:
                            scriptIndex = re.search('(?i).*?<html.*?>', html)
                        if scriptIndex is None:
                            scriptIndex = re.search('(?i).*?<!doctype html>', html)
                        if scriptIndex is None:
                            ctx.log.info("No start tags found in request {}. Skip injecting".format(flow.request.url))
                            return

                        scriptIndex = scriptIndex.end()

                        new_html = html[:scriptIndex] + "<script>" + js + "</script>" + html[scriptIndex:]

                        flow.response.content = bytes(new_html, encoding)
                        ctx.log.info("In request {} injected deterministic JS".format(flow.request.url))
                    else:
                        ctx.log.info("Script already injected in request {}".format(flow.request.url))

def start():
    ctx.log.info("Load Deterministic JS")
    return AddDeterministic()

