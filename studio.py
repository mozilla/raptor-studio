import click
import click_config_file


from apps.android.firefox import GeckoViewExample, Fenix, Fennec, RefBrow
from apps.desktop.firefox import DesktopFirefox as Firefox
from apps.desktop.chrome import DesktopChrome as Chrome
from proxy.mitmproxy import MITMProxy202, MITMProxy404
from proxy.webpagereplay import WebPageReplay

APPS = {
    "Firefox": Firefox,
    "GeckoViewExample": GeckoViewExample,
    "Fenix": Fenix,
    "Fennec": Fennec,
    "Refbrow": RefBrow,
    "Chrome": Chrome
}
PROXYS = {"mitm2": MITMProxy202, "mitm": MITMProxy404, "wpr": WebPageReplay}


@click.command()
@click.option(
    "--app", required=True, type=click.Choice(APPS.keys()), help="App to launch."
)
@click.option(
    "--proxy",
    required=True,
    type=click.Choice(PROXYS.keys()),
    help="Proxy Service to use.",
)
@click.option("--record/--replay", default=False)
@click.option("--certutil", help="Path to certutil.")
@click.option("--url", default="about:blank", help="Site to load.")
@click.argument("path")
@click_config_file.configuration_option()
def cli(app, proxy, record, certutil, url, path):
    with PROXYS[proxy](path=path, mode="record" if record else "replay") as proxy:
        app = APPS[app](proxy, certutil)
        app.start(url)


if __name__ == "__main__":
    cli()
