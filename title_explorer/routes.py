import asyncio
import re

from aiohttp import web

from .__version__ import __version__
from .graph import insert_to_db
from .json_serializer import dumps
from .logger import log

routes = web.RouteTableDef()


def setup_routes(app: web.Application):
    app.add_routes(routes)


@routes.get('/api/search')
async def search(request):
    scraper = request.app['movie_scraper']
    params = request.rel_url.query

    if 'title' in params:
        # Search by title
        search_str = params['title']
        res = await scraper.search_by_title(search_str)
        for i, entry in enumerate(res):
            id_ = entry['id']
            url = re.search('.*/api/search', str(request.url))[0]
            res[i]['url'] = f'{url}?id={id_}'
        status = 200
    elif 'id' in params:
        # Search by ID
        id_ = params['id']
        res = await scraper.get_title(id_)
        future = insert_to_db(request.app, res.copy())
        asyncio.ensure_future(future)
        status = 200
    else:
        res = {
            'status_code': 400,
            'error': '`title` or `id` is a required parameter'
        }
        status = 400

    return web.json_response(res, status=status, dumps=dumps)


@routes.get('/api/top')
async def get_top_titles(request):
    log.debug('Fetching top IMDb results')
    scraper = request.app['movie_scraper']
    results = await scraper.get_top_results()
    for res in results:
        future = insert_to_db(request.app, res.copy())
        asyncio.ensure_future(future)
    return web.json_response(results, dumps=dumps)


@routes.get('/api/version')
async def version(request):
    return web.json_response({
        'version': __version__
    }, dumps=dumps)
