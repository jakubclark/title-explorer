import asyncio

import aiotask_context as context
from aiohttp import ClientSession, web
from aiohttp_jinja2 import setup as jinja_setup
from jinja2 import FileSystemLoader
from neo4j import GraphDatabase

from .config import Config
from .middleware import exception_filter, request_id_middleware
from .routes import setup_routes
from .scraper import MovieScraper


async def inject_dependencies(app):
    config = app['config']
    jinja_setup(app, loader=FileSystemLoader('./templates'))
    app['movie_scraper'] = MovieScraper(ClientSession())
    app['neo4j_driver'] = GraphDatabase.driver(config.neo4j_host, auth=config.neo4j_auth)


def init_app():
    loop = asyncio.get_event_loop()
    loop.set_task_factory(context.task_factory)

    app = web.Application(middlewares=[
        request_id_middleware,
        exception_filter
    ])
    app['config'] = Config()
    app.on_startup.append(inject_dependencies)

    setup_routes(app)
    return app
