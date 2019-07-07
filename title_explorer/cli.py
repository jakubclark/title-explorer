import click
from aiohttp import web

from .app import init_app


@click.command()
def main():
    app = init_app()
    web.run_app(app, access_log_format='%a %r %s "%{User-Agent}i"')
