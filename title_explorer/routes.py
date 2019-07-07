import re

from aiohttp import web

from .__version__ import __version__
from .json_serializer import dumps

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
        res = await scraper.get_movie(id_)
        status = 200
    else:
        res = {
            'status_code': 400,
            'error': '`title` or `id` is a required parameter'
        }
        status = 400

    return web.json_response(res, status=status, dumps=dumps)


@routes.get('/api/version')
async def version(request):
    return web.json_response({
        'version': __version__
    })
