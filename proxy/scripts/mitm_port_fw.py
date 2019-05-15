from mitmproxy import ctx, http

portmap = [None]


def load(loader):
    ctx.log.info("Init MitmProxy port Forwarder")
    loader.add_option(name="portmap", typespec=str, default="", help="Port map")


def ensure_portmap(ctx):
    # Turn string list of integers `' x: y,z :w '` into `{x: y, z: w}`.
    global portmap

    if portmap[0] is None:
        portmap[0] = {}
        ctx.log.info("%s " % ctx.options.portmap.strip().split(","))
        for pair in ctx.options.portmap.strip().split(","):
            ctx.log.info("%s " % pair.split(":"))
            old, new = pair.split(":")
            old = int(old.strip())
            new = int(new.strip())
            portmap[0][old] = new

    return portmap[0]


def request(flow):
    # Consumers can use this to know the proxy is ready to service requests.
    if flow.request.pretty_url == "{}/mitmdump-generate-200".format(
        ctx.options.listen_host
    ):
        flow.response = http.HTTPResponse.make(200)


def serverconnect(server_conn):
    ctx.log.info("serverconnect")
    address = ctx.options.listen_host
    if server_conn.address == address:
        return

    old_address = server_conn.address
    old_port = old_address[1]
    new_port = ensure_portmap(ctx).get(old_port)
    if new_port:
        server_conn.address = (address, new_port)
    ctx.log.info(
        "{}:{} -> {}:{}".format(
            old_address[0],
            old_address[1],
            server_conn.address[0],
            server_conn.address[1],
        )
    )
