import click
import click_config_file

from apps import GeckoViewExample
from mitmproxy import MITMProxy


@click.command()
@click.option("--record/--replay", default=False)
@click.option("--certutil", required=True, help="Path to certutil.")
@click.option("--url", default="about:blank", help="Site to load.")
@click.argument("path")
@click_config_file.configuration_option()
def cli(record, certutil, url, path):
    with MITMProxy(path, record) as proxy:
        app = GeckoViewExample(certutil, proxy.cert)
        app.start(url)


if __name__ == "__main__":
    cli()
