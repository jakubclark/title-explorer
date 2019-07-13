import asyncio
import re

from aiohttp import web
from aiohttp_jinja2 import render_template

from .graph import get_title, insert_to_db
from .json_serializer import dumps, title_to_json

views = web.RouteTableDef()


@views.get('/')
async def index(request: web.Request):
    response = render_template('index.jinja', request, context={})
    return response


@views.get('/search')
async def search(request: web.Request):
    scraper = request.app['movie_scraper']
    params = request.rel_url.query

    if 'title' in params:
        search_str = params['title']
        search_results = await scraper.search_by_title(search_str)

        for i, entry in enumerate(search_results):
            id_ = entry['id']
            url = re.search('.*/search', str(request.url))[0]
            search_results[i]['url'] = f'{url}?id={id_}'

        response = render_template('search.jinja', request, context={
            'search_results': search_results
        })
        return response

    elif 'id' in params:
        id_ = params['id']

        search_results = await get_title(request.app, id_)
        if not search_results:
            result = await scraper.get_title(id_)
            future = insert_to_db(request.app, result.copy())
            asyncio.ensure_future(future)
        else:
            result = title_to_json(search_results)

        response = render_template('title.jinja', request, context={
            'result': result
        })
        return response

    res = {
        'status_code': 400,
        'error': '`title` or `id` is a required parameter'
    }
    status = 400

    return web.json_response(res, status=status, dumps=dumps)
