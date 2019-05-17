import click
import click_config_file

from apps import Firefox, GeckoViewExample, Fenix, Fennec, RefBrow, Chrome
from mitmproxy import MITMProxy

APPS = {
    "Firefox": Firefox,
    "GeckoViewExample": GeckoViewExample,
    "Fenix": Fenix,
    "Fennec": Fennec,
    "Refbrow": RefBrow,
}


@click.command()
@click.option(
    "--app", required=True, type=click.Choice(APPS.keys()), help="App to launch."
)
@click.option("--record/--replay", default=False)
@click.option("--certutil", help="Path to certutil.")
@click.option("--url", default="about:blank", help="Site to load.")
@click.argument("path")
@click_config_file.configuration_option()
def cli(app, record, certutil, url, path):
    with MITMProxy(path, record) as proxy:
        app = APPS[app](proxy, certutil)
        app.start(url)


if __name__ == "__main__":
    cli()
