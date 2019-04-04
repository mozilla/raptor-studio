import click
import click_config_file

from apps import Firefox, GeckoViewExample, Chrome
from mitmproxy import MITMProxy

APPS = {"Firefox": Firefox, "GeckoViewExample": GeckoViewExample, "Chrome": Chrome}


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
        with APPS[app](proxy, record, path, url=url, certutil=certutil) as app:
            # hit Enter while running to take the screenshot and stop the process
            option = raw_input("Hit Enter or CTRL+F2 while running to take the screenshot and stop the process!\n")
            if option or not option:
                raise KeyboardInterrupt


if __name__ == "__main__":
    cli()
