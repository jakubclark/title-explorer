import asyncio
from json.decoder import JSONDecodeError

from aiohttp import web
from jsonschema import ValidationError

from .__version__ import __version__
from .graph import insert_to_db
from .json_serializer import dumps
from .logger import log
from .validator import validate_title_object

routes = web.RouteTableDef()


def setup_routes(app: web.Application):
    try:
        from .scraper_search import routes as scraper_routes
        app.add_routes(scraper_routes)
    except ImportError:
        log.info(f'Could not import `scraper_routes`. Assuming, you don\'t have scraper endpoints')
    app.add_routes(routes)


@routes.post('/api/title')
async def post_title(request: web.Request):
    try:
        json_body = await request.json()
    except JSONDecodeError:
        return web.json_response({
            'error': '`application/json` is expected',
            'status': 400
        }, status=400)

    try:
        validate_title_object(json_body)
    except ValidationError as e:
        return web.json_response({
            'error': 'Invalid title-object',
            'message': e.message,
            'status': 400
        }, status=400)

    future = insert_to_db(request.app, json_body)
    asyncio.ensure_future(future)
    return web.json_response({
        'message': 'Added to the database',
        'status': 200
    })


@routes.get('/api/version')
async def version(request):
    return web.json_response({
        'version': __version__
    }, dumps=dumps)
