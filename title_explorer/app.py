import asyncio

import aiotask_context as context
from aiohttp import ClientSession, web

from .middleware import exception_filter, request_id_middleware
from .routes import setup_routes
from .scraper import MovieScraper


async def inject_movie_scraper(app):
    app['movie_scraper'] = MovieScraper(ClientSession())


def init_app():
    loop = asyncio.get_event_loop()
    loop.set_task_factory(context.task_factory)

    app = web.Application(middlewares=[
        request_id_middleware,
        exception_filter
    ])

    app.on_startup.append(inject_movie_scraper)

    setup_routes(app)
    return app
